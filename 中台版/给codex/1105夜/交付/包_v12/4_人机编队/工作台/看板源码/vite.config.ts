import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// 构建成一整包，再由 内联.mjs 并进单个 html
export default defineConfig({
  plugins: [react(), tailwindcss()],
  cacheDir: ".vite-cache",
  build: { outDir: "dist", emptyOutDir: true, chunkSizeWarningLimit: 4000, assetsInlineLimit: 100000000, cssCodeSplit: false, modulePreload: false },
});
