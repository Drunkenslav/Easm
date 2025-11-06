export function formatDate(dateString: string): string {
	if (!dateString) return 'N/A';
	const date = new Date(dateString);
	return date.toLocaleString();
}

export function formatRelativeTime(dateString: string): string {
	if (!dateString) return 'Never';

	const date = new Date(dateString);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffSecs = Math.floor(diffMs / 1000);
	const diffMins = Math.floor(diffSecs / 60);
	const diffHours = Math.floor(diffMins / 60);
	const diffDays = Math.floor(diffHours / 24);

	if (diffSecs < 60) return 'Just now';
	if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
	if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
	if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

	return formatDate(dateString);
}

export function getSeverityClass(severity: string): string {
	const severityMap: { [key: string]: string } = {
		info: 'badge-info',
		low: 'badge-low',
		medium: 'badge-medium',
		high: 'badge-high',
		critical: 'badge-critical'
	};
	return severityMap[severity.toLowerCase()] || 'badge-gray';
}

export function getStatusClass(status: string): string {
	const statusMap: { [key: string]: string } = {
		completed: 'badge-success',
		running: 'badge-info',
		pending: 'badge-gray',
		failed: 'badge-high',
		cancelled: 'badge-gray'
	};
	return statusMap[status.toLowerCase()] || 'badge-gray';
}

export function getStateClass(state: string): string {
	const stateMap: { [key: string]: string } = {
		new: 'badge-high',
		triaging: 'badge-medium',
		investigating: 'badge-info',
		remediation: 'badge-low',
		resolved: 'badge-success',
		false_positive: 'badge-gray',
		accepted_risk: 'badge-gray'
	};
	return stateMap[state.toLowerCase()] || 'badge-gray';
}

export function formatDuration(seconds: number): string {
	if (!seconds) return 'N/A';

	const hours = Math.floor(seconds / 3600);
	const mins = Math.floor((seconds % 3600) / 60);
	const secs = seconds % 60;

	if (hours > 0) return `${hours}h ${mins}m`;
	if (mins > 0) return `${mins}m ${secs}s`;
	return `${secs}s`;
}
