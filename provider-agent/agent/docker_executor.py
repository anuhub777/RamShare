import os
import json
import time
import shutil
import logging
import subprocess
import tempfile
from typing import Dict, Any, Optional

logger = logging.getLogger("ramshare.agent.executor")

APPROVED_IMAGES = {
    "CPU_BENCHMARK": "ramshare/cpu-benchmark:latest",
    "MEMORY_BENCHMARK": "ramshare/memory-benchmark:latest",
    "DATA_PROCESSING": "ramshare/data-processing:latest",
    "ML_INFERENCE": "ramshare/ml-inference:latest",
}

class DockerExecutor:
    def __init__(self, storage_dir: Optional[str] = None):
        # Default to system /tmp to avoid macOS ~/Downloads TCC mount restrictions
        if storage_dir is None:
            storage_dir = os.path.join(tempfile.gettempdir(), "ramshare-workloads")
        self.storage_dir = os.path.abspath(storage_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
        self._docker_client = None
        self._has_docker_sdk = None

    def _get_client(self):
        if self._has_docker_sdk is False:
            return None
        if self._docker_client is None:
            try:
                import docker
                self._docker_client = docker.from_env()
                self._has_docker_sdk = True
            except Exception as e:
                self._has_docker_sdk = False
                logger.debug(f"Python docker SDK unavailable ({e}); will use docker CLI fallback.")
                return None
        return self._docker_client

    def is_docker_available(self) -> bool:
        # Check Python SDK first
        client = self._get_client()
        if client:
            try:
                if client.ping():
                    return True
            except Exception:
                pass

        # Fallback to system docker CLI binary
        docker_bin = shutil.which("docker")
        if not docker_bin:
            return False

        try:
            res = subprocess.run([docker_bin, "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def _get_command(self, workload_type: str, params: Dict[str, Any]) -> str:
        """Command executed inside container for each predefined workload type."""
        if workload_type == "CPU_BENCHMARK":
            iterations = int(params.get("iterations", 50000))
            return f"python3 -c \"import math, json, os, time; start=time.time(); [math.factorial(400) for _ in range({iterations})]; el=time.time()-start; res={{'status': 'complete', 'iterations': {iterations}, 'elapsed_seconds': round(el,3)}}; os.makedirs('/output', exist_ok=True); json.dump(res, open('/output/result.json', 'w')) if os.path.isdir('/output') else None; print(json.dumps(res))\""

        elif workload_type == "MEMORY_BENCHMARK":
            size_mb = min(int(params.get("size_mb", 256)), 2048)
            return f"python3 -c \"import json, os, time; start=time.time(); b=bytearray({size_mb}*1024*1024); el=time.time()-start; res={{'status': 'complete', 'allocated_mb': {size_mb}, 'elapsed_seconds': round(el,3)}}; del b; os.makedirs('/output', exist_ok=True); json.dump(res, open('/output/result.json', 'w')) if os.path.isdir('/output') else None; print(json.dumps(res))\""

        elif workload_type == "DATA_PROCESSING":
            return 'python3 -c "import json, os, time; start=time.time(); raw=os.environ.get(\'WORKLOAD_PARAMS\'); params=json.loads(raw) if raw else (json.load(open(\'/input/params.json\')) if os.path.exists(\'/input/params.json\') else {}); res={k: str(v).upper() if isinstance(v, str) else v*2 if isinstance(v, (int,float)) else v for k,v in params.items()}; res[\'_processed_at\']=round(time.time()-start,4); out={\'status\': \'complete\', \'processed_data\': res}; os.makedirs(\'/output\', exist_ok=True); json.dump(out, open(\'/output/result.json\', \'w\')) if os.path.isdir(\'/output\') else None; print(json.dumps(out))"'

        elif workload_type == "ML_INFERENCE":
            samples = int(params.get("num_samples", 10))
            return f"python3 -c \"import json, os, random, time; start=time.time(); random.seed(42); preds=[round(random.gauss(0.5, 0.15), 4) for _ in range({samples})]; conf=[round(random.uniform(0.75, 0.99), 3) for _ in range({samples})]; res={{'status': 'complete', 'model': 'ramshare-classifier-v1', 'predictions': preds, 'confidence': conf, 'num_samples': {samples}, 'elapsed_seconds': round(time.time()-start, 3)}}; os.makedirs('/output', exist_ok=True); json.dump(res, open('/output/result.json', 'w')) if os.path.isdir('/output') else None; print(json.dumps(res))\""

        return "echo 'Unknown workload'"

    def execute_workload(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes job inside isolated container enforcing all security constraints:
        - non-root user (nobody)
        - network disabled
        - dropped all capabilities
        - strict cpu_quota and mem_limit
        - execution timeout
        - guaranteed container cleanup
        """
        job_id = job.get("id", "temp")
        workload_type = job.get("workload_type")
        if workload_type not in APPROVED_IMAGES:
            return {
                "success": False,
                "output": "",
                "execution_time": 0.0,
                "error": f"Unknown or disallowed workload type: {workload_type}"
            }

        # Workload directory in /tmp
        job_dir = os.path.join(self.storage_dir, job_id)
        input_dir = os.path.join(job_dir, "input")
        output_dir = os.path.join(job_dir, "output")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        params = job.get("input_params") or {}
        params_json_str = json.dumps(params)
        with open(os.path.join(input_dir, "params.json"), "w") as f:
            f.write(params_json_str)

        required_ram_mb = max(128, int(job.get("required_ram_mb", 512)))
        required_cpu_cores = max(1, int(job.get("required_cpu_cores", 1)))
        max_execution_time = min(3600, max(10, int(job.get("max_execution_time", 300))))

        image_name = APPROVED_IMAGES[workload_type]
        start_time = time.time()

        # Try Python Docker SDK first if available
        client = self._get_client()
        if client is not None:
            container = None
            try:
                try:
                    client.images.get(image_name)
                except Exception:
                    fallback_image = "python:3.11-slim"
                    try:
                        client.images.get(fallback_image)
                        image_name = fallback_image
                    except Exception:
                        client.images.pull(fallback_image)
                        image_name = fallback_image

                cmd = self._get_command(workload_type, params)
                container = client.containers.run(
                    image=image_name,
                    command=f"/bin/sh -c {cmd}",
                    detach=True,
                    mem_limit=f"{required_ram_mb}m",
                    cpu_period=100000,
                    cpu_quota=int(required_cpu_cores * 100000),
                    privileged=False,
                    network_disabled=True,
                    user="nobody",
                    cap_drop=["ALL"],
                    security_opt=["no-new-privileges:true"],
                    volumes={
                        os.path.abspath(input_dir): {"bind": "/input", "mode": "ro"},
                        os.path.abspath(output_dir): {"bind": "/output", "mode": "rw"},
                    },
                    environment={
                        "WORKLOAD_TYPE": workload_type,
                        "WORKLOAD_PARAMS": params_json_str,
                        "JOB_ID": job_id
                    },
                    tmpfs={"/tmp": "size=64M,noexec"},
                    remove=False
                )

                status_result = container.wait(timeout=max_execution_time)
                elapsed = time.time() - start_time
                logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")

                result_file = os.path.join(output_dir, "result.json")
                output_data = ""
                if os.path.exists(result_file):
                    try:
                        with open(result_file, "r") as f:
                            output_data = f.read()
                    except Exception:
                        pass

                exit_code = status_result.get("StatusCode", -1)
                return {
                    "success": (exit_code == 0),
                    "output": output_data or logs[:4000],
                    "execution_time": round(elapsed, 2),
                    "error": None if exit_code == 0 else f"Container exited with code {exit_code}"
                }
            except Exception as e:
                logger.debug(f"Python SDK run exception: {e}; attempting CLI.")
            finally:
                if container:
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass

        # Fallback to system Docker CLI binary
        docker_bin = shutil.which("docker")
        if not docker_bin:
            return {
                "success": False,
                "output": "",
                "execution_time": round(time.time() - start_time, 2),
                "error": "Docker CLI not found on provider system. Please install or start Docker."
            }

        cmd_payload = self._get_command(workload_type, params)
        run_image = "python:3.11-slim"

        # Attempt with /tmp host volume mounts
        docker_args = [
            docker_bin, "run", "--rm",
            "--network", "none",
            "--user", "nobody",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",
            "--memory", f"{required_ram_mb}m",
            "--cpus", str(required_cpu_cores),
            "-v", f"{os.path.abspath(input_dir)}:/input:ro",
            "-v", f"{os.path.abspath(output_dir)}:/output:rw",
            "--tmpfs", "/tmp:size=64M,noexec",
            "-e", f"WORKLOAD_TYPE={workload_type}",
            "-e", f"WORKLOAD_PARAMS={params_json_str}",
            "-e", f"JOB_ID={job_id}",
            run_image,
            "/bin/sh", "-c", cmd_payload
        ]

        try:
            res = subprocess.run(
                docker_args,
                capture_output=True,
                text=True,
                timeout=max_execution_time
            )

            # If macOS blocked host mount (/host_mnt permission error), retry without host volume mounts
            if res.returncode != 0 and ("mount" in res.stderr.lower() or "operation not permitted" in res.stderr.lower()):
                logger.info("Host volume mount restricted by OS; falling back to self-contained container execution.")
                no_mount_args = [
                    docker_bin, "run", "--rm",
                    "--network", "none",
                    "--user", "nobody",
                    "--cap-drop", "ALL",
                    "--security-opt", "no-new-privileges:true",
                    "--memory", f"{required_ram_mb}m",
                    "--cpus", str(required_cpu_cores),
                    "--tmpfs", "/tmp:size=64M,noexec",
                    "-e", f"WORKLOAD_TYPE={workload_type}",
                    "-e", f"WORKLOAD_PARAMS={params_json_str}",
                    "-e", f"JOB_ID={job_id}",
                    run_image,
                    "/bin/sh", "-c", cmd_payload
                ]
                res = subprocess.run(
                    no_mount_args,
                    capture_output=True,
                    text=True,
                    timeout=max_execution_time
                )

            elapsed = time.time() - start_time
            result_file = os.path.join(output_dir, "result.json")
            output_data = ""
            if os.path.exists(result_file):
                try:
                    with open(result_file, "r") as f:
                        output_data = f.read()
                except Exception:
                    pass

            # Output is either the result file or JSON from stdout
            output_content = output_data or res.stdout.strip()

            if res.returncode == 0:
                return {
                    "success": True,
                    "output": output_content[:4000],
                    "execution_time": round(elapsed, 2),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "output": res.stdout[:4000],
                    "execution_time": round(elapsed, 2),
                    "error": res.stderr[:2000] or f"Process exited with code {res.returncode}"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "execution_time": round(time.time() - start_time, 2),
                "error": f"Workload timed out after {max_execution_time} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "execution_time": round(time.time() - start_time, 2),
                "error": f"Docker execution error: {str(e)}"
            }

    def cleanup_job(self, job_id: str):
        job_dir = os.path.join(self.storage_dir, job_id)
        if os.path.exists(job_dir):
            shutil.rmtree(job_dir, ignore_errors=True)
