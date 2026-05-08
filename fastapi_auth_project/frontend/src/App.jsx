import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import ProtectedRoute from "./components/ProtectedRoute"
import Login         from "./pages/Login"
import Register      from "./pages/Register"
import Dashboard     from "./pages/Dashboard"
import Organizations from "./pages/Organizations"
import Invitations   from "./pages/Invitations"
import SuperAdmin from "./pages/SuperAdmin"


export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/"         element={<Navigate to="/login" replace />} />
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/dashboard" element={
            <ProtectedRoute><Dashboard /></ProtectedRoute>
          }/>

          <Route path="/organizations" element={
            <ProtectedRoute requiredRole="admin"><Organizations /></ProtectedRoute>
          }/>

          <Route path="/invitations" element={
            <ProtectedRoute><Invitations /></ProtectedRoute>
          }/>

          <Route path="/super" element={
          <ProtectedRoute requiredRole="super_admin">
            <SuperAdmin />
          </ProtectedRoute>
        }/>

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}