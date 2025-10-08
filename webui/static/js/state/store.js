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

