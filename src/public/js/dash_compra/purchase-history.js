import { apiRequest } from "./../fetchModule.js";

const API = window.env?.API_URL || window.location.origin;
let table = null;
let moduleInitialized = false;

function initTable() {
  table = new Tabulator("#purchase-history-table", {
    data: [],
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 15,
    height: "65vh",
    placeholder: "No hay registros de compras",
    columns: [
      { title: "ID", field: "order_id", width: 70, hozAlign: "center" },
      { 
        title: "Fecha", 
        field: "order_date", 
        width: 120,
        formatter: (cell) => {
          const date = new Date(cell.getValue());
          return date.toLocaleDateString("es-BO");
        }
      },
      { title: "Creado por", field: "created_by", minWidth: 150 },
      { title: "Proveedor", field: "supplier_name", minWidth: 150 },
      { 
        title: "Total", 
        field: "total", 
        width: 120, 
        hozAlign: "right",
        formatter: "money",
        formatterParams: { symbol: "$/. ", precision: 2 }
      },
      { 
        title: "Estado", 
        field: "status", 
        width: 110, 
        hozAlign: "center",
        formatter: (cell) => {
          const status = cell.getValue();
          const colors = {
            'pendiente': '#ffc107',
            'aprobado': '#28a745',
            'rechazado': '#dc3545',
            'completado': '#17a2b8'
          };
          const color = colors[status?.toLowerCase()] || '#6c757d';
          return `<span class="status-badge" style="background: ${color};">${status || 'N/A'}</span>`;
        }
      },
    ],
  });
}

async function loadSuppliers() {
  try {
    const res = await apiRequest(`${API}/supplier`);
    const suppliers = res.suppliers || [];
    const select = document.getElementById("filter-supplier");
    if (select) {
      select.innerHTML = '<option value="">Todos los proveedores</option>' +
        suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando proveedores:", error);
  }
}

async function loadHistory() {
  try {
    const supplierId = document.getElementById("filter-supplier")?.value || "";
    const startDate = document.getElementById("filter-start-date")?.value || "";
    const endDate = document.getElementById("filter-end-date")?.value || "";
    
    let url = `${API}/reports/aux-compra/purchase-history?`;
    if (supplierId) url += `supplier_id=${supplierId}&`;
    if (startDate) url += `start_date=${startDate}&`;
    if (endDate) url += `end_date=${endDate}&`;
    
    const res = await apiRequest(url);
    const data = res.data || [];
    table.replaceData(data);
    
    // Actualizar totales
    updateSummary(data);
  } catch (error) {
    console.error("Error cargando historial:", error);
    if (typeof Swal !== "undefined") {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo cargar el historial de compras",
      });
    }
  }
}

function updateSummary(data) {
  const totalOrders = data.length;
  const totalAmount = data.reduce((sum, order) => sum + (parseFloat(order.total) || 0), 0);
  
  const summaryEl = document.getElementById("history-summary");
  if (summaryEl) {
    summaryEl.innerHTML = `
      <div class="summary-card">
        <span class="summary-label">Total Órdenes</span>
        <span class="summary-value">${totalOrders}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Monto Total</span>
        <span class="summary-value">$/. ${totalAmount.toFixed(2)}</span>
      </div>
    `;
  }
}

function initFilters() {
  // Botón aplicar filtros
  const btnFilter = document.getElementById("btn-filter-history");
  if (btnFilter) {
    btnFilter.addEventListener("click", loadHistory);
  }
  
  // Botón limpiar filtros
  const btnClear = document.getElementById("btn-clear-filters");
  if (btnClear) {
    btnClear.addEventListener("click", () => {
      document.getElementById("filter-supplier").value = "";
      document.getElementById("filter-start-date").value = "";
      document.getElementById("filter-end-date").value = "";
      loadHistory();
    });
  }
}

async function initPurchaseHistoryModule() {
  if (moduleInitialized) {
    await loadHistory();
    return;
  }

  initTable();
  initFilters();
  await loadSuppliers();
  await loadHistory();
  
  moduleInitialized = true;
}

document.getElementById("btn-history")?.addEventListener("click", () => {
  initPurchaseHistoryModule();
});
