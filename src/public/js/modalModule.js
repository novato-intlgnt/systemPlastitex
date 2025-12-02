export function openModal(modalId) {
  document.getElementById(modalId).style.display = "flex";
}

export function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}

export function fillForm(formId, data) {
  const form = document.getElementById(formId);
  for (const key in data) {
    if (form[key]) form[key].value = data[key];
  }
}

export function clearForm(formId) {
  document.getElementById(formId).reset();
}
