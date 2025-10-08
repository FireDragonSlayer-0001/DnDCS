import { apiSpells } from "../../services/api.js";
import { getCurrent, getDerived } from "../../state/store.js";
import { el, $ } from "../../util/dom.js";
import { logError } from "../../util/logging.js";
import { toast } from "../../components/toast.js";
import { ensureSpellbook, getSpellbook, enforcePreparedCap } from "./book.js";

let ctx = null;
const elements = {};

const LEVEL_KEYS = ["C", "1", "2", "3", "4", "5", "6", "7", "8", "9"];

export function init(context) {
  ctx = context;
  elements.wrap = $("#spellLists");
  elements.levelSelect = $("#spellLevel");
  elements.nameInput = $("#spellName");
  elements.suggestions = $("#spellSuggestions");
  elements.addKnown = $("#addKnownBtn");
  elements.preparedOnly = $("#showPreparedOnly");

  if (elements.nameInput) {
    elements.nameInput.addEventListener("input", async () => {
      const term = elements.nameInput?.value.trim();
      if (!term) return;
      const current = getCurrent();
      const derived = getDerived();
      try {
        const cls = derived?.spellcasting?.class;
        const res = await apiSpells({ module: current?.module, name: term, cls });
        if (elements.suggestions) {
          elements.suggestions.innerHTML = "";
          res.spells.slice(0, 20).forEach((spell) => {
            elements.suggestions.append(el("option", { value: spell.name }));
          });
        }
      } catch (error) {
        console.error(error);
        logError(error, "spell suggestions");
      }
    });
  }

  if (elements.addKnown) {
    elements.addKnown.addEventListener("click", () => {
      const current = getCurrent();
      if (!current) return;
      const spellbook = ensureSpellbook();
      if (!spellbook) return;

      const level = elements.levelSelect?.value || "C";
      const name = elements.nameInput?.value.trim();
      if (!name) {
        toast("Spell name required");
        return;
      }

      if (level === "C") {
        if (!spellbook.known.cantrips.includes(name)) {
          spellbook.known.cantrips.push(name);
        }
      } else {
        const key = String(level);
        spellbook.known[key] = spellbook.known[key] || [];
        if (!spellbook.known[key].includes(name)) {
          spellbook.known[key].push(name);
        }
      }

      if (elements.nameInput) elements.nameInput.value = "";
      render();
      ctx.renderers.raw();
    });
  }

  if (elements.preparedOnly) {
    elements.preparedOnly.addEventListener("change", (event) => {
      document.body.classList.toggle("prepared-only", event.target.checked);
    });
  }
}

export function render() {
  const current = getCurrent();
  const derived = getDerived();

  if (!elements.wrap) return;

  if (!current) {
    elements.wrap.innerHTML = "";
    return;
  }

  let spellbook = getSpellbook();
  if (!spellbook) spellbook = ensureSpellbook();
  if (!spellbook) return;

  elements.wrap.innerHTML = "";
  const cap = derived?.spellcasting?.prepared_max ?? null;

  LEVEL_KEYS.forEach((levelKey) => {
    const column = el("div", { class: "spell-col" });
    const title = levelKey === "C" ? "Cantrips" : `Lvl ${levelKey}`;
    column.append(el("div", { class: "spell-col-title" }, title));

    const known = levelKey === "C"
      ? spellbook.known.cantrips || []
      : spellbook.known[String(levelKey)] || [];
    const prepared = levelKey === "C"
      ? []
      : spellbook.prepared[String(levelKey)] || [];

    const list = el("div", { class: "spell-list" });
    known.forEach((name, index) => {
      const row = el("div", { class: "spell-row" });
      const checkbox = el("input", { type: "checkbox" });
      if (levelKey !== "C") {
        checkbox.checked = prepared.includes(name);
        checkbox.disabled = false;
      } else {
        checkbox.checked = false;
        checkbox.disabled = true;
      }
      checkbox.addEventListener("change", () => {
        if (levelKey === "C") return;
        const store = spellbook.prepared[String(levelKey)] = spellbook.prepared[String(levelKey)] || [];
        if (checkbox.checked) {
          if (!store.includes(name)) store.push(name);
        } else {
          const idx = store.indexOf(name);
          if (idx >= 0) store.splice(idx, 1);
        }
        enforcePreparedCap(spellbook, cap);
        render();
        ctx.renderers.summary();
        ctx.renderers.raw();
      });

      const remove = el("button", {
        class: "btn-xs",
        onclick: () => {
          known.splice(index, 1);
          if (levelKey !== "C") {
            const store = spellbook.prepared[String(levelKey)] || [];
            const idx = store.indexOf(name);
            if (idx >= 0) store.splice(idx, 1);
          }
          render();
          ctx.renderers.summary();
          ctx.renderers.raw();
        },
      }, "✕");

      row.append(checkbox, el("span", { class: "spell-name" }, name), remove);
      list.append(row);
    });

    column.append(list);
    elements.wrap.append(column);
  });

  if (elements.preparedOnly) {
    document.body.classList.toggle("prepared-only", elements.preparedOnly.checked);
  }
}
