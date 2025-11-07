<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth.ts';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api.ts';
	import { writable } from 'svelte/store';

	$: isLoginPage = $page.url.pathname === '/login';

	// Sidebar collapse state
	const sidebarCollapsed = writable(false);

	function toggleSidebar() {
		sidebarCollapsed.update(val => !val);
	}
</script>

<div class="dark min-h-screen bg-gradient-to-br from-black to-slate-900">
	{#if !isLoginPage && $authStore.isAuthenticated}
		<!-- Left Sidebar Navigation -->
		<aside class="fixed left-0 top-0 h-screen bg-slate-900/95 backdrop-blur-lg border-r border-cyan-500/20 transition-all duration-300 z-50 {$sidebarCollapsed ? 'w-20' : 'w-64'} flex flex-col">
			<!-- Logo Section -->
			<div class="h-16 flex items-center justify-between px-4 border-b border-slate-800/50">
				{#if !$sidebarCollapsed}
					<div class="flex items-center gap-3">
						<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/50 ring-2 ring-cyan-500/30">
							<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
							</svg>
						</div>
						<span class="text-lg font-bold gradient-text">EASM</span>
					</div>
				{:else}
					<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/50 ring-2 ring-cyan-500/30 mx-auto">
						<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
						</svg>
					</div>
				{/if}
			</div>

			<!-- Navigation Items -->
			<nav class="flex-1 px-3 py-6 overflow-y-auto space-y-2">
				<a
					href="/"
					class="flex items-center gap-3 px-3 py-3 rounded-lg transition-all {$page.url.pathname === '/' ? 'bg-cyan-500/20 text-cyan-400 shadow-lg shadow-cyan-500/20 border border-cyan-500/30' : 'text-slate-300 hover:text-cyan-400 hover:bg-slate-800/50'}"
				>
					<svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
					</svg>
					{#if !$sidebarCollapsed}
						<span class="font-medium">Dashboard</span>
					{/if}
				</a>

				<a
					href="/assets"
					class="flex items-center gap-3 px-3 py-3 rounded-lg transition-all {$page.url.pathname.startsWith('/assets') ? 'bg-cyan-500/20 text-cyan-400 shadow-lg shadow-cyan-500/20 border border-cyan-500/30' : 'text-slate-300 hover:text-cyan-400 hover:bg-slate-800/50'}"
				>
					<svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
					</svg>
					{#if !$sidebarCollapsed}
						<span class="font-medium">Assets</span>
					{/if}
				</a>

				<a
					href="/scans"
					class="flex items-center gap-3 px-3 py-3 rounded-lg transition-all {$page.url.pathname.startsWith('/scans') ? 'bg-cyan-500/20 text-cyan-400 shadow-lg shadow-cyan-500/20 border border-cyan-500/30' : 'text-slate-300 hover:text-cyan-400 hover:bg-slate-800/50'}"
				>
					<svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
					</svg>
					{#if !$sidebarCollapsed}
						<span class="font-medium">Scans</span>
					{/if}
				</a>

				<a
					href="/vulnerabilities"
					class="flex items-center gap-3 px-3 py-3 rounded-lg transition-all {$page.url.pathname.startsWith('/vulnerabilities') ? 'bg-cyan-500/20 text-cyan-400 shadow-lg shadow-cyan-500/20 border border-cyan-500/30' : 'text-slate-300 hover:text-cyan-400 hover:bg-slate-800/50'}"
				>
					<svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
					{#if !$sidebarCollapsed}
						<span class="font-medium">Vulnerabilities</span>
					{/if}
				</a>

				<!-- Divider -->
				<div class="py-3">
					<div class="h-px bg-slate-800/50"></div>
				</div>

				<!-- Settings -->
				<button
					class="flex items-center gap-3 px-3 py-3 rounded-lg transition-all text-slate-300 hover:text-cyan-400 hover:bg-slate-800/50 w-full"
				>
					<svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
					</svg>
					{#if !$sidebarCollapsed}
						<span class="font-medium">Settings</span>
					{/if}
				</button>
			</nav>

			<!-- User Profile & Collapse Button -->
			<div class="border-t border-slate-800/50 p-3 space-y-3">
				{#if $authStore.user}
					<!-- User Info -->
					<div class="flex items-center gap-3 px-3 py-2 bg-slate-800/50 rounded-lg">
						<div class="h-9 w-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-md shadow-cyan-500/30 flex-shrink-0">
							{$authStore.user.username.charAt(0).toUpperCase()}
						</div>
						{#if !$sidebarCollapsed}
							<div class="flex-1 min-w-0">
								<p class="text-sm font-semibold text-slate-100 truncate">{$authStore.user.username}</p>
								<p class="text-xs text-slate-400 capitalize truncate">{$authStore.user.role}</p>
							</div>
						{/if}
					</div>

					<!-- Logout & Collapse Buttons -->
					<div class="flex gap-2">
						<button
							on:click={() => {
								authStore.logout();
								api.clearToken();
								goto('/login');
							}}
							class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all border border-red-500/30"
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
							</svg>
							{#if !$sidebarCollapsed}
								<span class="text-sm">Logout</span>
							{/if}
						</button>

						<button
							on:click={toggleSidebar}
							class="flex items-center justify-center px-3 py-2 rounded-lg bg-slate-800/50 text-slate-300 hover:text-cyan-400 hover:bg-slate-800 transition-all border border-slate-700/50"
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								{#if $sidebarCollapsed}
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
								{:else}
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
								{/if}
							</svg>
						</button>
					</div>
				{/if}
			</div>
		</aside>

		<!-- Main Content Area -->
		<main class="transition-all duration-300 {$sidebarCollapsed ? 'ml-20' : 'ml-64'}">
			<slot />
		</main>
	{:else}
		<main class="min-h-screen">
			<slot />
		</main>
	{/if}
</div>
