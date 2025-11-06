<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.ts';
	import { api } from '$lib/api.ts';

	let username = '';
	let password = '';
	let error = '';
	let loading = false;

	async function handleLogin() {
		error = '';
		loading = true;

		try {
			const response = await api.login(username, password);
			api.setToken(response.access_token);

			// Get user info
			const user = await api.getCurrentUser();
			authStore.login(user, response.access_token);

			goto('/');
		} catch (err: any) {
			error = err.response?.data?.detail || 'Login failed. Please check your credentials.';
		} finally {
			loading = false;
		}
	}

	async function initDefaultUser() {
		try {
			await api.initDefaultUser();
			username = 'admin';
			password = 'admin';
			error = 'Default user initialized. Username: admin, Password: admin';
		} catch (err) {
			error = 'Failed to initialize default user';
		}
	}
</script>

<svelte:head>
	<title>Login - EASM Platform</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
	<div class="max-w-md w-full">
		<div class="text-center mb-8">
			<h1 class="text-4xl font-bold text-primary-600 mb-2">EASM Platform</h1>
			<p class="text-gray-600">External Attack Surface Management</p>
		</div>

		<div class="card">
			<h2 class="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>

			{#if error}
				<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
					{error}
				</div>
			{/if}

			<form on:submit|preventDefault={handleLogin} class="space-y-4">
				<div>
					<label for="username" class="label">Username or Email</label>
					<input
						id="username"
						type="text"
						bind:value={username}
						required
						class="input"
						placeholder="admin"
						disabled={loading}
					/>
				</div>

				<div>
					<label for="password" class="label">Password</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						required
						class="input"
						placeholder="••••••••"
						disabled={loading}
					/>
				</div>

				<button type="submit" class="btn btn-primary w-full" disabled={loading}>
					{#if loading}
						<span>Signing in...</span>
					{:else}
						<span>Sign In</span>
					{/if}
				</button>
			</form>

			<div class="mt-6 pt-6 border-t border-gray-200">
				<p class="text-sm text-gray-600 text-center mb-3">
					First time setup? Initialize the default admin user.
				</p>
				<button on:click={initDefaultUser} class="btn btn-secondary w-full text-sm">
					Initialize Default User
				</button>
			</div>
		</div>

		<p class="mt-8 text-center text-sm text-gray-600">
			Tier A • Open Source Edition
		</p>
	</div>
</div>
