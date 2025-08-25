(function () {
  const moduleSelect = document.getElementById("moduleSelect");
  const newCharBtn = document.getElementById("newCharBtn");
  const fileInput = document.getElementById("file");
  const deriveBtn = document.getElementById("deriveBtn");
  const validateBtn = document.getElementById("validateBtn");
  const out = document.getElementById("output");
  const meta = document.getElementById("meta");

  let currentData = null;

  function setOutput(obj) {
    if (typeof obj === "string") {
      out.textContent = obj;
    } else {
      out.textContent = JSON.stringify(obj, null, 2);
    }
  }

  function setMeta(info) { meta.textContent = info || ""; }

  async function fetchJSON(url, opts) {
    const r = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return await r.json();
  }

  async function loadModules() {
    try {
      const data = await fetchJSON("/api/modules");
      moduleSelect.innerHTML = "";
      const saved = localStorage.getItem("dndcs.moduleId");
      data.modules.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m.id; opt.textContent = `${m.name} (${m.version})`;
        if (saved && saved === m.id) opt.selected = true;
        moduleSelect.appendChild(opt);
      });
      if (!moduleSelect.value && data.modules.length) {
        moduleSelect.value = data.modules[0].id;
      }
      localStorage.setItem("dndcs.moduleId", moduleSelect.value);
    } catch (e) {
      setOutput(`Failed to load modules: ${e}`);
    }
  }

  moduleSelect.addEventListener("change", () => {
    localStorage.setItem("dndcs.moduleId", moduleSelect.value);
  });

  newCharBtn.addEventListener("click", async () => {
    const module_id = moduleSelect.value;
    try {
      const data = await fetchJSON("/api/new_character", {
        method: "POST",
        body: JSON.stringify({ module_id, name: "New Hero" }),
      });
      currentData = data;
      setMeta(`Name: ${data.name} | Module: ${data.module} | Level: ${data.level}`);
      setOutput(data);
    } catch (e) {
      setOutput(`Error creating character: ${e}`);
    }
  });

  fileInput.addEventListener("change", async (e) => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    try {
      const text = await f.text();
      const data = JSON.parse(text);
      currentData = data;
      const name = data?.name ?? "(unknown)";
      const module = data?.module ?? "(no module)";
      const level = data?.level ?? "(no level)";
      setMeta(`Name: ${name} | Module: ${module} | Level: ${level}`);
      setOutput(data);
    } catch (err) {
      currentData = null;
      setMeta("");
      setOutput(`Error: ${String(err)}`);
    }
  });

  deriveBtn.addEventListener("click", async () => {
    if (!currentData) return setOutput("Load or create a character first.");
    try {
      const d = await fetchJSON("/api/derive", { method: "POST", body: JSON.stringify(currentData) });
      setMeta(`${meta.textContent} | PB: ${d.proficiency_bonus}`);
      setOutput({ derived: d, character: currentData });
    } catch (e) {
      setOutput(`Derive error: ${e}`);
    }
  });

  validateBtn.addEventListener("click", async () => {
    if (!currentData) return setOutput("Load or create a character first.");
    try {
      const r = await fetchJSON("/api/validate", { method: "POST", body: JSON.stringify(currentData) });
      setOutput({ issues: r.issues, character: currentData });
    } catch (e) {
      setOutput(`Validate error: ${e}`);
    }
  });

  loadModules();
})();
