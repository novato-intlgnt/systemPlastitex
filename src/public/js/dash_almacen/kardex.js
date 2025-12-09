import { apiRequest } from "./../fetchModule.js";

/**
 * Módulo de Kardex (Reporte de movimientos)
 * Para el rol aux_almacen
 * Implementa carga perezosa (lazy loading)
 */

const API = window.location.origin;
let table = null;
let moduleInitialized = false;

function initTable() {
  table = new Tabulator("#kardex-table", {
    data: [],
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 10,
    height: "50vh",
    placeholder: "Seleccione un producto para ver su kardex",
    columns: [
      { 
        title: "Fecha", 
        field: "movement_date", 
        width: 110,
        hozAlign: "center",
        formatter: (cell) => {
          const date = new Date(cell.getValue());
          return date.toLocaleDateString("es-BO");
        }
      },
      { 
        title: "Tipo", 
        field: "movement_type", 
        width: 100, 
        hozAlign: "center",
        formatter: (cell) => {
          const type = cell.getValue();
          const isEntry = type?.toUpperCase() === "ENTRADA";
          const color = isEntry ? "#f05454" : "#28a745";
          const icon = isEntry ? "↓" : "↑";
          return `<span style="color: ${color}; font-weight: bold;">${icon} ${type}</span>`;
        }
      },
      { title: "Referencia", field: "reference", width: 130 },
      { 
        title: "Cantidad", 
        field: "quantity", 
        width: 100, 
        hozAlign: "right",
        formatter: (cell) => {
          const value = cell.getValue();
          return `<strong>${value}</strong>`;
        }
      },
      { 
        title: "Balance", 
        field: "running_balance", 
        width: 100, 
        hozAlign: "right",
        formatter: (cell) => {
          const value = cell.getValue();
          const color = value >= 0 ? "#28a745" : "#f05454";
          const sign = value >= 0 ? "+" : "";
          return `<span style="color: ${color};">${sign}${value}</span>`;
        }
      },
      { title: "Proveedor/Cliente", field: "entity_name", minWidth: 150 },
      { title: "Tipo Entidad", field: "entity_type", width: 110, hozAlign: "center" },
    ],
  });
}

async function loadProducts() {
  try {
    const res = await apiRequest(`${API}/product`);
    const products = res.products || [];
    const select = document.getElementById("kardex-product");
    if (select) {
      select.innerHTML = '<option value="">Seleccione un producto</option>' +
        products.map(p => `<option value="${p.id}">${p.name}</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando productos:", error);
  }
}

async function loadKardex() {
  const productId = document.getElementById("kardex-product")?.value;
  
  if (!productId) {
    table.replaceData([]);
    updateProductInfo(null);
    return;
  }
  
  try {
    const startDate = document.getElementById("kardex-start-date")?.value || "";
    const endDate = document.getElementById("kardex-end-date")?.value || "";
    
    let url = `${API}/reports/aux-almacen/kardex/${productId}?`;
    if (startDate) url += `start_date=${startDate}&`;
    if (endDate) url += `end_date=${endDate}&`;
    
    const res = await apiRequest(url);
    const data = res.data || [];
    table.replaceData(data);
    
    // Cargar info del producto
    await loadProductInfo(productId);
    
    // Calcular resumen
    updateKardexSummary(data);
  } catch (error) {
    console.error("Error cargando kardex:", error);
    if (typeof Swal !== "undefined") {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo cargar el kardex del producto",
      });
    }
  }
}

async function loadProductInfo(productId) {
  try {
    const res = await apiRequest(`${API}/reports/aux-almacen/stock/${productId}`);
    const product = res.data?.[0] || res.data;
    updateProductInfo(product);
  } catch (error) {
    console.error("Error cargando info del producto:", error);
  }
}

function updateProductInfo(product) {
  const infoEl = document.getElementById("kardex-product-info");
  if (!infoEl) return;
  
  if (!product) {
    infoEl.innerHTML = '<p class="text-muted">Seleccione un producto para ver su información</p>';
    return;
  }
  
  const stockColor = product.stock < 10 ? "#f05454" : product.stock < 50 ? "#ffc107" : "#28a745";
  
  infoEl.innerHTML = `
    <div class="product-info-card">
      <h4>${product.product_name}</h4>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">Categoría</span>
          <span class="info-value">${product.category_name || 'N/A'}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Unidad</span>
          <span class="info-value">${product.unit_name || 'N/A'}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Stock Actual</span>
          <span class="info-value" style="color: ${stockColor}; font-weight: bold;">${product.stock}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Total Entradas</span>
          <span class="info-value" style="color: #28a745;">+${product.total_entries || 0}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Total Salidas</span>
          <span class="info-value" style="color: #f05454;">-${product.total_exits || 0}</span>
        </div>
      </div>
    </div>
  `;
}

function updateKardexSummary(data) {
  const entries = data.filter(m => m.movement_type?.toUpperCase() === "ENTRADA");
  const exits = data.filter(m => m.movement_type?.toUpperCase() === "SALIDA");
  
  const totalEntries = entries.reduce((sum, m) => sum + (m.quantity || 0), 0);
  const totalExits = exits.reduce((sum, m) => sum + (m.quantity || 0), 0);
  
  const summaryEl = document.getElementById("kardex-summary");
  if (summaryEl) {
    summaryEl.innerHTML = `
      <div class="summary-card">
        <span class="summary-label">Movimientos</span>
        <span class="summary-value">${data.length}</span>
      </div>
      <div class="summary-card success">
        <span class="summary-label">Entradas</span>
        <span class="summary-value">+${totalEntries}</span>
      </div>
      <div class="summary-card danger">
        <span class="summary-label">Salidas</span>
        <span class="summary-value">-${totalExits}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Balance</span>
        <span class="summary-value">${totalEntries - totalExits}</span>
      </div>
    `;
  }
}

function initEvents() {
  // Selector de producto
  const productSelect = document.getElementById("kardex-product");
  if (productSelect) {
    productSelect.addEventListener("change", loadKardex);
  }
  
  // Botón aplicar filtros
  const btnFilter = document.getElementById("btn-filter-kardex");
  if (btnFilter) {
    btnFilter.addEventListener("click", loadKardex);
  }
  
  // Botón limpiar filtros
  const btnClear = document.getElementById("btn-clear-kardex");
  if (btnClear) {
    btnClear.addEventListener("click", () => {
      document.getElementById("kardex-start-date").value = "";
      document.getElementById("kardex-end-date").value = "";
      loadKardex();
    });
  }
}

// ============================================================================
// INICIALIZACIÓN CON CARGA PEREZOSA
// ============================================================================

async function initKardexModule() {
  // Si ya está inicializado, solo recargar productos
  if (moduleInitialized) {
    await loadProducts();
    return;
  }

  // Primera inicialización
  initTable();
  initEvents();
  await loadProducts();
  
  moduleInitialized = true;
}

/* ============================================
   ACTIVAR CUANDO SE HAGA CLIC EN EL BOTÓN
============================================ */
document.getElementById("btn-kardex")?.addEventListener("click", () => {
  initKardexModule();
});
