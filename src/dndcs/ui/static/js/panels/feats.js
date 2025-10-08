import { getCurrent } from "../state/store.js";
import { el, $ } from "../util/dom.js";
import { toast } from "../components/toast.js";

let ctx = null;
const elements = {};

export function init(context) {
  ctx = context;
  elements.body = $("#featsBody");
  elements.addButton = $("#addFeatBtn");
  elements.nameInput = $("#featName");
  elements.descInput = $("#featDesc");

  if (elements.addButton) {
    elements.addButton.addEventListener("click", () => {
      const current = getCurrent();
      if (!current) return;

      const name = elements.nameInput?.value.trim();
      const description = elements.descInput?.value.trim() || "";
      if (!name) {
        toast("Feat name required");
        return;
      }

      current.feats = current.feats || [];
      current.feats.push({ name, description });

      if (elements.nameInput) elements.nameInput.value = "";
      if (elements.descInput) elements.descInput.value = "";

      render();
      ctx.renderers.raw();
    });
  }
}

export function render() {
  const current = getCurrent();

  if (!elements.body) {
    return;
  }

  if (!current) {
    elements.body.innerHTML = "";
    return;
  }

  current.feats = current.feats || [];
  elements.body.innerHTML = "";

  current.feats.forEach((feat, index) => {
    const removeButton = el("button", {
      class: "btn-sm",
      onclick: () => {
        current.feats.splice(index, 1);
        render();
        ctx.renderers.raw();
      },
    }, "Remove");

    const nameInput = el("input", {
      value: feat.name || "",
      oninput: (event) => {
        feat.name = event.target.value;
        ctx.renderers.raw();
      },
    });

    const descInput = el("input", {
      value: feat.description || "",
      oninput: (event) => {
        feat.description = event.target.value;
        ctx.renderers.raw();
      },
    });

    elements.body.append(
      el("tr", {},
        el("td", {}, nameInput),
        el("td", {}, descInput),
        el("td", {}, removeButton),
      ),
    );
  });
}
