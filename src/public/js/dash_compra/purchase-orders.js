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

const API = window.env?.API_URL || window.location.origin;
let table = null;
let isEditing = false;
let currentEditId = null;
let moduleInitialized = false;

let orderDetails = [];
let productsCache = [];

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
        formatterParams: { symbol: "S/. ", precision: 2 }
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
    const res = await apiRequest(`${API}/supplier/`);
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

/**
 * Carga los productos disponibles para agregar a la orden
 */
async function loadProducts() {
  try {
    const res = await apiRequest(`${API}/product/`);
    const products = res.products || [];
    productsCache = products;
    
    const select = document.getElementById("product-select");
    if (select) {
      select.innerHTML = '<option value="">Seleccione producto</option>' +
        products.map(p => `<option value="${p.id}" data-price="${p.purchase_price || 0}">${p.name}</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando productos:", error);
  }
}

/**
 * Obtiene un producto del cache por su ID
 */
function getProductById(productId) {
  return productsCache.find(p => p.id === parseInt(productId));
}

/**
 * Actualiza el precio unitario cuando se selecciona un producto
 */
function onProductSelect() {
  const select = document.getElementById("product-select");
  const priceInput = document.getElementById("product-unit-price");
  const quantityInput = document.getElementById("product-quantity");
  
  if (!select || !priceInput) return;
  
  const productId = select.value;
  if (!productId) {
    priceInput.value = "0";
    calculateLineTotal();
    return;
  }
  
  const product = getProductById(productId);
  if (product) {
    priceInput.value = parseFloat(product.purchase_price || 0).toFixed(2);
    quantityInput.value = 1;
    calculateLineTotal();
  }
}

/**
 * Calcula el total de la línea (cantidad * precio unitario)
 */
function calculateLineTotal() {
  const quantity = parseFloat(document.getElementById("product-quantity")?.value) || 0;
  const unitPrice = parseFloat(document.getElementById("product-unit-price")?.value) || 0;
  const lineTotalInput = document.getElementById("product-line-total");
  
  if (lineTotalInput) {
    lineTotalInput.value = (quantity * unitPrice).toFixed(2);
  }
}

/**
 * Agrega un producto a la lista de detalles de la orden
 */
function addProductToOrder() {
  const productSelect = document.getElementById("product-select");
  const quantityInput = document.getElementById("product-quantity");
  const unitPriceInput = document.getElementById("product-unit-price");
  
  const productId = parseInt(productSelect?.value);
  const quantity = parseInt(quantityInput?.value) || 0;
  const unitPrice = parseFloat(unitPriceInput?.value) || 0;
  
  if (!productId) {
    showError("Seleccione un producto");
    return;
  }
  
  if (quantity <= 0) {
    showError("La cantidad debe ser mayor a 0");
    return;
  }
  
  if (unitPrice <= 0) {
    showError("El precio unitario debe ser mayor a 0");
    return;
  }
  
  // Verificar si el producto ya está en la lista
  const existingIndex = orderDetails.findIndex(d => d.product_id === productId);
  if (existingIndex >= 0) {
    // Actualizar cantidad si ya existe
    orderDetails[existingIndex].quantity += quantity;
  } else {
    // Agregar nuevo detalle
    const product = getProductById(productId);
    orderDetails.push({
      product_id: productId,
      product_name: product?.name || 'Producto',
      quantity: quantity,
      unit_price: unitPrice
    });
  }
  
  // Actualizar UI
  renderOrderDetails();
  recalculateOrderTotal();
  
  // Limpiar campos de entrada
  productSelect.value = "";
  quantityInput.value = "1";
  unitPriceInput.value = "0";
  document.getElementById("product-line-total").value = "0";
}

/**
 * Elimina un producto de la lista de detalles
 */
function removeProductFromOrder(index) {
  orderDetails.splice(index, 1);
  renderOrderDetails();
  recalculateOrderTotal();
}

/**
 * Renderiza la tabla de detalles de la orden
 */
function renderOrderDetails() {
  const tbody = document.getElementById("order-details-body");
  const container = document.querySelector(".details-table-container");
  
  if (!tbody) return;
  
  if (orderDetails.length === 0) {
    tbody.innerHTML = "";
    container?.classList.remove("has-items");
    return;
  }
  
  container?.classList.add("has-items");
  
  tbody.innerHTML = orderDetails.map((detail, index) => `
    <tr>
      <td>${detail.product_name}</td>
      <td>${detail.quantity}</td>
      <td>${parseFloat(detail.unit_price).toFixed(2)}</td>
      <td>${(detail.quantity * detail.unit_price).toFixed(2)}</td>
      <td>
        <button type="button" class="btn-remove-item" onclick="window.removeOrderDetail(${index})" title="Eliminar">
          <i class="fi fi-rr-trash"></i>
        </button>
      </td>
    </tr>
  `).join("");
}

/**
 * Recalcula el total de la orden basándose en los detalles
 */
function recalculateOrderTotal() {
  const total = orderDetails.reduce((sum, detail) => {
    return sum + (detail.quantity * detail.unit_price);
  }, 0);
  
  const totalInput = document.getElementById("order-total");
  if (totalInput) {
    totalInput.value = total.toFixed(2);
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
  orderDetails = []; // Limpiar detalles
  
  clearForm("order-form");
  document.getElementById("order-modal-title").textContent = "Nueva Orden de Compra";
  document.getElementById("order-total").value = "0";
  
  // Limpiar campos de producto
  document.getElementById("product-select").value = "";
  document.getElementById("product-quantity").value = "1";
  document.getElementById("product-unit-price").value = "0";
  document.getElementById("product-line-total").value = "0";
  
  renderOrderDetails();
  openModal("order-modal");
}

async function openEdit(row) {
  isEditing = true;
  currentEditId = row.id;
  orderDetails = []; // Limpiar y cargar detalles existentes
  
  clearForm("order-form");
  
  try {
    // Cargar detalles de la orden
    const res = await apiRequest(`${API}/purchase-orders/${row.id}`);
    const order = res.data;
    
    if (order && order.details) {
      orderDetails = order.details.map(d => ({
        product_id: d.product_id,
        product_name: d.product_name || 'Producto',
        quantity: d.quantity,
        unit_price: parseFloat(d.unit_price)
      }));
    }
  } catch (error) {
    console.error("Error cargando detalles:", error);
  }
  
  fillForm("order-form", {
    supplier_id: row.supplier_id,
    total: row.total,
    status: row.status
  });
  
  // Limpiar campos de producto
  document.getElementById("product-select").value = "";
  document.getElementById("product-quantity").value = "1";
  document.getElementById("product-unit-price").value = "0";
  document.getElementById("product-line-total").value = "0";
  
  renderOrderDetails();
  recalculateOrderTotal();
  
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
          <p><strong>Total:</strong> S/. ${parseFloat(order.total || 0).toFixed(2)}</p>
          <p><strong>Estado:</strong> ${order.status || 'N/A'}</p>
        </div>
        <h4 style="color: white"><strong>Lista de Productos</strong></h4>
        <div class="detail-items">
          ${order.details?.length > 0 ? order.details.map(d => `
            <div class="detail-item">
              <span>${d.product_name}</span>
              <span>${d.quantity} x S/. ${parseFloat(d.unit_price || 0).toFixed(2)}</span>
              <span><strong>S/. ${(d.quantity * (d.unit_price || 0)).toFixed(2)}</strong></span>
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
  
  // Validar que haya al menos un producto
  if (orderDetails.length === 0) {
    showError("Debe agregar al menos un producto a la orden");
    return;
  }
  
  const form = document.getElementById("order-form");
  const formData = new FormData(form);
  
  // Calcular el total desde los detalles
  const calculatedTotal = orderDetails.reduce((sum, d) => sum + (d.quantity * d.unit_price), 0);
  
  const payload = {
    supplier_id: parseInt(formData.get("supplier_id")),
    total: calculatedTotal,
    status: formData.get("status") || "pendiente",
    details: orderDetails.map(d => ({
      product_id: d.product_id,
      quantity: d.quantity,
      unit_price: d.unit_price
    }))
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
  // Botón agregar orden
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

  // Selector de producto - mostrar precio al seleccionar
  const productSelect = document.getElementById("product-select");
  if (productSelect) {
    productSelect.addEventListener("change", onProductSelect);
  }

  // Cantidad - recalcular total de línea
  const quantityInput = document.getElementById("product-quantity");
  if (quantityInput) {
    quantityInput.addEventListener("input", calculateLineTotal);
  }

  // Botón añadir producto
  const btnAddProduct = document.getElementById("btn-add-product");
  if (btnAddProduct) {
    btnAddProduct.addEventListener("click", addProductToOrder);
  }

  // Exponer función para eliminar detalle (usada desde el HTML)
  window.removeOrderDetail = removeProductFromOrder;

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

async function initPurchaseOrdersModule() {
  if (moduleInitialized) {
    await loadOrders();
    return;
  }

  initTable();
  initEvents();
  await loadSuppliers();
  await loadProducts();
  await loadOrders();
  
  moduleInitialized = true;
}

document.getElementById("btn-orders")?.addEventListener("click", () => {
  initPurchaseOrdersModule();
});
