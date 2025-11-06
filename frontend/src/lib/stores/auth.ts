import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

interface User {
	id: number;
	username: string;
	email: string;
	full_name?: string;
	role: string;
	is_active: boolean;
	is_superuser: boolean;
}

interface AuthState {
	user: User | null;
	token: string | null;
	isAuthenticated: boolean;
}

function createAuthStore() {
	const { subscribe, set, update }: Writable<AuthState> = writable({
		user: null,
		token: null,
		isAuthenticated: false
	});

	return {
		subscribe,
		login: (user: User, token: string) => {
			set({
				user,
				token,
				isAuthenticated: true
			});
		},
		logout: () => {
			set({
				user: null,
				token: null,
				isAuthenticated: false
			});
		},
		setUser: (user: User) => {
			update((state) => ({
				...state,
				user
			}));
		}
	};
}

export const authStore = createAuthStore();
