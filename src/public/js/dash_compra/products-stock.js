import { apiRequest } from "./../fetchModule.js";

const API = window.env?.API_URL || window.location.origin;

console.log(window.env);
let table = null;
let moduleInitialized = false;

function initTable() {
  table = new Tabulator("#products-stock-table", {
    data: [],
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 17,
    height: "55vh",
    placeholder: "No hay productos",
    columns: [
      { title: "ID", field: "id", width: 70, hozAlign: "center" },
      { title: "Producto", field: "name", minWidth: 150 },
      { title: "Categoría", field: "category", minWidth: 120 },
      { title: "Unidad", field: "unit", width: 100, hozAlign: "center" },
      { 
        title: "Stock", 
        field: "stock", 
        width: 100, 
        hozAlign: "right",
        formatter: (cell) => {
          const value = cell.getValue();
          const color = value < 10 ? "#f05454" : value < 50 ? "#ffc107" : "#28a745";
          return `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
        }
      },
      { 
        title: "P. Compra", 
        field: "purchase_price", 
        width: 110, 
        hozAlign: "right",
        formatter: "money",
        formatterParams: { symbol: "$/. ", precision: 2 }
      },
    ],
  });
}

async function loadProducts() {
  try {
    const res = await apiRequest(`${API}/product/`);
    const products = res.products || [];
    table.replaceData(products);
  } catch (error) {
    console.error("Error cargando productos:", error);
    if (typeof Swal !== "undefined") {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudieron cargar los productos",
      });
    }
  }
}

// Búsqueda
function initSearch() {
  const searchInput = document.getElementById("products-stock-search");
  if (searchInput) {
    searchInput.addEventListener("keyup", (e) => {
      table.setFilter("name", "like", e.target.value);
    });
  }
}

// Reporte de bajo stock
async function loadLowStock() {
  try {
    const threshold = document.getElementById("low-stock-threshold")?.value || 10;
    const res = await apiRequest(`${API}/reports/aux-compra/low-stock?threshold=${threshold}`);
    
    if (res.data && res.data.length > 0) {
      const lowStockList = document.getElementById("low-stock-list");
      if (lowStockList) {
        lowStockList.innerHTML = res.data.map(p => `
          <div class="low-stock-item">
            <span class="product-name">${p.product_name}</span>
            <span class="stock-badge danger">${p.current_stock} unidades</span>
          </div>
        `).join("");
      }
    }
  } catch (error) {
    console.error("Error cargando bajo stock:", error);
  }
}

async function initProductsStockModule() {
  if (moduleInitialized) {
    await loadProducts();
    await loadLowStock();
    return;
  }

  initTable();
  initSearch();
  await loadProducts();
  await loadLowStock();
  
  moduleInitialized = true;
}

document.getElementById("btn-products-stock")?.addEventListener("click", () => {
  initProductsStockModule();
});

document.getElementById("btn-refresh-products")?.addEventListener("click", () => {
  initProductsStockModule();
});
