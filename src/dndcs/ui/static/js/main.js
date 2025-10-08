import * as api from "./services/api.js";
import * as store from "./state/store.js";
import { logError } from "./util/logging.js";
import { $ } from "./util/dom.js";
import * as tabs from "./components/tabs.js";
import * as summary from "./components/summary.js";
import { init as initToast, toast } from "./components/toast.js";
import * as overviewPanel from "./panels/overview.js";
import * as abilitiesPanel from "./panels/abilities.js";
import * as spellsPanel from "./panels/spells/index.js";
import * as itemsPanel from "./panels/items.js";
import * as featsPanel from "./panels/feats.js";
import * as notesPanel from "./panels/notes.js";
import * as rawPanel from "./panels/raw.js";
import { newCharacter, openFile, saveCharacter, validateCharacter } from "./features/storage.js";

let booted = false;

const context = {
  runDerive,
  renderers: {
    summary: () => summary.render(),
    abilities: () => abilitiesPanel.render(),
    spells: () => spellsPanel.render(),
    items: () => itemsPanel.render(),
    feats: () => featsPanel.render(),
    notes: () => notesPanel.render(),
    raw: () => rawPanel.render(),
  },
};

async function runDerive() {
  const current = store.getCurrent();
  if (!current) return;
  try {
    const result = await api.apiDerive(current);
    store.setDerived(result);
    summary.render();
    abilitiesPanel.render();
    spellsPanel.render();
    rawPanel.render();
  } catch (error) {
    store.setDerived(null);
    summary.render();
    toast(`Derive failed: ${error.message}`);
    logError(error, "derive");
  }
}

async function runValidate() {
  const current = store.getCurrent();
  if (!current) return [];
  try {
    return await validateCharacter(current);
  } catch (error) {
    toast(`Validate failed: ${error.message}`);
    logError(error, "validate");
    return ["Validation error"];
  }
}

function renderAll() {
  summary.render();
  overviewPanel.render();
  abilitiesPanel.render();
  spellsPanel.render();
  itemsPanel.render();
  featsPanel.render();
  notesPanel.render();
  rawPanel.render();
}

function registerGlobalErrorHandlers() {
  window.addEventListener("error", (event) => {
    const error = event.error || new Error(event.message);
    console.error(error);
    toast("Error: " + error.message);
    logError(error, "window.error");
  });

  window.addEventListener("unhandledrejection", (event) => {
    const reason = event.reason instanceof Error ? event.reason : new Error(event.reason);
    console.error(reason);
    toast("Error: " + reason.message);
    logError(reason, "unhandledrejection");
    event.preventDefault();
  });
}

async function loadModules() {
  try {
    const data = await api.apiModules();
    const modules = store.setModules(data.modules || []);
    const select = $("#moduleSelect");
    if (!select) return;
    select.innerHTML = "";

    modules.forEach((mod) => {
      const option = document.createElement("option");
      option.value = mod.id;
      option.textContent = `${mod.name} (${mod.version})`;
      select.append(option);
    });

    const saved = localStorage.getItem("dndcs.moduleId");
    let chosen = saved && modules.find((m) => m.id === saved) ? saved : null;
    if (!chosen) {
      const stock = modules.find((m) => m.id === "fivee_stock");
      chosen = stock ? stock.id : modules[0]?.id || "";
    }

    select.value = chosen;
    localStorage.setItem("dndcs.moduleId", chosen);
    select.addEventListener("change", () => localStorage.setItem("dndcs.moduleId", select.value));
  } catch (error) {
    toast("Failed to load modules");
    console.error(error);
    logError(error, "load modules");
  }
}

async function handleNewCharacter() {
  const select = $("#moduleSelect");
  const moduleId = select?.value || "";
  try {
    const character = await newCharacter(moduleId, "New Hero");
    store.setCurrent(character);
    store.setDerived(null);
    renderAll();
    await runDerive();
    tabs.activate("overview");
  } catch (error) {
    toast("New character failed: " + error.message);
    logError(error, "new character");
  }
}

async function handleOpenFile(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  try {
    const character = await openFile(file);
    store.setCurrent(character);
    store.setDerived(null);
    renderAll();
    await runDerive();
    tabs.activate("overview");
  } catch (error) {
    toast("Open failed: " + error.message);
    logError(error, "open file");
  } finally {
    event.target.value = "";
  }
}

async function handleSave() {
  const current = store.getCurrent();
  if (!current) {
    toast("Nothing to save");
    return;
  }
  const issues = await runValidate();
  if (issues.length) {
    toast(`Saved with warnings (${issues.length})`);
  } else {
    toast("Saved");
  }
  try {
    saveCharacter(current);
  } catch (error) {
    toast("Save failed: " + error.message);
    logError(error, "save file");
  }
}

async function handleValidate() {
  const issues = await runValidate();
  const message = issues.length ? `Validation issues:\n- ${issues.join("\n- ")}` : "OK";
  alert(message);
}

async function boot() {
  if (booted) return;
  booted = true;

  if (typeof window !== "undefined") {
    window.DnDCS = window.DnDCS || {};
    window.DnDCS.api = api;
    window.DnDCS.store = store;
  }

  initToast();
  summary.init();
  rawPanel.init();

  overviewPanel.init(context);
  abilitiesPanel.init(context);
  spellsPanel.init(context);
  itemsPanel.init(context);
  featsPanel.init(context);
  notesPanel.init(context);

  tabs.init("overview");
  registerGlobalErrorHandlers();
  await loadModules();

  const newButton = $("#newCharBtn");
  const fileInput = $("#file");
  const saveButton = $("#saveBtn");
  const deriveButton = $("#deriveBtn");
  const validateButton = $("#validateBtn");

  newButton?.addEventListener("click", handleNewCharacter);
  fileInput?.addEventListener("change", handleOpenFile);
  saveButton?.addEventListener("click", handleSave);
  deriveButton?.addEventListener("click", runDerive);
  validateButton?.addEventListener("click", handleValidate);

  renderAll();
}

function start() {
  boot().catch((error) => {
    console.error("Failed to boot UI", error);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start, { once: true });
} else {
  start();
}
