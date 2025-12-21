import { apiRequest } from "./../fetchModule.js";
import {
  openModal,
  closeModal,
  clearForm,
  setupModalBackdropClose,
  setupCancelButton,
  setupEscapeClose,
} from "./../modalModule.js";

const API = window.env?.API_URL || window.location.origin;
let notesTable = null;
let itemsTable = null;
let currentNoteId = null;
let moduleInitialized = false;

// ============================================================================
// TABLA DE NOTAS DE SALIDA
// ============================================================================

function initNotesTable() {
  notesTable = new Tabulator("#exit-notes-table", {
    data: [],
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 10,
    height: "45vh",
    placeholder: "No hay notas de salida",
    selectableRows: 1,
    columns: [
      { title: "ID", field: "id", width: 60, hozAlign: "center" },
      { 
        title: "Fecha", 
        field: "date", 
        width: 110,
        formatter: (cell) => {
          const date = new Date(cell.getValue());
          return date.toLocaleDateString("es-BO");
        }
      },
      { title: "Cliente", field: "customer_name", minWidth: 150 },
      { 
        title: "Total", 
        field: "total", 
        width: 110, 
        hozAlign: "right",
        formatter: "money",
        formatterParams: { symbol: "$/. ", precision: 2 }
      },
      { title: "Referencia", field: "reference", width: 120 },
      { title: "Items", field: "items_count", width: 70, hozAlign: "center" },
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
          else if (btn.classList.contains("view")) selectNote(row);
          else if (btn.classList.contains("delete")) deleteOrder(row.id);
        },
      },
    ],
  });
}

// ============================================================================
// TABLA DE ITEMS DE LA NOTA SELECCIONADA
// ============================================================================

function initItemsTable() {
  itemsTable = new Tabulator("#exit-items-table", {
    data: [],
    layout: "fitColumns",
    height: "25vh",
    placeholder: "Seleccione una nota para ver sus items",
    columns: [
      { title: "ID", field: "id", width: 60, hozAlign: "center" },
      { title: "Producto", field: "product_name", minWidth: 150 },
      { title: "Cantidad", field: "quantity", width: 100, hozAlign: "right" },
      {
        title: "Acciones",
        hozAlign: "center",
        headerSort: false,
        width: 100,
        formatter: () => `
          <button class="table-btn edit" title="Editar">
            <i class="fi fi-rr-edit"></i>
          </button>
          <button class="table-btn delete" title="Eliminar">
            <i class="fi fi-rr-trash"></i>
          </button>
        `,
        cellClick: (e, cell) => {
          const row = cell.getRow().getData();
          const btn = e.target.closest(".table-btn");
          if (!btn) return;

          if (btn.classList.contains("edit")) openEditItem(row);
          else if (btn.classList.contains("delete")) deleteItem(row.id);
        },
      },
    ],
  });
}

// ============================================================================
// CARGAR DATOS
// ============================================================================

