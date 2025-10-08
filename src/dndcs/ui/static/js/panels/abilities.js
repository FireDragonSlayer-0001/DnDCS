import { getCurrent, getDerived } from "../state/store.js";
import { ABILITIES } from "../util/abilities.js";
import { el, $ } from "../util/dom.js";

let ctx = null;
const elements = {};

export function init(context) {
  ctx = context;
  elements.abilitiesBody = $("#abilitiesBody");
  elements.savesBody = $("#savesBody");
}

export function render() {
  const current = getCurrent();
  const derived = getDerived();

  if (!elements.abilitiesBody || !elements.savesBody) {
    return;
  }

  if (!current) {
    elements.abilitiesBody.innerHTML = "";
    elements.savesBody.innerHTML = "";
    return;
  }

  current.abilities = current.abilities || {};
  elements.abilitiesBody.innerHTML = "";

  ABILITIES.forEach((ability) => {
    const score = current.abilities[ability]?.score ?? 10;
    const mod = derived?.ability_mods?.[ability] ?? Math.floor((score - 10) / 2);

    const decrease = el("button", {
      class: "btn-sm",
      onclick: async () => {
        const next = Math.max(1, score - 1);
        current.abilities[ability] = { name: ability, score: next };
        await ctx.runDerive();
        render();
      },
    }, "−");

    const increase = el("button", {
      class: "btn-sm",
      onclick: async () => {
        const next = Math.min(30, score + 1);
        current.abilities[ability] = { name: ability, score: next };
        await ctx.runDerive();
        render();
      },
    }, "+");

    const input = el("input", {
      type: "number",
      min: "1",
      max: "30",
      value: String(score),
      oninput: async (event) => {
        const value = parseInt(event.target.value || "10", 10);
        current.abilities[ability] = {
          name: ability,
          score: Math.max(1, Math.min(30, value)),
        };
        await ctx.runDerive();
        render();
      },
    });

    elements.abilitiesBody.append(
      el("tr", {},
        el("td", {}, ability),
        el("td", {}, input),
        el("td", {}, (mod >= 0 ? "+" : "") + mod),
        el("td", {}, decrease, " ", increase),
      ),
    );
  });

  elements.savesBody.innerHTML = "";
  ABILITIES.forEach((ability) => {
    const value = derived?.saving_throws?.[ability] ?? 0;
    elements.savesBody.append(
      el("tr", {},
        el("td", {}, ability),
        el("td", {}, (value >= 0 ? "+" : "") + value),
      ),
    );
  });
}
