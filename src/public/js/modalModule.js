/**
 * Módulo de gestión de modales
 * Proporciona funciones para abrir, cerrar y manejar formularios en modales
 */

export function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "flex";
    // Agregar clase para animación si existe
    modal.classList.add("active");
  }
}

export function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "none";
    modal.classList.remove("active");
  }
}

/**
 * Cierra el modal al hacer clic fuera del contenido
 * @param {string} modalId - ID del modal
 */
export function setupModalBackdropClose(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.addEventListener("click", (e) => {
      // Solo cerrar si se hace clic directamente en el backdrop (modal), no en el contenido
      if (e.target === modal) {
        closeModal(modalId);
      }
    });
  }
}

/**
 * Configura el botón de cancelar para cerrar el modal
 * @param {string} btnCancelId - ID del botón cancelar
 * @param {string} modalId - ID del modal
 */
export function setupCancelButton(btnCancelId, modalId) {
  const btnCancel = document.getElementById(btnCancelId);
  if (btnCancel) {
    btnCancel.addEventListener("click", () => closeModal(modalId));
  }
}

/**
 * Configura cerrar modal con tecla Escape
 * @param {string} modalId - ID del modal
 */
export function setupEscapeClose(modalId) {
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const modal = document.getElementById(modalId);
      if (modal && modal.style.display === "flex") {
        closeModal(modalId);
      }
    }
  });
}

/**
 * Llena un formulario con datos
 * @param {string} formId - ID del formulario
 * @param {object} data - Datos a llenar (las claves deben coincidir con el atributo 'name' de los inputs)
 */
export function fillForm(formId, data) {
  const form = document.getElementById(formId);
  if (!form) return;

  for (const key in data) {
    // Buscar por name attribute
    const input = form.querySelector(`[name="${key}"]`);
    if (input) {
      input.value = data[key] ?? "";
    }
  }
}

/**
 * Limpia/resetea un formulario
 * @param {string} formId - ID del formulario
 */
export function clearForm(formId) {
  const form = document.getElementById(formId);
  if (form) {
    form.reset();
    // También limpiar campos hidden
    const hiddenInputs = form.querySelectorAll('input[type="hidden"]');
    hiddenInputs.forEach((input) => (input.value = ""));
  }
}
