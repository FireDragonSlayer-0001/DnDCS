export const state = {
  current: null,
  derived: null,
  modules: [],
};

export function getCurrent() {
  return state.current;
}

export function setCurrent(value) {
  state.current = value;
  return state.current;
}

export function getDerived() {
  return state.derived;
}

export function setDerived(value) {
  state.derived = value;
  return state.derived;
}

export function getModules() {
  return state.modules;
}

export function setModules(list) {
  state.modules = Array.isArray(list) ? list : [];
  return state.modules;
}

export function updateSummary() {
  const current = state.current;
  const derived = state.derived;
  const has = !!current;
  const nameEl = document.querySelector("#sName");
  const levelEl = document.querySelector("#sLevel");
  const moduleEl = document.querySelector("#sModule");
  const pbEl = document.querySelector("#sPB");
  const acEl = document.querySelector("#sAC");
  const acSrcEl = document.querySelector("#sACsrc");
  const spellcastingEl = document.querySelector("#sSpellcasting");

  if (nameEl) nameEl.textContent = has ? current.name || "—" : "—";
  if (levelEl) levelEl.textContent = has ? `(Level ${current.level ?? "?"})` : "";
  if (moduleEl) moduleEl.textContent = has ? current.module || "—" : "—";
  if (pbEl) pbEl.textContent = derived?.proficiency_bonus ?? "—";
  if (acEl) acEl.textContent = derived?.ac?.value ?? "—";
  if (acSrcEl) acSrcEl.textContent = derived?.ac ? `(${derived.ac.source})` : "";

  if (spellcastingEl) {
    if (derived?.spellcasting) {
      spellcastingEl.classList.remove("hide");
      const dcEl = document.querySelector("#sDC");
      const atkEl = document.querySelector("#sATK");
      const prepCountEl = document.querySelector("#sPrepCount");
      const prepCapEl = document.querySelector("#sPrepCap");
      if (dcEl) dcEl.textContent = derived.spellcasting.spell_save_dc;
      if (atkEl) atkEl.textContent = `+${derived.spellcasting.spell_attack_mod}`;
      const prepared = derived.spellcasting.prepared_spells?.length ?? 0;
      if (prepCountEl) prepCountEl.textContent = prepared;
      if (prepCapEl) prepCapEl.textContent = derived.spellcasting.prepared_max ?? "—";
    } else {
      spellcastingEl.classList.add("hide");
    }
  }
}
