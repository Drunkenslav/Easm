import axios, { type AxiosInstance } from 'axios';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';

const API_BASE_URL = browser ? '/api/v1' : 'http://localhost:8000/api/v1';

class ApiClient {
	private client: AxiosInstance;

	constructor() {
		this.client = axios.create({
			baseURL: API_BASE_URL,
			headers: {
				'Content-Type': 'application/json'
			}
		});

		// Request interceptor to add token
		this.client.interceptors.request.use((config) => {
			const token = this.getToken();
			if (token) {
				config.headers.Authorization = `Bearer ${token}`;
			}
			return config;
		});

		// Response interceptor to handle 401
		this.client.interceptors.response.use(
			(response) => response,
			(error) => {
				if (error.response?.status === 401 && browser) {
					this.clearToken();
					goto('/login');
				}
				return Promise.reject(error);
			}
		);
	}

	private getToken(): string | null {
		if (!browser) return null;
		return localStorage.getItem('token');
	}

	setToken(token: string) {
		if (browser) {
			localStorage.setItem('token', token);
		}
	}

	clearToken() {
		if (browser) {
			localStorage.removeItem('token');
		}
	}

	// Auth
	async login(username: string, password: string) {
		const formData = new URLSearchParams();
		formData.append('username', username);
		formData.append('password', password);

		const response = await this.client.post('/auth/login', formData, {
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
		});
		return response.data;
	}

	async getCurrentUser() {
		const response = await this.client.get('/auth/me');
		return response.data;
	}

	async initDefaultUser() {
		const response = await this.client.get('/auth/init');
		return response.data;
	}

	// Assets
	async getAssets(params?: any) {
		const response = await this.client.get('/assets/', { params });
		return response.data;
	}

	async getAsset(id: number) {
		const response = await this.client.get(`/assets/${id}`);
		return response.data;
	}

	async getAssetStats(id: number) {
		const response = await this.client.get(`/assets/${id}/stats`);
		return response.data;
	}

	async createAsset(data: any) {
		const response = await this.client.post('/assets/', data);
		return response.data;
	}

	async updateAsset(id: number, data: any) {
		const response = await this.client.patch(`/assets/${id}`, data);
		return response.data;
	}

	async deleteAsset(id: number) {
		await this.client.delete(`/assets/${id}`);
	}

	async countAssets(params?: any) {
		const response = await this.client.get('/assets/count', { params });
		return response.data;
	}

	// Scans
	async getScans(params?: any) {
		const response = await this.client.get('/scans/', { params });
		return response.data;
	}

	async getScan(id: number) {
		const response = await this.client.get(`/scans/${id}`);
		return response.data;
	}

	async getScanDetails(id: number) {
		const response = await this.client.get(`/scans/${id}/details`);
		return response.data;
	}

	async createScan(data: any) {
		const response = await this.client.post('/scans/', data);
		return response.data;
	}

	async triggerScans(assetIds: number[], templateId?: number) {
		const response = await this.client.post('/scans/trigger', {
			asset_ids: assetIds,
			template_id: templateId,
			config_override: {}
		});
		return response.data;
	}

	async executeScan(id: number) {
		const response = await this.client.post(`/scans/${id}/execute`);
		return response.data;
	}

	async cancelScan(id: number) {
		const response = await this.client.post(`/scans/${id}/cancel`);
		return response.data;
	}

	async deleteScan(id: number) {
		await this.client.delete(`/scans/${id}`);
	}

	// Scan Templates
	async getScanTemplates(params?: any) {
		const response = await this.client.get('/scans/templates/', { params });
		return response.data;
	}

	async getScanTemplate(id: number) {
		const response = await this.client.get(`/scans/templates/${id}`);
		return response.data;
	}

	async createScanTemplate(data: any) {
		const response = await this.client.post('/scans/templates/', data);
		return response.data;
	}

	// Vulnerabilities
	async getVulnerabilities(params?: any) {
		const response = await this.client.get('/vulnerabilities/', { params });
		return response.data;
	}

	async getVulnerability(id: number) {
		const response = await this.client.get(`/vulnerabilities/${id}`);
		return response.data;
	}

	async getVulnerabilityStats(params?: any) {
		const response = await this.client.get('/vulnerabilities/stats', { params });
		return response.data;
	}

	async updateVulnerability(id: number, data: any) {
		const response = await this.client.patch(`/vulnerabilities/${id}`, data);
		return response.data;
	}

	async changeVulnerabilityState(id: number, state: string, notes?: string) {
		const response = await this.client.post(`/vulnerabilities/${id}/state`, {
			state,
			notes
		});
		return response.data;
	}

	async assignVulnerability(id: number, userId: number) {
		const response = await this.client.post(`/vulnerabilities/${id}/assign`, {
			assigned_to_user_id: userId
		});
		return response.data;
	}

	async acceptRisk(id: number, reason: string) {
		const response = await this.client.post(`/vulnerabilities/${id}/accept-risk`, null, {
			params: { reason }
		});
		return response.data;
	}

	async deleteVulnerability(id: number) {
		await this.client.delete(`/vulnerabilities/${id}`);
	}

	// Health
	async getHealth() {
		const response = await this.client.get('/health', { baseURL: 'http://localhost:8000' });
		return response.data;
	}
}

export const api = new ApiClient();
