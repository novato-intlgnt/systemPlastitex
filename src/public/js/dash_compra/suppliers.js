import { TableModule } from "./../tableModule.js";

let supplierTable = null;

function initSupplierModule() {
  if (supplierTable){
    supplierTable.loadData();
    return;
  }

  const API = window.env?.API_URL || window.location.origin;
  new TableModule({
    tableId: "#supplier-table",
    searchInputId: "supplier-search",
    modalId: "supplier-modal",
    formId: "supplier-form",
    btnAddId: "btn-add-supplier",
    btnCancelId: "btn-cancel",
    modalTitleId: "modal-title",
    // apiBase: `${API}/supplier`,
    apiBase: `/supplier`,

    columns: [
      { title: "ID", field: "id", width: 70 },
      { title: "Nombre", field: "name" },
      { title: "Dirección", field: "address" },
      { title: "Teléfono", field: "phone", hozAlign: "right" },
    ],

    mapResponse: (r) => r.suppliers,
  });

}


document.getElementById("btn-suppliers")?.addEventListener("click", () => {
  initSupplierModule();
});

document.addEventListener("DOMContentLoaded", () => {
  initSupplierModule();
});
