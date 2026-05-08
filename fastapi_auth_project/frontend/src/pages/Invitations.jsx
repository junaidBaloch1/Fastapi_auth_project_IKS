import { useState, useEffect } from "react"
import api from "../api/axios"
import { useAuth } from "../context/AuthContext"
import Navbar from "../components/Navbar"

const statusStyle = {
  pending:  "bg-amber-50  text-amber-700  border-amber-100",
  accepted: "bg-teal-50   text-teal-700   border-teal-100",
  declined: "bg-red-50    text-red-600    border-red-100",
}

export default function Invitations() {
  const { role } = useAuth()
  const [invitations, setInvitations] = useState([])
  const [error, setError]   = useState("")
  const [success, setSuccess] = useState("")

  useEffect(() => { fetchInvitations() }, [])

  const fetchInvitations = async () => {
    const url = role === "admin" ? "/invitations/sent" : "/invitations/my"
    const res = await api.get(url)
    setInvitations(res.data)
  }

  const respond = async (id, action) => {
    setError(""); 
    setSuccess("")
    try {
      const res = await api.post(`/invitations/${id}/${action}`)
      setSuccess(res.data.message)
      fetchInvitations()
    } catch (err) {
      setError(err.response?.data?.detail || "Action failed")
    }
  }

  const cancel = async (id) => {
    setError(""); 
    setSuccess("")
    try {
      await api.delete(`/invitations/${id}`)
      setSuccess("Invitation cancelled")
      fetchInvitations()
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to cancel")
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-lg font-medium text-gray-900 mb-6">
          {role === "admin" ? "Invitations sent" : "My invitations"}
        </h1>

        {error   && <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</div>}
        {success && <div className="mb-4 text-sm text-teal-600 bg-teal-50 border border-teal-100 rounded-lg px-3 py-2">{success}</div>}

        {invitations.length === 0 && (
          <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
            <p className="text-sm text-gray-400">No invitations yet.</p>
          </div>
        )}

        <div className="space-y-3">
          {invitations.map(inv => (
            <div key={inv.id} className="bg-white border border-gray-200 rounded-xl p-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-gray-900 text-sm">{inv.organization.name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {role === "admin"
                      ? `To user ID: ${inv.invited_user_id}`
                      : `From: ${inv.invited_by.username}`}
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(inv.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`text-xs border px-2 py-1 rounded-full font-medium ${statusStyle[inv.status]}`}>
                  {inv.status}
                </span>
              </div>

              {/* User actions */}
              {role === "user" && inv.status === "pending" && (
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => respond(inv.id, "accept")}
                    className="flex-1 text-sm bg-teal-600 text-white py-1.5 rounded-lg hover:bg-teal-700"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => respond(inv.id, "decline")}
                    className="flex-1 text-sm border border-gray-200 text-gray-600 py-1.5 rounded-lg hover:bg-gray-50"
                  >
                    Decline
                  </button>
                </div>
              )}

              {/* Admin cancel */}
              {role === "admin" && inv.status === "pending" && (
                <div className="mt-4">
                  <button
                    onClick={() => cancel(inv.id)}
                    className="text-sm text-red-500 hover:text-red-700"
                  >
                    Cancel invitation
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}