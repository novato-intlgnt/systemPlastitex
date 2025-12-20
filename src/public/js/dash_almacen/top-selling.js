import { apiRequest } from "./../fetchModule.js";

const API = window.location.origin;
let table = null;
let moduleInitialized = false;

function initTable() {
  table = new Tabulator("#top-selling-table", {
    data: [],
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 20,
    height: "65vh",
    placeholder: "No hay datos de productos vendidos",
    columns: [
      { 
        title: "#", 
        field: "rank", 
        width: 60, 
        hozAlign: "center",
        formatter: (cell) => {
          const rank = cell.getValue();
          let icon = "";
          if (rank === 1) icon = "🥇";
          else if (rank === 2) icon = "🥈";
          else if (rank === 3) icon = "🥉";
          else icon = rank;
          return `<span style="font-weight: bold;">${icon}</span>`;
        }
      },
      { title: "ID", field: "product_id", width: 60, hozAlign: "center" },
      { title: "Producto", field: "product_name", minWidth: 140 },
      { title: "Categoría", field: "category_name", width: 100 },
      { title: "Unidad", field: "unit_name", width: 100, hozAlign: "center" },
      { 
        title: "Total Vendido", 
        field: "total_sold", 
        width: 120, 
        hozAlign: "right",
        formatter: (cell) => {
          const value = cell.getValue();
          return `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
        }
      },
      { 
        title: "Stock Actual", 
        field: "current_stock", 
        width: 110, 
        hozAlign: "right",
        formatter: (cell) => {
          const value = cell.getValue();
          const color = value < 10 ? "#f05454" : value < 50 ? "#ffc107" : "#28a745";
          return `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
        }
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
        title: "Ingresos Est.", 
        field: "estimated_revenue", 
        width: 130, 
        hozAlign: "right",
        formatter: (cell, formatterParams, onRendered) => {
          const row = cell.getRow().getData();
          const revenue = (row.total_sold || 0) * (row.sale_price || 0);
          return `<span style="color: #17a2b8; font-weight: bold;">$/. ${revenue.toFixed(2)}</span>`;
        }
      },
    ],
  });
}

async function loadTopSelling() {
  try {
    const limit = document.getElementById("top-selling-limit")?.value || 10;
    const url = `${API}/reports/top_selling?limit=${limit}`;
    
    const res = await apiRequest(url);
    let data = res.data || [];
    
    // Agregar ranking
    data = data.map((item, index) => ({
      ...item,
      rank: index + 1
    }));
    
    table.replaceData(data);
    updateSummary(data);
  } catch (error) {
    console.error("Error cargando top ventas:", error);
    if (typeof Swal !== "undefined") {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo cargar el reporte de productos más vendidos",
      });
    }
  }
}

function updateSummary(data) {
  const totalProducts = data.length;
  const totalSold = data.reduce((sum, p) => sum + (p.total_sold || 0), 0);
  const totalRevenue = data.reduce((sum, p) => sum + ((p.total_sold || 0) * (p.sale_price || 0)), 0);
  const avgSold = totalProducts > 0 ? (totalSold / totalProducts).toFixed(1) : 0;
  
  const summaryEl = document.getElementById("top-selling-summary");
  if (summaryEl) {
    summaryEl.innerHTML = `
      <div class="summary-card">
        <span class="summary-label">Productos Listados</span>
        <span class="summary-value">${totalProducts}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Total Unidades Vendidas</span>
        <span class="summary-value">${totalSold}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Promedio Vendido</span>
        <span class="summary-value">${avgSold}</span>
      </div>
      <div class="summary-card success">
        <span class="summary-label">Ingresos Estimados</span>
        <span class="summary-value">$/. ${totalRevenue.toFixed(2)}</span>
      </div>
    `;
  }
}

function initEvents() {
  // Botón filtrar/actualizar
  const btnFilter = document.getElementById("btn-filter-top-selling");
  if (btnFilter) {
    btnFilter.addEventListener("click", loadTopSelling);
  }

  // Cambio en select también actualiza
  const limitSelect = document.getElementById("top-selling-limit");
  if (limitSelect) {
    limitSelect.addEventListener("change", loadTopSelling);
  }
}

// ============================================================================
// INICIALIZACIÓN CON CARGA PEREZOSA
// ============================================================================

async function initTopSellingModule() {
  if (moduleInitialized) {
    await loadTopSelling();
    return;
  }

  initTable();
  initEvents();
  await loadTopSelling();
  
  moduleInitialized = true;
}

/* ============================================
   ACTIVAR CUANDO SE HAGA CLIC EN EL BOTÓN
============================================ */
document.getElementById("btn-top-selling")?.addEventListener("click", () => {
  initTopSellingModule();
});
