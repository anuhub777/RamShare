import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="card p-6 m-6 text-center text-red-400">
          <h2 className="text-lg font-bold mb-2">Something went wrong</h2>
          <p className="text-sm text-slate-300">{this.state.error?.message || 'Unexpected application error'}</p>
        </div>
      );
    }
    return this.props.children;
  }
}
