<script lang="ts">
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';

	let form = {
		type: 'url',
		value: '',
		name: '',
		criticality: 'medium',
		tags: '',
		notes: ''
	};

	let loading = false;
	let error = '';

	async function handleSubmit() {
		error = '';
		loading = true;

		try {
			const data = {
				...form,
				tags: form.tags.split(',').map(t => t.trim()).filter(Boolean)
			};

			await api.createAsset(data);
			goto('/assets');
		} catch (err: any) {
			error = err.response?.data?.detail || 'Failed to create asset';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>New Asset - EASM Platform</title>
</svelte:head>

<div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-6">
		<h1 class="text-3xl font-bold text-gray-900">Add New Asset</h1>
		<p class="mt-2 text-sm text-gray-600">Register a new asset for vulnerability scanning</p>
	</div>

	<div class="card">
		{#if error}
			<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
				{error}
			</div>
		{/if}

		<form on:submit|preventDefault={handleSubmit} class="space-y-6">
			<div>
				<label for="type" class="label">Asset Type</label>
				<select id="type" bind:value={form.type} class="input" required>
					<option value="url">URL</option>
					<option value="domain">Domain</option>
					<option value="subdomain">Subdomain</option>
					<option value="ip">IP Address</option>
					<option value="api_endpoint">API Endpoint</option>
				</select>
			</div>

			<div>
				<label for="value" class="label">Asset Value *</label>
				<input
					id="value"
					type="text"
					bind:value={form.value}
					placeholder="https://example.com"
					class="input"
					required
				/>
				<p class="mt-1 text-sm text-gray-500">The URL, domain, IP, or endpoint to scan</p>
			</div>

			<div>
				<label for="name" class="label">Name (Optional)</label>
				<input
					id="name"
					type="text"
					bind:value={form.name}
					placeholder="My Production Server"
					class="input"
				/>
			</div>

			<div>
				<label for="criticality" class="label">Criticality</label>
				<select id="criticality" bind:value={form.criticality} class="input">
					<option value="low">Low</option>
					<option value="medium">Medium</option>
					<option value="high">High</option>
					<option value="critical">Critical</option>
				</select>
			</div>

			<div>
				<label for="tags" class="label">Tags (Optional)</label>
				<input
					id="tags"
					type="text"
					bind:value={form.tags}
					placeholder="production, web-app, critical"
					class="input"
				/>
				<p class="mt-1 text-sm text-gray-500">Comma-separated tags</p>
			</div>

			<div>
				<label for="notes" class="label">Notes (Optional)</label>
				<textarea
					id="notes"
					bind:value={form.notes}
					rows="3"
					class="input"
					placeholder="Additional information about this asset..."
				/>
			</div>

			<div class="flex gap-3">
				<button type="submit" class="btn btn-primary" disabled={loading}>
					{loading ? 'Creating...' : 'Create Asset'}
				</button>
				<button type="button" on:click={() => goto('/assets')} class="btn btn-secondary">
					Cancel
				</button>
			</div>
		</form>
	</div>
</div>
