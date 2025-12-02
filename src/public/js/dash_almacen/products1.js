const API = window.location.origin;

async function loadCategoriesAndUnits() {
  const [catRes, unitRes] = await Promise.all([
    fetch(`${API}/category`),
    fetch(`${API}/unit`)
  ]);

  const catObj = await catRes.json();
  const unitObj = await unitRes.json();

  const catSelect = document.getElementById("product-category");
  const unitSelect = document.getElementById("product-unit");

  catSelect.innerHTML = catObj.categories
    .map(c => `<option value="${c.id}">${c.name}</option>`)
    .join("");

  unitSelect.innerHTML = unitObj.units
    .map(u => `<option value="${u.id}">${u.name}</option>`)
    .join("");
}

let table;

function initTable() {
  table = new Tabulator("#products-table", {
    data: [],
    layout: "fitColumns",
    height: "76vh",
    pagination: "local",
    paginationSize: 20,
    placeholder: "Sin productos",
    columns: [
      { title: "ID", field: "id", width: 70 },
      { title: "Nombre", field: "name" },
      { title: "Categoría", field: "category" },
      { title: "Unidad", field: "unit" },
      { title: "Stock", field: "stock", hozAlign: "right" },
      { title: "Venta", field: "sale_price", hozAlign: "right" },
      { title: "Compra", field: "purchase_price", hozAlign: "right" },

      {
        title: "Acciones",
        field: "actions",
        hozAlign: "center",
        formatter: () => `
          <button class="table-btn edit">Editar</button>
          <button class="table-btn delete">Eliminar</button>
        `,
        cellClick: (e, cell) => {
          const row = cell.getRow().getData();

          if (e.target.classList.contains("edit"))
            editProduct(row);

          if (e.target.classList.contains("delete"))
            deleteProduct(row.id);
        }
      }
    ]
  });
}

async function loadProducts() {
  const res = await fetch(`${API}/product`);
  const data = await res.json();
  const products = data.products;

  table.replaceData(products); 
}

document.getElementById("search-input").addEventListener("keyup", function () {
  table.setFilter("name", "like", this.value);
});

const modal = document.getElementById("product-modal");
const btnAdd = document.getElementById("btn-add-product");
const btnCancel = document.getElementById("btn-cancel");
const form = document.getElementById("product-form");

btnAdd.onclick = () => {
  document.getElementById("modal-title").textContent = "Nuevo Producto";
  form.reset();
  document.getElementById("product-id").value = "";
  modal.style.display = "flex";
};

btnCancel.onclick = () => (modal.style.display = "none");

function editProduct(p) {
  modal.style.display = "flex";
  document.getElementById("modal-title").textContent = "Editar Producto";

  document.getElementById("product-id").value = p.id;
  document.getElementById("product-name").value = p.name;
  document.getElementById("product-category").value = p.category_id;
  document.getElementById("product-unit").value = p.unit_id;
  document.getElementById("product-stock").value = p.stock;
  document.getElementById("product-sale").value = p.sale_price;
  document.getElementById("product-purchase").value = p.purchase_price;
}

form.onsubmit = async (e) => {
  e.preventDefault();

  const id = document.getElementById("product-id").value;

  const payload = {
    name: document.getElementById("product-name").value,
    category_id: parseInt(document.getElementById("product-category").value),
    unit_id: parseInt(document.getElementById("product-unit").value),
    stock: parseInt(document.getElementById("product-stock").value),
    sale_price: parseInt(document.getElementById("product-sale").value),
    purchase_price: parseInt(document.getElementById("product-purchase").value),
  };

  const url = id ? `${API}/product/${id}` : `${API}/product`;
  const method = id ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });

  if (!res.ok) return alert("Error al guardar el producto");

  const result = await res.json();
  modal.style.display = "none";

  if (!id) {
    table.addData([result.product], true);
  } else {
    table.updateData([result.product]);
  }
};

async function deleteProduct(id) {
  if (!confirm("¿Eliminar producto?")) return;

  const res = await fetch(`${API}/product/${id}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!res.ok) return alert("Error al eliminar");

  table.deleteRow(id);
}

(async function init() {
  initTable();
  await loadCategoriesAndUnits();
  await loadProducts();
})();
