<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth.ts';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api.ts';

	$: isLoginPage = $page.url.pathname === '/login';
</script>

<div class="min-h-screen bg-gray-50">
	{#if !isLoginPage && $authStore.isAuthenticated}
		<!-- Navigation -->
		<nav class="bg-white shadow-sm border-b border-gray-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between h-16">
					<div class="flex">
						<div class="flex-shrink-0 flex items-center">
							<h1 class="text-xl font-bold text-primary-600">EASM Platform</h1>
						</div>
						<div class="hidden sm:ml-6 sm:flex sm:space-x-8">
							<a
								href="/"
								class="border-transparent hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
								class:border-primary-500={$page.url.pathname === '/'}
								class:text-gray-900={$page.url.pathname === '/'}
								class:text-gray-500={$page.url.pathname !== '/'}
							>
								Dashboard
							</a>
							<a
								href="/assets"
								class="border-transparent hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
								class:border-primary-500={$page.url.pathname.startsWith('/assets')}
								class:text-gray-900={$page.url.pathname.startsWith('/assets')}
								class:text-gray-500={!$page.url.pathname.startsWith('/assets')}
							>
								Assets
							</a>
							<a
								href="/scans"
								class="border-transparent hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
								class:border-primary-500={$page.url.pathname.startsWith('/scans')}
								class:text-gray-900={$page.url.pathname.startsWith('/scans')}
								class:text-gray-500={!$page.url.pathname.startsWith('/scans')}
							>
								Scans
							</a>
							<a
								href="/vulnerabilities"
								class="border-transparent hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
								class:border-primary-500={$page.url.pathname.startsWith('/vulnerabilities')}
								class:text-gray-900={$page.url.pathname.startsWith('/vulnerabilities')}
								class:text-gray-500={!$page.url.pathname.startsWith('/vulnerabilities')}
							>
								Vulnerabilities
							</a>
						</div>
					</div>
					<div class="flex items-center">
						{#if $authStore.user}
							<div class="flex items-center gap-4">
								<span class="text-sm text-gray-700">
									{$authStore.user.username}
									<span class="text-xs text-gray-500">({$authStore.user.role})</span>
								</span>
								<button
									on:click={() => {
										authStore.logout();
										api.clearToken();
										goto('/login');
									}}
									class="btn btn-sm btn-secondary"
								>
									Logout
								</button>
							</div>
						{/if}
					</div>
				</div>
			</div>
		</nav>
	{/if}

	<main>
		<slot />
	</main>
</div>
