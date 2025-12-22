import { apiRequest } from "./fetchModule.js";import {
  openModal,
  closeModal,
  fillForm,
  clearForm,
  setupModalBackdropClose,
  setupCancelButton,
  setupEscapeClose,
} from "./modalModule.js";

/**
 * Módulo de tabla reutilizable para operaciones CRUD
 * Utiliza Tabulator para renderizar la tabla
 */
export class TableModule {
  constructor({
    tableId,
    searchInputId,
    modalId,
    formId,
    btnAddId,
    btnCancelId = "btn-cancel", // ID del botón cancelar (default: btn-cancel)
    modalTitleId = "modal-title", // ID del título del modal
    apiBase,
    columns,
    mapResponse,
    messages = {}, // Mensajes personalizables
  }) {
    this.tableId = tableId;
    this.searchInputId = searchInputId;
    this.modalId = modalId;
    this.formId = formId;
    this.btnAddId = btnAddId;
    this.btnCancelId = btnCancelId;
    this.modalTitleId = modalTitleId;
    this.apiBase = apiBase;
    this.columns = columns;
    this.mapResponse = mapResponse;

    // Mensajes por defecto
    this.messages = {
      newTitle: "Nuevo Registro",
      editTitle: "Editar Registro",
      confirmDelete: "¿Está seguro de eliminar este registro?",
      deleteSuccess: "Registro eliminado correctamente",
      saveSuccess: "Registro guardado correctamente",
      loadError: "Error al cargar los datos",
      ...messages,
    };

    this.table = null;
    this.isEditing = false;
    this.currentEditId = null;

    this.init();
  }

  async init() {
    this.initTable();
    await this.loadData();
    this.initEvents();
    this.initModalEvents();
  }

  initTable() {
    this.table = new Tabulator(this.tableId, {
      data: [],
      layout: "fitColumns",
      pagination: "local",
      paginationSize: 20,
      height: "76vh",
      placeholder: "No hay datos",
      columns: [
        ...this.columns,
        {
          title: "Acciones",
          hozAlign: "center",
          headerSort: false,
          width: 120,
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
            const target = e.target;

            // Buscar el botón padre si se hizo clic en el icono
            const btn = target.closest(".table-btn");
            if (!btn) return;

            if (btn.classList.contains("edit")) {
              this.openEdit(row);
            } else if (btn.classList.contains("delete")) {
              this.delete(row.id);
            }
          },
        },
      ],
    });
  }

  async loadData() {
    try {
      const res = await apiRequest(`${this.apiBase}/`);
      const items = this.mapResponse(res);
      this.table.replaceData(items);
    } catch (error) {
      console.error("Error loading data:", error);
      this.showError(this.messages.loadError);
    }
  }

  initEvents() {
    // Búsqueda
    const searchInput = document.getElementById(this.searchInputId);
    if (searchInput) {
      searchInput.addEventListener("keyup", (e) => {
        this.table.setFilter("name", "like", e.target.value);
      });
    }

    // Botón agregar
    const btnAdd = document.getElementById(this.btnAddId);
    if (btnAdd) {
      btnAdd.addEventListener("click", () => this.openCreate());
    }

    // Submit del formulario
    const form = document.getElementById(this.formId);
    if (form) {
      form.addEventListener("submit", (e) => this.submit(e));
    }
  }

  initModalEvents() {
    // Botón cancelar
    setupCancelButton(this.btnCancelId, this.modalId);

    // Cerrar al hacer clic fuera
    setupModalBackdropClose(this.modalId);

    // Cerrar con Escape
    setupEscapeClose(this.modalId);
  }

  openCreate() {
    this.isEditing = false;
    this.currentEditId = null;
    clearForm(this.formId);

    const titleEl = document.getElementById(this.modalTitleId);
    if (titleEl) {
      titleEl.textContent = this.messages.newTitle;
    }

    openModal(this.modalId);
  }

  openEdit(row) {
    this.isEditing = true;
    this.currentEditId = row.id;

    clearForm(this.formId);
    fillForm(this.formId, row);

    const titleEl = document.getElementById(this.modalTitleId);
    if (titleEl) {
      titleEl.textContent = this.messages.editTitle;
    }

    openModal(this.modalId);
  }

  async submit(e) {
    e.preventDefault();

    const form = document.getElementById(this.formId);
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData);

    // Usar el ID almacenado para determinar si es edición
    const id = this.currentEditId || payload.id;

    try {
      let res;
      if (id) {
        // Actualizar
        res = await apiRequest(`${this.apiBase}/${id}`, "PUT", payload);
      } else {
        // Crear
        res = await apiRequest(`${this.apiBase}/`, "POST", payload);
      }

      // Recargar datos para asegurar consistencia
      await this.loadData();

      closeModal(this.modalId);
      this.showSuccess(this.messages.saveSuccess);
    } catch (error) {
      console.error("Error saving:", error);
      this.showError(error.message || "Error al guardar");
    }
  }

  async delete(id) {
    // Usar SweetAlert2 si está disponible, sino confirm nativo
    const confirmed = await this.confirmDelete();
    if (!confirmed) return;

    try {
      await apiRequest(`${this.apiBase}/${id}`, "DELETE");
      this.table.deleteRow(id);
      this.showSuccess(this.messages.deleteSuccess);
    } catch (error) {
      console.error("Error deleting:", error);
      this.showError(error.message || "Error al eliminar");
    }
  }

  async confirmDelete() {
    if (typeof Swal !== "undefined") {
      const result = await Swal.fire({
        title: "¿Confirmar eliminación?",
        text: this.messages.confirmDelete,
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
      });
      return result.isConfirmed;
    }
    return confirm(this.messages.confirmDelete);
  }

  showSuccess(message) {
    if (typeof Swal !== "undefined") {
      Swal.fire({
        icon: "success",
        title: "Éxito",
        text: message,
        timer: 2000,
        showConfirmButton: false,
      });
    } else {
      console.log("Success:", message);
    }
  }

  showError(message) {
    if (typeof Swal !== "undefined") {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: message,
      });
    } else {
      alert(message);
    }
  }
}
