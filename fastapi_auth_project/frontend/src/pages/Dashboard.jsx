import { useAuth } from "../context/AuthContext"
import Navbar from "../components/Navbar"
import { Link } from "react-router-dom"

export default function Dashboard() {
  const { role } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-lg font-medium text-gray-900 mb-2">Dashboard</h1>
        <p className="text-sm text-gray-500 mb-8">
          You are logged in as <span className={`font-medium ${role === "admin" ? "text-purple-600" : "text-teal-600"}`}>{role}</span>
        </p>

        <div className="grid grid-cols-2 gap-4">
          {role === "admin" && (
            <Link to="/organizations"
              className="bg-white border border-gray-200 rounded-xl p-6 hover:border-purple-200 hover:bg-purple-50 transition-colors">
              <p className="font-medium text-gray-900 text-sm">Organizations</p>
              <p className="text-xs text-gray-400 mt-1">Create orgs and invite users</p>
            </Link>
          )}
          <Link to="/invitations"
            className="bg-white border border-gray-200 rounded-xl p-6 hover:border-teal-200 hover:bg-teal-50 transition-colors">
            <p className="font-medium text-gray-900 text-sm">
              {role === "admin" ? "Sent invitations" : "My invitations"}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {role === "admin" ? "Track all sent invites" : "Accept or decline invites"}
            </p>
          </Link>
        </div>
      </div>
    </div>
  )
}