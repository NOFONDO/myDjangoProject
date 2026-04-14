/* ================================================================
   AgriConnect — script.js  (Frontend ↔ Django REST API)
   All TODO blocks are now REAL fetch() calls.
   Drop this file into your frontend/ folder replacing the old one.
   ================================================================ */

'use strict';

/* ── API Config ─────────────────────────────────────────────────── */
const API = {
  BASE: 'http://127.0.0.1:8000/api',   // ← change to your server URL in production

  ENDPOINTS: {
    register:    '/auth/register/',
    login:       '/auth/login/',
    logout:      '/auth/logout/',
    me:          '/auth/me/',
    products:    '/products/',
    productMine: '/products/mine/',
    categories:  '/products/categories/',
    create:      '/products/create/',
    orders:      '/products/orders/',
    ordersMine:  '/products/orders/mine/',
  },

  url(path) { return this.BASE + path; },
};

/* ── Auth Helpers ───────────────────────────────────────────────── */
const Auth = {
  getToken:    ()  => localStorage.getItem('agri_token'),
  setToken:    (t) => localStorage.setItem('agri_token', t),
  getUser:     ()  => { try { return JSON.parse(localStorage.getItem('agri_user')); } catch { return null; } },
  setUser:     (u) => localStorage.setItem('agri_user', JSON.stringify(u)),
  clearAll:    ()  => { localStorage.removeItem('agri_token'); localStorage.removeItem('agri_user'); },
  isLoggedIn:  ()  => !!localStorage.getItem('agri_token'),
  authHeaders: ()  => ({
    'Authorization': `Token ${Auth.getToken()}`,
    'Content-Type':  'application/json',
  }),
};

/* ── Generic fetch wrapper ──────────────────────────────────────── */
async function apiFetch(path, options = {}) {
  /**
   * Central fetch function used by all API calls.
   * - Attaches auth token automatically if logged in
   * - Returns { ok, data } so callers don't need to parse JSON
   * - For FormData (file uploads), don't set Content-Type — browser sets it
   */
  const headers = options.headers || {};

  // Attach token if user is logged in
  if (Auth.isLoggedIn()) {
    headers['Authorization'] = `Token ${Auth.getToken()}`;
  }

  // For JSON bodies, set Content-Type (skip for FormData)
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(API.url(path), { ...options, headers });
    const data     = await response.json();
    return { ok: response.ok, status: response.status, data };
  } catch (err) {
    console.error('Network error:', err);
    return { ok: false, status: 0, data: { error: 'Network error. Check your connection.' } };
  }
}

/* ── Toast Notifications ─────────────────────────────────────────── */
function toast(msg, type = 'ok', ms = 3500) {
  document.querySelectorAll('.toast').forEach(t => t.remove());
  const el = document.createElement('div');
  el.className = `toast toast--${type}`;
  el.textContent = msg;
  document.body.appendChild(el);
  requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('show')));
  setTimeout(() => { el.classList.remove('show'); setTimeout(() => el.remove(), 400); }, ms);
}

/* ── Navbar: mobile toggle + active link ─────────────────────────── */
(function initNavbar() {
  const ham   = document.querySelector('.navbar__ham');
  const links = document.querySelector('.navbar__links');
  if (ham && links) {
    ham.addEventListener('click', () => links.classList.toggle('nav-open'));
    links.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => links.classList.remove('nav-open'));
    });
  }
  const page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.navbar__links a[href]').forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });
})();

/* ── Form Validation Helpers ─────────────────────────────────────── */
const V = {
  required: v => v.trim().length > 0,
  minLen:   (v, n) => v.trim().length >= n,
  phone:    v => /^[+\d][\d\s\-]{6,14}$/.test(v.trim()),
  password: v => v.length >= 8,
  positive: v => !isNaN(+v) && +v > 0,
};

