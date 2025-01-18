import './LoadingSpinner.css';

export function LoadingSpinner() {
    return (
        <div className="loading-container">
            <div className="loading-spinner"></div>
            <span className="loading-text">Loading recipe...</span>
        </div>
    );
} 