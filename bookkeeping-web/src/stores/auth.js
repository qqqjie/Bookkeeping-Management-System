import { readonly, reactive } from 'vue'

const TOKEN_KEY = 'bookkeeping_token'
const USER_KEY = 'bookkeeping_user'

const state = reactive({
  token: localStorage.getItem(TOKEN_KEY) || '',
  user: safeParseUser(localStorage.getItem(USER_KEY))
})

function safeParseUser(raw) {
  if (!raw) {
    return null
  }
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function setAuth(token, user) {
  state.token = token
  state.user = user
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

function clear() {
  state.token = ''
  state.user = null
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export const authStore = {
  state: readonly(state),
  getToken: () => state.token,
  getUser: () => state.user,
  isLoggedIn: () => Boolean(state.token),
  setAuth,
  clear
}
