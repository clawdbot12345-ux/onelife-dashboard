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

async function cartAdd(id, qty = 1, sellingPlan = null) {
  const item = { id, quantity: qty };
  if (sellingPlan) item.selling_plan = sellingPlan;
  const r = await fetch("/cart/add.js", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ items: [item] }),
  });
  return r.json();
}

/* Resolve the selected selling plan for a PDP add button (subscribe toggle). */
function selectedSellingPlan(btn) {
  if (!btn || !btn.closest || !btn.closest(".pdp-buybox")) return null;
  const toggle = document.querySelector("[data-sub-toggle]");
  if (!toggle) return null;
  const active = toggle.querySelector(".sub-opt.active");
  if (!active || active.dataset.purchase !== "subscribe") return null;
  const freq = document.querySelector("[data-sub-freq-select]");
  return (freq && freq.value) || active.dataset.sellingPlan || null;
}

window.vividCartAdd = async (id) => { await cartAdd(id, 1); await renderCart(); };

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
      <div class="cart-item-img">${i.image ? `<img src="${i.image}${i.image.includes("?") ? "&" : "?"}width=180&height=180&crop=center" alt="" loading="lazy" style="width:100%;height:100%;object-fit:cover;border-radius:8px">` : ""}</div>
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
  body.innerHTML += '<div id="cartUpsell" class="cart-upsell"></div>';
  renderCartUpsell(cart);
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
  const detailLink = $("[data-quiz-stack-link]", root);
  const summary = $("[data-quiz-summary]", root);
  const primary = $("[data-quiz-primary]", root);
  const reasons = $("[data-quiz-reasons]", root);
  const plan = $("[data-quiz-plan]", root);
  const products = $("[data-quiz-products]", root);
  const whatsapp = $(".quiz-whatsapp", root);

  const labels = {
    goal: {
      gut: "Gut health",
      immunity: "Immunity",
      stress: "Sleep & stress",
      joints: "Joints & mobility",
      daily: "Daily nutrients",
      energy: "Energy",
      women: "Women's health",
      men: "Men's health",
    },
    signal: {
      cleanse: "Reset or cleanse",
      lining: "Daily gut repair",
      seasonal: "Seasonal flare-ups",
      "daily-immune": "Daily defence",
      sleep: "Restless nights",
      mood: "Mood and stress load",
      bone: "Bone structure",
      mobility: "Joint comfort",
      cellular: "Cellular energy",
      foundation: "Daily foundation",
      cycle: "Cycle or hormones",
      prostate: "Prostate support",
    },
    style: {
      single: "One clear bottle",
      pair: "Two-product route",
      stack: "Complete stack",
    },
    format: {
      capsule: "Capsules",
      powder: "Powders",
      open: "No preference",
    },
  };

  const catalog = [
    { type: "product", name: "Colon Flush", range: "Gut Health", goals: ["gut"], signals: ["cleanse"], format: "capsule", url: "/products/vivid-health-gut-health-colon-flush-120-capsules", price: "R196.07", form: "120 capsules", why: "Capsule cleanse support when the goal is a defined gut reset.", timing: "Use as a short, structured reset route.", intensity: "active" },
    { type: "product", name: "Colon Flush Powder", range: "Gut Health", goals: ["gut"], signals: ["cleanse"], format: "powder", url: "/products/vivid-health-gut-health-colon-flush-powder-135g", price: "R143.00", form: "135g", why: "Powder format gives more flexible cleanse dosing.", timing: "Best when you prefer water-mix routines.", intensity: "active" },
    { type: "product", name: "L-Glutamine", range: "Gut Health", goals: ["gut"], signals: ["lining"], format: "powder", url: "/products/vivid-health-physical-health-l-glutamine-500g", price: "R345.00", form: "500g powder", why: "A cleaner first step for gut lining and recovery routines.", timing: "Use daily before adding cleanse botanicals.", intensity: "gentle" },
    { type: "product", name: "Wormwood", range: "Gut Health", goals: ["gut"], signals: ["cleanse"], format: "capsule", url: "/products/vivid-health-gut-health-immune-wormwood-60-capsules", price: "R133.00", form: "60 capsules", why: "Botanical gut support for a more targeted cleanse route.", timing: "Use after the anchor product if the reset needs support.", intensity: "active" },
    { type: "product", name: "Black Walnut", range: "Gut Health", goals: ["gut"], signals: ["cleanse"], format: "capsule", url: "/products/vivid-health-gut-health-black-walnut-60-capsules", price: "R140.41", form: "60 capsules", why: "A targeted add-on for cleanse-led gut routines.", timing: "Add only when the routine is already clear.", intensity: "active" },

    { type: "product", name: "Allergy Control", range: "Immune Health", goals: ["immunity"], signals: ["seasonal"], format: "capsule", url: "/products/vivid-health-immune-allergy-control-60-capsules", price: "R199.00", form: "60 capsules", why: "The cleanest anchor when the real issue is seasonal allergy or histamine support.", timing: "Use as the first seasonal-support product.", intensity: "gentle" },
    { type: "product", name: "Quercetin Complex", range: "Immune Health", goals: ["immunity"], signals: ["seasonal"], format: "capsule", url: "/products/vivid-health-immune-quercetin-complex-60-capsules", price: "R285.20", form: "60 capsules", why: "A logical second product for flavonoid-based seasonal support.", timing: "Add if Allergy Control alone is not enough.", intensity: "support" },
    { type: "product", name: "Buffered C", range: "Immune Health", goals: ["immunity", "daily"], signals: ["daily-immune", "foundation", "seasonal"], format: "capsule", url: "/products/vivid-health-immune-buffered-c-90-capsules", price: "R189.76", form: "90 capsules", why: "A simple daily immune foundation without a complicated routine.", timing: "Use daily as a low-friction base.", intensity: "gentle" },
    { type: "product", name: "Buffered C Powder", range: "Immune Health", goals: ["immunity", "daily"], signals: ["daily-immune", "foundation"], format: "powder", url: "/products/vivid-health-immune-buffered-c-150g", price: "R105.34", form: "150g", why: "Powder-friendly immune support for customers who dislike capsules.", timing: "Mix into water when a capsule routine will not stick.", intensity: "gentle" },
    { type: "product", name: "Immune Plus", range: "Immune Health", goals: ["immunity"], signals: ["daily-immune"], format: "capsule", url: "/products/vivid-health-immune-immune-plus-60-capsules", price: "R125.00", form: "60 capsules", why: "A concise immune-complex option when the goal is daily defence.", timing: "Use as a simple immune starting point.", intensity: "support" },
    { type: "product", name: "Mullein", range: "Immune Health", goals: ["immunity"], signals: ["seasonal", "daily-immune"], format: "capsule", url: "/products/vivid-health-immune-mullein-60-capsules", price: "R133.00", form: "60 capsules", why: "Better fit when seasonal support leans respiratory.", timing: "Use as a targeted add-on, not a random extra.", intensity: "support" },

    { type: "product", name: "Griffonia (5-HTP)", range: "Stress, Sleep & Mood", goals: ["stress"], signals: ["sleep", "mood"], format: "capsule", url: "/products/vivid-health-stay-vivid-griffonia-5-htp-60-capsules", price: "R275.00", form: "60 capsules", why: "The anchor product when sleep, mood, and evening calm are connected.", timing: "Start in the evening routine before adding daytime support.", intensity: "support" },
    { type: "product", name: "Tranquil", range: "Stress, Sleep & Mood", goals: ["stress"], signals: ["sleep"], format: "capsule", url: "/products/vivid-health-stay-vivid-tranquil-60-capsules", price: "R130.00", form: "60 capsules", why: "Best fit when the main gap is wind-down and sleep rhythm.", timing: "Use as the evening calm product.", intensity: "support" },
    { type: "product", name: "GABA Powder", range: "Stress, Sleep & Mood", goals: ["stress"], signals: ["sleep", "mood"], format: "powder", url: "/products/vivid-health-stay-vivid-gaba-150g", price: "R258.00", form: "150g", why: "Powder format for customers who want flexible evening support.", timing: "Use as a controlled wind-down add-on.", intensity: "active" },
    { type: "product", name: "Liquorice Root", range: "Stress, Sleep & Mood", goals: ["stress", "gut"], signals: ["mood", "lining"], format: "capsule", url: "/products/vivid-health-stay-vivid-liquorice-root-60-capsules", price: "R132.99", form: "60 capsules", why: "A better fit when stress support overlaps with gut comfort.", timing: "Use as a targeted bridge product.", intensity: "support" },

    { type: "product", name: "Bone Supreme", range: "Joints & Mobility", goals: ["joints", "daily"], signals: ["bone"], format: "capsule", url: "/products/vivid-health-vivid-body-bone-supreme-120-capsules", price: "R437.00", form: "120 capsules", why: "The structural anchor when bone matrix and long-term mineral support are the priority.", timing: "Use as the foundation before adding mobility support.", intensity: "gentle" },
    { type: "product", name: "Flexijoint Advanced", range: "Joints & Mobility", goals: ["joints"], signals: ["mobility"], format: "capsule", url: "/products/vivid-health-vivid-body-flexijoint-advanced-120-capsules", price: "R322.00", form: "120 capsules", why: "The better match when the customer is focused on joint movement and comfort.", timing: "Use when mobility is the daily gap.", intensity: "support" },
    { type: "product", name: "MSM", range: "Joints & Mobility", goals: ["joints"], signals: ["mobility"], format: "capsule", url: "/products/vivid-health-vivid-body-msm-90-capsules", price: "R170.78", form: "90 capsules", why: "A clean connective-tissue add-on for joint and skin routines.", timing: "Add after the anchor product if movement support needs depth.", intensity: "support" },
    { type: "product", name: "MSM Powder", range: "Joints & Mobility", goals: ["joints"], signals: ["mobility"], format: "powder", url: "/products/vivid-health-vivid-body-msm-150g", price: "R136.85", form: "150g", why: "Powder option for people who prefer flexible joint-support dosing.", timing: "Use when capsules are not the preferred format.", intensity: "support" },
    { type: "product", name: "Joint Relief", range: "Joints & Mobility", goals: ["joints"], signals: ["mobility"], format: "capsule", url: "/products/vivid-health-vivid-body-joint-relief-60-capsules", price: "R138.00", form: "60 capsules", why: "A simple joint-comfort product when the goal is daily movement ease.", timing: "Use as the conservative mobility start.", intensity: "gentle" },

    { type: "product", name: "D-Ribose", range: "Energy & Vitality", goals: ["energy"], signals: ["cellular"], format: "powder", url: "/products/vivid-health-stay-vivid-d-ribose-150g", price: "R307.39", form: "150g powder", why: "The strongest fit when the brief is cellular fuel rather than stimulants.", timing: "Use around the routine where energy demand is highest.", intensity: "support" },
    { type: "product", name: "Coenzyme Q10", range: "Energy & Vitality", goals: ["energy", "daily"], signals: ["cellular", "foundation"], format: "capsule", url: "/products/vivid-health-vivid-body-coenzyme-q10-60-capsules", price: "R340.40", form: "60 capsules", why: "Capsule-based mitochondrial and heart-support route.", timing: "Use daily when capsule convenience matters.", intensity: "gentle" },
    { type: "product", name: "Moringa", range: "Daily Nutrients", goals: ["daily", "energy"], signals: ["foundation", "cellular"], format: "capsule", url: "/products/vivid-health-vivid-nourishment-moringa-powder-300-capsules", price: "R298.08", form: "300 capsules", why: "A broader daily-nutrition product when energy may be nutrient-linked.", timing: "Use as an everyday shelf product.", intensity: "gentle" },

    { type: "product", name: "Omega Oil", range: "Daily Nutrients", goals: ["daily", "joints"], signals: ["foundation", "mobility"], format: "capsule", url: "/products/vivid-health-physical-health-omega-oil-90-capsules", price: "R237.18", form: "90 capsules", why: "A clean daily foundation before more specialised support.", timing: "Use daily as a low-friction nutritional base.", intensity: "gentle" },
    { type: "product", name: "Barley Grass Powder", range: "Daily Nutrients", goals: ["daily"], signals: ["foundation"], format: "powder", url: "/products/vivid-health-nutritent-health-barley-grass-200g", price: "R224.25", form: "200g", why: "Greens support in a flexible powder format.", timing: "Use in a smoothie or water routine.", intensity: "gentle" },
    { type: "product", name: "Barley Grass", range: "Daily Nutrients", goals: ["daily"], signals: ["foundation"], format: "capsule", url: "/products/vivid-health-nutritent-health-barley-grass-300-capsules", price: "R283.02", form: "300 capsules", why: "Greens support without needing a powder routine.", timing: "Use daily when capsule consistency matters.", intensity: "gentle" },
    { type: "product", name: "Turmeric Plus", range: "Daily Nutrients", goals: ["daily", "joints"], signals: ["foundation", "mobility"], format: "capsule", url: "/products/vivid-health-nutrient-health-turmeric-plus-60-capsules", price: "R257.60", form: "60 capsules", why: "Daily botanical support when the foundation also needs joint relevance.", timing: "Use as a simple botanical base.", intensity: "support" },

    { type: "product", name: "Angus Castus", range: "Women's Health", goals: ["women"], signals: ["cycle"], format: "capsule", url: "/products/vivid-health-woman-angus-castus-60-capsules", price: "R180.00", form: "60 capsules", why: "Best match when cycle rhythm or PMS is the main question.", timing: "Use as the first women's health anchor.", intensity: "support" },
    { type: "product", name: "Sage", range: "Women's Health", goals: ["women"], signals: ["cycle"], format: "capsule", url: "/products/vivid-health-woman-sage-60-capsules", price: "R120.61", form: "60 capsules", why: "A better fit when the life-stage concern is hot flush or menopause support.", timing: "Use as a targeted life-stage product.", intensity: "support" },
    { type: "product", name: "Maca", range: "Women's Health", goals: ["women", "energy"], signals: ["cycle", "cellular"], format: "capsule", url: "/products/vivid-health-woman-maca-60-capsules", price: "R179.86", form: "60 capsules", why: "A broader endocrine-adaptogen route when hormones overlap with vitality.", timing: "Use when balance and energy are both relevant.", intensity: "support" },
    { type: "product", name: "Prosta Care", range: "Men's Health", goals: ["men"], signals: ["prostate"], format: "capsule", url: "/products/vivid-health-men-prosta-care-60-capsules", price: "R263.93", form: "60 capsules", why: "The direct men's health match for prostate and daily vitality support.", timing: "Use as the men's health anchor product.", intensity: "support" },

    { type: "stack", name: "Vivid Allergy Stack", range: "Immune Health", goals: ["immunity"], signals: ["seasonal"], format: "capsule", url: "/products/vivid-allergy-stack-complete-allergy-support-bundle", price: "R594.72", form: "3-product stack", why: "Allergy Control, Quercetin Complex, and Buffered C in one seasonal route.", timing: "Choose this when allergies keep returning and one bottle is not enough.", intensity: "stack" },
    { type: "stack", name: "Vivid Bone & Joint Pack", range: "Joints & Mobility", goals: ["joints"], signals: ["bone", "mobility"], format: "capsule", url: "/products/vivid-bone-joint-pack-complete-skeletal-support-bundle", price: "R742.66", form: "3-product stack", why: "Bone Supreme, MSM, and Flexijoint paired for structure and movement.", timing: "Choose this when bone, connective tissue, and mobility all matter.", intensity: "stack" },
    { type: "stack", name: "Vivid Rest & Focus Stack", range: "Stress, Sleep & Mood", goals: ["stress"], signals: ["sleep", "mood"], format: "capsule", url: "/products/vivid-rest-focus-stack-sleep-calm-and-mental-clarity-bundle", price: "R587.67", form: "3-product stack", why: "Griffonia, Tranquil, and GABA arranged into a calmer evening system.", timing: "Choose this when sleep, stress, and next-day focus are connected.", intensity: "stack" },
  ];

  const selected = (group) => $(`[data-quiz-choice="${group}"].selected`, root);
  const signalChoices = $$("[data-quiz-choice='signal']", root);
  const productCache = new Map();
  const imageMapEl = document.querySelector("[data-quiz-image-map]");
  const imageMap = (() => {
    try {
      return imageMapEl ? JSON.parse(imageMapEl.textContent || "{}") : {};
    } catch (_error) {
      return {};
    }
  })();
  const variantMap = {
    "vivid-health-gut-health-colon-flush-powder-135g": 44794457292886,
    "vivid-health-physical-health-l-glutamine-500g": 44794457456726,
    "vivid-health-gut-health-immune-wormwood-60-capsules": 44794455425110,
    "vivid-health-gut-health-black-walnut-60-capsules": 44794455392342,
    "vivid-health-immune-allergy-control-60-capsules": 44794457260118,
    "vivid-health-immune-quercetin-complex-60-capsules": 44794458308694,
    "vivid-health-immune-buffered-c-90-capsules": 44794457915478,
    "vivid-health-immune-buffered-c-150g": 44794457981014,
    "vivid-health-immune-immune-plus-60-capsules": 44794458472534,
    "vivid-health-immune-mullein-60-capsules": 44794455162966,
    "vivid-health-stay-vivid-griffonia-5-htp-60-capsules": 44794458505302,
    "vivid-health-stay-vivid-tranquil-60-capsules": 44794457555030,
    "vivid-health-stay-vivid-gaba-150g": 44794458538070,
    "vivid-health-stay-vivid-liquorice-root-60-capsules": 44794457751638,
    "vivid-health-vivid-body-msm-90-capsules": 44794457653334,
    "vivid-health-vivid-body-msm-150g": 44794458406998,
    "vivid-health-vivid-body-joint-relief-60-capsules": 44794457784406,
    "vivid-health-stay-vivid-d-ribose-150g": 44794455556182,
    "vivid-health-vivid-body-coenzyme-q10-60-capsules": 44794459062358,
    "vivid-health-vivid-nourishment-moringa-powder-300-capsules": 44794458439766,
    "vivid-health-physical-health-omega-oil-90-capsules": 44794456309846,
    "vivid-health-nutrient-health-turmeric-plus-60-capsules": 44794458046550,
    "vivid-health-woman-angus-castus-60-capsules": 44794459258966,
    "vivid-health-woman-sage-60-capsules": 44794457620566,
    "vivid-allergy-stack-complete-allergy-support-bundle": 44794645610582,
    "vivid-bone-joint-pack-complete-skeletal-support-bundle": 44794645577814,
    "vivid-rest-focus-stack-sleep-calm-and-mental-clarity-bundle": 44794645545046,
  };
  let resultToken = 0;

  const currentSelections = () => ({
    goal: selected("goal")?.dataset.goalKey || "gut",
    signal: selected("signal")?.dataset.signalKey || "cleanse",
    style: selected("style")?.dataset.styleKey || "single",
    format: selected("format")?.dataset.formatKey || "capsule",
  });

  const syncSignalChoices = () => {
    const activeGoal = selected("goal")?.dataset.goalKey || "gut";
    const visibleSignals = signalChoices.filter((choice) => {
      const goals = (choice.dataset.signalGoals || "").split(" ");
      const visible = goals.includes(activeGoal);
      choice.hidden = !visible;
      return visible;
    });
    const currentSignal = selected("signal");
    if (!currentSignal || currentSignal.hidden) {
      signalChoices.forEach((choice) => choice.classList.remove("selected"));
      visibleSignals[0]?.classList.add("selected");
    }
  };

  const escapeHtml = (value) => String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

  const normaliseImage = (url) => {
    if (!url) return "";
    if (url.startsWith("//")) return `https:${url}`;
    return url;
  };

  const productHandle = (product) => product?.url?.split("/products/")[1]?.split("?")[0]?.replace(/\/$/, "") || "";

  const hydrateProduct = (product) => {
    if (!product?.url?.includes("/products/")) return Promise.resolve(product);
    if (productCache.has(product.url)) return productCache.get(product.url);
    const handle = productHandle(product);
    const mappedImage = imageMap[handle];
    const fallbackVariantId = variantMap[handle];
    const fallbackCartUrl = fallbackVariantId
      ? `/cart/add?id=${fallbackVariantId}&quantity=1&return_to=/cart`
      : product.url;
    const promise = fetch(`${product.url.replace(/\/$/, "")}.js`)
      .then((response) => response.ok ? response.json() : null)
      .then((data) => {
        const variants = data?.variants || [];
        const availableVariant = variants.find((variant) => variant.available) || variants[0];
        const variantId = availableVariant?.id || fallbackVariantId;
        const available = variants.length ? Boolean(availableVariant?.available) : Boolean(fallbackVariantId);
        return {
          ...product,
          shopifyTitle: data?.title || product.name,
          image: normaliseImage(mappedImage || data?.featured_image || data?.images?.[0] || product.image),
          variantId,
          available,
          cartUrl: available && variantId
            ? `/cart/add?id=${variantId}&quantity=1&return_to=/cart`
            : product.url,
        };
      })
      .catch(() => ({
        ...product,
        image: normaliseImage(mappedImage || product.image || ""),
        variantId: fallbackVariantId,
        available: Boolean(fallbackVariantId),
        cartUrl: fallbackCartUrl,
      }));
    productCache.set(product.url, promise);
    return promise;
  };

  const scoreProduct = (product, state) => {
    let score = 0;
    if (product.goals.includes(state.goal)) score += 12;
    if (product.signals.includes(state.signal)) score += 16;
    if (state.format === "open") score += 2;
    else if (product.format === state.format) score += 20;
    else score -= 18;
    if (state.style === "stack") score += product.type === "stack" ? 18 : 0;
    if (state.style === "pair") score += product.type === "product" ? 4 : 7;
    if (state.style === "single") score += product.type === "product" ? 8 : -12;
    if (product.type === "product") score += 1;
    return score;
  };

  const rankedCatalog = (state) => catalog
      .map((product) => ({ product, score: scoreProduct(product, state) }))
      .sort((a, b) => b.score - a.score)
      .map((item) => item.product);

  const directMatches = (items, state) => items.filter((product) => {
    if (!product.goals.includes(state.goal)) return false;
    if (state.format !== "open" && product.format !== state.format) return false;
    return true;
  });

  const preferredPrimary = (items, state) => {
    if (state.style === "stack" && state.format !== "powder") {
      const stack = items.find((product) => product.type === "stack");
      if (stack) return stack;
    }
    return items.find((product) => product.type === "product") || items[0];
  };

  const recommendationSet = async (state) => {
    const ranked = rankedCatalog(state);
    const hydrationPool = Array.from(new Set([
      ...directMatches(ranked, state),
      ...ranked.slice(0, 10),
    ]));
    const hydrated = await Promise.all(hydrationPool.map(hydrateProduct));
    const strict = directMatches(hydrated, state);
    const availableStrict = strict.filter((product) => product.available !== false);
    const availableHydrated = hydrated.filter((product) => product.available !== false);
    const candidatePool = availableStrict.length
      ? availableStrict
      : strict.length
        ? strict
        : availableHydrated.length
          ? availableHydrated
          : hydrated;
    const primaryProduct = preferredPrimary(candidatePool, state) || preferredPrimary(hydrated, state) || ranked[0];
    const supportMatches = (product) => {
      if (product.name === primaryProduct.name || product.type !== "product") return false;
      if (product.available === false) return false;
      if (product.goals.includes(state.goal)) return true;
      if (product.signals.includes(state.signal)) return true;
      return product.range === primaryProduct.range;
    };
    const supportSource = availableHydrated.length ? availableHydrated : hydrated;
    const support = supportSource
      .filter(supportMatches)
      .slice(0, state.style === "single" ? 2 : 3);
    return { primary: primaryProduct, support };
  };

  const renderSummary = (state) => {
    if (!summary) return;
    summary.innerHTML = "";
    [
      labels.goal[state.goal],
      labels.signal[state.signal],
      labels.style[state.style],
      labels.format[state.format],
    ].forEach((text) => {
      const pill = document.createElement("span");
      pill.textContent = text;
      summary.appendChild(pill);
    });
  };

  const renderPrimary = (product) => {
    if (!primary) return;
    primary.innerHTML = "";
    const card = document.createElement("a");
    card.className = "quiz-primary-card";
    card.href = product.available === false ? product.url : product.cartUrl;
    const image = product.image
      ? `<div class="quiz-primary-image"><img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}"></div>`
      : "";
    card.innerHTML = `
      ${image}
      <span>${product.type === "stack" ? "Recommended stack" : "Best first product"}</span>
      <strong>${product.name}</strong>
      <em>${product.range} · ${product.form}</em>
      <p>${product.why}</p>
      <b>${product.price}</b>
      <span class="quiz-card-cta">${product.available === false ? "View product" : "Add to cart"}</span>
      <small class="quiz-stock-note">${product.available === false ? "Currently unavailable - view product" : "Add directly to cart"}</small>
    `;
    primary.appendChild(card);
  };

  const renderReasons = (product, state) => {
    if (!reasons) return;
    reasons.innerHTML = "";
    const items = [
      `Matches your ${labels.goal[state.goal].toLowerCase()} goal.`,
      `Prioritises "${labels.signal[state.signal]}" instead of sending you to a generic collection.`,
      state.format === "open"
        ? "Format was left open, so the strongest product fit wins."
        : `Favours ${labels.format[state.format].toLowerCase()} where the range has a strong option.`,
      product.type === "stack"
        ? "You asked for a complete routine, so the stack is allowed to win."
        : "Starts with one anchor product before adding extras.",
    ];
    if (state.format !== "open" && product.format === state.format) {
      items.push(`Respects your ${labels.format[state.format].toLowerCase()} preference for the primary match.`);
    }
    items.forEach((text) => {
      const li = document.createElement("li");
      li.textContent = text;
      reasons.appendChild(li);
    });
  };

  const renderPlan = (product, support, state) => {
    if (!plan) return;
    plan.innerHTML = "";
    const steps = [];
    steps.push(`Start with ${product.name}. ${product.timing}`);
    if (state.style === "single") {
      steps.push("Keep it to one product for the first week so you know what is actually helping.");
    } else if (support[0]) {
      steps.push(`If the first product fits your day, add ${support[0].name} as the next logical support product.`);
    }
    if (state.style === "stack" && product.type === "stack") {
      steps.push("Use the stack only if you want the full routine from day one; otherwise start with the anchor product.");
    } else if (support[1]) {
      steps.push(`Keep ${support[1].name} as an optional later add-on, not an automatic purchase.`);
    }
    steps.forEach((text) => {
      const li = document.createElement("li");
      li.textContent = text;
      plan.appendChild(li);
    });
  };

  const renderProducts = (items) => {
    if (!products) return;
    const section = products.closest(".quiz-result-section");
    if (section) section.hidden = !(items || []).length;
    products.innerHTML = "";
    (items || []).forEach((product) => {
      const item = document.createElement("a");
      item.href = product.available === false ? product.url : product.cartUrl || product.url;
      item.className = "quiz-mini-product";
      const image = product.image
        ? `<img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}">`
        : "";
      item.innerHTML = `
        ${image}
        <em>${product.type === "stack" ? "Stack" : product.range}</em>
        <strong>${product.name}</strong>
        <small>${product.form} · ${product.price}</small>
      `;
      products.appendChild(item);
    });
  };

  const updateResult = async () => {
    const token = ++resultToken;
    const state = currentSelections();
    renderSummary(state);
    if (title) title.textContent = "Building your match...";
    if (desc) desc.textContent = "Checking product format and current availability so the result can move straight to cart.";
    if (primary) {
      primary.innerHTML = `<div class="quiz-primary-card quiz-primary-card--loading"><span>Matching</span><strong>Checking availability</strong><p>We are finding the cleanest available product for your answers.</p></div>`;
    }
    const recs = await recommendationSet(state);
    if (token !== resultToken) return;
    const resultTitle = `${recs.primary.name} is your cleanest start`;
    const consultUrl = `https://wa.me/27713744910?text=${encodeURIComponent(`Hi, I took the Vivid quiz. My result is ${recs.primary.name}. Can you help me confirm this is the right fit?`)}`;
    const resultUrl = recs.primary.available === false ? recs.primary.url : recs.primary.cartUrl;
    if (title) title.textContent = resultTitle;
    if (desc) {
      desc.textContent = `${recs.primary.why} ${state.format !== "open" && recs.primary.format === state.format ? `You asked for ${labels.format[state.format].toLowerCase()}, so the primary result stays in that format.` : "The quiz is keeping the first step focused so the recommendation is useful, not overwhelming."}`;
    }
    renderPrimary(recs.primary);
    renderReasons(recs.primary, state);
    renderPlan(recs.primary, recs.support, state);
    renderProducts(recs.support);
    if (link) {
      link.href = resultUrl;
      link.textContent = recs.primary.available === false ? `View ${recs.primary.name}` : `Add ${recs.primary.name} to cart`;
      link.removeAttribute("target");
      link.removeAttribute("rel");
    }
    if (detailLink) {
      detailLink.hidden = false;
      detailLink.href = recs.primary.url;
      detailLink.textContent = "View product details";
    }
    if (whatsapp) {
      whatsapp.href = consultUrl;
      whatsapp.textContent = "Ask a consultant before you combine products";
    }
  };

  root.addEventListener("click", (e) => {
    const choice = e.target.closest("[data-quiz-choice]");
    if (!choice) return;
    const group = choice.dataset.quizChoice;
    $$(`[data-quiz-choice="${group}"]`, root).forEach((item) => item.classList.remove("selected"));
    choice.classList.add("selected");
    if (group === "goal") syncSignalChoices();
    updateResult();
  });

  syncSignalChoices();
  updateResult();
}

