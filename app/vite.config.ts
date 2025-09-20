import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.ico", "icon-192.png", "icon-512.png"],
      manifest: {
        name: "KeyQuest",
        short_name: "KeyQuest",
        description: "Accessible training drills and quests for keyboard mastery.",
        theme_color: "#000000",
        background_color: "#000000",
        display: "standalone",
        orientation: "portrait-primary",
        start_url: "/keyquest/",
        icons: [
          { src: "icon-192.png", sizes: "192x192", type: "image/png", purpose: "any maskable" },
          { src: "icon-512.png", sizes: "512x512", type: "image/png", purpose: "any maskable" }
        ],
      },
      workbox: { globPatterns: ["**/*.{js,css,html,ico,png,svg,webmanifest}"] },
      devOptions: { enabled: true },
    }),
  ],
  base: "/keyquest/",
});
