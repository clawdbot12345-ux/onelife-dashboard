const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));

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
async function cartChange(id, qty) {
  const r = await fetch("/cart/change.js", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ id, quantity: qty }),
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
  await renderCart();
}
function closeCart() {
  $("#scrim")?.classList.remove("open");
  $("#drawer")?.classList.remove("open");
}

async function renderCart() {
  const cart = await cartFetch();
  setPip(cart.item_count);
  const body = $("#drawerBody");
  const foot = $("#drawerFoot");
  if (!body) return;
  if (cart.item_count === 0) {
    body.innerHTML =
      '<div class="cart-empty"><p>Your basket is empty.</p><a href="/collections/all" class="btn btn--ghost" style="margin-top:18px" onclick="closeCart()">Browse the range</a></div>';
    foot.innerHTML = "";
    return;
  }
  body.innerHTML = cart.items
    .map(
      (i) => `
    <div class="cart-item">
      <div class="cart-item-img"><img src="${i.image}" alt=""></div>
      <div>
        <div class="cart-item-name">${i.product_title}</div>
        <div class="cart-item-meta">${i.variant_title || ""}</div>
        <div style="display:flex;gap:8px;margin-top:8px">
          <div class="qty" style="height:30px">
            <button onclick="cartChange(${i.key !== undefined ? `'${i.key}'` : i.id}, ${i.quantity - 1}).then(renderCart)">−</button>
            <input value="${i.quantity}" readonly>
            <button onclick="cartChange(${i.key !== undefined ? `'${i.key}'` : i.id}, ${i.quantity + 1}).then(renderCart)">+</button>
          </div>
        </div>
      </div>
      <div class="cart-item-price">${formatR(i.final_line_price)}</div>
    </div>`
    )
    .join("");
  const ship = cart.total_price >= 60000 ? 0 : 7900;
  foot.innerHTML = `
    <div class="cart-totals"><span>Subtotal</span><span>${formatR(cart.total_price)}</span></div>
    <div class="cart-totals"><span>Shipping</span><span>${ship === 0 ? "Free over R600" : formatR(ship)}</span></div>
    <div class="cart-totals total"><span>Total</span><span>${formatR(cart.total_price + ship)}</span></div>
    <a class="btn btn--forest btn--block" href="/checkout">Checkout — ${formatR(cart.total_price + ship)}</a>
  `;
}

document.addEventListener("DOMContentLoaded", async () => {
  $("#cartBtn")?.addEventListener("click", openCart);
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
      i.value = Math.max(1, (parseInt(i.value, 10) || 1) + parseInt(b.dataset.step, 10));
    })
  );
  $$(".js-tab").forEach((b) =>
    b.addEventListener("click", () => {
      $$(".js-tab").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      $$(".tab-body").forEach((x) => x.classList.toggle("active", x.dataset.tab === b.dataset.tab));
    })
  );
  $$(".js-thumb").forEach((t) =>
    t.addEventListener("click", () => {
      $$(".js-thumb").forEach((x) => x.classList.remove("active"));
      t.classList.add("active");
      $("#pdpMainImg").src = t.dataset.src;
    })
  );
  const cart = await cartFetch();
  setPip(cart.item_count);
});
