import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Navbar() {
  const { role, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate("/login")
  }

  return (
    <nav className="border-b border-gray-200 px-6 py-3 flex items-center justify-between bg-white">
      <div className="flex items-center gap-6">
        <span className="font-medium text-gray-900">NoteApp</span>
          {role === "super_admin" && (
            <Link to="/super" className="text-sm text-gray-600 hover:text-gray-900">
              Super Admin
            </Link>
        )}

        {role === "admin" && (
          <>
            <Link to="/dashboard"     className="text-sm text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link to="/organizations" className="text-sm text-gray-600 hover:text-gray-900">Organizations</Link>
            <Link to="/invitations"   className="text-sm text-gray-600 hover:text-gray-900">Invitations sent</Link>
          </>
        )}
        {role === "user" && (
          <>
            <Link to="/dashboard"   className="text-sm text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link to="/invitations" className="text-sm text-gray-600 hover:text-gray-900">My Invitations</Link>
          </>
        )}
      </div>
      <div className="flex items-center gap-3">
        <span className={`text-xs px-2 py-1 rounded-full font-medium
          ${role === "admin"
            ? "bg-purple-50 text-purple-700"
            : "bg-teal-50 text-teal-700"}`}>
          {role}
        </span>
        <button
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-gray-900 border border-gray-200 px-3 py-1.5 rounded-lg hover:bg-gray-50"
        >
          Logout
        </button>
      </div>
    </nav>
  )
}