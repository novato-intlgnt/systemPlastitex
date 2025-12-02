import { TableModule } from "./../tableModule.js";

new TableModule({
  tableId: "#products-table",
  searchInputId: "product-search",
  modalId: "product-modal",
  formId: "product-form",
  btnAddId: "btn-add-product",
  btnCancelId: "btn-cancel-product",
  modalTitleId: "modal-title-product",
  apiBase: `${window.location.origin}/product`,

  columns: [
    { title: "ID", field: "id", width: 70 },
    { title: "Nombre", field: "name" },
    { title: "Categoría", field: "category" },
    { title: "Unidad", field: "unit" },
    { title: "Stock", field: "stock", hozAlign: "right" },
    { title: "Venta", field: "sale_price", hozAlign: "right" },
    { title: "Compra", field: "purchase_price", hozAlign: "right" },
  ],

  mapResponse: (r) => r.products,
});
