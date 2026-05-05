import { useState, useEffect } from "react"
import api from "../api/axios"
import Navbar from "../components/Navbar"

export default function Organizations() {
  const [orgs, setOrgs]         = useState([])
  const [members, setMembers]   = useState({})
  const [newOrgName, setNewOrgName] = useState("")
  const [inviteData, setInviteData] = useState({ org_id: "", invited_user_id: "" })
  const [error, setError]       = useState("")
  const [success, setSuccess]   = useState("")

  useEffect(() => { fetchOrgs() }, [])

  const fetchOrgs = async () => {
    const res = await api.get("/org/my")
    setOrgs(res.data)
  }

  const fetchMembers = async (orgId) => {
    const res = await api.get(`/org/${orgId}/members`)
    setMembers(prev => ({ ...prev, [orgId]: res.data }))
  }

  const createOrg = async (e) => {
    e.preventDefault()
    setError(""); setSuccess("")
    try {
      await api.post("/org/", { name: newOrgName })
      setSuccess("Organization created")
      setNewOrgName("")
      fetchOrgs()
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create org")
    }
  }

  const sendInvite = async (e) => {
    e.preventDefault()
    setError(""); setSuccess("")
    try {
      await api.post("/invitations/", {
        org_id: parseInt(inviteData.org_id),
        invited_user_id: parseInt(inviteData.invited_user_id),
      })
      setSuccess("Invitation sent successfully")
      setInviteData({ org_id: "", invited_user_id: "" })
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to send invitation")
    }
  }

  const removeMember = async (orgId, userId) => {
    try {
      await api.delete(`/org/${orgId}/members/${userId}`)
      fetchMembers(orgId)
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to remove member")
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">

        {error   && <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</div>}
        {success && <div className="text-sm text-teal-600 bg-teal-50 border border-teal-100 rounded-lg px-3 py-2">{success}</div>}

        {/* Create org */}
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="font-medium text-gray-900 mb-4">Create organization</h2>
          <form onSubmit={createOrg} className="flex gap-3">
            <input
              required
              placeholder="Organization name"
              value={newOrgName}
              onChange={e => setNewOrgName(e.target.value)}
              className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-200"
            />
            <button
              type="submit"
              className="bg-gray-900 text-white text-sm px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Create
            </button>
          </form>
        </div>

        {/* Send invitation */}
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="font-medium text-gray-900 mb-4">Send invitation</h2>
          <form onSubmit={sendInvite} className="flex gap-3">
            <select
              required
              value={inviteData.org_id}
              onChange={e => setInviteData({ ...inviteData, org_id: e.target.value })}
              className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-200"
            >
              <option value="">Select organization</option>
              {orgs.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
            </select>
            <input
              required
              type="number"
              placeholder="User ID"
              value={inviteData.invited_user_id}
              onChange={e => setInviteData({ ...inviteData, invited_user_id: e.target.value })}
              className="w-28 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-200"
            />
            <button
              type="submit"
              className="bg-purple-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Invite
            </button>
          </form>
        </div>

        {/* My organizations */}
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="font-medium text-gray-900 mb-4">My organizations</h2>
          {orgs.length === 0 && (
            <p className="text-sm text-gray-400">No organizations yet.</p>
          )}
          <div className="space-y-3">
            {orgs.map(org => (
              <div key={org.id} className="border border-gray-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{org.name}</p>
                    <p className="text-xs text-gray-400">ID: {org.id}</p>
                  </div>
                  <button
                    onClick={() => fetchMembers(org.id)}
                    className="text-xs text-purple-600 border border-purple-100 px-3 py-1 rounded-lg hover:bg-purple-50"
                  >
                    View members
                  </button>
                </div>

                {members[org.id] && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    {members[org.id].length === 0
                      ? <p className="text-xs text-gray-400">No members yet.</p>
                      : members[org.id].map(m => (
                        <div key={m.id} className="flex items-center justify-between py-1">
                          <div>
                            <span className="text-sm text-gray-700">{m.user.username}</span>
                            <span className="text-xs text-gray-400 ml-2">{m.user.email}</span>
                          </div>
                          <button
                            onClick={() => removeMember(org.id, m.user_id)}
                            className="text-xs text-red-500 hover:text-red-700"
                          >
                            Remove
                          </button>
                        </div>
                      ))
                    }
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}