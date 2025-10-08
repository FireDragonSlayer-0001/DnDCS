import { boot } from "./app.js";

function start() {
  boot().catch((err) => {
    console.error("Failed to boot UI", err);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start, { once: true });
} else {
  start();
}
