// Runs in the page via script.callFunction before a click, type or hover, so the user can
// watch what Claude does. Display only: aria-hidden, pointer-events none, no layout change,
// and walker.js skips it. rect is the target's {x, y, w, h} in viewport pixels.
// kind: click, right, double (ripples), drag, move, hover, type. The cursor slides from the
// last drawn position (the root is reused); the first root starts at the viewport center.
(x, y, kind, label, rect) => {
  const ID = "__zenpilot_overlay";
  const FADE_MS = 1500;
  const COLOR = "#e8590c";
  const SVG_NS = "http://www.w3.org/2000/svg";
  let root = document.getElementById(ID);
  if (!root || !root.isConnected) {
    root = document.createElement("div");
    root.id = ID;
    root.setAttribute("aria-hidden", "true");
    root.style.cssText = "position:fixed;inset:0;z-index:2147483647;pointer-events:none;" +
      "margin:0;padding:0;border:0;opacity:1;transition:opacity 300ms;";
    const style = document.createElement("style");
    style.textContent = "@keyframes __zp_ripple{from{transform:scale(1);opacity:.9}to{transform:scale(4);opacity:0}}";
    const box = document.createElement("div");
    box.dataset.part = "box";
    box.style.cssText = `position:fixed;border:2px solid ${COLOR};border-radius:4px;` +
      "box-shadow:0 0 0 1px rgba(255,255,255,.6);";
    const cursor = document.createElement("div");
    cursor.dataset.part = "cursor";
    cursor.style.cssText = "position:fixed;left:0;top:0;width:20px;height:20px;margin:0;pointer-events:none;" +
      "transition:left 250ms ease,top 250ms ease;";
    const arrow = document.createElementNS(SVG_NS, "svg");
    arrow.setAttribute("width", "20");
    arrow.setAttribute("height", "20");
    arrow.setAttribute("viewBox", "0 0 20 20");
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("d", "M1 1 L1 16 L5.5 12 L8.5 18.5 L11 17.5 L8 11.5 L14 11.5 Z");
    path.setAttribute("fill", COLOR);
    path.setAttribute("stroke", "#fff");
    path.setAttribute("stroke-width", "1.5");
    path.setAttribute("stroke-linejoin", "round");
    arrow.appendChild(path);
    cursor.appendChild(arrow);
    const chip = document.createElement("div");
    chip.dataset.part = "label";
    chip.style.cssText = "position:fixed;padding:2px 6px;border-radius:4px;background:#1a1a1a;color:#fff;" +
      "font:12px/1.4 system-ui,sans-serif;white-space:nowrap;";
    root.append(style, box, cursor, chip);
    cursor.style.left = window.innerWidth / 2 + "px";
    cursor.style.top = window.innerHeight / 2 + "px";
    document.documentElement.appendChild(root);
    void cursor.offsetWidth; // commit the center position so the first move slides from it
  }
  const part = (name) => root.querySelector(`[data-part="${name}"]`);
  const box = part("box");
  const cursor = part("cursor");
  const chip = part("label");

  root.style.opacity = "1";
  Object.assign(box.style, { left: rect.x + "px", top: rect.y + "px",
    width: rect.w + "px", height: rect.h + "px", display: "block" });
  Object.assign(cursor.style, { left: x + "px", top: y + "px" });
  chip.textContent = label;
  Object.assign(chip.style, { left: x + 12 + "px", top: y + 12 + "px" });

  const ripples = { click: 1, right: 1, double: 2 }[kind] || 0;
  for (let i = 0; i < ripples; i++) {
    const delay = i * 120;
    const ripple = document.createElement("div");
    ripple.style.cssText = `position:fixed;left:${x}px;top:${y}px;width:14px;height:14px;margin:-7px 0 0 -7px;` +
      `border:2px solid ${COLOR};border-radius:50%;box-sizing:border-box;` +
      `animation:__zp_ripple 400ms ease-out ${delay}ms forwards;`;
    root.appendChild(ripple);
    setTimeout(() => ripple.remove(), delay + 450);
  }

  clearTimeout(root._zpFade);
  root._zpFade = setTimeout(() => { root.style.opacity = "0"; }, FADE_MS);
}
