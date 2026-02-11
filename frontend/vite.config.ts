import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Docker needs this to listen on network
    port: 5173,
    proxy: {
      "/api": {
        target: "http://backend:5000", // Still talking to the backend container
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
