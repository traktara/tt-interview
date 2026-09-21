import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    // Polling also supports bind mounts through Docker Desktop on Windows.
    watch: { usePolling: true },
    proxy: { '/api': 'http://api:5000' },
  },
});
