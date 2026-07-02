/* Vivid Health theme — runtime behaviours.
   Cart: real Shopify cart.js API
   Sticky CTA: mirrors vivid/index.html .sticky-atc-- variants
   Reveal: IntersectionObserver-driven section fade-in */

const $  = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));

/* ─── Shopify cart ─── */

async function cartFetch() {
  const r = await fetch("/cart.js", { headers: { Accept: "application/json" } });
  return r.json();
}

async function cartAdd(id, qty = 1) {
  const r = await fetch("/cart/add.js", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ items: [{ id, quantity: qty }] }),
  });
  return r.json();
}

async function cartChange(line, qty) {
  const r = await fetch("/cart/change.js", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ line, quantity: qty }),
  });
  return r.json();
}

const formatR = (cents) =>
  "R" + (cents / 100).toLocaleString("en-ZA", { minimumFractionDigits: 2 });

function setPip(count) {
  const btn = $("#cartBtn");
  if (btn) btn.setAttribute("data-count", count);
}

async function openCart() {
  $("#scrim")?.classList.add("open");
  $("#drawer")?.classList.add("open");
  $("#drawer")?.setAttribute("aria-hidden", "false");
  await renderCart();
}

function closeCart() {
  $("#scrim")?.classList.remove("open");
  $("#drawer")?.classList.remove("open");
  $("#drawer")?.setAttribute("aria-hidden", "true");
}

async function renderCart() {
  const cart = await cartFetch();
  setPip(cart.item_count);
  const body = $("#drawerBody");
  const foot = $("#drawerFoot");
  if (!body) return;
  if (cart.item_count === 0) {
    body.innerHTML =
      '<div class="cart-empty"><p>Your basket is empty.</p><a href="/collections/all-formulations" class="btn btn--ghost" style="margin-top:18px" onclick="closeCart()">Browse the range</a></div>';
    if (foot) foot.innerHTML = "";
    return;
  }
  body.innerHTML = cart.items
    .map(
      (i, idx) => `
    <div class="cart-item">
      <div class="cart-item-img"><img src="${i.image}" alt="" loading="lazy"></div>
      <div>
        <div class="cart-item-name">${i.product_title}</div>
        <div class="cart-item-meta">${i.variant_title || ""}</div>
        <div style="display:flex;gap:8px;margin-top:8px">
          <div class="qty" style="height:30px">
            <button type="button" onclick="cartChange(${idx + 1}, ${i.quantity - 1}).then(renderCart)" aria-label="Decrease">−</button>
            <input value="${i.quantity}" readonly aria-label="Quantity">
            <button type="button" onclick="cartChange(${idx + 1}, ${i.quantity + 1}).then(renderCart)" aria-label="Increase">+</button>
          </div>
        </div>
      </div>
      <div class="cart-item-price">${formatR(i.final_line_price)}</div>
    </div>`
    )
    .join("");
  const ship = cart.total_price >= 40000 ? 0 : 10000;
  const fillPct = Math.min(100, (cart.total_price / 40000) * 100);
  const togo = Math.max(0, 40000 - cart.total_price);
  const shipMsg =
    togo === 0
      ? `<div class="ship-msg"><strong>You've unlocked free shipping.</strong> Nice.</div>`
      : `<div class="ship-msg">Spend <strong>${formatR(togo)}</strong> more for free shipping</div>`;
  if (foot) {
    foot.innerHTML = `
      <div class="ship-bar"><div class="ship-bar-fill" style="width:${fillPct}%"></div></div>
      ${shipMsg}
      <div class="cart-totals"><span>Subtotal</span><span>${formatR(cart.total_price)}</span></div>
      <div class="cart-totals"><span>Shipping</span><span>${ship === 0 ? "Free over R400" : formatR(ship)}</span></div>
      <div class="cart-totals total"><span>Total</span><span>${formatR(cart.total_price + ship)}</span></div>
      <a class="btn btn--forest btn--block" href="/checkout">Checkout — ${formatR(cart.total_price + ship)}</a>
    `;
  }
}

/* ─── Sticky mobile ATC / CTA ─── */

let stickyEl = null;
let stickyObserver = null;

function clearSticky() {
  if (stickyObserver) { stickyObserver.disconnect(); stickyObserver = null; }
  if (stickyEl) { stickyEl.remove(); stickyEl = null; }
}

/* Product-context sticky (PDP). Variant id + price + Add button. */
function initStickyProduct({ name, price, variantId, inStock }) {
  clearSticky();
  const el = document.createElement("div");
  el.className = "sticky-atc";
  el.innerHTML = `
    <span class="name">${name}</span>
    <span class="price">${price}</span>
    <button class="btn btn--forest" type="button" ${inStock ? "" : "disabled"} data-variant-id="${variantId}" data-action="sticky-add">
      ${inStock ? "Add" : "Sold out"}
    </button>
  `;
  document.body.appendChild(el);
  stickyEl = el;
  const addRow = document.querySelector(".add-row");
  if (!addRow) return;
  stickyObserver = new IntersectionObserver(([e]) => {
    if (stickyEl !== el || !el.isConnected) return;
    el.classList.toggle("visible", !e.isIntersecting);
  }, { threshold: 0 });
  stickyObserver.observe(addRow);
}