/* ─── In-page commerce filters ─── */

function initHomeProductFilter() {
  const root = $("[data-home-product-filter]");
  if (!root) return;
  const heading = $("[data-home-products-heading]", root);
  const groups = $$("[data-home-group]", root);
  const buttons = $$("[data-home-filter]", root);

  const activate = (filter) => {
    const fallbackFilter = groups[0]?.dataset.homeGroup || buttons[0]?.dataset.homeFilter || "gut";
    const groupFilter = groups.some((group) => group.dataset.homeGroup === filter) ? filter : fallbackFilter;
    const selected = buttons.find((button) => button.dataset.homeFilter === groupFilter) || buttons[0];
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button === selected);
      button.setAttribute("aria-pressed", button === selected ? "true" : "false");
    });
    groups.forEach((group) => {
      const active = group.dataset.homeGroup === groupFilter;
      group.hidden = !active;
      group.classList.toggle("is-active", active);
    });
    if (heading && selected?.dataset.heading) heading.textContent = selected.dataset.heading;
  };

  buttons.forEach((button) => {
    button.setAttribute("aria-pressed", button.classList.contains("is-active") ? "true" : "false");
    button.addEventListener("click", () => activate(button.dataset.homeFilter || "start"));
  });
}

function initCollectionFilters() {
  const root = $("[data-collection-filter]");
  const grid = $(".products-row--shop");
  if (!root || !grid) return;
  const cards = $$(".card", grid);
  const chips = $$("[data-filter-goal]", root);
  const count = $("[data-filter-count]");
  const sort = $("[data-filter-sort]", root);
  const initial = root.dataset.activeFilter || "all";
  const collectionHead = $(".collection-head");
  const collectionCrumb = $(".collection-head .crumb");
  const collectionTitle = $(".collection-head h1");
  const collectionLead = $("[data-collection-lead]") || $(".collection-head p");
  const filterLabels = {
    all: "All formulations",
    bundles: "Curated stacks",
    gut: "Gut Health",
    immunity: "Immunity",
    stress: "Stress, Sleep & Mood",
    joints: "Joints & Mobility",
    energy: "Energy & Vitality",
    women: "Women's Health",
    men: "Men's Health",
    daily: "Daily Nutrients",
  };
  const filterLeads = {
    all: "Browse the complete Vivid Health range, then narrow by outcome without reloading the page.",
    bundles: "Pre-paired Vivid routines with a 10% stack offer.",
    gut: "Cleanse, digestive balance, lining support, and gut reset routines.",
    immunity: "Daily defence, allergy-season structure, and year-round immune support.",
    stress: "Calm, sleep, focus, and nervous-system support.",
    joints: "Bone, joint, connective-tissue, and mobility support.",
    energy: "Recovery, vitality, and daily fuel without stimulant theatre.",
    women: "Targeted support for women's daily rhythms.",
    men: "Targeted support for men's daily foundations.",
    daily: "The everyday wellness shelf: nutrients, greens, omegas, and foundations.",
  };

  const visibleCards = () => cards.filter((card) => !card.hidden);

  const applySort = () => {
    const value = sort?.value || "featured";
    const ordered = [...cards];
    if (value === "title-ascending") {
      ordered.sort((a, b) => (a.dataset.title || "").localeCompare(b.dataset.title || ""));
    } else if (value === "price-ascending") {
      ordered.sort((a, b) => Number(a.dataset.price || 0) - Number(b.dataset.price || 0));
    } else if (value === "price-descending") {
      ordered.sort((a, b) => Number(b.dataset.price || 0) - Number(a.dataset.price || 0));
    }
    ordered.forEach((card) => grid.appendChild(card));
  };

  const applyFilter = (filter) => {
    if (!filterLabels[filter]) filter = "all";
    let selectedChip = null;
    chips.forEach((chip) => {
      const active = chip.dataset.filterGoal === filter;
      chip.classList.toggle("is-active", active);
      chip.setAttribute("aria-pressed", active ? "true" : "false");
      if (active) selectedChip = chip;
    });
    cards.forEach((card) => {
      const goal = card.dataset.goal || "";
      const show = filter === "all" ? goal !== "bundles" : goal === filter;
      card.hidden = !show;
    });
    applySort();
    if (count) count.textContent = String(visibleCards().length);
    if (collectionTitle) collectionTitle.textContent = filterLabels[filter];
    if (collectionLead && filterLeads[filter]) collectionLead.textContent = filterLeads[filter];
    if (collectionCrumb) {
      const homeLink = collectionCrumb.querySelector("a")?.outerHTML || '<a href="/">Home</a>';
      collectionCrumb.innerHTML = `${homeLink} · ${filterLabels[filter]}`;
    }
    if (collectionHead && selectedChip?.dataset.filterBanner) {
      collectionHead.dataset.activeFilter = filter;
      collectionHead.style.setProperty("--banner", `url('${selectedChip.dataset.filterBanner}')`);
    }
  };

  chips.forEach((chip) => {
    chip.setAttribute("role", "button");
    chip.setAttribute("aria-pressed", chip.classList.contains("is-active") ? "true" : "false");
    chip.addEventListener("click", (e) => {
      e.preventDefault();
      applyFilter(chip.dataset.filterGoal || "all");
    });
  });
  sort?.addEventListener("change", applySort);
  applyFilter(window.location.hash?.replace("#", "") || initial);
}

