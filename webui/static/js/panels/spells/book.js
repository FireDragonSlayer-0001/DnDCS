import { getCurrent } from "../../state/store.js";

export function getSpellbook() {
  const character = getCurrent();
  if (!character || !character.items) return null;
  const item = character.items.find((it) =>
    (it.name || "").toLowerCase() === "spellbook" || (it.props && it.props.spellbook),
  );
  return item ? item.props.spellbook : null;
}

export function ensureSpellbook() {
  const character = getCurrent();
  if (!character) return null;
  if (!Array.isArray(character.items)) character.items = [];

  let spellbook = getSpellbook();
  if (spellbook) {
    spellbook.known = spellbook.known || {};
    spellbook.prepared = spellbook.prepared || {};
    spellbook.known.cantrips = spellbook.known.cantrips || [];
    return spellbook;
  }

  spellbook = { known: { cantrips: [] }, prepared: {} };
  character.items.push({ name: "Spellbook", quantity: 1, props: { spellbook } });
  return spellbook;
}

export function enforcePreparedCap(spellbook, cap) {
  if (!Number.isFinite(cap) || cap == null) return;

  const all = [];
  for (let level = 1; level <= 9; level++) {
    const list = spellbook.prepared[String(level)] || [];
    for (const spell of list) {
      all.push({ level, spell });
    }
  }

  if (all.length <= cap) return;

  const extras = all.length - cap;
  for (let i = 0; i < extras; i++) {
    const last = all.pop();
    const list = spellbook.prepared[String(last.level)];
    const index = list.indexOf(last.spell);
    if (index >= 0) list.splice(index, 1);
  }
}
