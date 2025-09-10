import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          mui: ['@mui/material', '@mui/icons-material'],
          'mui-x': ['@mui/x-charts', '@mui/x-data-grid'],
          emotion: ['@emotion/react', '@emotion/styled']
        }
      }

    }
  }
});
