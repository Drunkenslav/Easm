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

		// Load dashboard stats
		await loadStats();
	});

	async function loadStats() {
		try {
			// Get asset count
			const assetCount = await api.countAssets();
			stats.assets = { count: assetCount.count, loading: false };

			// Get vulnerability stats
			const vulnStats = await api.getVulnerabilityStats();
			stats.vulnerabilities = { ...vulnStats, loading: false };

			// Get recent scans
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

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
		<p class="mt-2 text-sm text-gray-600">Overview of your attack surface and vulnerabilities</p>
	</div>

	<!-- Stats Grid -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
		<!-- Total Assets -->
		<div class="card">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Total Assets</p>
					<p class="mt-2 text-3xl font-bold text-gray-900">
						{#if stats.assets.loading}
							<span class="text-gray-400">...</span>
						{:else}
							{stats.assets.count}
						{/if}
					</p>
				</div>
				<div class="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
					<svg class="h-6 w-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
					</svg>
				</div>
			</div>
		</div>

		<!-- Open Vulnerabilities -->
		<div class="card">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Open Vulnerabilities</p>
					<p class="mt-2 text-3xl font-bold text-gray-900">
						{#if stats.vulnerabilities.loading}
							<span class="text-gray-400">...</span>
						{:else}
							{stats.vulnerabilities.open_count}
						{/if}
					</p>
				</div>
				<div class="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
					<svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
				</div>
			</div>
		</div>

		<!-- Critical -->
		<div class="card">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Critical Severity</p>
					<p class="mt-2 text-3xl font-bold text-purple-600">
						{#if stats.vulnerabilities.loading}
							<span class="text-gray-400">...</span>
						{:else}
							{stats.vulnerabilities.by_severity?.critical || 0}
						{/if}
					</p>
				</div>
				<div class="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
					<svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
					</svg>
				</div>
			</div>
		</div>

		<!-- High -->
		<div class="card">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">High Severity</p>
					<p class="mt-2 text-3xl font-bold text-red-600">
						{#if stats.vulnerabilities.loading}
							<span class="text-gray-400">...</span>
						{:else}
							{stats.vulnerabilities.by_severity?.high || 0}
						{/if}
					</p>
				</div>
				<div class="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
					<svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
			</div>
		</div>
	</div>

	<!-- Recent Activity -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Recent Scans -->
		<div class="card">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-lg font-semibold text-gray-900">Recent Scans</h2>
				<a href="/scans" class="text-sm text-primary-600 hover:text-primary-700">View all →</a>
			</div>

			{#if stats.scans.loading}
				<p class="text-gray-500">Loading...</p>
			{:else if stats.scans.recent.length === 0}
				<p class="text-gray-500">No scans yet</p>
			{:else}
				<div class="space-y-3">
					{#each stats.scans.recent as scan}
						<div class="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
							<div class="flex-1">
								<p class="text-sm font-medium text-gray-900">{scan.target}</p>
								<p class="text-xs text-gray-500">{new Date(scan.created_at).toLocaleString()}</p>
							</div>
							<span class="badge {scan.status === 'completed' ? 'badge-success' : scan.status === 'running' ? 'badge-info' : 'badge-gray'}">
								{scan.status}
							</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Vulnerability Breakdown -->
		<div class="card">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Vulnerability Breakdown</h2>

			{#if stats.vulnerabilities.loading}
				<p class="text-gray-500">Loading...</p>
			{:else}
				<div class="space-y-3">
					{#each Object.entries(stats.vulnerabilities.by_severity || {}) as [severity, count]}
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-2">
								<span class="badge badge-{severity.toLowerCase()}">{severity}</span>
							</div>
							<span class="text-lg font-semibold text-gray-900">{count}</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>

	<!-- Quick Actions -->
	<div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
		<a href="/assets/new" class="card hover:shadow-lg transition-shadow cursor-pointer">
			<div class="flex items-center gap-4">
				<div class="h-10 w-10 bg-primary-100 rounded-lg flex items-center justify-center">
					<svg class="h-5 w-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
				</div>
				<div>
					<p class="font-medium text-gray-900">Add Asset</p>
					<p class="text-sm text-gray-600">Register new asset for scanning</p>
				</div>
			</div>
		</a>

		<a href="/scans" class="card hover:shadow-lg transition-shadow cursor-pointer">
			<div class="flex items-center gap-4">
				<div class="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
					<svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
					</svg>
				</div>
				<div>
					<p class="font-medium text-gray-900">Trigger Scan</p>
					<p class="text-sm text-gray-600">Start vulnerability scanning</p>
				</div>
			</div>
		</a>

		<a href="/vulnerabilities" class="card hover:shadow-lg transition-shadow cursor-pointer">
			<div class="flex items-center gap-4">
				<div class="h-10 w-10 bg-orange-100 rounded-lg flex items-center justify-center">
					<svg class="h-5 w-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
					</svg>
				</div>
				<div>
					<p class="font-medium text-gray-900">Review Findings</p>
					<p class="text-sm text-gray-600">Triage vulnerabilities</p>
				</div>
			</div>
		</a>
	</div>
</div>
