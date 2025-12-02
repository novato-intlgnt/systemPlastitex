import { apiRequest } from "./fetchModule.js";
import { openModal, closeModal, fillForm, clearForm } from "./modalModule.js";

export class TableModule {
  constructor({
    tableId,
    searchInputId,
    modalId,
    formId,
    btnAddId,
    apiBase,
    columns,
    mapResponse
  }) {
    this.tableId = tableId;
    this.searchInputId = searchInputId;
    this.modalId = modalId;
    this.formId = formId;
    this.btnAddId = btnAddId;
    this.apiBase = apiBase;
    this.columns = columns;
    this.mapResponse = mapResponse;

    this.table = null;

    this.init();
  }

  async init() {
    this.initTable();
    await this.loadData();
    this.initEvents();
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
          formatter: () => `
            <button class="table-btn edit"><i class="fi fi-rr-edit"></i></button>
            <button class="table-btn delete"><i class="fi fi-rr-trash"></i></button>
          `,
          cellClick: (e, cell) => {
            const row = cell.getRow().getData();

            if (e.target.classList.contains("edit")) this.openEdit(row);
            if (e.target.classList.contains("delete")) this.delete(row.id);
          },
        }
      ],
    });
  }

  async loadData() {
    const res = await apiRequest(this.apiBase);
    const items = this.mapResponse(res); 
    this.table.replaceData(items);
  }

  initEvents() {
    document.getElementById(this.searchInputId).addEventListener("keyup", (e) => {
      this.table.setFilter("name", "like", e.target.value);
    });

    document.getElementById(this.btnAddId).onclick = () => this.openCreate();

    document.getElementById(this.formId).onsubmit = (e) => this.submit(e);
  }

  openCreate() {
    clearForm(this.formId);
    document.getElementById("modal-title").textContent = "Nuevo Registro";
    openModal(this.modalId);
  }

  openEdit(row) {
    fillForm(this.formId, row);
    document.getElementById("modal-title").textContent = "Editar Registro";
    openModal(this.modalId);
  }

  async submit(e) {
    e.preventDefault();
    const form = document.getElementById(this.formId);

    const payload = Object.fromEntries(new FormData(form));
    const id = payload.id;

    const res = id
      ? await apiRequest(`${this.apiBase}/${id}`, "PUT", payload)
      : await apiRequest(this.apiBase, "POST", payload);

    // Backend devuelve `item`
    const item = res.item;

    if (!id) this.table.addData([item], true);
    else this.table.updateData([item]);

    closeModal(this.modalId);
  }

  async delete(id) {
    if (!confirm("¿Eliminar?")) return;

    await apiRequest(`${this.apiBase}/${id}`, "DELETE");
    this.table.deleteRow(id);
  }
}
