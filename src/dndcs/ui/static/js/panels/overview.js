import { getCurrent } from "../state/store.js";
import { ABILITIES } from "../util/abilities.js";
import { $, el } from "../util/dom.js";

let ctx = null;
const elements = {};

export function init(context) {
  ctx = context;
  elements.name = $("#iName");
  elements.level = $("#iLevel");
  elements.module = $("#iModule");
  elements.saveProfRow = $("#saveProfRow");

  if (elements.name) {
    elements.name.addEventListener("input", () => {
      const current = getCurrent();
      if (!current) return;
      current.name = elements.name.value;
      ctx.renderers.summary();
      ctx.renderers.raw();
    });
  }

  if (elements.level) {
    elements.level.addEventListener("change", async () => {
      const current = getCurrent();
      if (!current) return;
      const value = parseInt(elements.level.value || "1", 10);
      current.level = Number.isFinite(value) ? Math.max(1, Math.min(20, value)) : 1;
      await ctx.runDerive();
      ctx.renderers.spells();
    });
  }
}

export function render() {
  const current = getCurrent();

  if (!current) {
    if (elements.name) elements.name.value = "";
    if (elements.level) elements.level.value = "1";
    if (elements.module) elements.module.value = "";
    if (elements.saveProfRow) elements.saveProfRow.innerHTML = "";
    return;
  }

  if (elements.name) elements.name.value = current.name ?? "";
  if (elements.level) elements.level.value = current.level ?? 1;
  if (elements.module) elements.module.value = current.module ?? "";

  current.proficiencies = current.proficiencies || { saving_throws: {} };
  const savingThrows = current.proficiencies.saving_throws || {};

  if (elements.saveProfRow) {
    elements.saveProfRow.innerHTML = "";
    ABILITIES.forEach((ability) => {
      const id = `st_${ability}`;
      const checkbox = el("input", { type: "checkbox", id });
      checkbox.checked = !!savingThrows[ability];
      checkbox.addEventListener("change", async () => {
        current.proficiencies.saving_throws[ability] = checkbox.checked;
        await ctx.runDerive();
        ctx.renderers.abilities();
      });
      const label = el("label", { class: "chip", for: id }, checkbox, ` ${ability}`);
      elements.saveProfRow.append(label);
    });
  }
}
