import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function ProtectedRoute({ children, requiredRole, excludeRole }) {
  const { token, role } = useAuth()

  if (!token) return <Navigate to="/login" replace />

  // redirect super_admin away from /dashboard to /super
  if (role === "super_admin" && excludeRole === "super_admin") {
    return <Navigate to="/super" replace />
  }

  if (requiredRole && role !== requiredRole) {
    return <Navigate to="/login" replace />
  }

  return children
}