<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { formatDate, formatRelativeTime, getSeverityClass } from '$lib/utils';

	let assetId: number;
	let asset: any = null;
	let vulnerabilities: any[] = [];
	let scans: any[] = [];
	let loading = true;

	$: assetId = parseInt($page.params.id);

	onMount(async () => {
		await Promise.all([
			loadAsset(),
			loadVulnerabilities(),
			loadScans()
		]);
	});

	async function loadAsset() {
		try {
			asset = await api.getAssetStats(assetId);
		} catch (error) {
			console.error('Failed to load asset:', error);
		} finally {
			loading = false;
		}
	}

	async function loadVulnerabilities() {
		try {
			vulnerabilities = await api.getVulnerabilities({ asset_id: assetId, limit: 10 });
		} catch (error) {
			console.error('Failed to load vulnerabilities:', error);
		}
	}

	async function loadScans() {
		try {
			scans = await api.getScans({ asset_id: assetId, limit: 5 });
		} catch (error) {
			console.error('Failed to load scans:', error);
		}
	}

	async function triggerScan() {
		try {
			await api.triggerScans([assetId]);
			alert('Scan triggered successfully!');
			await loadScans();
		} catch (error) {
			console.error('Failed to trigger scan:', error);
			alert('Failed to trigger scan');
		}
	}
</script>

<svelte:head>
	<title>Asset #{assetId} - EASM Platform</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<button on:click={() => goto('/assets')} class="text-sm text-gray-500 hover:text-gray-700 mb-2">
				← Back to Assets
			</button>
			<h1 class="text-3xl font-bold text-gray-900">Asset Details</h1>
		</div>
		<button on:click={triggerScan} class="btn btn-primary">
			<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
			</svg>
			Trigger Scan
		</button>
	</div>

	{#if loading}
		<div class="card">
			<p class="text-center text-gray-500 py-8">Loading asset details...</p>
		</div>
	{:else if !asset}
		<div class="card">
			<p class="text-center text-red-500 py-8">Asset not found</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Main Info -->
			<div class="lg:col-span-2 space-y-6">
				<div class="card">
					<h2 class="text-2xl font-bold text-gray-900 mb-4">{asset.value}</h2>
					{#if asset.name}
						<p class="text-gray-600 mb-4">{asset.name}</p>
					{/if}

					<div class="grid grid-cols-2 gap-4">
						<div>
							<span class="text-sm text-gray-500">Type</span>
							<p class="font-medium">{asset.type}</p>
						</div>
						<div>
							<span class="text-sm text-gray-500">Status</span>
							<p><span class="badge {asset.status === 'active' ? 'badge-success' : 'badge-gray'}">{asset.status}</span></p>
						</div>
						<div>
							<span class="text-sm text-gray-500">Criticality</span>
							<p class="font-medium capitalize">{asset.criticality}</p>
						</div>
						<div>
							<span class="text-sm text-gray-500">Last Scanned</span>
							<p class="text-sm">{formatRelativeTime(asset.last_scanned_at)}</p>
						</div>
					</div>

					{#if asset.tags && asset.tags.length > 0}
						<div class="mt-4 pt-4 border-t">
							<span class="text-sm text-gray-500 block mb-2">Tags</span>
							<div class="flex flex-wrap gap-2">
								{#each asset.tags as tag}
									<span class="badge badge-info">{tag}</span>
								{/each}
							</div>
						</div>
					{/if}

					{#if asset.notes}
						<div class="mt-4 pt-4 border-t">
							<span class="text-sm text-gray-500 block mb-2">Notes</span>
							<p class="text-sm text-gray-700">{asset.notes}</p>
						</div>
					{/if}
				</div>

				<!-- Vulnerabilities -->
				<div class="card">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold text-gray-900">Recent Vulnerabilities</h3>
						<a href="/vulnerabilities?asset_id={assetId}" class="text-sm text-primary-600 hover:text-primary-700">
							View all →
						</a>
					</div>

					{#if vulnerabilities.length === 0}
						<p class="text-gray-500 text-center py-4">No vulnerabilities found</p>
					{:else}
						<div class="space-y-3">
							{#each vulnerabilities as vuln}
								<div class="border border-gray-200 rounded-lg p-3">
									<div class="flex items-start justify-between">
										<div class="flex-1">
											<h4 class="font-medium text-gray-900 text-sm">{vuln.name}</h4>
											<p class="text-xs text-gray-500 mt-1">{formatRelativeTime(vuln.created_at)}</p>
										</div>
										<span class="badge {getSeverityClass(vuln.severity)} ml-2">
											{vuln.severity}
										</span>
									</div>
									<button
										on:click={() => goto(`/vulnerabilities/${vuln.id}`)}
										class="text-xs text-primary-600 hover:text-primary-900 mt-2"
									>
										View Details →
									</button>
								</div>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Scans -->
				<div class="card">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold text-gray-900">Recent Scans</h3>
						<a href="/scans?asset_id={assetId}" class="text-sm text-primary-600 hover:text-primary-700">
							View all →
						</a>
					</div>

					{#if scans.length === 0}
						<p class="text-gray-500 text-center py-4">No scans yet</p>
					{:else}
						<div class="space-y-3">
							{#each scans as scan}
								<div class="flex items-center justify-between border-b border-gray-100 pb-3 last:border-0">
									<div>
										<p class="text-sm font-medium text-gray-900">#{scan.id}</p>
										<p class="text-xs text-gray-500">{formatRelativeTime(scan.created_at)}</p>
									</div>
									<div class="flex items-center gap-2">
										<span class="badge {scan.status === 'completed' ? 'badge-success' : scan.status === 'running' ? 'badge-info' : 'badge-gray'}">
											{scan.status}
										</span>
										<button
											on:click={() => goto(`/scans/${scan.id}`)}
											class="text-xs text-primary-600 hover:text-primary-900"
										>
											View
										</button>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Sidebar -->
			<div class="space-y-6">
				<!-- Stats -->
				<div class="card">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Vulnerability Stats</h3>
					<div class="space-y-3">
						<div class="flex justify-between items-center">
							<span class="text-sm text-gray-600">Total</span>
							<span class="text-2xl font-bold text-gray-900">{asset.vulnerability_count}</span>
						</div>
						{#if asset.vulnerability_count_by_severity}
							{#each Object.entries(asset.vulnerability_count_by_severity) as [severity, count]}
								<div class="flex justify-between items-center">
									<span class="badge {getSeverityClass(severity)}">{severity}</span>
									<span class="font-semibold text-gray-900">{count}</span>
								</div>
							{/each}
						{/if}
					</div>
				</div>

				<!-- Metadata -->
				<div class="card">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Metadata</h3>
					<dl class="space-y-3">
						<div>
							<dt class="text-xs font-medium text-gray-500">Discovered</dt>
							<dd class="mt-1 text-sm text-gray-900">{formatDate(asset.discovered_at)}</dd>
						</div>
						<div>
							<dt class="text-xs font-medium text-gray-500">Last Seen</dt>
							<dd class="mt-1 text-sm text-gray-900">{formatDate(asset.last_seen_at)}</dd>
						</div>
						{#if asset.discovery_method}
							<div>
								<dt class="text-xs font-medium text-gray-500">Discovery Method</dt>
								<dd class="mt-1 text-sm text-gray-900">{asset.discovery_method}</dd>
							</div>
						{/if}
					</dl>
				</div>
			</div>
		</div>
	{/if}
</div>
