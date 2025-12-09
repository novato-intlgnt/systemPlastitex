import { apiRequest, TableModule } from "../fetchModule.js";

// ============================================================
// MÓDULO: PROVEEDORES (CRUD)
// ============================================================

let suppliersTable = null;
let moduleInitialized = false;

// Inicialización del módulo (lazy loading)
async function initSuppliersModule() {
  console.log("[Suppliers] Inicializando módulo...");

  if (moduleInitialized) {
    console.log("[Suppliers] Módulo ya inicializado, recargando datos...");
    if (suppliersTable) {
      suppliersTable.reload();
    }
    return;
  }

  // Crear tabla
  suppliersTable = new TableModule({
    tableId: "#supplier-table",
    endpoint: "/supplier",
    responseKey: "suppliers",
    searchInputId: "#supplier-search",
    columns: [
      { title: "ID", field: "id", width: 60 },
      { title: "Nombre", field: "name", widthGrow: 2 },
      { title: "Teléfono", field: "phone", widthGrow: 1 },
      { title: "Dirección", field: "address", widthGrow: 2 },
      {
        title: "Acciones",
        field: "actions",
        width: 120,
        hozAlign: "center",
        formatter: () =>
          `<button class="btn-icon btn-edit"><i class="fi fi-rr-edit"></i></button>
           <button class="btn-icon btn-delete"><i class="fi fi-rr-trash"></i></button>`,
        cellClick: handleTableActions,
      },
    ],
  });

  // Configurar eventos del formulario
  initFormEvents();

  moduleInitialized = true;
  console.log("[Suppliers] Módulo inicializado correctamente");
}

// Manejador de acciones de la tabla
function handleTableActions(e, cell) {
  const row = cell.getRow().getData();
  const target = e.target.closest("button");
  if (!target) return;

  if (target.classList.contains("btn-edit")) {
    openEditModal(row);
  } else if (target.classList.contains("btn-delete")) {
    deleteSupplier(row.id);
  }
}

// Abrir modal para editar
function openEditModal(data) {
  document.getElementById("modal-title").textContent = "Editar Proveedor";
  document.getElementById("supplier-id").value = data.id;
  document.getElementById("supplier-name").value = data.name;
  document.getElementById("supplier-phone").value = data.phone;
  document.getElementById("supplier-address").value = data.address;
  document.getElementById("supplier-modal").style.display = "flex";
}

// Abrir modal para nuevo
function openNewModal() {
  document.getElementById("modal-title").textContent = "Nuevo Proveedor";
  document.getElementById("supplier-form").reset();
  document.getElementById("supplier-id").value = "";
  document.getElementById("supplier-modal").style.display = "flex";
}

// Cerrar modal
function closeModal() {
  document.getElementById("supplier-modal").style.display = "none";
}

// Eliminar proveedor
async function deleteSupplier(id) {
  const result = await Swal.fire({
    title: "¿Eliminar proveedor?",
    text: "Esta acción no se puede deshacer",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#e74c3c",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  });

  if (result.isConfirmed) {
    const res = await apiRequest(`/supplier/${id}`, "DELETE");
    if (res) {
      Swal.fire("Eliminado", "El proveedor ha sido eliminado", "success");
      suppliersTable.reload();
    }
  }
}

// Guardar proveedor (crear o actualizar)
async function saveSupplier(e) {
  e.preventDefault();
  const form = e.target;
  const id = form.id.value;
  const data = {
    name: form.name.value,
    phone: form.phone.value,
    address: form.address.value,
  };

  let res;
  if (id) {
    res = await apiRequest(`/supplier/${id}`, "PUT", data);
  } else {
    res = await apiRequest("/supplier", "POST", data);
  }

  if (res) {
    Swal.fire("Guardado", "El proveedor ha sido guardado", "success");
    closeModal();
    suppliersTable.reload();
  }
}

// Inicializar eventos del formulario
function initFormEvents() {
  // Botón nuevo proveedor
  document.getElementById("btn-add-supplier")?.addEventListener("click", openNewModal);

  // Botón cancelar
  document.getElementById("btn-cancel")?.addEventListener("click", closeModal);

  // Formulario submit
  document.getElementById("supplier-form")?.addEventListener("submit", saveSupplier);
}

// ============================================================
// EVENT LISTENERS - Lazy Loading
// ============================================================

// Cargar cuando se hace clic en el botón del sidebar
document.getElementById("btn-suppliers")?.addEventListener("click", () => {
  initSuppliersModule();
});

// AUTO-CARGAR: Esta es la primera sección visible, cargar automáticamente
document.addEventListener("DOMContentLoaded", () => {
  // Esperar un momento para que Tabulator esté disponible
  setTimeout(() => {
    // Verificar si la sección de proveedores es visible (primera sección)
    const supplierSection = document.getElementById("supplier-section");
    if (supplierSection) {
      console.log("[Suppliers] Cargando módulo inicial automáticamente...");
      initSuppliersModule();
    }
  }, 100);
});
