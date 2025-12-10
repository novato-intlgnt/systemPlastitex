import { apiRequest } from "./../fetchModule.js";
import {
  openModal,
  closeModal,
  clearForm,
  setupModalBackdropClose,
  setupCancelButton,
  setupEscapeClose,
} from "./../modalModule.js";

/**
 * Módulo de Notas de Ingreso (Warehouse Inbound)
 * Para el rol aux_almacen
 */

const API = window.location.origin;
let notesTable;
let itemsTable;
let currentNoteId = null;

// ============================================================================
// TABLA DE NOTAS DE INGRESO
// ============================================================================

function initNotesTable() {
  notesTable = new Tabulator("#entry-notes-table", {
    data: [],
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 10,
    height: "45vh",
    placeholder: "No hay notas de ingreso",
    rowClick: (e, row) => selectNote(row.getData()),
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
      { title: "Proveedor", field: "supplier_name", minWidth: 150 },
      { title: "Referencia", field: "reference", width: 120 },
      { title: "Items", field: "items_count", width: 70, hozAlign: "center" },
      {
        title: "Acciones",
        hozAlign: "center",
        headerSort: false,
        width: 100,
        formatter: () => `
          <button class="table-btn delete" title="Eliminar">
            <i class="fi fi-rr-trash"></i>
          </button>
        `,
        cellClick: (e, cell) => {
          e.stopPropagation();
          const btn = e.target.closest(".table-btn");
          if (btn?.classList.contains("delete")) {
            deleteNote(cell.getRow().getData().id);
          }
        },
      },
    ],
  });
}

// ============================================================================
// TABLA DE ITEMS DE LA NOTA SELECCIONADA
// ============================================================================

function initItemsTable() {
  itemsTable = new Tabulator("#entry-items-table", {
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

async function loadSuppliers() {
  try {
    const res = await apiRequest(`${API}/supplier`);
    const suppliers = res.suppliers || [];
    const select = document.getElementById("entry-supplier");
    if (select) {
      select.innerHTML = '<option value="">Seleccione proveedor</option>' +
        suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando proveedores:", error);
  }
}

async function loadProducts() {
  try {
    const res = await apiRequest(`${API}/product`);
    const products = res.products || [];
    const select = document.getElementById("item-product");
    if (select) {
      select.innerHTML = '<option value="">Seleccione producto</option>' +
        products.map(p => `<option value="${p.id}">${p.name} (Stock: ${p.stock})</option>`).join("");
    }
  } catch (error) {
    console.error("Error cargando productos:", error);
  }
}

async function loadNotes() {
  try {
    const res = await apiRequest(`${API}/warehouse/inbound`);
    const notes = res.data || [];
    notesTable.replaceData(notes);
  } catch (error) {
    console.error("Error cargando notas:", error);
    showError("No se pudieron cargar las notas de ingreso");
  }
}

async function selectNote(note) {
  currentNoteId = note.id;
  document.getElementById("selected-note-info").textContent = 
    `Nota #${note.id} - ${note.supplier_name}`;
  document.getElementById("btn-add-item").disabled = false;
  
  try {
    const res = await apiRequest(`${API}/warehouse/inbound/${note.id}`);
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
  clearForm("entry-note-form");
  document.getElementById("entry-note-modal-title").textContent = "Nueva Nota de Ingreso";
  openModal("entry-note-modal");
}

async function submitNote(e) {
  e.preventDefault();
  
  const form = document.getElementById("entry-note-form");
  const formData = new FormData(form);
  const payload = {
    supplier_id: parseInt(formData.get("supplier_id")),
    reference: formData.get("reference") || ""
  };

  try {
    await apiRequest(`${API}/warehouse/inbound`, "POST", payload);
    await loadNotes();
    closeModal("entry-note-modal");
    showSuccess("Nota de ingreso creada correctamente");
  } catch (error) {
    console.error("Error creando nota:", error);
    showError(error.message || "Error al crear la nota");
  }
}

async function deleteNote(noteId) {
  // Por ahora solo mostramos mensaje ya que el endpoint no existe
  showError("La eliminación de notas completas no está implementada");
}

// ============================================================================
// OPERACIONES CRUD - ITEMS
// ============================================================================

let editingItemId = null;

function openAddItem() {
  if (!currentNoteId) {
    showError("Primero seleccione una nota de ingreso");
    return;
  }
  editingItemId = null;
  clearForm("entry-item-form");
  document.getElementById("entry-item-modal-title").textContent = "Agregar Producto";
  openModal("entry-item-modal");
}

function openEditItem(item) {
  editingItemId = item.id;
  document.getElementById("item-product").value = item.product_id;
  document.getElementById("item-quantity").value = item.quantity;
  document.getElementById("entry-item-modal-title").textContent = "Editar Producto";
  openModal("entry-item-modal");
}

async function submitItem(e) {
  e.preventDefault();
  
  const form = document.getElementById("entry-item-form");
  const formData = new FormData(form);
  const payload = {
    product_id: parseInt(formData.get("product_id")),
    quantity: parseInt(formData.get("quantity"))
  };

  try {
    if (editingItemId) {
      await apiRequest(`${API}/warehouse/inbound/${currentNoteId}/items/${editingItemId}`, "PUT", payload);
    } else {
      await apiRequest(`${API}/warehouse/inbound/${currentNoteId}/items`, "POST", payload);
    }
    
    // Recargar items y productos (stock actualizado)
    await selectNote({ id: currentNoteId, supplier_name: document.getElementById("selected-note-info").textContent.split(" - ")[1] });
    await loadProducts();
    closeModal("entry-item-modal");
    showSuccess("Producto guardado correctamente");
  } catch (error) {
    console.error("Error guardando item:", error);
    showError(error.message || "Error al guardar el producto");
  }
}

async function deleteItem(itemId) {
  const confirmed = await confirmDelete("¿Eliminar este producto de la nota?");
  if (!confirmed) return;

  try {
    await apiRequest(`${API}/warehouse/inbound/${currentNoteId}/items/${itemId}`, "DELETE");
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
  const btnAddNote = document.getElementById("btn-add-entry-note");
  if (btnAddNote) btnAddNote.addEventListener("click", openCreateNote);

  // Nota - submit form
  const noteForm = document.getElementById("entry-note-form");
  if (noteForm) noteForm.addEventListener("submit", submitNote);

  // Item - botón agregar
  const btnAddItem = document.getElementById("btn-add-item");
  if (btnAddItem) btnAddItem.addEventListener("click", openAddItem);

  // Item - submit form
  const itemForm = document.getElementById("entry-item-form");
  if (itemForm) itemForm.addEventListener("submit", submitItem);

  // Modales
  setupCancelButton("btn-cancel-entry-note", "entry-note-modal");
  setupModalBackdropClose("entry-note-modal");
  setupEscapeClose("entry-note-modal");

  setupCancelButton("btn-cancel-entry-item", "entry-item-modal");
  setupModalBackdropClose("entry-item-modal");
  setupEscapeClose("entry-item-modal");
}

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

(async function init() {
  initNotesTable();
  initItemsTable();
  initEvents();
  await loadSuppliers();
  await loadProducts();
  await loadNotes();
})();