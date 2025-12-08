import { TableModule } from "./../tableModule.js";
import { apiRequest } from "./../fetchModule.js";

const API = window.location.origin;

/* ============================================
   CARGA CATEGORÍAS Y UNIDADES
============================================ */
async function loadSelectOptions() {
  try {
    const [catRes, unitRes] = await Promise.all([
      apiRequest(`${API}/category`),
      apiRequest(`${API}/unit`)
    ]);

    const categories = catRes.categories || [];
    const units = unitRes.units || [];

    const catSelect = document.getElementById("product-category");
    const unitSelect = document.getElementById("product-unit");

    if (catSelect) {
      catSelect.innerHTML = `
        <option value="">Seleccione categoría</option>
        ${categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("")}
      `;
    }

    if (unitSelect) {
      unitSelect.innerHTML = `
        <option value="">Seleccione unidad</option>
        ${units.map(u => `<option value="${u.id}">${u.name}</option>`).join("")}
      `;
    }
  } catch (error) {
    console.error("Error cargando opciones:", error);
  }
}

/* ============================================
   INICIALIZAR MÓDULO DE PRODUCTOS
============================================ */
let productsTable = null; // evita instancias duplicadas

function initProductsModule() {
  // refrescar selects
  loadSelectOptions();
  
  // Si ya existe la tabla, solo recargar sus datos
  if (productsTable) {
    productsTable.reload();
    return;
  }

  // Crear tabla por primera vez
  productsTable = new TableModule({
    tableId: "#products-table",
    searchInputId: "product-search",
    modalId: "product-modal",
    formId: "product-form",
    btnAddId: "btn-add-product",
    btnCancelId: "btn-cancel-product",
    modalTitleId: "modal-title-product",
    apiBase: `${API}/product`,

    columns: [
      { title: "ID", field: "id", width: 60, hozAlign: "center" },
      { title: "Nombre", field: "name", minWidth: 150 },
      { title: "Categoría", field: "category", minWidth: 100 },
      { title: "Unidad", field: "unit", width: 90, hozAlign: "center" },

      { 
        title: "Stock", 
        field: "stock", 
        width: 90, 
        hozAlign: "right",
        formatter: (cell) => {
          const value = cell.getValue();
          const color = value < 10 ? "#f05454" : value < 50 ? "#ffc107" : "#28a745";
          return `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
        }
      },

      { 
        title: "P. Venta", 
        field: "sale_price", 
        width: 100, 
        hozAlign: "right",
        formatter: "money",
        formatterParams: { symbol: "$/. ", precision: 2 }
      },

      { 
        title: "P. Compra", 
        field: "purchase_price", 
        width: 100, 
        hozAlign: "right",
        formatter: "money",
        formatterParams: { symbol: "$/. ", precision: 2 }
      },
    ],

    mapResponse: (r) => r.products,

    messages: {
      newTitle: "Nuevo Producto",
      editTitle: "Editar Producto",
      confirmDelete: "¿Está seguro de eliminar este producto?",
      deleteSuccess: "Producto eliminado correctamente",
      saveSuccess: "Producto guardado correctamente",
      loadError: "Error al cargar los productos",
    },
  });
}

/* ============================================
   ACTIVAR CUANDO SE HAGA CLIC EN EL BOTÓN
============================================ */
document.getElementById("btn-products").addEventListener("click", () => {
  initProductsModule();
});
