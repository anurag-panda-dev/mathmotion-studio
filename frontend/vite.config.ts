import path from "node:path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"

// The backend (FastAPI, 127.0.0.1:8765) only accepts state-changing requests from
// the Vite dev origins (localhost:5173 / 127.0.0.1:5173). We therefore serve the
// dev app on exactly 5173 and proxy /api to the backend, so the browser always
// sees same-origin relative URLs — identical to the production build, which the
// backend serves itself from frontend/dist.
const backendOrigin = process.env.MATHMOTION_BACKEND_ORIGIN ?? "http://127.0.0.1:8765"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    strictPort: true,
    host: "127.0.0.1",
    proxy: {
      "/api": {
        target: backendOrigin,
        changeOrigin: false,
      },
    },
  },
  preview: {
    port: 5173,
    strictPort: true,
    host: "127.0.0.1",
    proxy: {
      "/api": {
        target: backendOrigin,
        changeOrigin: false,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
})
