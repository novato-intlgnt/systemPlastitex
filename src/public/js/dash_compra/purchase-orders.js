import { apiRequest } from "./../fetchModule.js";
import {
  openModal,
  closeModal,
  fillForm,
  clearForm,
  setupModalBackdropClose,
  setupCancelButton,
  setupEscapeClose,
} from "./../modalModule.js";

/**
 * Módulo de órdenes de compra (CRUD)
 * Para el rol aux_compra
 */

const API = window.location.origin;
let table;
let isEditing = false;
let currentEditId = null;

function initTable() {
  table = new Tabulator("#purchase-orders-table", {
    data: [],
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 15,
    height: "68vh",
    placeholder: "No hay órdenes de compra",
    columns: [
      { title: "ID", field: "id", width: 70, hozAlign: "center" },
      { 
        title: "Fecha", 
        field: "date", 
        width: 120,
        formatter: (cell) => {
          const date = new Date(cell.getValue());
          return date.toLocaleDateString("es-BO");
        }
      },
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
          return `<span class="status-badge" style="background: ${color}; padding: 4px 8px; border-radius: 4px; color: white; font-size: 11px;">${status || 'N/A'}</span>`;
        }
      },
      {
        title: "Acciones",
        hozAlign: "center",
        headerSort: false,
        width: 150,
        formatter: () => `
          <button class="table-btn edit" title="Editar">
            <i class="fi fi-rr-edit"></i>
          </button>
          <button class="table-btn view" title="Ver Detalles" style="background: #17a2b8;">
            <i class="fi fi-rr-eye"></i>
          </button>
          <button class="table-btn delete" title="Eliminar">
            <i class="fi fi-rr-trash"></i>
          </button>
        `,
        cellClick: (e, cell) => {
          const row = cell.getRow().getData();
          const btn = e.target.closest(".table-btn");
          if (!btn) return;

          if (btn.classList.contains("edit")) openEdit(row);
          else if (btn.classList.contains("view")) viewDetails(row.id);
          else if (btn.classList.contains("delete")) deleteOrder(row.id);
        },
      },
    ],
  });
}

