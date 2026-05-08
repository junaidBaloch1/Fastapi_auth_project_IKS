// src/pages/SuperAdmin.jsx
import { useState, useEffect } from "react"
import api from "../api/axios"
import Navbar from "../components/Navbar"

const tabs = ["Stats", "Users", "Admins", "Organizations", "No Org Users"]

export default function SuperAdmin() {
  const [activeTab, setActiveTab] = useState("Stats")
  const [data, setData]           = useState([])
  const [stats, setStats]         = useState(null)
  const [error, setError]         = useState("")
  const [success, setSuccess]     = useState("")

  useEffect(() => { fetchTab(activeTab) }, [activeTab])

  const fetchTab = async (tab) => {
    setError(""); setData([])
    try {
      const routes = {
        "Stats":          "/super/stats",
        "Users":          "/super/users",
        "Admins":         "/super/users/admins",
        "Organizations":  "/super/orgs",
        "No Org Users":   "/super/users/no-org",
      }
      const res = await api.get(routes[tab])
      tab === "Stats" ? setStats(res.data) : setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch")
    }
  }

  const deleteUser = async (id, username) => {
    if (!confirm(`Delete ${username}?`)) return
    try {
      await api.delete(`/super/users/${id}`)
      setSuccess(`${username} deleted`)
      fetchTab(activeTab)
    } catch (err) { setError(err.response?.data?.detail) }
  }

  const deleteOrg = async (id, name) => {
    if (!confirm(`Delete org "${name}"?`)) return
    try {
      await api.delete(`/super/orgs/${id}`)
      setSuccess(`Org "${name}" deleted`)
      fetchTab(activeTab)
    } catch (err) { setError(err.response?.data?.detail) }
  }

  const changeRole = async (id, newRole) => {
    try {
      await api.patch(`/super/users/${id}/role?new_role=${newRole}`)
      setSuccess("Role updated")
      fetchTab(activeTab)
    } catch (err) { setError(err.response?.data?.detail) }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">

        <div className="flex items-center gap-3 mb-6">
          {/* <h1 className="text-lg font-medium text-gray-900">Super Admin</h1> */}
          <span className="text-xs bg-purple-100 text-purple-700 border border-purple-200 px-2 py-1 rounded-full font-medium">
            super_admin
          </span>
        </div>

        {error   && <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</div>}
        {success && <div className="mb-4 text-sm text-teal-600 bg-teal-50 border border-teal-100 rounded-lg px-3 py-2">{success}</div>}

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-white border border-gray-200 rounded-xl p-1 w-fit">
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`text-sm px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab
                  ? "bg-gray-900 text-white"
                  : "text-gray-500 hover:text-gray-900"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Stats */}
        {activeTab === "Stats" && stats && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(stats).map(([key, val]) => (
              <div key={key} className="bg-white border border-gray-200 rounded-xl p-5">
                <p className="text-2xl font-semibold text-gray-900">{val}</p>
                <p className="text-sm text-gray-400 mt-1">
                  {key.replace(/_/g, " ")}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Users / Admins / No Org Users */}
        {["Users", "Admins", "No Org Users"].includes(activeTab) && (
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">ID</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Username</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Email</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Role</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.map(user => (
                  <tr key={user.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-400">{user.id}</td>
                    <td className="px-4 py-3 font-medium text-gray-900">{user.username}</td>
                    <td className="px-4 py-3 text-gray-500">{user.email}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-1 rounded-full border font-medium ${
                        user.role === "admin"
                          ? "bg-amber-50 text-amber-700 border-amber-100"
                          : user.role === "super_admin"
                          ? "bg-purple-50 text-purple-700 border-purple-100"
                          : "bg-teal-50 text-teal-700 border-teal-100"
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {/* Role change dropdown */}
                        <select
                          defaultValue=""
                          onChange={e => e.target.value && changeRole(user.id, e.target.value)}
                          className="text-xs border border-gray-200 rounded-lg px-2 py-1 text-gray-600"
                        >
                          <option value="">Change role</option>
                          <option value="user">user</option>
                          <option value="admin">admin</option>
                          <option value="super_admin">super_admin</option>
                        </select>
                        <button
                          onClick={() => deleteUser(user.id, user.username)}
                          className="text-xs text-red-500 hover:text-red-700 border border-red-100 px-2 py-1 rounded-lg hover:bg-red-50"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {data.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">
                      No records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Organizations */}
        {activeTab === "Organizations" && (
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">ID</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Name</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Created by</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Created at</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.map(org => (
                  <tr key={org.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-400">{org.id}</td>
                    <td className="px-4 py-3 font-medium text-gray-900">{org.name}</td>
                    <td className="px-4 py-3 text-gray-500">Admin ID: {org.created_by}</td>
                    <td className="px-4 py-3 text-gray-400">
                      {new Date(org.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => deleteOrg(org.id, org.name)}
                        className="text-xs text-red-500 hover:text-red-700 border border-red-100 px-2 py-1 rounded-lg hover:bg-red-50"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
                {data.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">
                      No organizations found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

      </div>
    </div>
  )
}