/* CTA-context sticky (home, journal, about, etc.). Mirrors hero CTAs. */
function initStickyCTA(triggerSelector, ctas) {
  clearSticky();
  const el = document.createElement("div");
  el.className = "sticky-atc sticky-atc--cta";
  el.innerHTML = ctas
    .map((c) => `<a href="${c.href}" class="btn ${c.cls || ""}">${c.label}</a>`)
    .join("");
  document.body.appendChild(el);
  stickyEl = el;
  const trigger = document.querySelector(triggerSelector);
  if (!trigger) return;
  stickyObserver = new IntersectionObserver(([e]) => {
    if (stickyEl !== el || !el.isConnected) return;
    el.classList.toggle("visible", !e.isIntersecting);
  }, { threshold: 0 });
  stickyObserver.observe(trigger);
}

/* ─── Reveal-on-scroll for .reveal sections ─── */

function initReveal() {
  if (!("IntersectionObserver" in window)) {
    $$(".reveal").forEach((el) => el.classList.add("in"));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -10% 0px" });
  $$(".reveal").forEach((el) => io.observe(el));
}

/* ─── Floating consultation chat ─── */

function escapeHTML(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function openChat() {
  const widget = $("#chatWidget");
  const btn = $("#chatBtn");
  if (!widget) return;
  widget.classList.add("open");
  widget.setAttribute("aria-hidden", "false");
  btn?.setAttribute("aria-expanded", "true");
  $("#chatInput")?.focus();
}

function closeChat() {
  const widget = $("#chatWidget");
  const btn = $("#chatBtn");
  if (!widget) return;
  widget.classList.remove("open");
  widget.setAttribute("aria-hidden", "true");
  btn?.setAttribute("aria-expanded", "false");
}

function consultationReply(message) {
  const term = String(message || "").toLowerCase();
  if (term.includes("stack") || term.includes("routine") || term.includes("combine")) {
    return 'Start with one outcome. The <a href="/collections/bundles">curated stacks</a> are the cleanest path: Allergy, Bone & Joint, or Rest & Focus, each with a 10% stack offer routed at checkout.';
  }
  if (term.includes("allergy") || term.includes("hay") || term.includes("sinus")) {
    return 'For seasonal support, start with the <a href="/collections/immunity">Immunity range</a> or go straight to the Allergy Stack. If you use medication or have severe reactions, <a href="https://wa.me/27713744910" target="_blank" rel="noopener">WhatsApp a consultant</a> before combining products.';
  }
  if (term.includes("sleep") || term.includes("stress") || term.includes("calm") || term.includes("mood")) {
    return 'For evenings, look at <a href="/collections/stress">Stress, Sleep & Mood</a>. If you want the routine built for you, the Rest & Focus Stack is the more complete starting point.';
  }
  if (term.includes("joint") || term.includes("bone") || term.includes("mobility") || term.includes("pain")) {
    return 'For structure and movement, start with <a href="/collections/joints">Joints & Mobility</a>. Bone Supreme is the foundation; the Bone & Joint Stack is the fuller mobility routine.';
  }
  if (term.includes("gut") || term.includes("digest") || term.includes("cleanse")) {
    return 'For digestion, use the <a href="/collections/gut">Gut Health range</a>. If you are unsure whether you need cleanse, lining support, or daily balance, the quiz will narrow that down.';
  }
  if (term.includes("quiz") || term.includes("recommend") || term.includes("choose")) {
    return 'Use the <a href="/pages/quiz">premium formulation quiz</a>. It starts with your goal, routine style, and format preference so you do not have to browse 52 products cold.';
  }
  if (term.includes("consult") || term.includes("human") || term.includes("whatsapp")) {
    return 'For personal suitability, dosage, or supplement-combination questions, <a href="https://wa.me/27713744910" target="_blank" rel="noopener">WhatsApp a Vivid consultant</a>. It is the best route for anything specific to your situation.';
  }
  return 'The fastest route is the <a href="/pages/quiz">premium quiz</a>. For a human check before you combine products, <a href="https://wa.me/27713744910" target="_blank" rel="noopener">WhatsApp a consultant</a>. For pre-built routines, shop <a href="/collections/bundles">curated stacks</a>.';
}

function sendChat(input) {
  const field = input || $("#chatInput");
  const body = $("#chatBody");
  if (!field || !body) return;
  const msg = field.value.trim();
  if (!msg) return;
  field.value = "";
  body.querySelector(".chat-suggestions")?.remove();
  body.insertAdjacentHTML("beforeend", `<div class="chat-msg chat-msg--me"><p>${escapeHTML(msg)}</p></div>`);
  body.insertAdjacentHTML("beforeend", '<div class="chat-typing" id="chatTyping"><span></span><span></span><span></span></div>');
  body.scrollTop = body.scrollHeight;
  window.setTimeout(() => {
    $("#chatTyping")?.remove();
    body.insertAdjacentHTML("beforeend", `<div class="chat-msg chat-msg--them"><p>${consultationReply(msg)}</p><span class="chat-time">Vivid Health</span></div>`);
    body.scrollTop = body.scrollHeight;
  }, 650);
}

function initFloatingChat() {
  $("#chatBtn")?.addEventListener("click", openChat);
  $("#chatCloseBtn")?.addEventListener("click", closeChat);
  $("#chatSendBtn")?.addEventListener("click", () => sendChat($("#chatInput")));
  $("#chatInput")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChat(e.currentTarget);
  });
  $$(".chat-suggestions button").forEach((button) => {
    button.addEventListener("click", () => {
      const input = $("#chatInput");
      if (!input) return;
      input.value = button.dataset.chatPrompt || button.textContent || "";
      sendChat(input);
    });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && $("#chatWidget")?.classList.contains("open")) closeChat();
  });
}

