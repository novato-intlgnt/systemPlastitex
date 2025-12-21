/**
 * Obtiene el token almacenado en localStorage
 * @returns {string|null} Token de autenticación o null
 */
export function getToken() {
  return localStorage.getItem("access_token");
}

/**
 * Guarda el token en localStorage
 * @param {string} token - Token JWT a guardar
 */
export function setToken(token) {
  localStorage.setItem("access_token", token);
}

/**
 * Elimina el token de localStorage (logout)
 */
export function removeToken() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_data");
}

/**
 * Guarda los datos del usuario en localStorage
 * @param {Object} userData - Datos del usuario
 */
export function setUserData(userData) {
  localStorage.setItem("user_data", JSON.stringify(userData));
}

/**
 * Obtiene los datos del usuario de localStorage
 * @returns {Object|null} Datos del usuario o null
 */
export function getUserData() {
  const data = localStorage.getItem("user_data");
  return data ? JSON.parse(data) : null;
}

/**
 * Realiza peticiones HTTP con autenticación Bearer automática
 * @param {string} url - URL del endpoint
 * @param {string} method - Método HTTP (GET, POST, PUT, DELETE)
 * @param {Object|null} body - Cuerpo de la petición
 * @returns {Promise<Object>} Respuesta JSON
 */
export async function apiRequest(url, method = "GET", body = null) {
  const token = getToken();
  
  const headers = {
    "Content-Type": "application/json",
  };

  // Agregar token Bearer si existe
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers,
  };

  if (body) options.body = JSON.stringify(body);

  const res = await fetch(url, options);
  
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Error en la petición");
  }
  return await res.json();
}
