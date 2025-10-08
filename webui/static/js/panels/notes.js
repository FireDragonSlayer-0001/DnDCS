import { getCurrent } from "../state/store.js";
import { $ } from "../util/dom.js";

let ctx = null;
let textarea = null;

export function init(context) {
  ctx = context;
  textarea = $("#notesArea");
  if (textarea) {
    textarea.addEventListener("input", () => {
      const current = getCurrent();
      if (!current) return;
      current.notes = textarea.value;
      ctx.renderers.raw();
    });
  }
}

export function render() {
  const current = getCurrent();
  if (textarea) {
    textarea.value = current?.notes || "";
  }
}
