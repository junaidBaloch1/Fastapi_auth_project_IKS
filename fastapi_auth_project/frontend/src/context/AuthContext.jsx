import { createContext, useContext, useState } from "react"
import api from "../api/axios"

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser]   = useState(null)
  const [role, setRole]   = useState(localStorage.getItem("role"))
  const [token, setToken] = useState(localStorage.getItem("token"))

  const login = async (username, password) => {
    const res = await api.post("/auth/login", { username, password })
    localStorage.setItem("token", res.data.access_token)
    localStorage.setItem("role",  res.data.role)

    setToken(res.data.access_token)
    setRole(res.data.role)
    return res.data.role   // return role so caller can redirect correctly
  }

  const logout = async () => {
    try { await api.post("/auth/logout") } catch {}
    localStorage.removeItem("token")
    localStorage.removeItem("role")
    setToken(null)
    setRole(null)
    setUser(null)
  }

  const register = async (data) => {
    return await api.post("/auth/register", data)
  }

  return (
    <AuthContext.Provider value={{ user, role, token, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)