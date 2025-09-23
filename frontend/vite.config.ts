import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0', // Allow external connections (needed for Docker)
		port: 5173,
		strictPort: true,
		watch: {
			usePolling: true, // Better for Docker file watching
			interval: 100, // Check for changes every 100ms
		},
		hmr: {
			port: 5173,
			host: 'localhost' // HMR client connects to host
		}
	},
	optimizeDeps: {
		exclude: ['@sveltejs/kit'] // Prevent pre-bundling issues in dev
	}
});
