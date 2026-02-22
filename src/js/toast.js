let container = null;

function ensureContainer() {
  if (container) return container;
  container = document.createElement("div");
  container.className = "toast-container";
  document.body.appendChild(container);
  return container;
}

export function showToast(message, type = "info", duration = 3000) {
  const c = ensureContainer();
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;

  const icon = type === "success" ? "\u2713" : type === "error" ? "\u2717" : "\u24D8";
  el.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-msg">${message}</span>`;

  c.appendChild(el);
  requestAnimationFrame(() => el.classList.add("show"));

  setTimeout(() => {
    el.classList.remove("show");
    el.addEventListener("transitionend", () => el.remove());
  }, duration);
}