/* ─── Boot ─── */

document.addEventListener("DOMContentLoaded", async () => {
  initReveal();
  initFloatingChat();
  initPremiumQuiz();
  initHomeProductFilter();
  initCollectionFilters();
  initSubToggle();
  initMobileNav();

  /* Cart open */
  $("#cartBtn")?.addEventListener("click", openCart);

  /* PDP: add-to-cart from .js-add-to-cart, quantity stepper, tab switching, thumb switching */
  $$(".js-add-to-cart").forEach((b) =>
    b.addEventListener("click", async (e) => {
      e.preventDefault();
      const id = b.dataset.variantId;
      const qty = parseInt($("#qty")?.value || 1, 10);
      const sp = selectedSellingPlan(b);
      await cartAdd(id, qty, sp);
      await openCart();
    })
  );

  /* PDP: variant pills — sync price, add-to-cart target, and buy-now link */
  $$(".opt[data-variant-id]").forEach((b) =>
    b.addEventListener("click", () => {
      $$(".opt[data-variant-id]").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      const price = b.dataset.price;
      const vid = b.dataset.variantId;
      const available = b.dataset.available !== "false";
      const priceEl = $(".pdp-price");
      if (priceEl && price) priceEl.textContent = price;
      const atc = $(".js-add-to-cart");
      if (atc) {
        atc.dataset.variantId = vid;
        atc.disabled = !available;
        atc.textContent = available ? `Add to basket — ${price}` : "Notify me when back";
      }
      const bn = $(".pdp-buy-now");
      if (bn && vid) bn.href = `/cart/${vid}:1?checkout`;
      try {
        const u = new URL(location.href);
        u.searchParams.set("variant", vid);
        history.replaceState(null, "", u);
      } catch (_) {}
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


/* ─── Subscribe & Save toggle (PDP) ─── */
function initSubToggle() {
  const toggle = document.querySelector("[data-sub-toggle]");
  if (!toggle) return;
  const freq = document.querySelector("[data-sub-freq]");
  const addBtn = document.querySelector(".pdp-buybox .js-add-to-cart");
  const oneTimeLabel = addBtn ? addBtn.textContent.trim() : "";
  toggle.querySelectorAll(".sub-opt").forEach((opt) => {
    opt.addEventListener("click", () => {
      toggle.querySelectorAll(".sub-opt").forEach((o) => o.classList.remove("active"));
      opt.classList.add("active");
      const subscribe = opt.dataset.purchase === "subscribe";
      if (freq) freq.hidden = !subscribe;
      if (addBtn) {
        if (subscribe) {
          const desc = opt.querySelector(".sub-desc");
          addBtn.textContent = desc ? "Subscribe — " + desc.textContent.replace(/\s*\/.*$/, "") + " / delivery" : "Subscribe & Save";
        } else {
          addBtn.textContent = oneTimeLabel;
        }
      }
    });
  });
}

/* ─── Cart cross-sell (bestsellers not already in cart) ─── */
let _bestsellerCache = null;
async function fetchBestsellers() {
  if (_bestsellerCache) return _bestsellerCache;
  try {
    const r = await fetch("/collections/bestsellers/products.json?limit=8", { headers: { Accept: "application/json" } });
    const j = await r.json();
    _bestsellerCache = j.products || [];
  } catch (e) { _bestsellerCache = []; }
  return _bestsellerCache;
}
async function renderCartUpsell(cart) {
  const el = document.getElementById("cartUpsell");
  if (!el) return;
  const inCart = new Set(cart.items.map((i) => i.product_id));
  const products = await fetchBestsellers();
  const picks = products.filter((p) => !inCart.has(p.id)).slice(0, 2);
  if (!picks.length) { el.innerHTML = ""; return; }
  el.innerHTML =
    '<div class="cart-upsell-head">Popular add-ons</div>' +
    picks.map((p) => {
      const v = (p.variants || [])[0] || {};
      const img = (p.images || [])[0]?.src || "";
      const price = formatR(Math.round(parseFloat(v.price || 0) * 100));
      const name = (p.title || "").split(" - ").pop();
      return '<div class="cart-upsell-item">' +
        (img ? '<img src="' + img + '&width=120" alt="" loading="lazy">' : '') +
        '<div class="cart-upsell-info"><div class="cart-upsell-name">' + name + '</div><div class="cart-upsell-price">' + price + '</div></div>' +
        '<button type="button" class="cart-upsell-add" onclick="vividCartAdd(' + v.id + ')" aria-label="Add ' + name + '">Add</button>' +
        '</div>';
    }).join("");
}

/* ─── Mobile nav drawer ─── */
function openMobNav() { document.getElementById("mobnavScrim")?.classList.add("open"); document.getElementById("mobnav")?.classList.add("open"); document.body.style.overflow = "hidden"; }
function closeMobNav() { document.getElementById("mobnavScrim")?.classList.remove("open"); document.getElementById("mobnav")?.classList.remove("open"); document.body.style.overflow = ""; }
function initMobileNav() {
  const burger = document.getElementById("navBurger");
  if (burger) burger.addEventListener("click", openMobNav);
  document.getElementById("mobnavScrim")?.addEventListener("click", closeMobNav);
  document.getElementById("mobnavClose")?.addEventListener("click", closeMobNav);
  document.querySelectorAll("#mobnav a").forEach((a) => a.addEventListener("click", closeMobNav));
}
window.closeMobNav = closeMobNav;
