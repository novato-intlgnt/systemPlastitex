const sidebar = document.querySelector('.sidebar')
const closeBtn = document.querySelector('#btn')
const containerPopup = document.querySelector('.container-popup')
const artistInput = document.querySelector('#artist')
const songInput = document.querySelector('#songs')

closeBtn.addEventListener('click', () => {
  sidebar.classList.toggle('open')
  songInput.value = ''
  artistInput.value = ''
  menuBtnChange()// calling the function(optional)
})


// following are the code to change sidebar button(optional)
function menuBtnChange () {
  if (sidebar.classList.contains('open')) {
    closeBtn.classList.replace('fi-rr-menu-burger', 'fi-rr-bars-staggered')// replacing the iocns class
  } else {
    closeBtn.classList.replace('fi-rr-bars-staggered', 'fi-rr-menu-burger')// replacing the iocns class
    containerPopup.classList.remove('open')
  }
}

/**
 * Verifica si hay un token válido, si no redirige al login
 */
function checkAuth() {
  const token = localStorage.getItem('access_token')
  if (!token) {
    window.location.href = '/'
    return false
  }
  return true
}

/**
 * Función de logout - elimina el token y redirige al login
 */
function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_data')
  window.location.href = '/'
}

// Exponer logout globalmente para poder usarlo en onclick
window.logout = logout

document.addEventListener('DOMContentLoaded', function () {
  // Verificar autenticación
  if (!checkAuth()) return

  const path = window.location.pathname
  const parts = path.split('/')
  const userName = parts[2]

  // Set the userName in the html
  const nameHtml = document.getElementById('user')
  if (userName) {
    nameHtml.innerText = userName
  }

  // También podemos usar los datos guardados del usuario
  const userData = localStorage.getItem('user_data')
  if (userData) {
    try {
      const user = JSON.parse(userData)
      console.log('Usuario logueado:', user.name, '- Rol:', user.role)
    } catch (e) {
      console.error('Error parsing user data:', e)
    }
  }
})
