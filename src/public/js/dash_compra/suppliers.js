import { TableModule } from "./../tableModule.js";

new TableModule({
  tableId: "#supplier-table",
  searchInputId: "supplier-search",
  modalId: "supplier-modal",
  formId: "supplier-form",
  btnAddId: "btn-add-supplier",
  apiBase: `${window.location.origin}/supplier`,

  columns: [
    { title: "ID", field: "id", width: 70 },
    { title: "Nombre", field: "name" },
    { title: "Dirección", field: "address" },
    { title: "Telefono", field: "phone", hozAlign: "right" },
  ],

  mapResponse: (r) => r.suppliers,
});
