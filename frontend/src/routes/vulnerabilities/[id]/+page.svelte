<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api.ts';
	import { formatDate, getSeverityClass, getStateClass } from '$lib/utils.ts';

	let vulnId: number;
	let vuln: any = null;
	let loading = true;
	let changingState = false;

	$: vulnId = parseInt($page.params.id);

	onMount(async () => {
		await loadVulnerability();
	});

	async function loadVulnerability() {
		try {
			vuln = await api.getVulnerability(vulnId);
		} catch (error) {
			console.error('Failed to load vulnerability:', error);
		} finally {
			loading = false;
		}
	}

	async function changeState(newState: string) {
		if (changingState) return;

		const notes = newState === 'resolved' || newState === 'false_positive'
			? prompt(`Notes for marking as ${newState}:`)
			: null;

		if ((newState === 'resolved' || newState === 'false_positive') && !notes) return;

		try {
			changingState = true;
			await api.changeVulnerabilityState(vulnId, newState, notes || undefined);
			await loadVulnerability();
		} catch (error) {
			console.error('Failed to change state:', error);
			alert('Failed to change vulnerability state');
		} finally {
			changingState = false;
		}
	}

	async function acceptRisk() {
		const reason = prompt('Reason for accepting risk (minimum 10 characters):');
		if (!reason || reason.length < 10) return;

		try {
			await api.acceptRisk(vulnId, reason);
			await loadVulnerability();
		} catch (error) {
			console.error('Failed to accept risk:', error);
			alert('Failed to accept risk');
		}
	}

	function getStateActions(state: string) {
		const actions: { [key: string]: string[] } = {
			new: ['triaging', 'false_positive'],
			triaging: ['investigating', 'false_positive'],
			investigating: ['remediation', 'false_positive'],
			remediation: ['resolved', 'investigating'],
			resolved: ['investigating'],
			false_positive: ['new']
		};
		return actions[state] || [];
	}
</script>

