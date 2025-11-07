<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api.ts';
	import { formatRelativeTime, getStatusClass, formatDuration } from '$lib/utils.ts';

	let scans: any[] = [];
	let loading = true;

	onMount(async () => {
		await loadScans();
	});

	async function loadScans() {
		try {
			loading = true;
			scans = await api.getScans({ limit: 100 });
		} catch (error) {
			console.error('Failed to load scans:', error);
		} finally {
			loading = false;
		}
	}

	async function cancelScan(id: number) {
		if (!confirm('Are you sure you want to cancel this scan?')) return;

		try {
			await api.cancelScan(id);
			await loadScans();
		} catch (error) {
			console.error('Failed to cancel scan:', error);
			alert('Failed to cancel scan');
		}
	}

	async function deleteScan(id: number) {
		if (!confirm('Are you sure you want to delete this scan?')) return;

		try {
			await api.deleteScan(id);
			await loadScans();
		} catch (error) {
			console.error('Failed to delete scan:', error);
			alert('Failed to delete scan');
		}
	}
</script>

<svelte:head>
	<title>Scans - EASM Platform</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold gradient-text">Scans</h1>
			<p class="mt-2 text-sm text-slate-400">View and manage vulnerability scans</p>
		</div>
		<a href="/assets" class="btn btn-primary">
			<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
			</svg>
			Trigger New Scan
		</a>
	</div>

	<div class="card">
		{#if loading}
			<p class="text-center text-slate-400 py-8">Loading scans...</p>
		{:else if scans.length === 0}
			<div class="text-center py-12">
				<svg class="mx-auto h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
				</svg>
				<h3 class="mt-2 text-sm font-medium text-slate-100">No scans</h3>
				<p class="mt-1 text-sm text-slate-400">Get started by triggering a scan on an asset.</p>
				<div class="mt-6">
					<a href="/assets" class="btn btn-primary">
						View Assets
					</a>
				</div>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-slate-700">
					<thead class="bg-slate-800/50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Target</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Status</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Vulnerabilities</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Duration</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Started</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Actions</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-700">
						{#each scans as scan}
							<tr class="hover:bg-slate-800/30 transition-colors">
								<td class="px-6 py-4">
									<div class="text-sm font-medium text-slate-100">{scan.target}</div>
									{#if scan.name}
										<div class="text-sm text-slate-400">{scan.name}</div>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="badge {getStatusClass(scan.status)}">
										{scan.status}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									{#if scan.status === 'completed'}
										<div class="flex gap-1">
											{#if scan.vulnerabilities_by_severity?.critical}
												<span class="badge badge-critical">{scan.vulnerabilities_by_severity.critical}C</span>
											{/if}
											{#if scan.vulnerabilities_by_severity?.high}
												<span class="badge badge-high">{scan.vulnerabilities_by_severity.high}H</span>
											{/if}
											{#if scan.vulnerabilities_by_severity?.medium}
												<span class="badge badge-medium">{scan.vulnerabilities_by_severity.medium}M</span>
											{/if}
										</div>
									{:else}
										<span class="text-sm text-slate-400">-</span>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
									{scan.duration_seconds ? formatDuration(scan.duration_seconds) : '-'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
									{formatRelativeTime(scan.started_at || scan.created_at)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
									<div class="flex gap-2">
										<a href="/scans/{scan.id}" class="text-cyan-400 hover:text-cyan-300 transition-colors">
											View
										</a>
										{#if scan.status === 'running' || scan.status === 'pending'}
											<button on:click={() => cancelScan(scan.id)} class="text-orange-400 hover:text-orange-300 transition-colors">
												Cancel
											</button>
										{/if}
										<button on:click={() => deleteScan(scan.id)} class="text-red-400 hover:text-red-300 transition-colors">
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
