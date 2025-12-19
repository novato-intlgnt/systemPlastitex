import { apiRequest } from "./../fetchModule.js";

/**
 * Módulo de Stock (Reporte)
 * Para el rol aux_almacen
 * Implementa carga perezosa (lazy loading)
 */

const API = window.location.origin;
let table = null;
let moduleInitialized = false;

function initTable() {
  table = new Tabulator("#stock-table", {
    data: [],
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 20,
    height: "65vh",
    placeholder: "No hay datos de stock",
    columns: [
      { title: "ID", field: "product_id", width: 60, hozAlign: "center" },
      { title: "Producto", field: "product_name", minWidth: 150 },
      { title: "Categoría", field: "category_name", minWidth: 120 },
      { title: "Unidad", field: "unit_name", width: 90, hozAlign: "center" },
      { 
        title: "Stock", 
        field: "stock", 
        width: 90, 
        hozAlign: "right",
        formatter: (cell) => {
          const value = cell.getValue();
          const color = value < 10 ? "#f05454" : value < 50 ? "#ffc107" : "#28a745";
          return `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
        }
      },
      { 
        title: "Entradas", 
        field: "total_entries", 
        width: 90, 
        hozAlign: "right",
        formatter: (cell) => `<span style="color: #28a745;">+${cell.getValue() || 0}</span>`
      },
      { 
        title: "Salidas", 
        field: "total_exits", 
        width: 90, 
        hozAlign: "right",
        formatter: (cell) => `<span style="color: #f05454;">-${cell.getValue() || 0}</span>`
      },
      { 
        title: "P. Venta", 
        field: "sale_price", 
        width: 100, 
        hozAlign: "right",
        formatter: "money",
        formatterParams: { symbol: "$/. ", precision: 2 }
      },
      { 
        title: "P. Compra", 
        field: "purchase_price", 
        width: 100, 
        hozAlign: "right",
        formatter: "money",
        formatterParams: { symbol: "$/. ", precision: 2 }
      },
    ],
  });
}

async function loadStock() {
  try {
    const cateogryId = document.getElementById("stock-category")?.value || "";
    const unitId = document.getElementById("stock-unit")?.value || "";
    let url = new URL(`${API}/reports/aux-almacen/stock`);
    if (cateogryId) url.searchParams.append('category_id', cateogryId);
    if (unitId) url.searchParams.append('unit_id', unitId);
    
    const res = await apiRequest(url.toString());
    const data = res.data || [];
    table.replaceData(data);

    console.log(data);
    
    updateSummary(data);
  } catch (error) {
    console.error("Error cargando stock:", error);
    if (typeof Swal !== "undefined") {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo cargar el reporte de stock",
      });
    }
  }
}

function updateSummary(data) {
  const totalProducts = data.length;
  const totalStock = data.reduce((sum, p) => sum + (p.stock || 0), 0);
  const lowStock = data.filter(p => p.stock < 10).length;
  const totalValue = data.reduce((sum, p) => sum + (p.stock * (p.purchase_price || 0)), 0);
  
  const summaryEl = document.getElementById("stock-summary");
  if (summaryEl) {
    summaryEl.innerHTML = `
      <div class="summary-card">
        <span class="summary-label">Total Productos</span>
        <span class="summary-value">${totalProducts}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Stock Total</span>
        <span class="summary-value">${totalStock}</span>
      </div>
      <div class="summary-card warning">
        <span class="summary-label">Bajo Stock</span>
        <span class="summary-value">${lowStock}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Valor Inventario</span>
        <span class="summary-value">$/. ${totalValue.toFixed(2)}</span>
      </div>
    `;
  }
}

async function loadSelectOptions() {
  try {
    const [catRes, unitRes] = await Promise.all([
      apiRequest(`${API}/category`),
      apiRequest(`${API}/unit`)
    ]);

    const categories = catRes.categories || [];
    const units = unitRes.units || [];

    const catSelect = document.getElementById("stock-category");
    const unitSelect = document.getElementById("stock-unit");

    if (catSelect) {
      catSelect.innerHTML = `
        <option value="">Todas las categorias</option>
        ${categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("")}
      `;
    }

    if (unitSelect) {
      unitSelect.innerHTML = `
        <option value="">Todas las unidades</option>
        ${units.map(u => `<option value="${u.id}">${u.name}</option>`).join("")}
      `;
    }
  } catch (error) {
    console.error("Error cargando opciones:", error);
  }
}



function initEvents() {
  // Búsqueda
  const searchInput = document.getElementById("stock-search");
  if (searchInput) {
    searchInput.addEventListener("keyup", (e) => {
      table.setFilter("product_name", "like", e.target.value);
    });
  }

  const productSelect = document.getElementById("filter-product");
  if (productSelect) {
    productSelect.addEventListener("change", loadStock);
  }

  const catSelect = document.getElementById("stock-category");
  if (catSelect) {
    catSelect.addEventListener("change", loadStock);
  }
  const unitSelect = document.getElementById("stock-unit");
  if (unitSelect) {
    unitSelect.addEventListener("change", loadStock);
  }

  // Botón limpiar filtros
  const btnClear = document.getElementById("btn-clear-stock");
  if (btnClear) {
    btnClear.addEventListener("click", () => {
      document.getElementById("stock-category").value = "";
      document.getElementById("stock-unit").value = "";
      loadStock();
    });
  }
}

// ============================================================================
// INICIALIZACIÓN CON CARGA PEREZOSA
// ============================================================================

async function initStockModule() {
  if (moduleInitialized) {
    await loadStock();
    return;
  }

  initTable();
  initEvents();
  await loadSelectOptions();
  await loadStock();
  
  moduleInitialized = true;
}

/* ============================================
   ACTIVAR CUANDO SE HAGA CLIC EN EL BOTÓN
============================================ */
document.getElementById("btn-stock")?.addEventListener("click", () => {
  initStockModule();
});