function validateInput(input, rules) {
  const errEl = input.closest('.form-group')?.querySelector('.form-error');
  for (const rule of rules) {
    if (!rule.fn(input.value)) {
      input.classList.add('is-error');
      if (errEl) { errEl.textContent = rule.msg; errEl.classList.add('show'); }
      return false;
    }
  }
  input.classList.remove('is-error');
  if (errEl) errEl.classList.remove('show');
  return true;
}

function liveValidate(map) {
  Object.entries(map).forEach(([sel, rules]) => {
    const el = document.querySelector(sel);
    if (!el) return;
    el.addEventListener('blur',  () => validateInput(el, rules));
    el.addEventListener('input', () => { if (el.classList.contains('is-error')) validateInput(el, rules); });
  });
}

function setBtn(btn, loading, defaultText) {
  btn.disabled    = loading;
  btn.textContent = loading ? 'Please wait…' : defaultText;
}

/* ══════════════════════════════════════════════════════════════════
   REGISTER PAGE  →  POST /api/auth/register/
   ══════════════════════════════════════════════════════════════════ */
(function initRegister() {
  const form = document.getElementById('registerForm');
  if (!form) return;

  liveValidate({
    '#reg-name':     [{ fn: V.required,          msg: 'Name is required.' },
                      { fn: v => V.minLen(v, 2), msg: 'At least 2 characters.' }],
    '#reg-phone':    [{ fn: V.required, msg: 'Phone is required.' },
                      { fn: V.phone,   msg: 'Enter a valid phone number.' }],
    '#reg-password': [{ fn: V.required,  msg: 'Password is required.' },
                      { fn: V.password,  msg: 'Minimum 8 characters.' }],
    '#reg-location': [{ fn: V.required, msg: 'Location is required.' }],
    '#reg-role':     [{ fn: V.required, msg: 'Select a role.' }],
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const f = {
      name:     document.getElementById('reg-name'),
      phone:    document.getElementById('reg-phone'),
      password: document.getElementById('reg-password'),
      confirm:  document.getElementById('reg-password-confirm'),
      role:     document.getElementById('reg-role'),
      location: document.getElementById('reg-location'),
    };

    const valid = [
      validateInput(f.name,     [{ fn: V.required, msg: 'Name required.' }]),
      validateInput(f.phone,    [{ fn: V.required, msg: 'Phone required.' }, { fn: V.phone, msg: 'Invalid phone.' }]),
      validateInput(f.password, [{ fn: V.required, msg: 'Password required.' }, { fn: V.password, msg: 'Min 8 chars.' }]),
      validateInput(f.location, [{ fn: V.required, msg: 'Location required.' }]),
      validateInput(f.role,     [{ fn: V.required, msg: 'Select a role.' }]),
    ].every(Boolean);

    if (!valid) return;

    const btn = form.querySelector('[type="submit"]');
    setBtn(btn, true, 'Create Account →');

    const { ok, data } = await apiFetch(API.ENDPOINTS.register, {
      method: 'POST',
      body: JSON.stringify({
        name:             f.name.value.trim(),
        phone:            f.phone.value.trim(),
        password:         f.password.value,
        password_confirm: f.confirm?.value || f.password.value,
        role:             f.role.value,
        location:         f.location.value.trim(),
      }),
    });

    setBtn(btn, false, 'Create Account →');

    if (ok) {
      // Store token and user so they stay logged in
      Auth.setToken(data.data.token);
      Auth.setUser(data.data.user);
      toast(data.message || 'Account created!', 'ok');
      setTimeout(() => {
        window.location.href = data.data.user.role === 'farmer' ? 'dashboard.html' : 'products.html';
      }, 1500);
    } else {
      const errMsg = data.error || data.errors?.phone?.[0] || 'Registration failed.';
      toast(errMsg, 'err');
    }
  });
})();

/* ══════════════════════════════════════════════════════════════════
   LOGIN PAGE  →  POST /api/auth/login/
   ══════════════════════════════════════════════════════════════════ */
