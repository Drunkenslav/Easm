<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.ts';
	import { api } from '$lib/api.ts';

	let stats = {
		assets: { count: 0, loading: true },
		vulnerabilities: { total: 0, open: 0, by_severity: {}, loading: true },
		scans: { recent: [], loading: true }
	};

	onMount(async () => {
		if (!$authStore.isAuthenticated) {
			goto('/login');
			return;
		}

		await loadStats();
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
</script>

<svelte:head>
	<title>Dashboard - EASM Platform</title>
</svelte:head>

<div class="min-h-screen">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header with Gradient -->
		<div class="mb-10 fade-in">
			<h1 class="text-4xl font-bold gradient-text mb-2">Attack Surface Dashboard</h1>
			<p class="text-lg text-gray-600">Real-time overview of your security posture</p>
		</div>

		<!-- Stats Grid with Modern Cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10 fade-in">
			<!-- Total Assets -->
			<div class="stat-card group">
				<div class="flex items-center justify-between relative z-10">
					<div>
						<p class="text-sm font-semibold text-gray-600 mb-1">Total Assets</p>
						<p class="text-4xl font-bold text-gray-900">
							{#if stats.assets.loading}
								<span class="text-gray-400 animate-pulse">...</span>
							{:else}
								{stats.assets.count}
							{/if}
						</p>
						<p class="text-xs text-gray-500 mt-1">Monitored endpoints</p>
					</div>
					<div class="icon-box icon-box-primary">
						<svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
						</svg>
					</div>
				</div>
			</div>

			<!-- Open Vulnerabilities -->
			<div class="stat-card group">
				<div class="flex items-center justify-between relative z-10">
					<div>
						<p class="text-sm font-semibold text-gray-600 mb-1">Open Vulnerabilities</p>
						<p class="text-4xl font-bold text-rose-600">
							{#if stats.vulnerabilities.loading}
								<span class="text-gray-400 animate-pulse">...</span>
							{:else}
								{stats.vulnerabilities.open_count}
							{/if}
						</p>
						<p class="text-xs text-gray-500 mt-1">Require attention</p>
					</div>
					<div class="icon-box icon-box-danger">
						<svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
				</div>
			</div>

			<!-- Critical Severity -->
			<div class="stat-card group">
				<div class="flex items-center justify-between relative z-10">
					<div>
						<p class="text-sm font-semibold text-gray-600 mb-1">Critical Severity</p>
						<p class="text-4xl font-bold text-purple-600">
							{#if stats.vulnerabilities.loading}
								<span class="text-gray-400 animate-pulse">...</span>
							{:else}
								{stats.vulnerabilities.by_severity?.critical || 0}
							{/if}
						</p>
						<p class="text-xs text-gray-500 mt-1">Immediate action needed</p>
					</div>
					<div class="icon-box icon-box-purple">
						<svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
						</svg>
					</div>
				</div>
			</div>

			<!-- High Severity -->
			<div class="stat-card group">
				<div class="flex items-center justify-between relative z-10">
					<div>
						<p class="text-sm font-semibold text-gray-600 mb-1">High Severity</p>
						<p class="text-4xl font-bold text-orange-600">
							{#if stats.vulnerabilities.loading}
								<span class="text-gray-400 animate-pulse">...</span>
							{:else}
								{stats.vulnerabilities.by_severity?.high || 0}
							{/if}
						</p>
						<p class="text-xs text-gray-500 mt-1">Priority fixes</p>
					</div>
					<div class="icon-box icon-box-warning">
						<svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
				</div>
			</div>
		</div>

		<!-- Activity Section -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10 fade-in">
			<!-- Recent Scans -->
			<div class="card">
				<div class="flex items-center justify-between mb-6">
					<h2 class="text-xl font-bold text-gray-900">Recent Scans</h2>
					<a href="/scans" class="text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1">
						View all
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
						</svg>
					</a>
				</div>

				{#if stats.scans.loading}
					<div class="space-y-3">
						{#each Array(3) as _}
							<div class="h-16 bg-gray-100/50 rounded-xl animate-pulse"></div>
						{/each}
					</div>
				{:else if stats.scans.recent.length === 0}
					<div class="text-center py-8">
						<p class="text-gray-500">No scans yet</p>
						<a href="/scans" class="btn btn-primary mt-4">Start First Scan</a>
					</div>
				{:else}
					<div class="space-y-3">
						{#each stats.scans.recent as scan}
							<div class="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50/50 to-transparent rounded-xl hover:from-blue-50/50 transition-all border border-gray-100/50">
								<div class="flex-1">
									<p class="font-semibold text-gray-900">{scan.target}</p>
									<p class="text-xs text-gray-500 mt-1">
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
				<h2 class="text-xl font-bold text-gray-900 mb-6">Vulnerability Breakdown</h2>

				{#if stats.vulnerabilities.loading}
					<div class="space-y-3">
						{#each Array(4) as _}
							<div class="h-12 bg-gray-100/50 rounded-xl animate-pulse"></div>
						{/each}
					</div>
				{:else}
					<div class="space-y-4">
						{#each Object.entries(stats.vulnerabilities.by_severity || {}) as [severity, count]}
							<div class="group">
								<div class="flex items-center justify-between mb-2">
									<span class="badge badge-{severity.toLowerCase()} text-sm">{severity.toUpperCase()}</span>
									<span class="text-2xl font-bold text-gray-900">{count}</span>
								</div>
								<div class="h-2 bg-gray-100 rounded-full overflow-hidden">
									<div 
										class="h-full bg-gradient-to-r {severity === 'critical' ? 'from-purple-500 to-purple-600' : severity === 'high' ? 'from-red-500 to-rose-600' : severity === 'medium' ? 'from-orange-500 to-amber-600' : 'from-yellow-500 to-yellow-600'} rounded-full transition-all duration-500"
										style="width: {Math.min((count / Math.max(...Object.values(stats.vulnerabilities.by_severity || {})) * 100), 100)}%"
									></div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="fade-in">
			<h2 class="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<a href="/assets/new" class="card card-hover group cursor-pointer">
					<div class="flex items-center gap-4">
						<div class="icon-box icon-box-primary">
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
						</div>
						<div>
							<p class="font-bold text-gray-900 group-hover:text-blue-600 transition-colors">Add Asset</p>
							<p class="text-sm text-gray-600">Register new endpoint</p>
						</div>
					</div>
				</a>

				<a href="/scans" class="card card-hover group cursor-pointer">
					<div class="flex items-center gap-4">
						<div class="icon-box icon-box-success">
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
						</div>
						<div>
							<p class="font-bold text-gray-900 group-hover:text-emerald-600 transition-colors">Trigger Scan</p>
							<p class="text-sm text-gray-600">Start vulnerability scan</p>
						</div>
					</div>
				</a>

				<a href="/vulnerabilities" class="card card-hover group cursor-pointer">
					<div class="flex items-center gap-4">
						<div class="icon-box icon-box-warning">
							<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
							</svg>
						</div>
						<div>
							<p class="font-bold text-gray-900 group-hover:text-orange-600 transition-colors">Review Findings</p>
							<p class="text-sm text-gray-600">Triage vulnerabilities</p>
						</div>
					</div>
				</a>
			</div>
		</div>
	</div>
</div>
