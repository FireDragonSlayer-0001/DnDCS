import { $$ } from "../util/dom.js";

let activeTab = null;

export function init(defaultTab = "overview") {
  const tabs = $$(".tab");
  tabs.forEach((btn) => {
    btn.addEventListener("click", () => {
      activate(btn.dataset.tab);
    });
  });
  if (!activeTab) {
    activate(defaultTab);
  }
}

export function activate(id) {
  activeTab = id;
  $$(".tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === id);
  });
  $$(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `tab-${id}`);
  });
}

export function current() {
  return activeTab;
}

export function render() {
  if (activeTab) {
    activate(activeTab);
  }
}