(function initLogin() {
  const form = document.getElementById('loginForm');
  if (!form) return;

  liveValidate({
    '#login-phone':    [{ fn: V.required, msg: 'Phone required.' }, { fn: V.phone, msg: 'Invalid phone.' }],
    '#login-password': [{ fn: V.required, msg: 'Password required.' }],
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const phone = document.getElementById('login-phone');
    const pass  = document.getElementById('login-password');

    const valid = [
      validateInput(phone, [{ fn: V.required, msg: 'Phone required.' }, { fn: V.phone, msg: 'Invalid phone.' }]),
      validateInput(pass,  [{ fn: V.required, msg: 'Password required.' }]),
    ].every(Boolean);

    if (!valid) return;

    const btn = form.querySelector('[type="submit"]');
    setBtn(btn, true, 'Login →');

    const { ok, data } = await apiFetch(API.ENDPOINTS.login, {
      method: 'POST',
      body: JSON.stringify({
        phone:    phone.value.trim(),
        password: pass.value,
      }),
    });

    setBtn(btn, false, 'Login →');

    if (ok) {
      Auth.setToken(data.data.token);
      Auth.setUser(data.data.user);
      toast(data.message || 'Welcome back!', 'ok');
      setTimeout(() => {
        window.location.href = data.data.user.role === 'farmer' ? 'dashboard.html' : 'products.html';
      }, 1200);
    } else {
      toast(data.error || 'Invalid phone or password.', 'err');
    }
  });
})();

/* ══════════════════════════════════════════════════════════════════
   PRODUCTS PAGE  →  GET /api/products/
   ══════════════════════════════════════════════════════════════════ */
(function initProducts() {
  const grid    = document.getElementById('productsGrid');
  const countEl = document.getElementById('resultsCount');
  if (!grid) return;

  async function load(search = '', category = '', page = 1) {
    grid.innerHTML = '<p style="color:var(--light-gray);padding:2rem;grid-column:1/-1">Loading…</p>';

    const params = new URLSearchParams({ page });
    if (search)   params.set('search', search);
    if (category) params.set('category', category);

    const { ok, data } = await apiFetch(
      API.ENDPOINTS.products + '?' + params.toString()
    );

    if (!ok) {
      grid.innerHTML = '<p style="color:#c03030;padding:2rem;grid-column:1/-1">Failed to load products.</p>';
      return;
    }

    const { results, total } = data.data;
    if (countEl) countEl.textContent = `${total} product${total !== 1 ? 's' : ''} found`;

    if (!results.length) {
      grid.innerHTML = '<p style="color:var(--light-gray);padding:2rem;grid-column:1/-1">No products match your search.</p>';
      return;
    }

    grid.innerHTML = results.map(p => cardHTML(p)).join('');
  }

  // Load categories into filter dropdown
  async function loadCategories() {
    const sel = document.getElementById('categoryFilter');
    if (!sel) return;
    const { ok, data } = await apiFetch(API.ENDPOINTS.categories);
    if (!ok) return;
    data.data.forEach(cat => {
      const opt = document.createElement('option');
      opt.value       = cat.slug;
      opt.textContent = cat.name;
      sel.appendChild(opt);
    });
  }

  const searchEl = document.getElementById('searchInput');
  const catEl    = document.getElementById('categoryFilter');
  let timer;
  searchEl?.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(() => load(searchEl.value, catEl?.value), 350);
  });
  catEl?.addEventListener('change', () => load(searchEl?.value, catEl.value));
  document.getElementById('searchBtn')?.addEventListener('click', () => load(searchEl?.value, catEl?.value));

  loadCategories();
  load();
})();

/* ── Shared card renderer ────────────────────────────────────────── */
function cardHTML(p) {
  const imageTag = p.image_url
    ? `<img src="${p.image_url}" alt="${p.name}" width="400" height="200"
             style="width:100%;height:200px;object-fit:cover;" loading="lazy" />`
    : `<div class="img-ph"><span class="ph-icon">🌾</span><span>No image</span></div>`;

  return `
    <article class="card fade-up">
      <div class="card__img">
        ${imageTag}
        ${p.status === 'sold_out' ? '<span class="card__badge" style="background:#c03030;">Sold Out</span>' : ''}
      </div>
      <div class="card__body">
        <h3 class="card__name">${p.name}</h3>
        <p class="card__price">XAF ${Number(p.price).toLocaleString()} <sub>/ ${p.unit}</sub></p>
        <p class="card__location">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
          </svg>
          ${p.location}
        </p>
        <p style="font-size:.8rem;color:var(--light-gray)">
          by ${p.farmer?.name || 'Farmer'} ${p.farmer?.is_verified ? '✅' : ''}
        </p>
      </div>
      <div class="card__footer">
        <a href="product-details.html?id=${p.id}" class="btn btn-primary btn-sm">View Details</a>
      </div>
    </article>`;
}

