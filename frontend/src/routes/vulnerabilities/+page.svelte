<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api.ts';
	import { formatRelativeTime, getSeverityClass, getStateClass } from '$lib/utils.ts';

	let vulnerabilities: any[] = [];
	let loading = true;
	let filter = {
		state: '',
		severity: '',
		asset_id: ''
	};

	onMount(async () => {
		await loadVulnerabilities();
	});

	async function loadVulnerabilities() {
		try {
			loading = true;
			const params: any = { limit: 100 };
			if (filter.state) params.state = filter.state;
			if (filter.severity) params.severity = filter.severity;
			if (filter.asset_id) params.asset_id = parseInt(filter.asset_id);

			vulnerabilities = await api.getVulnerabilities(params);
		} catch (error) {
			console.error('Failed to load vulnerabilities:', error);
		} finally {
			loading = false;
		}
	}

	async function changeState(id: number, state: string) {
		try {
			await api.changeVulnerabilityState(id, state);
			await loadVulnerabilities();
		} catch (error) {
			console.error('Failed to change state:', error);
			alert('Failed to change vulnerability state');
		}
	}
</script>

<svelte:head>
	<title>Vulnerabilities - EASM Platform</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-6">
		<h1 class="text-3xl font-bold gradient-text">Vulnerabilities</h1>
		<p class="mt-2 text-sm text-slate-400">Manage and triage discovered vulnerabilities</p>
	</div>

	<!-- Filters -->
	<div class="card mb-6">
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<div>
				<label for="state" class="label">State</label>
				<select id="state" bind:value={filter.state} on:change={loadVulnerabilities} class="input">
					<option value="">All States</option>
					<option value="new">New</option>
					<option value="triaging">Triaging</option>
					<option value="investigating">Investigating</option>
					<option value="remediation">Remediation</option>
					<option value="resolved">Resolved</option>
					<option value="false_positive">False Positive</option>
					<option value="accepted_risk">Accepted Risk</option>
				</select>
			</div>
			<div>
				<label for="severity" class="label">Severity</label>
				<select id="severity" bind:value={filter.severity} on:change={loadVulnerabilities} class="input">
					<option value="">All Severities</option>
					<option value="critical">Critical</option>
					<option value="high">High</option>
					<option value="medium">Medium</option>
					<option value="low">Low</option>
					<option value="info">Info</option>
				</select>
			</div>
			<div>
				<label for="asset_id" class="label">Asset ID</label>
				<input
					id="asset_id"
					type="text"
					bind:value={filter.asset_id}
					on:input={loadVulnerabilities}
					placeholder="Filter by asset ID"
					class="input"
				/>
			</div>
		</div>
	</div>

	<div class="card">
		{#if loading}
			<p class="text-center text-slate-400 py-8">Loading vulnerabilities...</p>
		{:else if vulnerabilities.length === 0}
			<div class="text-center py-12">
				<svg class="mx-auto h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				<h3 class="mt-2 text-sm font-medium text-slate-100">No vulnerabilities</h3>
				<p class="mt-1 text-sm text-slate-400">
					{#if filter.state || filter.severity || filter.asset_id}
						No vulnerabilities match your filters.
					{:else}
						Run some scans to discover vulnerabilities.
					{/if}
				</p>
				<div class="mt-6">
					<a href="/scans" class="btn btn-primary">
						View Scans
					</a>
				</div>
			</div>
		{:else}
			<div class="space-y-4">
				{#each vulnerabilities as vuln}
					<div class="border border-slate-700/50 rounded-lg p-4 hover:bg-slate-800/30 transition-all bg-slate-800/20">
						<div class="flex items-start justify-between mb-3">
							<div class="flex-1">
								<div class="flex items-center gap-2 mb-2">
									<span class="badge {getSeverityClass(vuln.severity)}">
										{vuln.severity}
									</span>
									<span class="badge {getStateClass(vuln.state)}">
										{vuln.state}
									</span>
									{#if vuln.cve_ids && vuln.cve_ids.length > 0}
										<span class="badge badge-gray text-xs">{vuln.cve_ids[0]}</span>
									{/if}
								</div>
								<h3 class="font-semibold text-slate-100 text-lg">{vuln.name}</h3>
								<p class="text-sm text-slate-400 mt-1">{vuln.matched_at}</p>
							</div>
						</div>

						{#if vuln.description}
							<p class="text-sm text-slate-300 mb-3">{vuln.description}</p>
						{/if}

						<div class="flex items-center justify-between pt-3 border-t border-slate-700/50">
							<div class="flex items-center gap-4 text-xs text-slate-400">
								<span>Template: {vuln.template_id}</span>
								<span>Found: {formatRelativeTime(vuln.created_at)}</span>
								{#if vuln.occurrences > 1}
									<span class="text-orange-400 font-medium">Seen {vuln.occurrences}x</span>
								{/if}
							</div>

							<div class="flex items-center gap-2">
								{#if vuln.state === 'new'}
									<button
										on:click={() => changeState(vuln.id, 'triaging')}
										class="btn btn-sm btn-secondary"
									>
										Start Triage
									</button>
								{:else if vuln.state === 'triaging'}
									<button
										on:click={() => changeState(vuln.id, 'investigating')}
										class="btn btn-sm btn-secondary"
									>
										Investigate
									</button>
								{:else if vuln.state === 'investigating'}
									<button
										on:click={() => changeState(vuln.id, 'remediation')}
										class="btn btn-sm btn-secondary"
									>
										Remediate
									</button>
								{:else if vuln.state === 'remediation'}
									<button
										on:click={() => changeState(vuln.id, 'resolved')}
										class="btn btn-sm btn-primary"
									>
										Mark Resolved
									</button>
								{/if}

								<button
									on:click={() => goto(`/vulnerabilities/${vuln.id}`)}
									class="btn btn-sm btn-secondary"
								>
									Details
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