<svelte:head>
	<title>Vulnerability #{vulnId} - EASM Platform</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-6">
		<button on:click={() => goto('/vulnerabilities')} class="text-sm text-slate-400 hover:text-slate-300 mb-2">
			← Back to Vulnerabilities
		</button>
		<h1 class="text-3xl font-bold gradient-text">Vulnerability #{vulnId}</h1>
	</div>

	{#if loading}
		<div class="card">
			<p class="text-center text-slate-400 py-8">Loading vulnerability details...</p>
		</div>
	{:else if !vuln}
		<div class="card">
			<p class="text-center text-red-500 py-8">Vulnerability not found</p>
		</div>
	{:else}
		<!-- Status Bar -->
		<div class="card mb-6 bg-gradient-to-r from-gray-50 to-gray-100">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-3">
					<span class="badge {getSeverityClass(vuln.severity)} text-lg">
						{vuln.severity}
					</span>
					<span class="badge {getStateClass(vuln.state)} text-lg">
						{vuln.state}
					</span>
					{#if vuln.occurrences > 1}
						<span class="badge badge-gray">Seen {vuln.occurrences}x</span>
					{/if}
				</div>
				<div class="flex gap-2">
					{#each getStateActions(vuln.state) as action}
						<button
							on:click={() => changeState(action)}
							disabled={changingState}
							class="btn btn-sm btn-secondary"
						>
							→ {action}
						</button>
					{/each}
					{#if vuln.state !== 'accepted_risk' && !vuln.is_risk_accepted}
						<button on:click={acceptRisk} class="btn btn-sm btn-danger">
							Accept Risk
						</button>
					{/if}
				</div>
			</div>
		</div>

		<!-- Main Details -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<div class="lg:col-span-2 space-y-6">
				<!-- Title and Description -->
				<div class="card">
					<h2 class="text-2xl font-bold text-slate-100 mb-4">{vuln.name}</h2>
					{#if vuln.description}
						<p class="text-slate-300 whitespace-pre-wrap">{vuln.description}</p>
					{/if}
				</div>

				<!-- Location -->
				<div class="card">
					<h3 class="text-lg font-semibold text-slate-100 mb-3">Location</h3>
					<div class="bg-slate-800/50 p-3 rounded-lg">
						<p class="font-mono text-sm text-slate-100 break-all">{vuln.matched_at}</p>
					</div>
				</div>

				<!-- CVE/CWE -->
				{#if (vuln.cve_ids && vuln.cve_ids.length > 0) || (vuln.cwe_ids && vuln.cwe_ids.length > 0)}
					<div class="card">
						<h3 class="text-lg font-semibold text-slate-100 mb-3">Identifiers</h3>
						<div class="space-y-2">
							{#if vuln.cve_ids && vuln.cve_ids.length > 0}
								<div>
									<span class="text-sm font-medium text-slate-400">CVE:</span>
									<div class="flex flex-wrap gap-2 mt-1">
										{#each vuln.cve_ids as cve}
											<a
												href="https://nvd.nist.gov/vuln/detail/{cve}"
												target="_blank"
												rel="noopener"
												class="badge badge-gray hover:bg-gray-300"
											>
												{cve} ↗
											</a>
										{/each}
									</div>
								</div>
							{/if}
							{#if vuln.cwe_ids && vuln.cwe_ids.length > 0}
								<div>
									<span class="text-sm font-medium text-slate-400">CWE:</span>
									<div class="flex flex-wrap gap-2 mt-1">
										{#each vuln.cwe_ids as cwe}
											<span class="badge badge-gray">{cwe}</span>
										{/each}
									</div>
								</div>
							{/if}
							{#if vuln.cvss_score}
								<div>
									<span class="text-sm font-medium text-slate-400">CVSS Score:</span>
									<span class="ml-2 font-semibold">{vuln.cvss_score}</span>
								</div>
							{/if}
						</div>
					</div>
				{/if}

				<!-- References -->
				{#if vuln.reference_urls && vuln.reference_urls.length > 0}
					<div class="card">
						<h3 class="text-lg font-semibold text-slate-100 mb-3">References</h3>
						<ul class="space-y-2">
							{#each vuln.reference_urls as url}
								<li>
									<a href={url} target="_blank" rel="noopener" class="text-cyan-400 hover:text-cyan-300 text-sm break-all">
										{url} ↗
									</a>
								</li>
							{/each}
						</ul>
					</div>
				{/if}

				<!-- Request/Response -->
				{#if vuln.request || vuln.response}
					<div class="card">
						<h3 class="text-lg font-semibold text-slate-100 mb-3">HTTP Details</h3>

						{#if vuln.request}
							<div class="mb-4">
								<h4 class="text-sm font-medium text-slate-300 mb-2">Request:</h4>
								<pre class="bg-slate-800/50 p-3 rounded-lg overflow-x-auto text-xs text-slate-100">{vuln.request}</pre>
							</div>
						{/if}

						{#if vuln.response}
							<div>
								<h4 class="text-sm font-medium text-slate-300 mb-2">Response:</h4>
								<pre class="bg-slate-800/50 p-3 rounded-lg overflow-x-auto text-xs text-slate-100">{vuln.response}</pre>
							</div>
						{/if}

						{#if vuln.curl_command}
							<div class="mt-4">
								<h4 class="text-sm font-medium text-slate-300 mb-2">cURL Command:</h4>
								<pre class="bg-gray-900 text-green-400 p-3 rounded-lg overflow-x-auto text-xs">{vuln.curl_command}</pre>
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Sidebar -->
			<div class="space-y-6">
				<!-- Metadata -->
				<div class="card">
					<h3 class="text-lg font-semibold text-slate-100 mb-4">Metadata</h3>
					<dl class="space-y-3">
						<div>
							<dt class="text-xs font-medium text-slate-400">Template ID</dt>
							<dd class="mt-1 text-sm text-slate-100 font-mono">{vuln.template_id}</dd>
						</div>
						<div>
							<dt class="text-xs font-medium text-slate-400">First Seen</dt>
							<dd class="mt-1 text-sm text-slate-100">{formatDate(vuln.first_seen_at)}</dd>
						</div>
						<div>
							<dt class="text-xs font-medium text-slate-400">Last Seen</dt>
							<dd class="mt-1 text-sm text-slate-100">{formatDate(vuln.last_seen_at)}</dd>
						</div>
						{#if vuln.state_changed_at}
							<div>
								<dt class="text-xs font-medium text-slate-400">State Changed</dt>
								<dd class="mt-1 text-sm text-slate-100">{formatDate(vuln.state_changed_at)}</dd>
							</div>
						{/if}
					</dl>
				</div>

				<!-- Tags -->
				{#if vuln.tags && vuln.tags.length > 0}
					<div class="card">
						<h3 class="text-lg font-semibold text-slate-100 mb-3">Tags</h3>
						<div class="flex flex-wrap gap-2">
							{#each vuln.tags as tag}
								<span class="badge badge-info">{tag}</span>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Resolution Notes -->
				{#if vuln.resolution_notes}
					<div class="card">
						<h3 class="text-lg font-semibold text-slate-100 mb-3">Resolution Notes</h3>
						<p class="text-sm text-slate-300 whitespace-pre-wrap">{vuln.resolution_notes}</p>
					</div>
				{/if}

				<!-- Risk Acceptance -->
				{#if vuln.is_risk_accepted}
					<div class="card bg-yellow-50 border-yellow-200">
						<h3 class="text-lg font-semibold text-yellow-900 mb-3">Risk Accepted</h3>
						<p class="text-sm text-yellow-800">{vuln.risk_acceptance_reason}</p>
						{#if vuln.risk_accepted_at}
							<p class="text-xs text-yellow-600 mt-2">{formatDate(vuln.risk_accepted_at)}</p>
						{/if}
					</div>
				{/if}

				<!-- Actions -->
				<div class="card">
					<h3 class="text-lg font-semibold text-slate-100 mb-3">Actions</h3>
					<div class="space-y-2">
						<button on:click={() => goto(`/assets/${vuln.asset_id}`)} class="btn btn-secondary w-full">
							View Asset
						</button>
						<button on:click={() => goto(`/scans/${vuln.scan_id}`)} class="btn btn-secondary w-full">
							View Scan
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
