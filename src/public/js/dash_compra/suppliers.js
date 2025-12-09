import { TableModule } from "./../tableModule.js";

/**
 * Módulo de proveedores (CRUD)
 * Para el rol aux_compra
 * Implementa carga perezosa (lazy loading)
 */

let suppliersTable = null;

function initSuppliersModule() {
  // Si ya existe la tabla, solo recargar sus datos
  if (suppliersTable) {
    suppliersTable.reload();
    return;
  }

  // Crear tabla por primera vez
  suppliersTable = new TableModule({
    tableId: "#supplier-table",
    searchInputId: "supplier-search",
    modalId: "supplier-modal",
    formId: "supplier-form",
    btnAddId: "btn-add-supplier",
    btnCancelId: "btn-cancel",
    modalTitleId: "modal-title",
    apiBase: `${window.location.origin}/supplier`,

    columns: [
      { title: "ID", field: "id", width: 70 },
      { title: "Nombre", field: "name" },
      { title: "Dirección", field: "address" },
      { title: "Teléfono", field: "phone", hozAlign: "right" },
    ],

    mapResponse: (r) => r.suppliers,

    messages: {
      newTitle: "Nuevo Proveedor",
      editTitle: "Editar Proveedor",
      confirmDelete: "¿Está seguro de eliminar este proveedor?",
      deleteSuccess: "Proveedor eliminado correctamente",
      saveSuccess: "Proveedor guardado correctamente",
      loadError: "Error al cargar los proveedores",
    },
  });
}

/* ============================================
   ACTIVAR CUANDO SE HAGA CLIC EN EL BOTÓN
============================================ */
document.getElementById("btn-suppliers")?.addEventListener("click", () => {
  initSuppliersModule();
});

// Cargar automáticamente si es la primera sección visible
if (window.location.hash === "" || window.location.hash === "#supplier-section") {
  initSuppliersModule();
}