async function loadSuppliers() {
  try {
    const res = await apiRequest(`${API}/supplier`);
    const suppliers = res.suppliers || [];
    const select = document.getElementById("order-supplier");
    if (select) {
      select.innerHTML = '<option value="">Seleccione proveedor</option>' +
        suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando proveedores:", error);
  }
}

async function loadOrders() {
  try {
    const res = await apiRequest(`${API}/purchase-orders`);
    const orders = res.data || [];
    table.replaceData(orders);
  } catch (error) {
    console.error("Error cargando órdenes:", error);
    showError("No se pudieron cargar las órdenes de compra");
  }
}

function openCreate() {
  isEditing = false;
  currentEditId = null;
  clearForm("order-form");
  document.getElementById("order-modal-title").textContent = "Nueva Orden de Compra";
  openModal("order-modal");
}

function openEdit(row) {
  isEditing = true;
  currentEditId = row.id;
  clearForm("order-form");
  fillForm("order-form", {
    supplier_id: row.supplier_id,
    total: row.total,
    status: row.status
  });
  document.getElementById("order-modal-title").textContent = "Editar Orden de Compra";
  openModal("order-modal");
}

async function viewDetails(orderId) {
  try {
    const res = await apiRequest(`${API}/purchase-orders/${orderId}`);
    const order = res.data;
    
    // Mostrar modal de detalles
    const detailContent = document.getElementById("order-detail-content");
    if (detailContent) {
      detailContent.innerHTML = `
        <div class="detail-header">
          <p><strong>Orden #:</strong> ${order.id}</p>
          <p><strong>Proveedor:</strong> ${order.supplier_name || 'N/A'}</p>
          <p><strong>Fecha:</strong> ${new Date(order.date).toLocaleDateString("es-BO")}</p>
          <p><strong>Total:</strong> $/. ${parseFloat(order.total || 0).toFixed(2)}</p>
          <p><strong>Estado:</strong> ${order.status || 'N/A'}</p>
        </div>
        <h4 style="color: white"><strong>Lista de Productos</strong></h4>
        <div class="detail-items">
          ${order.details?.length > 0 ? order.details.map(d => `
            <div class="detail-item">
              <span>${d.product_name}</span>
              <span>${d.quantity} x $/. ${parseFloat(d.unit_price || 0).toFixed(2)}</span>
              <span><strong>$/. ${(d.quantity * (d.unit_price || 0)).toFixed(2)}</strong></span>
            </div>
          `).join("") : '<p>No hay detalles registrados</p>'}
        </div>
      `;
    }
    openModal("order-detail-modal");
  } catch (error) {
    console.error("Error cargando detalles:", error);
    showError("No se pudieron cargar los detalles de la orden");
  }
}

async function submitOrder(e) {
  e.preventDefault();
  
  const form = document.getElementById("order-form");
  const formData = new FormData(form);
  const payload = {
    supplier_id: parseInt(formData.get("supplier_id")),
    total: parseFloat(formData.get("total")) || 0,
    status: formData.get("status") || "pendiente"
  };

  try {
    if (isEditing && currentEditId) {
      await apiRequest(`${API}/purchase-orders/${currentEditId}`, "PUT", payload);
    } else {
      await apiRequest(`${API}/purchase-orders`, "POST", payload);
    }
    
    await loadOrders();
    closeModal("order-modal");
    showSuccess("Orden guardada correctamente");
  } catch (error) {
    console.error("Error guardando orden:", error);
    showError(error.message || "Error al guardar la orden");
  }
}

async function deleteOrder(id) {
  const confirmed = await confirmDelete();
  if (!confirmed) return;

  try {
    await apiRequest(`${API}/purchase-orders/${id}`, "DELETE");
    table.deleteRow(id);
    showSuccess("Orden eliminada correctamente");
  } catch (error) {
    console.error("Error eliminando orden:", error);
    showError(error.message || "Error al eliminar la orden");
  }
}

async function confirmDelete() {
  if (typeof Swal !== "undefined") {
    const result = await Swal.fire({
      title: "¿Confirmar eliminación?",
      text: "Esta acción no se puede deshacer",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    });
    return result.isConfirmed;
  }
  return confirm("¿Está seguro de eliminar esta orden?");
}

function showSuccess(message) {
  if (typeof Swal !== "undefined") {
    Swal.fire({ icon: "success", title: "Éxito", text: message, timer: 2000, showConfirmButton: false });
  }
}

function showError(message) {
  if (typeof Swal !== "undefined") {
    Swal.fire({ icon: "error", title: "Error", text: message });
  } else {
    alert(message);
  }
}

function initEvents() {
  // Botón agregar
  const btnAdd = document.getElementById("btn-add-order");
  if (btnAdd) btnAdd.addEventListener("click", openCreate);

  // Submit del formulario
  const form = document.getElementById("order-form");
  if (form) form.addEventListener("submit", submitOrder);

  // Búsqueda
  const searchInput = document.getElementById("order-search");
  if (searchInput) {
    searchInput.addEventListener("keyup", (e) => {
      table.setFilter("supplier_name", "like", e.target.value);
    });
  }

  // Modal events
  setupCancelButton("btn-cancel-order", "order-modal");
  setupModalBackdropClose("order-modal");
  setupEscapeClose("order-modal");
  
  // Modal de detalles
  setupModalBackdropClose("order-detail-modal");
  setupEscapeClose("order-detail-modal");
  const btnCloseDetail = document.getElementById("btn-close-detail");
  if (btnCloseDetail) btnCloseDetail.addEventListener("click", () => closeModal("order-detail-modal"));
}

// Inicialización
(async function init() {
  initTable();
  initEvents();
  await loadSuppliers();
  await loadOrders();
})();
