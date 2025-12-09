import { TableModule } from "./../tableModule.js";

/**
 * Módulo de clientes (CRUD)
 * Para el rol aux_almacen
 * Implementa carga perezosa (lazy loading)
 */

let clientsTable = null;

function initClientsModule() {
  // Si ya existe la tabla, solo recargar sus datos
  if (clientsTable) {
    clientsTable.reload();
    return;
  }

  // Crear tabla por primera vez
  clientsTable = new TableModule({
    tableId: "#clients-table",
    searchInputId: "client-search",
    modalId: "client-modal",
    formId: "client-form",
    btnAddId: "btn-add-client",
    btnCancelId: "btn-cancel-client",
    modalTitleId: "modal-title-client",
    apiBase: `${window.location.origin}/clients`,

    columns: [
      { title: "ID", field: "id", width: 70, hozAlign: "center" },
      { title: "Nombre", field: "name", minWidth: 150 },
      { title: "Teléfono", field: "phone", width: 120 },
      { title: "Dirección", field: "address", minWidth: 150 },
    ],

    mapResponse: (r) => r.data || [],

    messages: {
      newTitle: "Nuevo Cliente",
      editTitle: "Editar Cliente",
      confirmDelete: "¿Está seguro de eliminar este cliente?",
      deleteSuccess: "Cliente eliminado correctamente",
      saveSuccess: "Cliente guardado correctamente",
      loadError: "Error al cargar los clientes",
    },
  });
}

/* ============================================
   ACTIVAR CUANDO SE HAGA CLIC EN EL BOTÓN
============================================ */
document.getElementById("btn-clients")?.addEventListener("click", () => {
  initClientsModule();
});
