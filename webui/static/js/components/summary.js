import { getCurrent, getDerived } from "../state/store.js";
import { $ } from "../util/dom.js";

const elements = {};

export function init() {
  elements.name = $("#sName");
  elements.level = $("#sLevel");
  elements.module = $("#sModule");
  elements.pb = $("#sPB");
  elements.ac = $("#sAC");
  elements.acSrc = $("#sACsrc");
  elements.spellcasting = $("#sSpellcasting");
  elements.dc = $("#sDC");
  elements.atk = $("#sATK");
  elements.prepCount = $("#sPrepCount");
  elements.prepCap = $("#sPrepCap");
  render();
}

export function render() {
  const current = getCurrent();
  const derived = getDerived();
  const hasCharacter = Boolean(current);

  if (elements.name) elements.name.textContent = hasCharacter ? current.name || "—" : "—";
  if (elements.level) elements.level.textContent = hasCharacter ? `(Level ${current.level ?? "?"})` : "";
  if (elements.module) elements.module.textContent = hasCharacter ? current.module || "—" : "—";
  if (elements.pb) elements.pb.textContent = derived?.proficiency_bonus ?? "—";
  if (elements.ac) elements.ac.textContent = derived?.ac?.value ?? "—";
  if (elements.acSrc) elements.acSrc.textContent = derived?.ac ? `(${derived.ac.source})` : "";

  if (elements.spellcasting) {
    if (derived?.spellcasting) {
      elements.spellcasting.classList.remove("hide");
      if (elements.dc) elements.dc.textContent = derived.spellcasting.spell_save_dc;
      if (elements.atk) elements.atk.textContent = `+${derived.spellcasting.spell_attack_mod}`;
      if (elements.prepCount) {
        const prepared = derived.spellcasting.prepared_spells?.length ?? 0;
        elements.prepCount.textContent = prepared;
      }
      if (elements.prepCap) {
        elements.prepCap.textContent = derived.spellcasting.prepared_max ?? "—";
      }
    } else {
      elements.spellcasting.classList.add("hide");
    }
  }
}
