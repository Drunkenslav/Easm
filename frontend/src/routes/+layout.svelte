<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth.ts';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api.ts';

	$: isLoginPage = $page.url.pathname === '/login';
</script>

<div class="min-h-screen">
	{#if !isLoginPage && $authStore.isAuthenticated}
		<!-- Modern Navigation -->
		<nav class="bg-white/80 backdrop-blur-lg shadow-lg border-b border-white/20 sticky top-0 z-50">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between h-16">
					<div class="flex items-center gap-8">
						<!-- Logo -->
						<div class="flex-shrink-0 flex items-center gap-3">
							<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
								<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
								</svg>
							</div>
							<h1 class="text-xl font-bold gradient-text hidden sm:block">EASM Platform</h1>
						</div>

						<!-- Navigation Links -->
						<div class="hidden md:flex items-center gap-2">
							<a
								href="/"
								class="nav-link px-4 py-2 rounded-lg transition-all"
								class:nav-link-active={$page.url.pathname === '/'}
								class:bg-blue-50={$page.url.pathname === '/'}
							>
								<div class="flex items-center gap-2">
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
									</svg>
									Dashboard
								</div>
							</a>
							<a
								href="/assets"
								class="nav-link px-4 py-2 rounded-lg transition-all"
								class:nav-link-active={$page.url.pathname.startsWith('/assets')}
								class:bg-blue-50={$page.url.pathname.startsWith('/assets')}
							>
								<div class="flex items-center gap-2">
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
									</svg>
									Assets
								</div>
							</a>
							<a
								href="/scans"
								class="nav-link px-4 py-2 rounded-lg transition-all"
								class:nav-link-active={$page.url.pathname.startsWith('/scans')}
								class:bg-blue-50={$page.url.pathname.startsWith('/scans')}
							>
								<div class="flex items-center gap-2">
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
									</svg>
									Scans
								</div>
							</a>
							<a
								href="/vulnerabilities"
								class="nav-link px-4 py-2 rounded-lg transition-all"
								class:nav-link-active={$page.url.pathname.startsWith('/vulnerabilities')}
								class:bg-blue-50={$page.url.pathname.startsWith('/vulnerabilities')}
							>
								<div class="flex items-center gap-2">
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
									</svg>
									Vulnerabilities
								</div>
							</a>
						</div>
					</div>

					<!-- User Menu -->
					<div class="flex items-center gap-4">
						{#if $authStore.user}
							<div class="hidden sm:flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border border-gray-200/50">
								<div class="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
									{$authStore.user.username.charAt(0).toUpperCase()}
								</div>
								<div class="text-left">
									<p class="text-sm font-semibold text-gray-900">{$authStore.user.username}</p>
									<p class="text-xs text-gray-500 capitalize">{$authStore.user.role}</p>
								</div>
							</div>
							<button
								on:click={() => {
									authStore.logout();
									api.clearToken();
									goto('/login');
								}}
								class="btn btn-sm btn-secondary flex items-center gap-2"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
								</svg>
								<span class="hidden sm:inline">Logout</span>
							</button>
						{/if}
					</div>
				</div>
			</div>
		</nav>
	{/if}

	<main class="min-h-screen">
		<slot />
	</main>
</div>
