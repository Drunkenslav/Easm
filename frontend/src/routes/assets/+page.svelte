<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api.ts';
	import { formatRelativeTime, getSeverityClass } from '$lib/utils.ts';

	let assets: any[] = [];
	let loading = true;

	onMount(async () => {
		await loadAssets();
	});

	async function loadAssets() {
		try {
			loading = true;
			assets = await api.getAssets({ limit: 100 });
		} catch (error) {
			console.error('Failed to load assets:', error);
		} finally {
			loading = false;
		}
	}

	async function deleteAsset(id: number) {
		if (!confirm('Are you sure you want to delete this asset?')) return;

		try {
			await api.deleteAsset(id);
			await loadAssets();
		} catch (error) {
			console.error('Failed to delete asset:', error);
			alert('Failed to delete asset');
		}
	}

	async function triggerScan(assetId: number) {
		try {
			await api.triggerScans([assetId]);
			alert('Scan triggered successfully!');
		} catch (error) {
			console.error('Failed to trigger scan:', error);
			alert('Failed to trigger scan');
		}
	}
</script>

<svelte:head>
	<title>Assets - EASM Platform</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold gradient-text">Assets</h1>
			<p class="mt-2 text-sm text-slate-400">Manage your attack surface inventory</p>
		</div>
		<a href="/assets/new" class="btn btn-primary">
			<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			Add Asset
		</a>
	</div>

	<div class="card">
		{#if loading}
			<p class="text-center text-slate-400 py-8">Loading assets...</p>
		{:else if assets.length === 0}
			<div class="text-center py-12">
				<svg class="mx-auto h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
				</svg>
				<h3 class="mt-2 text-sm font-medium text-slate-100">No assets</h3>
				<p class="mt-1 text-sm text-slate-400">Get started by creating a new asset.</p>
				<div class="mt-6">
					<a href="/assets/new" class="btn btn-primary">
						<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						New Asset
					</a>
				</div>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-slate-700">
					<thead class="bg-slate-800/50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Asset</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Type</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Status</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Last Seen</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Actions</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-700">
						{#each assets as asset}
							<tr class="hover:bg-slate-800/30 transition-colors">
								<td class="px-6 py-4 whitespace-nowrap">
									<div>
										<div class="text-sm font-medium text-slate-100">{asset.value}</div>
										{#if asset.name}
											<div class="text-sm text-slate-400">{asset.name}</div>
										{/if}
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="badge badge-info">{asset.type}</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="badge {asset.status === 'active' ? 'badge-success' : 'badge-gray'}">
										{asset.status}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
									{formatRelativeTime(asset.last_seen_at)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
									<div class="flex gap-2">
										<button on:click={() => goto(`/assets/${asset.id}`)} class="text-cyan-400 hover:text-cyan-300 transition-colors">
											View
										</button>
										<button on:click={() => triggerScan(asset.id)} class="text-green-400 hover:text-green-300 transition-colors">
											Scan
										</button>
										<button on:click={() => deleteAsset(asset.id)} class="text-red-400 hover:text-red-300 transition-colors">
											Delete
										</button>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>
