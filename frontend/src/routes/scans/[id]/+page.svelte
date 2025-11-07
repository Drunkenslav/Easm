<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api.ts';
	import { formatDate, getStatusClass, getSeverityClass } from '$lib/utils.ts';

	let scanId: number;
	let scan: any = null;
	let vulnerabilities: any[] = [];
	let loading = true;

	$: scanId = parseInt($page.params.id);

	onMount(async () => {
		await loadScan();
		await loadVulnerabilities();
	});

	async function loadScan() {
		try {
			scan = await api.getScanDetails(scanId);
		} catch (error) {
			console.error('Failed to load scan:', error);
		} finally {
			loading = false;
		}
	}

	async function loadVulnerabilities() {
		try {
			vulnerabilities = await api.getVulnerabilities({ scan_id: scanId, limit: 100 });
		} catch (error) {
			console.error('Failed to load vulnerabilities:', error);
		}
	}
</script>

<svelte:head>
	<title>Scan #{scanId} - EASM Platform</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<button on:click={() => goto('/scans')} class="text-sm text-slate-400 hover:text-slate-300 mb-2">
				← Back to Scans
			</button>
			<h1 class="text-3xl font-bold gradient-text">Scan #{scanId}</h1>
		</div>
	</div>

	{#if loading}
		<div class="card">
			<p class="text-center text-slate-400 py-8">Loading scan details...</p>
		</div>
	{:else if !scan}
		<div class="card">
			<p class="text-center text-red-500 py-8">Scan not found</p>
		</div>
	{:else}
		<!-- Scan Details -->
		<div class="card mb-6">
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div>
					<h3 class="text-sm font-medium text-slate-400 mb-2">Target</h3>
					<p class="text-lg font-semibold text-slate-100">{scan.target}</p>
				</div>
				<div>
					<h3 class="text-sm font-medium text-slate-400 mb-2">Status</h3>
					<span class="badge {getStatusClass(scan.status)} text-base">
						{scan.status}
					</span>
				</div>
				<div>
					<h3 class="text-sm font-medium text-slate-400 mb-2">Started</h3>
					<p class="text-slate-100">{formatDate(scan.started_at || scan.created_at)}</p>
				</div>
				<div>
					<h3 class="text-sm font-medium text-slate-400 mb-2">Duration</h3>
					<p class="text-slate-100">
						{#if scan.duration_seconds}
							{Math.floor(scan.duration_seconds / 60)}m {scan.duration_seconds % 60}s
						{:else}
							-
						{/if}
					</p>
				</div>
				<div>
					<h3 class="text-sm font-medium text-slate-400 mb-2">Vulnerabilities Found</h3>
					<p class="text-2xl font-bold text-slate-100">{scan.vulnerabilities_found || 0}</p>
				</div>
				{#if scan.error_message}
					<div class="md:col-span-2">
						<h3 class="text-sm font-medium text-slate-400 mb-2">Error</h3>
						<div class="p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-sm text-red-400">
							{scan.error_message}
						</div>
					</div>
				{/if}
			</div>

			<!-- Severity Breakdown -->
			{#if scan.vulnerabilities_by_severity && Object.keys(scan.vulnerabilities_by_severity).length > 0}
				<div class="mt-6 pt-6 border-t border-slate-700/50">
					<h3 class="text-sm font-medium text-slate-400 mb-3">Severity Breakdown</h3>
					<div class="flex flex-wrap gap-2">
						{#each Object.entries(scan.vulnerabilities_by_severity) as [severity, count]}
							<span class="badge {getSeverityClass(severity)} text-base">
								{severity}: {count}
							</span>
						{/each}
					</div>
				</div>
			{/if}
		</div>

		<!-- Vulnerabilities -->
		<div class="card">
			<h2 class="text-lg font-semibold text-slate-100 mb-4">Discovered Vulnerabilities</h2>

			{#if vulnerabilities.length === 0}
				<p class="text-center text-slate-400 py-8">No vulnerabilities found</p>
			{:else}
				<div class="space-y-3">
					{#each vulnerabilities as vuln}
						<div class="border border-slate-700/50 rounded-lg p-4 hover:shadow-md transition-shadow">
							<div class="flex items-start justify-between mb-2">
								<div class="flex-1">
									<h3 class="font-medium text-slate-100">{vuln.name}</h3>
									<p class="text-sm text-slate-400 mt-1">{vuln.matched_at}</p>
								</div>
								<span class="badge {getSeverityClass(vuln.severity)} ml-4">
									{vuln.severity}
								</span>
							</div>

							{#if vuln.description}
								<p class="text-sm text-slate-300 mt-2">{vuln.description}</p>
							{/if}

							<div class="flex items-center gap-2 mt-3">
								<span class="text-xs text-slate-400">Template: {vuln.template_id}</span>
								{#if vuln.cve_ids && vuln.cve_ids.length > 0}
									<span class="badge badge-gray text-xs">{vuln.cve_ids[0]}</span>
								{/if}
							</div>

							<div class="mt-3">
								<button
									on:click={() => goto(`/vulnerabilities/${vuln.id}`)}
									class="text-sm text-cyan-400 hover:text-cyan-300"
								>
									View Details →
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Nuclei Output -->
		{#if scan.nuclei_output}
			<div class="card mt-6">
				<h2 class="text-lg font-semibold text-slate-100 mb-4">Nuclei Output</h2>
				<pre class="bg-slate-800/50 p-4 rounded-lg overflow-x-auto text-xs text-slate-100">{scan.nuclei_output}</pre>
			</div>
		{/if}
	{/if}
</div>
