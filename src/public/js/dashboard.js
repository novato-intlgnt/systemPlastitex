const sidebar = document.querySelector('.sidebar')
const closeBtn = document.querySelector('#btn')
const containerPopup = document.querySelector('.container-popup')
const artistInput = document.querySelector('#artist')
const songInput = document.querySelector('#songs')

closeBtn.addEventListener('click', () => {
  sidebar.classList.toggle('open')
  songInput.value = ''
  artistInput.value = ''
  menuBtnChange()
})


function menuBtnChange () {
  if (sidebar.classList.contains('open')) {
    closeBtn.classList.replace('fi-rr-menu-burger', 'fi-rr-bars-staggered')// replacing the iocns class
  } else {
    closeBtn.classList.replace('fi-rr-bars-staggered', 'fi-rr-menu-burger')// replacing the iocns class
    containerPopup.classList.remove('open')
  }
}

function checkAuth() {
  const token = localStorage.getItem('access_token')
  if (!token) {
    window.location.href = '/'
    return false
  }
  return true
}

function logout() {
  localStorage.removeItem('access_token')
  window.location.href = '/'
}

window.logout = logout

document.addEventListener('DOMContentLoaded', async function () {
  const path = window.location.pathname
  const parts = path.split('/')
  const userName = parts[2]

  const url = window.location.origin
  const res = await fetch(`${url}/user/${userName}`)
  const data = await res.json()

  const nameHtml = document.getElementById('user')
  if (userName) {
    nameHtml.innerText = data.data.fullName
  }

  if (data.data && data.data.access_token) {
    localStorage.setItem("access_token", data.data.access_token);
  }

  if (!checkAuth()) return
})
