import { apiRequest } from "./../fetchModule.js";

/**
 * Módulo de Stock (Reporte)
 * Para el rol aux_almacen
 */

const API = window.location.origin;
let table;

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
    const productId = document.getElementById("filter-product")?.value || "";
    let url = `${API}/reports/aux-almacen/stock`;
    if (productId) url += `?product_id=${productId}`;
    
    const res = await apiRequest(url);
    const data = res.data || [];
    table.replaceData(data);
    
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

async function loadProductsFilter() {
  try {
    const res = await apiRequest(`${API}/product`);
    const products = res.products || [];
    const select = document.getElementById("filter-product");
    if (select) {
      select.innerHTML = '<option value="">Todos los productos</option>' +
        products.map(p => `<option value="${p.id}">${p.name}</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando productos:", error);
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

  // Filtro por producto
  const filterProduct = document.getElementById("filter-product");
  if (filterProduct) {
    filterProduct.addEventListener("change", loadStock);
  }

  // Botón refrescar
  const btnRefresh = document.getElementById("btn-refresh-stock");
  if (btnRefresh) {
    btnRefresh.addEventListener("click", loadStock);
  }
}

// Inicialización
(async function init() {
  initTable();
  initEvents();
  await loadProductsFilter();
  await loadStock();
})();