/* ══════════════════════════════════════════════════════════════════
   HOME PAGE — Featured products
   ══════════════════════════════════════════════════════════════════ */
(function initHome() {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;

  apiFetch(API.ENDPOINTS.products + '?page=1').then(({ ok, data }) => {
    if (!ok || !data.data?.results?.length) {
      grid.innerHTML = '<p style="color:var(--light-gray)">No products yet.</p>';
      return;
    }
    // Show first 4 products as featured
    grid.innerHTML = data.data.results.slice(0, 4).map(p => cardHTML(p)).join('');
  });
})();

/* ══════════════════════════════════════════════════════════════════
   PRODUCT DETAILS PAGE  →  GET /api/products/<id>/
   ══════════════════════════════════════════════════════════════════ */
(function initProductDetail() {
  if (!document.getElementById('detailSection')) return;

  const id = new URLSearchParams(window.location.search).get('id');
  if (!id) { window.location.href = 'products.html'; return; }

  apiFetch(`${API.ENDPOINTS.products}${id}/`).then(({ ok, data }) => {
    if (!ok) {
      toast('Product not found.', 'err');
      setTimeout(() => window.location.href = 'products.html', 1500);
      return;
    }
    const p = data.data;

    document.getElementById('detailName').textContent  = p.name;
    document.getElementById('detailPrice').textContent = `XAF ${Number(p.price).toLocaleString()} / ${p.unit}`;
    document.getElementById('detailDesc').textContent  = p.description || 'No description provided.';
    document.getElementById('detailCat').textContent   = p.category?.name || '—';
    document.getElementById('detailLoc').textContent   = p.location;
    document.getElementById('detailQty').textContent   = `${p.quantity} ${p.unit} available`;
    document.getElementById('farmerName').textContent  = p.farmer?.name || '—';
    document.getElementById('farmerLoc').textContent   = `📍 ${p.farmer?.location || '—'}`;
    document.title = `${p.name} | AgriConnect`;

    // Set image if available
    const imgWrap = document.querySelector('.detail-img-wrap');
    if (imgWrap && p.image_url) {
      imgWrap.innerHTML = `<img src="${p.image_url}" alt="${p.name}"
                                style="width:100%;height:100%;object-fit:cover;" />`;
    }
  });

  // Buy Now
  document.getElementById('buyBtn')?.addEventListener('click', async () => {
    if (!Auth.isLoggedIn()) {
      toast('Please log in to place an order.', 'err');
      setTimeout(() => window.location.href = 'login.html', 1500);
      return;
    }
    const user = Auth.getUser();
    if (user?.role === 'farmer') {
      toast('Farmers cannot place orders. Log in as a buyer.', 'err');
      return;
    }
    const { ok, data } = await apiFetch(API.ENDPOINTS.orders, {
      method: 'POST',
      body: JSON.stringify({ product: id, quantity: 1 }),
    });
    if (ok) {
      toast(data.message || 'Order placed!', 'ok');
    } else {
      toast(data.error || 'Order failed. Please try again.', 'err');
    }
  });

  document.getElementById('contactBtn')?.addEventListener('click', () => {
    if (!Auth.isLoggedIn()) {
      toast('Please log in to contact the farmer.', 'err');
      return;
    }
    toast('Place an order and the farmer will contact you.', 'ok');
  });
})();

