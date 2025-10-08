import { getCurrent } from "../state/store.js";
import { el, $ } from "../util/dom.js";
import { toast } from "../components/toast.js";
import { logError } from "../util/logging.js";

let ctx = null;
const elements = {};

export function init(context) {
  ctx = context;
  elements.body = $("#itemsBody");
  elements.addButton = $("#addItemBtn");
  elements.nameInput = $("#itemName");
  elements.qtyInput = $("#itemQty");
  elements.propsInput = $("#itemProps");

  if (elements.addButton) {
    elements.addButton.addEventListener("click", async () => {
      const current = getCurrent();
      if (!current) return;

      const name = elements.nameInput?.value.trim() || "";
      const quantity = parseInt(elements.qtyInput?.value || "1", 10) || 1;
      let props = {};

      if (elements.propsInput && elements.propsInput.value.trim()) {
        try {
          props = JSON.parse(elements.propsInput.value);
        } catch (error) {
          logError(error, "item props parse");
          toast("Invalid props JSON");
          return;
        }
      }

      current.items = current.items || [];
      current.items.push({ name, quantity, props });

      if (elements.nameInput) elements.nameInput.value = "";
      if (elements.qtyInput) elements.qtyInput.value = 1;
      if (elements.propsInput) elements.propsInput.value = "";

      await ctx.runDerive();
      render();
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

  current.items = current.items || [];
  elements.body.innerHTML = "";

  current.items.forEach((item, index) => {
    const removeButton = el("button", {
      class: "btn-sm",
      onclick: async () => {
        current.items.splice(index, 1);
        await ctx.runDerive();
        render();
      },
    }, "Remove");

    const nameInput = el("input", {
      value: item.name || "",
      oninput: (event) => {
        item.name = event.target.value;
        ctx.renderers.raw();
      },
    });

    const quantityInput = el("input", {
      type: "number",
      min: "1",
      value: item.quantity ?? 1,
      oninput: (event) => {
        item.quantity = parseInt(event.target.value || "1", 10) || 1;
        ctx.renderers.raw();
      },
    });

    const propsInput = el("input", {
      value: JSON.stringify(item.props || {}),
      onchange: async (event) => {
        try {
          item.props = JSON.parse(event.target.value || "{}");
        } catch (error) {
          toast("Invalid props JSON");
          logError(error, "item props parse");
          return;
        }
        await ctx.runDerive();
        render();
      },
    });

    elements.body.append(
      el("tr", {},
        el("td", {}, nameInput),
        el("td", {}, quantityInput),
        el("td", {}, propsInput),
        el("td", {}, removeButton),
      ),
    );
  });
}
