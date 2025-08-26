(() => {
  // ---------- state ----------
  const ABILS = ["STR","DEX","CON","INT","WIS","CHA"];
  let current = null;       // character JSON
  let derived = null;       // derived payload
  let modules = [];         // discovered modules

  // ---------- el helpers ----------
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  const el = (tag, attrs={}, ...children) => {
    const n = document.createElement(tag);
    Object.entries(attrs).forEach(([k,v]) => {
      if (k === "class") n.className = v;
      else if (k === "html") n.innerHTML = v;
      else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.substring(2), v);
      else n.setAttribute(k, v);
    });
    children.forEach(c => n.append(c));
    return n;
  };

  const toast = (msg, ms=1800) => {
    const d = $("#toast");
    d.textContent = msg;
    d.show();
    setTimeout(() => d.close(), ms);
  };

  async function logError(err, context="") {
    const message = err?.message || String(err);
    const payload = {
      level: "error",
      message: context ? `${context}: ${message}` : message,
      stack: err?.stack,
    };
    try {
      await fetch("/api/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (_) {}
  }

  // Global error handlers – show a toast but allow UI to remain usable
  window.addEventListener("error", (e) => {
    const err = e.error || new Error(e.message);
    console.error(err);
    toast("Error: " + err.message);
    logError(err, "window.error");
  });

  window.addEventListener("unhandledrejection", (e) => {
    const err = e.reason instanceof Error ? e.reason : new Error(e.reason);
    console.error(err);
    toast("Error: " + err.message);
    logError(err, "unhandledrejection");
    e.preventDefault();
  });

  // ---------- api ----------
  async function getJSON(url, opts={}) {
    const r = await fetch(url, { ...opts, headers: { "Content-Type": "application/json", ...(opts.headers||{}) }});
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return await r.json();
  }

  async function apiModules() { return getJSON("/api/modules"); }
  async function apiNewCharacter(module_id, name="New Hero") {
    return getJSON("/api/new_character", { method: "POST", body: JSON.stringify({ module_id, name })});
  }
  async function apiDerive(char) {
    return getJSON("/api/derive", { method: "POST", body: JSON.stringify(char) });
  }
  async function apiValidate(char) {
    return getJSON("/api/validate", { method: "POST", body: JSON.stringify(char) });
  }
  async function apiSpells(params={}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k,v]) => {
      if (v !== undefined && v !== null && v !== "") q.append(k, v);
    });
    return getJSON(`/api/spells?${q.toString()}`);
  }

  // ---------- utilities ----------
  function slug(s){ return (s||"character").toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,""); }
  function deepCopy(x){ return JSON.parse(JSON.stringify(x)); }

  // Ensure Spellbook structure exists (for wizard flows in our SRD module)
  function ensureSpellbook() {
    if (!current) return;
    if (!Array.isArray(current.items)) current.items = [];
    const found = current.items.find(it =>
      (it.name||"").toLowerCase()==="spellbook" || (it.props && it.props.spellbook)
    );
    if (found) {
      found.props = found.props || {};
      found.props.spellbook = found.props.spellbook || { known:{}, prepared:{} };
      found.props.spellbook.known = found.props.spellbook.known || {};
      found.props.spellbook.prepared = found.props.spellbook.prepared || {};
      found.props.spellbook.known.cantrips = found.props.spellbook.known.cantrips || [];
      return found.props.spellbook;
    }
    const sb = { known:{ cantrips: [] }, prepared:{} };
    current.items.push({ name:"Spellbook", quantity:1, props: { spellbook: sb }});
    return sb;
  }

  function getSpellbook() {
    if (!current || !current.items) return null;
    const it = current.items.find(it =>
      (it.name||"").toLowerCase()==="spellbook" || (it.props && it.props.spellbook)
    );
    return it ? it.props.spellbook : null;
  }

  // ---------- summary bar ----------
  function updateSummary() {
    const has = !!current;
    $("#sName").textContent = has ? current.name || "—" : "—";
    $("#sLevel").textContent = has ? `(Level ${current.level ?? "?"})` : "";
    $("#sModule").textContent = has ? current.module || "—" : "—";
    $("#sPB").textContent = derived?.proficiency_bonus ?? "—";
    $("#sAC").textContent = derived?.ac?.value ?? "—";
    $("#sACsrc").textContent = derived?.ac ? `(${derived.ac.source})` : "";

    const sc = $("#sSpellcasting");
    if (derived?.spellcasting) {
      sc.classList.remove("hide");
      $("#sDC").textContent = derived.spellcasting.spell_save_dc;
      $("#sATK").textContent = `+${derived.spellcasting.spell_attack_mod}`;
      const prep = derived.spellcasting.prepared_spells?.length ?? 0;
      $("#sPrepCount").textContent = prep;
      $("#sPrepCap").textContent = derived.spellcasting.prepared_max ?? "—";
    } else {
      sc.classList.add("hide");
    }
  }

  // ---------- tabs ----------
  function switchTab(id) {
    $$(".tab").forEach(t => t.classList.toggle("active", t.dataset.tab === id));
    $$(".panel").forEach(p => p.classList.toggle("active", p.id === `tab-${id}`));
  }
  $$(".tab").forEach(btn => btn.addEventListener("click", () => switchTab(btn.dataset.tab)));

  // ---------- overview panel ----------
  function renderOverview() {
    if (!current) return;
    $("#iName").value = current.name ?? "";
    $("#iLevel").value = current.level ?? 1;
    $("#iModule").value = current.module ?? "";

    // saving throw profs
    const row = $("#saveProfRow");
    row.innerHTML = "";
    current.proficiencies = current.proficiencies || { saving_throws: {} };
    const st = current.proficiencies.saving_throws || {};
    ABILS.forEach(ab => {
      const id = `st_${ab}`;
      const cb = el("input", { type:"checkbox", id });
      cb.checked = !!st[ab];
      cb.addEventListener("change", async () => {
        current.proficiencies.saving_throws[ab] = cb.checked;
        await runDerive();
        renderAbilities();
      });
      row.append(
        el("label", { class:"chip", for:id }, cb, ` ${ab}`)
      );
    });

    $("#iName").oninput = () => { current.name = $("#iName").value; updateSummary(); renderRaw(); };
    $("#iLevel").onchange = async () => {
      const v = parseInt($("#iLevel").value || "1", 10);
      current.level = Number.isFinite(v) ? Math.max(1, Math.min(20, v)) : 1;
      await runDerive();
      renderSpells(); // prepared cap may change
    };
  }

  // ---------- abilities panel ----------
  function renderAbilities() {
    if (!current) return;
    current.abilities = current.abilities || {};
    // table rows
    const body = $("#abilitiesBody");
    body.innerHTML = "";
    ABILS.forEach(ab => {
      const score = current.abilities[ab]?.score ?? 10;
      const mod = derived?.ability_mods?.[ab] ?? Math.floor((score - 10)/2);
      const dec = el("button", { class:"btn-sm", onclick: async () => {
        const s = Math.max(1, score - 1);
        current.abilities[ab] = { name: ab, score: s };
        await runDerive();
        renderAbilities();
      }}, "−");
      const inc = el("button", { class:"btn-sm", onclick: async () => {
        const s = Math.min(30, score + 1);
        current.abilities[ab] = { name: ab, score: s };
        await runDerive();
        renderAbilities();
      }}, "+");
      body.append(el("tr", {},
        el("td", {}, ab),
        el("td", {}, el("input", { type:"number", min:"1", max:"30", value:String(score), oninput: async (e)=>{
          const v = parseInt(e.target.value||"10",10);
          current.abilities[ab] = { name: ab, score: Math.max(1,Math.min(30, v)) };
          await runDerive();
          renderAbilities();
        }})),
        el("td", {}, (mod>=0?"+":"") + mod),
        el("td", {}, dec, " ", inc),
      ));
    });

    const sb = $("#savesBody");
    sb.innerHTML = "";
    ABILS.forEach(ab => {
      const val = derived?.saving_throws?.[ab] ?? 0;
      sb.append(el("tr", {}, el("td", {}, ab), el("td", {}, (val>=0?"+":"") + val)));
    });
  }

  // ---------- items panel ----------
  function renderItems() {
    if (!current) return;
    current.items = current.items || [];
    const body = $("#itemsBody");
    body.innerHTML = "";
    current.items.forEach((it, idx) => {
      const remove = el("button", { class:"btn-sm", onclick: async () => {
        current.items.splice(idx,1);
        await runDerive();
        renderItems();
      }}, "Remove");
      body.append(el("tr", {},
        el("td", {}, el("input", { value: it.name || "", oninput: (e)=>{ it.name=e.target.value; } })),
        el("td", {}, el("input", { type:"number", min:"1", value: it.quantity ?? 1, oninput: (e)=>{ it.quantity = parseInt(e.target.value||"1",10)||1; } })),
        el("td", {}, el("input", { value: JSON.stringify(it.props || {}), onchange: async (e)=>{
          try { it.props = JSON.parse(e.target.value || "{}"); }
          catch (e) { toast("Invalid props JSON"); logError(e, "item props parse"); }
          await runDerive(); // AC etc. may change
        }})),
        el("td", {}, remove),
      ));
    });

    $("#addItemBtn").onclick = async () => {
      const name = $("#itemName").value.trim();
      const qty = parseInt($("#itemQty").value||"1",10) || 1;
      let props = {};
      if ($("#itemProps").value.trim()) {
        try { props = JSON.parse($("#itemProps").value); } catch (e) { logError(e, "item props parse"); return toast("Invalid props JSON"); }
      }
      current.items.push({ name, quantity: qty, props });
      $("#itemName").value = ""; $("#itemQty").value = 1; $("#itemProps").value = "";
      await runDerive(); renderItems();
    };
  }

  // ---------- feats panel ----------
  function renderFeats() {
    if (!current) return;
    current.feats = current.feats || [];
    const body = $("#featsBody");
    body.innerHTML = "";
    current.feats.forEach((ft, idx) => {
      const remove = el("button", { class:"btn-sm", onclick: () => { current.feats.splice(idx,1); renderFeats(); }}, "Remove");
      body.append(el("tr", {},
        el("td", {}, el("input", { value: ft.name || "", oninput: (e)=>{ ft.name=e.target.value; } })),
        el("td", {}, el("input", { value: ft.description || "", oninput: (e)=>{ ft.description=e.target.value; } })),
        el("td", {}, remove),
      ));
    });

    $("#addFeatBtn").onclick = () => {
      const name = $("#featName").value.trim();
      const description = $("#featDesc").value.trim();
      if (!name) return toast("Feat name required");
      current.feats.push({ name, description });
      $("#featName").value = ""; $("#featDesc").value = "";
      renderFeats();
    };
  }

  // ---------- notes panel ----------
  function renderNotes() {
    if (!current) return;
    $("#notesArea").value = current.notes || "";
    $("#notesArea").oninput = () => { current.notes = $("#notesArea").value; renderRaw(); };
  }

  // ---------- spells panel ----------
  function levelKeys() { return ["C","1","2","3","4","5","6","7","8","9"]; }

  function renderSpells() {
    if (!current) return;
    const sb = ensureSpellbook();
    const wrap = $("#spellLists");
    wrap.innerHTML = "";

    // update suggestions as user types spell names
    const nameInput = $("#spellName");
    nameInput.oninput = async () => {
      const term = nameInput.value.trim();
      if (!term) return;
      try {
        const cls = derived?.spellcasting?.class;
        const res = await apiSpells({ module: current?.module, name: term, cls });
        const dl = $("#spellSuggestions");
        dl.innerHTML = "";
        res.spells.slice(0, 20).forEach(sp => dl.append(el("option", { value: sp.name })));
      } catch (e) {
        console.error(e);
        logError(e, "spell suggestions");
      }
    };

    // derived spellcasting summary available?
    const cap = derived?.spellcasting?.prepared_max ?? null;

    levelKeys().forEach((L) => {
      const col = el("div", { class:"spell-col" });
      const title = L === "C" ? "Cantrips" : `Lvl ${L}`;
      col.append(el("div", { class:"spell-col-title" }, title));

      // known list for this level
      const known = (L==="C" ? (sb.known.cantrips || []) : (sb.known[String(L)] || []));
      const prep = (L==="C" ? [] : (sb.prepared[String(L)] || []));

      const list = el("div", { class:"spell-list" });
      known.forEach((name, idx) => {
        const row = el("div", { class:"spell-row" });
        const chk = el("input", { type:"checkbox" });
        if (L!=="C") chk.checked = prep.includes(name);
        chk.disabled = (L==="C"); // cantrips aren't "prepared" in 5e
        chk.addEventListener("change", () => {
          const target = sb.prepared[String(L)] = sb.prepared[String(L)] || [];
          if (chk.checked) {
            if (!target.includes(name)) target.push(name);
          } else {
            const i = target.indexOf(name);
            if (i>=0) target.splice(i,1);
          }
          enforcePreparedCap(sb, cap);
          renderSpells();
          updateSummary();
          renderRaw();
        });

        const del = el("button", { class:"btn-xs", onclick: () => {
          known.splice(idx,1);
          // also unprepare if present
          if (L!=="C") {
            const t = sb.prepared[String(L)] || [];
            const i = t.indexOf(name); if (i>=0) t.splice(i,1);
          }
          renderSpells(); updateSummary(); renderRaw();
        }}, "✕");

        row.append(chk, el("span", { class:"spell-name" }, name), del);
        list.append(row);
      });

      col.append(list);
      wrap.append(col);
    });

    // Add known handler
    $("#addKnownBtn").onclick = () => {
      const L = $("#spellLevel").value;
      const name = $("#spellName").value.trim();
      if (!name) return toast("Spell name required");
      if (L==="C") {
        if (!sb.known.cantrips.includes(name)) sb.known.cantrips.push(name);
      } else {
        const key = String(L);
        sb.known[key] = sb.known[key] || [];
        if (!sb.known[key].includes(name)) sb.known[key].push(name);
      }
      $("#spellName").value = "";
      renderSpells(); renderRaw();
    };

    // Prepared-only toggle
    $("#showPreparedOnly").onchange = (e) => {
      document.body.classList.toggle("prepared-only", e.target.checked);
    };
  }

  function enforcePreparedCap(sb, cap) {
    if (!Number.isFinite(cap) || cap == null) return;
    // Flatten prepared across levels
    const all = [];
    for (let L=1; L<=9; L++) {
      const arr = sb.prepared[String(L)] || [];
      for (const s of arr) all.push({ L, s });
    }
    if (all.length <= cap) return;
    // Trim extras from the end
    const extras = all.length - cap;
    for (let i=0; i<extras; i++) {
      const last = all.pop();
      const arr = sb.prepared[String(last.L)];
      const idx = arr.indexOf(last.s);
      if (idx>=0) arr.splice(idx,1);
    }
  }

  // ---------- raw panel ----------
  function renderRaw() {
    $("#rawOut").textContent = current ? JSON.stringify(current, null, 2) : "(no character loaded)";
  }

  // ---------- derive/validate ----------
  async function runDerive() {
    if (!current) return;
    try {
      derived = await apiDerive(current);
      updateSummary();
      renderRaw();
    } catch (e) {
      derived = null;
      updateSummary();
      toast("Derive failed: " + e.message);
      logError(e, "derive");
    }
  }

  async function runValidate() {
    if (!current) return [];
    try {
      const res = await apiValidate(current);
      return res.issues || [];
    } catch (e) {
      toast("Validate failed: " + e.message);
      logError(e, "validate");
      return ["Validation error"];
    }
  }

  // ---------- load/save ----------
  function downloadJSON(filename, data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  // ---------- boot ----------
  async function boot() {
    // modules
    try {
      const data = await apiModules();
      modules = data.modules || [];
      const sel = $("#moduleSelect");
      sel.innerHTML = "";
      // build options
modules.forEach(m => {
  const opt = el("option", { value: m.id }, `${m.name} (${m.version})`);
  sel.append(opt);
});

// Prefer saved -> fivee_stock -> first available
const saved = localStorage.getItem("dndcs.moduleId");
let chosen = saved && modules.find(m => m.id === saved) ? saved : null;
if (!chosen) {
  const stock = modules.find(m => m.id === "fivee_stock");
  chosen = stock ? stock.id : (modules[0]?.id || "");
}
sel.value = chosen;
localStorage.setItem("dndcs.moduleId", chosen);
sel.onchange = () => localStorage.setItem("dndcs.moduleId", sel.value);

    } catch (e) {
      toast("Failed to load modules"); console.error(e); logError(e, "load modules");
    }

    // buttons
    $("#newCharBtn").onclick = async () => {
      const module_id = $("#moduleSelect").value;
      try {
        current = await apiNewCharacter(module_id, "New Hero");
        derived = null;
        updateSummary();
        renderOverview(); renderAbilities(); renderItems(); renderFeats(); renderNotes(); renderSpells(); renderRaw();
        await runDerive();
        switchTab("overview");
      } catch (e) {
        toast("New character failed: " + e.message);
        logError(e, "new character");
      }
    };

    $("#file").addEventListener("change", async (e) => {
      const f = e.target.files?.[0]; if (!f) return;
      try {
        current = JSON.parse(await f.text());
        derived = null;
        updateSummary();
        renderOverview(); renderAbilities(); renderItems(); renderFeats(); renderNotes(); renderSpells(); renderRaw();
        await runDerive();
        switchTab("overview");
      } catch (err) {
        toast("Open failed: " + err.message);
        logError(err, "open file");
      }
    });

    $("#saveBtn").onclick = async () => {
      if (!current) return toast("Nothing to save");
      const issues = await runValidate();
      if (issues.length) {
        toast(`Saved with warnings (${issues.length})`);
      } else {
        toast("Saved");
      }
      const fn = `${slug(current.name||"character")}.json`;
      downloadJSON(fn, current);
    };

    $("#deriveBtn").onclick = runDerive;
    $("#validateBtn").onclick = async () => {
      const issues = await runValidate();
      const msg = issues.length ? `Validation issues:\n- ${issues.join("\n- ")}` : "OK";
      alert(msg);
    };

    // initial empty render
    renderRaw();
  }

  boot();
})();
