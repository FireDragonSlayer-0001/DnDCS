import { boot } from "./app.js";
import * as api from "./services/api.js";
import * as store from "./state/store.js";

if (typeof window !== "undefined") {
  window.DnDCS = window.DnDCS || {};
  window.DnDCS.api = api;
  window.DnDCS.store = store;
}

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
