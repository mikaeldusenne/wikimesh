import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  base: "/wikimesh/",
  plugins: [vue()],
  resolve: { alias: { "@": new URL("./src", import.meta.url).pathname } },
  build: { assetsDir: "static" }, // Flask serves this directory itself.
  server: {
    host: true,
    proxy: { "/wikimesh/api": "http://app:5000" },
  },
});
