(function () {
  const fileInput = document.getElementById("file");
  const out = document.getElementById("output");
  const meta = document.getElementById("meta");

  function setOutput(text) { out.textContent = text; }
  function setMeta(info) { meta.textContent = info || ""; }

  fileInput.addEventListener("change", async (e) => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    try {
      const text = await f.text();
      const data = JSON.parse(text);
      const name = data?.name ?? "(unknown)";
      const module = data?.module ?? "(no module)";
      const level = data?.level ?? "(no level)";
      setMeta(`Name: ${name} | Module: ${module} | Level: ${level}`);
      setOutput(JSON.stringify(data, null, 2));
    } catch (err) {
      setMeta("");
      setOutput(`Error: ${String(err)}`);
    }
  });
})();