async function loadClients() {
  try {
    const res = await apiRequest(`${API}/clients/`);
    const clients = res.data || [];
    const select = document.getElementById("exit-customer");
    if (select) {
      select.innerHTML = '<option value="">Seleccione cliente</option>' +
        clients.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando clientes:", error);
  }
}

async function loadProducts() {
  try {
    const res = await apiRequest(`${API}/product/`);
    const products = res.products || [];
    const select = document.getElementById("exit-item-product");
    if (select) {
      select.innerHTML = '<option value="">Seleccione producto</option>' +
        products.map(p => `<option value="${p.id}" data-stock="${p.stock}">${p.name} (Stock: ${p.stock})</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando productos:", error);
  }
}

async function loadNotes() {
  try {
    const res = await apiRequest(`${API}/warehouse/outbound/`);
    const notes = res.data || [];
    notesTable.replaceData(notes);
  } catch (error) {
    console.error("Error cargando notas:", error);
    showError("No se pudieron cargar las notas de salida");
  }
}

async function selectNote(note) {
  currentNoteId = note.id;
  document.getElementById("selected-exit-note-info").textContent = 
    `Nota #${note.id} - ${note.customer_name}`;
  document.getElementById("btn-add-exit-item").disabled = false;
  
  try {
    const res = await apiRequest(`${API}/warehouse/outbound/${note.id}`);
    const items = res.data?.details || [];
    itemsTable.replaceData(items);
  } catch (error) {
    console.error("Error cargando items:", error);
    showError("No se pudieron cargar los items de la nota");
  }
}

// ============================================================================
// OPERACIONES CRUD - NOTAS
// ============================================================================

function openCreateNote() {
  clearForm("exit-note-form");
  document.getElementById("exit-note-modal-title").textContent = "Nueva Nota de Salida";
  openModal("exit-note-modal");
}

async function submitNote(e) {
  e.preventDefault();
  
  const form = document.getElementById("exit-note-form");
  const formData = new FormData(form);
  const payload = {
    customer_id: parseInt(formData.get("customer_id")),
    total: parseFloat(formData.get("total")) || 0,
    reference: formData.get("reference") || ""
  };

  try {
    await apiRequest(`${API}/warehouse/outbound`, "POST", payload);
    await loadNotes();
    closeModal("exit-note-modal");
    showSuccess("Nota de salida creada correctamente");
  } catch (error) {
    console.error("Error creando nota:", error);
    showError(error.message || "Error al crear la nota");
  }
}

async function deleteNote(noteId) {
  showError("La eliminación de notas completas no está implementada");
}

// ============================================================================
// OPERACIONES CRUD - ITEMS
// ============================================================================

let editingItemId = null;

function openAddItem() {
  if (!currentNoteId) {
    showError("Primero seleccione una nota de salida");
    return;
  }
  editingItemId = null;
  clearForm("exit-item-form");
  document.getElementById("exit-item-modal-title").textContent = "Agregar Producto";
  openModal("exit-item-modal");
}

function openEditItem(item) {
  editingItemId = item.id;
  document.getElementById("exit-item-product").value = item.product_id;
  document.getElementById("exit-item-quantity").value = item.quantity;
  document.getElementById("exit-item-modal-title").textContent = "Editar Producto";
  openModal("exit-item-modal");
}

async function validateStock() {
  const productId = document.getElementById("exit-item-product").value;
  const quantity = parseInt(document.getElementById("exit-item-quantity").value) || 0;
  
  if (!productId || quantity <= 0) return true;
  
  try {
    const res = await apiRequest(`${API}/warehouse/outbound/validate-stock?product_id=${productId}&quantity=${quantity}`);
    if (!res.is_valid) {
      showError(`Stock insuficiente. Stock actual: ${res.current_stock}`);
      return false;
    }
    return true;
  } catch (error) {
    console.error("Error validando stock:", error);
    return false;
  }
}

async function submitItem(e) {
  e.preventDefault();
  
  const form = document.getElementById("exit-item-form");
  const formData = new FormData(form);
  const payload = {
    product_id: parseInt(formData.get("product_id")),
    quantity: parseInt(formData.get("quantity"))
  };

  if (!editingItemId) {
    const isValid = await validateStock();
    if (!isValid) return;
  }

  try {
    if (editingItemId) {
      await apiRequest(`${API}/warehouse/outbound/${currentNoteId}/items/${editingItemId}`, "PUT", payload);
    } else {
      await apiRequest(`${API}/warehouse/outbound/${currentNoteId}/items`, "POST", payload);
    }
    
    // Recargar items y productos (stock actualizado)
    const noteInfo = document.getElementById("selected-exit-note-info").textContent;
    await selectNote({ id: currentNoteId, customer_name: noteInfo.split(" - ")[1] });
    await loadProducts();
    closeModal("exit-item-modal");
    showSuccess("Producto guardado correctamente");
  } catch (error) {
    console.error("Error guardando item:", error);
    showError(error.message || "Error al guardar el producto");
  }
}

async function deleteItem(itemId) {
  const confirmed = await confirmDelete("¿Eliminar este producto de la nota? El stock se revertirá.");
  if (!confirmed) return;

  try {
    await apiRequest(`${API}/notas-salida/${currentNoteId}/items/${itemId}`, "DELETE");
    itemsTable.deleteRow(itemId);
    await loadProducts(); // Actualizar stock
    showSuccess("Producto eliminado de la nota");
  } catch (error) {
    console.error("Error eliminando item:", error);
    showError(error.message || "Error al eliminar el producto");
  }
}

// ============================================================================
// UTILIDADES
// ============================================================================

async function confirmDelete(message) {
  if (typeof Swal !== "undefined") {
    const result = await Swal.fire({
      title: "¿Confirmar eliminación?",
      text: message,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    });
    return result.isConfirmed;
  }
  return confirm(message);
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

// ============================================================================
// EVENTOS
// ============================================================================

function initEvents() {
  // Nota - botón agregar
  const btnAddNote = document.getElementById("btn-add-exit-note");
  if (btnAddNote) btnAddNote.addEventListener("click", openCreateNote);

  // Nota - submit form
  const noteForm = document.getElementById("exit-note-form");
  if (noteForm) noteForm.addEventListener("submit", submitNote);

  // Item - botón agregar
  const btnAddItem = document.getElementById("btn-add-exit-item");
  if (btnAddItem) btnAddItem.addEventListener("click", openAddItem);

  // Item - submit form
  const itemForm = document.getElementById("exit-item-form");
  if (itemForm) itemForm.addEventListener("submit", submitItem);

  // Modales
  setupCancelButton("btn-cancel-exit-note", "exit-note-modal");
  setupModalBackdropClose("exit-note-modal");
  setupEscapeClose("exit-note-modal");

  setupCancelButton("btn-cancel-exit-item", "exit-item-modal");
  setupModalBackdropClose("exit-item-modal");
  setupEscapeClose("exit-item-modal");
}

async function initExitNotesModule() {
  if (moduleInitialized) {
    await loadNotes();
    return;
  }

  initNotesTable();
  initItemsTable();
  initEvents();
  await loadClients();
  await loadProducts();
  await loadNotes();
  
  moduleInitialized = true;
}

document.getElementById("btn-exit-note")?.addEventListener("click", () => {
  initExitNotesModule();
});