/* ─── Premium quiz page ─── */

function initPremiumQuiz() {
  const root = $("[data-vivid-quiz]");
  if (!root) return;
  const title = $("[data-quiz-result-title]", root);
  const desc = $("[data-quiz-result-desc]", root);
  const link = $("[data-quiz-result-link]", root);
  root.addEventListener("click", (e) => {
    const choice = e.target.closest("[data-quiz-choice]");
    if (!choice) return;
    const group = choice.dataset.quizChoice;
    $$(`[data-quiz-choice="${group}"]`, root).forEach((item) => item.classList.remove("selected"));
    choice.classList.add("selected");
    if (!choice.dataset.title || !choice.dataset.url) return;
    if (title) title.textContent = choice.dataset.title;
    if (desc) desc.textContent = choice.dataset.desc || "";
    if (link) {
      link.href = choice.dataset.url;
      link.textContent = choice.dataset.url.includes("/bundles") ? "Shop curated stacks" : "Shop this range";
    }
  });
}

/* ─── Boot ─── */

document.addEventListener("DOMContentLoaded", async () => {
  initReveal();
  initFloatingChat();
  initPremiumQuiz();

  /* Cart open */
  $("#cartBtn")?.addEventListener("click", openCart);

  /* PDP: add-to-cart from .js-add-to-cart, quantity stepper, tab switching, thumb switching */
  $$(".js-add-to-cart").forEach((b) =>
    b.addEventListener("click", async (e) => {
      e.preventDefault();
      const id = b.dataset.variantId;
      const qty = parseInt($("#qty")?.value || 1, 10);
      await cartAdd(id, qty);
      await openCart();
    })
  );

  $$(".js-qty-step").forEach((b) =>
    b.addEventListener("click", () => {
      const i = $("#qty");
      if (!i) return;
      i.value = Math.max(1, (parseInt(i.value, 10) || 1) + parseInt(b.dataset.step, 10));
    })
  );

  $$(".js-tab").forEach((b) =>
    b.addEventListener("click", () => {
      $$(".js-tab").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      $$(".tab-body").forEach((x) =>
        x.classList.toggle("active", x.dataset.tab === b.dataset.tab)
      );
    })
  );

  $$(".js-thumb").forEach((t) =>
    t.addEventListener("click", () => {
      $$(".js-thumb").forEach((x) => x.classList.remove("active"));
      t.classList.add("active");
      const main = $("#pdpMainImg");
      if (main) main.src = t.dataset.src;
    })
  );

  /* Sticky add-on for the sticky ATC button (CTA variant doesn't need this) */
  document.body.addEventListener("click", async (e) => {
    const btn = e.target.closest('[data-action="sticky-add"]');
    if (!btn) return;
    e.preventDefault();
    await cartAdd(btn.dataset.variantId, 1);
    await openCart();
  });

  /* Initial cart pip */
  const cart = await cartFetch();
  setPip(cart.item_count);

  /* Page-level sticky CTA wiring.
     Each template can declare data-sticky-cta on <body> to opt-in. */
  const body = document.body;
  if (body.dataset.stickyCta === "home") {
    initStickyCTA(".hero-cta", [
      { href: "/collections/all-formulations", label: "Shop the range",    cls: "btn--forest btn-arrow" },
      { href: "/pages/quiz",       label: "Find my formulation", cls: "btn--ghost" },
    ]);
  }
});

/* Expose helpers for inline handlers and PDP template. */
window.cartFetch = cartFetch;
window.cartAdd = cartAdd;
window.cartChange = cartChange;
window.renderCart = renderCart;
window.openCart = openCart;
window.closeCart = closeCart;
window.openChat = openChat;
window.closeChat = closeChat;
window.sendChat = sendChat;
window.initStickyProduct = initStickyProduct;
window.initStickyCTA = initStickyCTA;
