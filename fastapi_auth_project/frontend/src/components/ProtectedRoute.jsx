import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// requiredRole is optional — if passed, also checks role
export default function ProtectedRoute({ children, requiredRole }) {
  const { token, role } = useAuth()

  if (!token) return <Navigate to="/login" replace />
  if (requiredRole && role !== requiredRole) return <Navigate to="/dashboard" replace />

  return children
}