/* ══════════════════════════════════════════════════════════════════
   UPLOAD PAGE  →  POST /api/products/create/
   ══════════════════════════════════════════════════════════════════ */
(function initUpload() {
  const form = document.getElementById('uploadForm');
  if (!form) return;

  // Redirect non-farmers away
  if (Auth.isLoggedIn() && Auth.getUser()?.role !== 'farmer') {
    toast('Only farmers can upload products.', 'err');
    setTimeout(() => window.location.href = 'products.html', 1500);
    return;
  }

  // Image drag-and-drop and preview
  const fileInput = document.getElementById('product-image');
  const preview   = document.getElementById('imgPreview');
  const zone      = document.querySelector('.file-zone');

  if (fileInput && preview && zone) {
    fileInput.addEventListener('change', showPreview);
    zone.addEventListener('dragover',  e => { e.preventDefault(); zone.classList.add('over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('over'));
    zone.addEventListener('drop', e => {
      e.preventDefault(); zone.classList.remove('over');
      if (e.dataTransfer.files[0]?.type.startsWith('image/')) {
        fileInput.files = e.dataTransfer.files;
        showPreview();
      }
    });
  }

  function showPreview() {
    const file = fileInput?.files[0];
    if (!file || !preview) return;
    const reader = new FileReader();
    reader.onload = e => { preview.src = e.target.result; preview.style.display = 'block'; };
    reader.readAsDataURL(file);
  }

  liveValidate({
    '#product-name':     [{ fn: V.required, msg: 'Product name required.' }],
    '#product-price':    [{ fn: V.required, msg: 'Price required.' }, { fn: V.positive, msg: 'Valid price.' }],
    '#product-quantity': [{ fn: V.required, msg: 'Quantity required.' }, { fn: V.positive, msg: 'Valid quantity.' }],
    '#product-location': [{ fn: V.required, msg: 'Location required.' }],
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!Auth.isLoggedIn()) {
      toast('Please log in first.', 'err');
      window.location.href = 'login.html';
      return;
    }

    const valid = [
      validateInput(document.getElementById('product-name'),     [{ fn: V.required, msg: 'Name required.' }]),
      validateInput(document.getElementById('product-price'),    [{ fn: V.required, msg: 'Price required.' }, { fn: V.positive, msg: 'Valid price.' }]),
      validateInput(document.getElementById('product-quantity'), [{ fn: V.required, msg: 'Qty required.' }, { fn: V.positive, msg: 'Valid qty.' }]),
      validateInput(document.getElementById('product-location'), [{ fn: V.required, msg: 'Location required.' }]),
    ].every(Boolean);

    if (!valid) return;

    // Use FormData — required for file uploads
    // DO NOT set Content-Type manually; browser sets multipart boundary automatically
    const fd = new FormData();
    fd.append('name',        document.getElementById('product-name').value.trim());
    fd.append('price',       document.getElementById('product-price').value);
    fd.append('quantity',    document.getElementById('product-quantity').value);
    fd.append('location',    document.getElementById('product-location').value.trim());
    fd.append('unit',        document.getElementById('product-unit')?.value || 'kg');
    fd.append('description', document.getElementById('product-desc')?.value.trim() || '');

    const catEl = document.getElementById('product-category');
    if (catEl?.value) fd.append('category_id', catEl.value);

    const harvestEl = document.getElementById('product-harvest');
    if (harvestEl?.value) fd.append('harvest_date', harvestEl.value);

    if (fileInput?.files[0]) fd.append('image', fileInput.files[0]);

    const btn = form.querySelector('[type="submit"]');
    setBtn(btn, true, '🌾 List My Product');

    // For FormData, skip Content-Type header (let browser set it)
    const headers = {};
    if (Auth.isLoggedIn()) headers['Authorization'] = `Token ${Auth.getToken()}`;

    try {
      const response = await fetch(API.url(API.ENDPOINTS.create), {
        method: 'POST',
        headers,
        body: fd,
      });
      const data = await response.json();

      if (response.ok) {
        toast('Product listed successfully!', 'ok');
        form.reset();
        if (preview) preview.style.display = 'none';
        setTimeout(() => window.location.href = 'dashboard.html', 1500);
      } else {
        const errMsg = data.error || Object.values(data.errors || {})[0]?.[0] || 'Upload failed.';
        toast(errMsg, 'err');
      }
    } catch {
      toast('Network error. Please try again.', 'err');
    } finally {
      setBtn(btn, false, '🌾 List My Product');
    }
  });
})();

/* ══════════════════════════════════════════════════════════════════
   DASHBOARD PAGE  →  requires auth token
   ══════════════════════════════════════════════════════════════════ */
(function initDashboard() {
  if (!document.getElementById('dashSection')) return;

  // Protect this page — redirect if not logged in
  if (!Auth.isLoggedIn()) {
    toast('Please log in to view your dashboard.', 'err');
    window.location.href = 'login.html';
    return;
  }

  // Show user info from stored data immediately (fast)
  const user = Auth.getUser();
  if (user) {
    document.getElementById('dashUserName')?.setAttribute('textContent', user.name);
    document.getElementById('dashUserName') && (document.getElementById('dashUserName').textContent = user.name);
    document.getElementById('dashUserNameSide') && (document.getElementById('dashUserNameSide').textContent = user.name);
    document.getElementById('dashUserRole')     && (document.getElementById('dashUserRole').textContent     = user.role);
  }

  // Tab switching
  document.querySelectorAll('.dash-nav__link').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.dash-nav__link').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const target = tab.dataset.tab;
      document.querySelectorAll('.dash-tab-panel').forEach(p => {
        p.style.display = (p.id === target) ? 'block' : 'none';
      });
    });
  });

  // Load all dashboard data
  loadMyProducts();
  loadMyOrders();

  async function loadMyProducts() {
    const tbody = document.getElementById('myProductsBody');
    if (!tbody) return;

    const { ok, data } = await apiFetch(API.ENDPOINTS.productMine);
    if (!ok) { tbody.innerHTML = '<tr><td colspan="5">Failed to load.</td></tr>'; return; }

    const products = data.data;
    if (!products.length) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--light-gray)">No products yet. <a href="upload.html" style="color:var(--forest-mid)">Upload one!</a></td></tr>';
      return;
    }

    tbody.innerHTML = products.map(p => `
      <tr>
        <td><strong>${p.name}</strong></td>
        <td>XAF ${Number(p.price).toLocaleString()}</td>
        <td>${p.quantity}</td>
        <td><span class="badge ${p.status === 'active' ? 'badge--green' : 'badge--red'}">${p.status}</span></td>
        <td><a href="upload.html?edit=${p.id}" class="btn btn-outline btn-sm">Edit</a></td>
      </tr>`).join('');
  }

  async function loadMyOrders() {
    const tbody = document.getElementById('ordersBody');
    if (!tbody) return;

    const { ok, data } = await apiFetch(API.ENDPOINTS.ordersMine);
    if (!ok) { tbody.innerHTML = '<tr><td colspan="5">Failed to load.</td></tr>'; return; }

    const orders = data.data;
    if (!orders.length) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--light-gray)">No orders yet.</td></tr>';
      return;
    }

    const cls = { pending:'badge--orange', confirmed:'badge--green', completed:'badge--green', cancelled:'badge--red' };
    tbody.innerHTML = orders.map(o => `
      <tr>
        <td><strong>#${String(o.id).slice(0,8)}</strong></td>
        <td>${o.product?.name || '—'}</td>
        <td>${o.buyer?.name  || '—'}</td>
        <td>XAF ${Number(o.total_price).toLocaleString()}</td>
        <td><span class="badge ${cls[o.status] || ''}">${o.status}</span></td>
      </tr>`).join('');
  }

  // Logout
  document.getElementById('logoutBtn')?.addEventListener('click', async () => {
    await apiFetch(API.ENDPOINTS.logout, { method: 'POST' });
    Auth.clearAll();
    toast('Logged out.', 'ok');
    setTimeout(() => window.location.href = 'index.html', 900);
  });
})();
