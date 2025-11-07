<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.ts';
	import { api } from '$lib/api.ts';

	let stats = {
		assets: { count: 0, loading: true },
		vulnerabilities: { total: 0, open: 0, open_count: 0, by_severity: {}, loading: true },
		scans: { recent: [], loading: true }
	};

	let cpuUsage = 42;
	let memoryUsage = 68;
	let networkStatus = 92;
	let securityLevel = 75;
	let systemStatus = 85;
	let currentTime = new Date();

	onMount(async () => {
		if (!$authStore.isAuthenticated) {
			goto('/login');
			return;
		}

		// Load stats
		await loadStats();

		// Update time
		const timeInterval = setInterval(() => {
			currentTime = new Date();
		}, 1000);

		// Simulate changing data
		const dataInterval = setInterval(() => {
			cpuUsage = Math.floor(Math.random() * 30) + 30;
			memoryUsage = Math.floor(Math.random() * 20) + 60;
			networkStatus = Math.floor(Math.random() * 15) + 80;
			systemStatus = Math.floor(Math.random() * 10) + 80;
		}, 3000);

		return () => {
			clearInterval(timeInterval);
			clearInterval(dataInterval);
		};
	});

	async function loadStats() {
		try {
			const assetCount = await api.countAssets();
			stats.assets = { count: assetCount.count, loading: false };

			const vulnStats = await api.getVulnerabilityStats();
			stats.vulnerabilities = { ...vulnStats, loading: false };

			const scans = await api.getScans({ limit: 5 });
			stats.scans = { recent: scans, loading: false };
		} catch (error) {
			console.error('Failed to load stats:', error);
		}
	}

	function formatTime(date: Date) {
		return date.toLocaleTimeString('en-US', {
			hour12: false,
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
	}

	function formatDate(date: Date) {
		return date.toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>Dashboard - EASM Platform</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-black to-slate-900">
	<!-- Top Header Bar -->
	<div class="bg-slate-900/50 backdrop-blur-lg border-b border-slate-800/50 sticky top-0 z-40">
		<div class="px-8 py-4">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-2xl font-bold gradient-text">Dashboard</h1>
					<p class="text-sm text-slate-400 mt-1">Attack surface monitoring and threat intelligence</p>
				</div>
				<div class="flex items-center gap-4">
					<div class="text-right">
						<div class="text-xs text-slate-400">Last Updated</div>
						<div class="text-sm font-mono text-slate-300">{formatTime(currentTime)}</div>
					</div>
					<button on:click={loadStats} class="btn btn-primary btn-sm">
						<svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
						</svg>
						Refresh
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Main Content -->
	<div class="p-8">
		<!-- Quick Stats Row -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
			<!-- Total Assets -->
			<div class="card group relative overflow-hidden">
				<div class="flex items-center justify-between mb-2">
					<div class="text-sm text-slate-400">Total Assets</div>
					<div class="icon-box icon-box-primary h-12 w-12">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
						</svg>
					</div>
				</div>
				<div class="text-3xl font-bold bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
					{#if stats.assets.loading}
						<span class="text-slate-600 animate-pulse">...</span>
					{:else}
						{stats.assets.count}
					{/if}
				</div>
				<div class="text-xs text-slate-500 mt-1">Monitored endpoints</div>
				<div class="absolute -bottom-6 -right-6 h-16 w-16 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 opacity-20 blur-xl"></div>
			</div>

			<!-- Open Vulnerabilities -->
			<div class="card group relative overflow-hidden">
				<div class="flex items-center justify-between mb-2">
					<div class="text-sm text-slate-400">Open Vulnerabilities</div>
					<div class="icon-box icon-box-danger h-12 w-12">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
				</div>
				<div class="text-3xl font-bold text-rose-600">
					{#if stats.vulnerabilities.loading}
						<span class="text-slate-600 animate-pulse">...</span>
					{:else}
						{stats.vulnerabilities.open_count || 0}
					{/if}
				</div>
				<div class="text-xs text-slate-500 mt-1">Require attention</div>
				<div class="absolute -bottom-6 -right-6 h-16 w-16 rounded-full bg-gradient-to-r from-red-500 to-rose-500 opacity-20 blur-xl"></div>
			</div>

			<!-- CPU Usage -->
			<div class="card group relative overflow-hidden">
				<div class="flex items-center justify-between mb-2">
					<div class="text-sm text-slate-400">CPU Usage</div>
					<div class="icon-box icon-box-warning h-12 w-12">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
						</svg>
					</div>
				</div>
				<div class="text-3xl font-bold text-cyan-400">
					{cpuUsage}%
				</div>
				<div class="text-xs text-slate-500 mt-1">System load</div>
				<div class="absolute -bottom-6 -right-6 h-16 w-16 rounded-full bg-gradient-to-r from-orange-500 to-amber-500 opacity-20 blur-xl"></div>
			</div>

			<!-- Security Level -->
			<div class="card group relative overflow-hidden">
				<div class="flex items-center justify-between mb-2">
					<div class="text-sm text-slate-400">Security Level</div>
					<div class="icon-box icon-box-success h-12 w-12">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
						</svg>
					</div>
				</div>
				<div class="text-3xl font-bold text-emerald-400">
					{securityLevel}%
				</div>
				<div class="text-xs text-slate-500 mt-1">Protected</div>
				<div class="absolute -bottom-6 -right-6 h-16 w-16 rounded-full bg-gradient-to-r from-emerald-500 to-green-500 opacity-20 blur-xl"></div>
			</div>
		</div>

		<!-- Two Column Layout -->
		<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
			<!-- Left Column - Main Content -->
			<div class="lg:col-span-9 space-y-6">
				<!-- Recent Scans -->
				<div class="card">
					<div class="flex items-center justify-between mb-6">
						<h2 class="text-xl font-bold text-slate-100 flex items-center">
							<svg class="mr-2 h-5 w-5 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
							</svg>
							Recent Scans
						</h2>
						<div class="flex items-center space-x-2">
							<span class="badge badge-info text-xs">
								<div class="h-1.5 w-1.5 rounded-full bg-cyan-500 mr-1 animate-pulse"></div>
								LIVE
							</span>
							<a href="/scans" class="text-sm font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
								View all
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
								</svg>
							</a>
						</div>
					</div>

					{#if stats.scans.loading}
						<div class="space-y-3">
							{#each Array(3) as _}
								<div class="h-16 bg-slate-800/30 rounded-xl animate-pulse"></div>
							{/each}
						</div>
					{:else if stats.scans.recent.length === 0}
						<div class="text-center py-8">
							<p class="text-slate-500">No scans yet</p>
							<a href="/scans" class="btn btn-primary mt-4">Start First Scan</a>
						</div>
					{:else}
						<div class="space-y-3">
							{#each stats.scans.recent as scan}
								<div class="flex items-center justify-between p-4 bg-slate-800/30 rounded-xl hover:bg-slate-800/50 transition-all border border-slate-700/30">
									<div class="flex-1">
										<p class="font-semibold text-slate-200">{scan.target}</p>
										<p class="text-xs text-slate-500 mt-1 font-mono">
											{new Date(scan.created_at).toLocaleString()}
										</p>
									</div>
									<span class="badge badge-{scan.status === 'completed' ? 'success' : scan.status === 'running' ? 'info' : 'gray'}">
										{scan.status}
									</span>
								</div>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Vulnerability Breakdown -->
				<div class="card">
					<h2 class="text-xl font-bold text-slate-100 mb-6 flex items-center">
						<svg class="mr-2 h-5 w-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
						</svg>
						Vulnerability Breakdown
					</h2>

					{#if stats.vulnerabilities.loading}
						<div class="space-y-3">
							{#each Array(4) as _}
								<div class="h-12 bg-slate-800/30 rounded-xl animate-pulse"></div>
							{/each}
						</div>
					{:else}
						<div class="space-y-4">
							{#each Object.entries(stats.vulnerabilities.by_severity || {}) as [severity, count]}
								<div class="group">
									<div class="flex items-center justify-between mb-2">
										<span class="badge badge-{severity.toLowerCase()} text-sm">{severity.toUpperCase()}</span>
										<span class="text-2xl font-bold text-slate-100">{count}</span>
									</div>
									<div class="h-2 bg-slate-800/50 rounded-full overflow-hidden border border-slate-700/30">
										<div
											class="h-full rounded-full {severity === 'critical' ? 'bg-gradient-to-r from-purple-500 to-purple-600' : severity === 'high' ? 'bg-gradient-to-r from-red-500 to-rose-600' : severity === 'medium' ? 'bg-gradient-to-r from-orange-500 to-amber-600' : 'bg-gradient-to-r from-yellow-500 to-yellow-600'} transition-all duration-500"
											style="width: {Math.min((count / Math.max(...Object.values(stats.vulnerabilities.by_severity || {})) * 100), 100)}%"
										></div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Right Column - Sidebar -->
			<div class="lg:col-span-3 space-y-6">
				<!-- System Time -->
				<div class="card overflow-hidden p-0">
					<div class="bg-gradient-to-br from-slate-800 to-slate-900 p-6 border-b border-slate-700/50">
						<div class="text-center">
							<div class="text-xs text-slate-500 mb-1 font-mono">SYSTEM TIME</div>
							<div class="text-3xl font-mono text-cyan-400 mb-1">{formatTime(currentTime)}</div>
							<div class="text-sm text-slate-400">{formatDate(currentTime)}</div>
						</div>
					</div>
					<div class="p-4">
						<div class="grid grid-cols-2 gap-3">
							<div class="bg-slate-800/50 rounded-md p-3 border border-slate-700/50">
								<div class="text-xs text-slate-500 mb-1">Uptime</div>
								<div class="text-sm font-mono text-slate-200">14d 06:42</div>
							</div>
							<div class="bg-slate-800/50 rounded-md p-3 border border-slate-700/50">
								<div class="text-xs text-slate-500 mb-1">Status</div>
								<div class="text-sm font-mono text-emerald-400">ACTIVE</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Quick Actions -->
				<div class="card">
					<h3 class="text-base font-bold text-slate-100 mb-4">Quick Actions</h3>
					<div class="grid grid-cols-2 gap-3">
						<a href="/assets/new" class="btn btn-secondary h-auto py-3 px-3 flex flex-col items-center justify-center space-y-1 w-full">
							<svg class="h-5 w-5 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							<span class="text-xs">Add Asset</span>
						</a>

						<a href="/scans" class="btn btn-secondary h-auto py-3 px-3 flex flex-col items-center justify-center space-y-1 w-full">
							<svg class="h-5 w-5 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							<span class="text-xs">Scan</span>
						</a>

						<a href="/vulnerabilities" class="btn btn-secondary h-auto py-3 px-3 flex flex-col items-center justify-center space-y-1 w-full">
							<svg class="h-5 w-5 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
							</svg>
							<span class="text-xs">Review</span>
						</a>

						<a href="/assets" class="btn btn-secondary h-auto py-3 px-3 flex flex-col items-center justify-center space-y-1 w-full">
							<svg class="h-5 w-5 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
							</svg>
							<span class="text-xs">Assets</span>
						</a>
					</div>
				</div>

				<!-- Security Status -->
				<div class="card">
					<h3 class="text-base font-bold text-slate-100 mb-4 flex items-center">
						<svg class="mr-2 h-5 w-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
						</svg>
						Security Status
					</h3>
					<div class="space-y-3">
						<div class="flex items-center justify-between">
							<div class="text-sm text-slate-400">Firewall</div>
							<span class="badge badge-success">Active</span>
						</div>
						<div class="flex items-center justify-between">
							<div class="text-sm text-slate-400">Intrusion Detection</div>
							<span class="badge badge-success">Active</span>
						</div>
						<div class="flex items-center justify-between">
							<div class="text-sm text-slate-400">Encryption</div>
							<span class="badge badge-success">Active</span>
						</div>
						<div class="pt-2 mt-2 border-t border-slate-700/50">
							<div class="flex items-center justify-between mb-2">
								<div class="text-sm font-medium text-slate-300">Security Level</div>
								<div class="text-sm text-cyan-400">{securityLevel}%</div>
							</div>
							<div class="h-2 bg-slate-800/50 rounded-full overflow-hidden">
								<div
									class="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full"
									style="width: {securityLevel}%"
								></div>
							</div>
						</div>
					</div>
				</div>

				<!-- System Resources -->
				<div class="card">
					<h3 class="text-base font-bold text-slate-100 mb-4">System Resources</h3>
					<div class="space-y-4">
						<div>
							<div class="flex items-center justify-between mb-1">
								<div class="text-sm text-slate-400">CPU</div>
								<div class="text-xs text-cyan-400">{cpuUsage}%</div>
							</div>
							<div class="h-2 bg-slate-800/50 rounded-full overflow-hidden">
								<div
									class="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
									style="width: {cpuUsage}%"
								></div>
							</div>
						</div>

						<div>
							<div class="flex items-center justify-between mb-1">
								<div class="text-sm text-slate-400">Memory</div>
								<div class="text-xs text-purple-400">{memoryUsage}%</div>
							</div>
							<div class="h-2 bg-slate-800/50 rounded-full overflow-hidden">
								<div
									class="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
									style="width: {memoryUsage}%"
								></div>
							</div>
						</div>

						<div>
							<div class="flex items-center justify-between mb-1">
								<div class="text-sm text-slate-400">Network</div>
								<div class="text-xs text-blue-400">{networkStatus}%</div>
							</div>
							<div class="h-2 bg-slate-800/50 rounded-full overflow-hidden">
								<div
									class="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"
									style="width: {networkStatus}%"
								></div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
