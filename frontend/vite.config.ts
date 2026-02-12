import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      "/api": {
        target: "http://backend:5000", // Still talking to the backend container
        changeOrigin: true,
        secure: false,
      },

      "/login": {
        target: "http://backend:5000", // Still talking to the backend container
        changeOrigin: true,
        secure: false,
      },

      "/register": {
        target: "http://backend:5000", // Still talking to the backend container
        changeOrigin: true,
        secure: false,
      },

      "/logout": {
        target: "http://backend:5000", // Still talking to the backend container
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
