from setuptools import setup, find_packages

setup(
    name="ramshare-agent",
    version="1.0.0",
    description="RAMShare Provider Agent - Share computer CPU & RAM securely",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "psutil>=6.0.0",
        "docker>=7.0.0",
        "httpx>=0.27.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ramshare-agent=agent.main:cli",
        ],
    },
)
