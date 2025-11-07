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

<div class="dark min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
	<!-- Dark Cyberpunk Background -->
	<div class="absolute inset-0 bg-gradient-to-br from-black via-slate-900 to-slate-800"></div>
	<div class="absolute top-0 -left-4 w-72 h-72 bg-cyan-500/20 rounded-full filter blur-3xl opacity-50 animate-blob"></div>
	<div class="absolute top-0 -right-4 w-72 h-72 bg-blue-500/20 rounded-full filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>
	<div class="absolute -bottom-8 left-20 w-72 h-72 bg-purple-500/20 rounded-full filter blur-3xl opacity-50 animate-blob animation-delay-4000"></div>

	<div class="max-w-md w-full relative z-10 fade-in">
		<!-- Logo & Title -->
		<div class="text-center mb-8">
			<div class="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-2xl shadow-cyan-500/50 mb-4 transform hover:scale-110 transition-transform duration-300 ring-2 ring-cyan-500/30">
				<svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
				</svg>
			</div>
			<h1 class="text-5xl font-bold gradient-text mb-2">EASM Platform</h1>
			<p class="text-slate-400 font-medium">External Attack Surface Management</p>
		</div>

		<!-- Dark Glass Card -->
		<div class="bg-slate-900/50 backdrop-blur-lg rounded-3xl p-8 shadow-2xl border border-slate-700/50">
			<h2 class="text-2xl font-bold text-slate-100 mb-6">Welcome Back</h2>

			{#if error}
				<div class="mb-4 p-4 bg-red-500/20 backdrop-blur-sm border border-red-500/30 rounded-xl text-sm text-red-400">
					<div class="flex items-center gap-2">
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span>{error}</span>
					</div>
				</div>
			{/if}

			<form on:submit|preventDefault={handleLogin} class="space-y-5">
				<div>
					<label for="username" class="label">Username or Email</label>
					<div class="relative">
						<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
							<svg class="h-5 w-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
						</div>
						<input
							id="username"
							type="text"
							bind:value={username}
							required
							class="input pl-11"
							placeholder="admin"
							disabled={loading}
						/>
					</div>
				</div>

				<div>
					<label for="password" class="label">Password</label>
					<div class="relative">
						<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
							<svg class="h-5 w-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
							</svg>
						</div>
						<input
							id="password"
							type="password"
							bind:value={password}
							required
							class="input pl-11"
							placeholder="••••••••"
							disabled={loading}
						/>
					</div>
				</div>

				<button type="submit" class="btn btn-primary w-full text-lg" disabled={loading}>
					{#if loading}
						<div class="flex items-center justify-center gap-2">
							<svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							<span>Signing in...</span>
						</div>
					{:else}
						<span>Sign In</span>
					{/if}
				</button>
			</form>

			<div class="mt-6 pt-6 border-t border-slate-700/50">
				<p class="text-sm text-slate-400 text-center mb-3">
					First time setup? Initialize the default admin user.
				</p>
				<button on:click={initDefaultUser} class="btn btn-secondary w-full text-sm">
					Initialize Default User
				</button>
			</div>
		</div>

		<p class="mt-8 text-center text-sm text-slate-400 font-medium">
			Tier A • Open Source Edition
		</p>
	</div>
</div>

<style>
	@keyframes blob {
		0% { transform: translate(0px, 0px) scale(1); }
		33% { transform: translate(30px, -50px) scale(1.1); }
		66% { transform: translate(-20px, 20px) scale(0.9); }
		100% { transform: translate(0px, 0px) scale(1); }
	}

	.animate-blob {
		animation: blob 7s infinite;
	}

	.animation-delay-2000 {
		animation-delay: 2s;
	}

	.animation-delay-4000 {
		animation-delay: 4s;
	}
</style>
