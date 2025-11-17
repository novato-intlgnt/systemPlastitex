function switchTab(tab) {
  // Cambiar tabs activos
  document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
  event.target.classList.add("active");

  // Cambiar contenido
  document
    .querySelectorAll(".form-content")
    .forEach((form) => form.classList.remove("active"));
  document.getElementById(tab + "-form").classList.add("active");

  hideAlert();
}

/* ----------------------------- LOGIN REAL ----------------------------- */

async function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  if (!email || !password) {
    return showAlert("Completa todos los campos", "error");
  }

  const url = window.location.origin;
  console.log(url)

  showAlert("Verificando credenciales...", "success");

  try {
    const res = await fetch(`${url}/user/signin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        pass: password,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      return showAlert(data.message || "Error al iniciar sesión", "error");
    }

    showAlert("¡Acceso concedido! Redirigiendo...", "success");

    if (data.redirect) {
      setTimeout(() => {
        window.location.href = data.redirect;
      }, 1500);
    }
  } catch (err) {
    showAlert("Error de conexión con el servidor", "error");
  }
}

/* ---------------------------- REGISTER REAL --------------------------- */

async function handleRegister(event) {
  event.preventDefault();

  const name = document.getElementById("register-name").value;
  const email = document.getElementById("register-email").value;
  const role = document.getElementById("register-role").value;
  const password = document.getElementById("register-password").value;
  const confirm = document.getElementById("register-confirm").value;

  if (!role) {
    return showAlert("Selecciona un rol", "error");
  }
  if (password !== confirm) {
    return showAlert("Las contraseñas no coinciden", "error");
  }

  const url = window.location.origin;
  console.log(url)

  showAlert("Registrando usuario...", "success");

  try {
    const res = await fetch(`${url}/user/signup/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user: name,
        email: email,
        pass: password,
        role: role,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      return showAlert(data.message || "Error al registrarse", "error");
    }

    showAlert("¡Usuario creado correctamente!", "success");

    setTimeout(() => {
      document.querySelector('[data-tab="login"]').click();
    }, 2000);

  } catch (err) {
    showAlert("Error de conexión con el servidor", "error");
  }
}


/* -------------------------- UTILIDADES ---------------------------- */

function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const type = input.type === "password" ? "text" : "password";
  input.type = type;
}

function showAlert(message, type) {
  const alert = document.getElementById("alert");
  alert.textContent = message;
  alert.className = "alert " + type + " show";
}

function hideAlert() {
  document.getElementById("alert").classList.remove("show");
}

setInterval(() => {
  const alert = document.getElementById("alert");
  if (alert.classList.contains("show")) {
    setTimeout(() => hideAlert(), 5000);
  }
}, 100);
