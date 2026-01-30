'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, FamilyMember, Exposure } from '@/lib/api'

export function Dashboard() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [newMember, setNewMember] = useState({ name: '', email: '', phone: '', address: '' })

  // Fetch data
  const { data: members = [], isLoading: membersLoading } = useQuery({
    queryKey: ['familyMembers'],
    queryFn: api.familyMembers.list,
  })

  const { data: exposures = [], isLoading: exposuresLoading } = useQuery({
    queryKey: ['exposures'],
    queryFn: () => api.exposures.list(),
  })

  // Mutations
  const addMemberMutation = useMutation({
    mutationFn: api.familyMembers.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['familyMembers'] })
      setShowAddForm(false)
      setNewMember({ name: '', email: '', phone: '', address: '' })
    },
  })

  const deleteMemberMutation = useMutation({
    mutationFn: api.familyMembers.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['familyMembers'] })
      queryClient.invalidateQueries({ queryKey: ['exposures'] })
    },
  })

  const triggerScanMutation = useMutation({
    mutationFn: () => api.scans.trigger('full'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exposures'] })
    },
  })

  const requestRemovalMutation = useMutation({
    mutationFn: api.exposures.requestRemoval,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exposures'] })
    },
  })

  const markRemovedMutation = useMutation({
    mutationFn: api.exposures.markRemoved,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exposures'] })
    },
  })

  // Calculate stats
  const activeExposures = exposures.filter(e => e.status === 'detected').length
  const removalInProgress = exposures.filter(e =>
    e.status === 'removal_requested' || e.status === 'removal_in_progress'
  ).length
  const removed = exposures.filter(e => e.status === 'removed').length

  const handleAddMember = (e: React.FormEvent) => {
    e.preventDefault()
    addMemberMutation.mutate(newMember)
  }

  const getMemberName = (memberId: number) => {
    const member = members.find(m => m.id === memberId)
    return member?.name || 'Unknown'
  }

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      detected: 'bg-red-100 text-red-800',
      removal_requested: 'bg-yellow-100 text-yellow-800',
      removal_in_progress: 'bg-blue-100 text-blue-800',
      removed: 'bg-green-100 text-green-800',
      removal_failed: 'bg-gray-100 text-gray-800',
    }
    return styles[status] || 'bg-gray-100 text-gray-800'
  }

  const formatStatus = (status: string) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Fibertap</h1>
          <p className="text-gray-600">Personal data privacy monitoring</p>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/settings"
            className="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
          >
            Settings
          </Link>
          <button
            onClick={() => triggerScanMutation.mutate()}
            disabled={triggerScanMutation.isPending}
            className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {triggerScanMutation.isPending ? 'Scanning...' : 'Run Full Scan'}
          </button>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-sm font-medium text-gray-500">Family Members</h2>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {membersLoading ? '...' : members.length}
          </p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-sm font-medium text-gray-500">Active Exposures</h2>
          <p className="mt-2 text-3xl font-semibold text-red-600">
            {exposuresLoading ? '...' : activeExposures}
          </p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-sm font-medium text-gray-500">Removals In Progress</h2>
          <p className="mt-2 text-3xl font-semibold text-yellow-600">
            {exposuresLoading ? '...' : removalInProgress}
          </p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-sm font-medium text-gray-500">Removed</h2>
          <p className="mt-2 text-3xl font-semibold text-green-600">
            {exposuresLoading ? '...' : removed}
          </p>
        </div>
      </div>

      {/* Family Members Section */}
      <section className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Family Members</h2>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="rounded-md bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700"
          >
            {showAddForm ? 'Cancel' : '+ Add Member'}
          </button>
        </div>

        {showAddForm && (
          <form onSubmit={handleAddMember} className="mb-4 rounded-lg bg-white p-4 shadow">
            <div className="grid gap-4 md:grid-cols-2">
              <input
                type="text"
                placeholder="Full Name *"
                required
                value={newMember.name}
                onChange={e => setNewMember({ ...newMember, name: e.target.value })}
                className="rounded border p-2"
              />
              <input
                type="email"
                placeholder="Email"
                value={newMember.email}
                onChange={e => setNewMember({ ...newMember, email: e.target.value })}
                className="rounded border p-2"
              />
              <input
                type="tel"
                placeholder="Phone"
                value={newMember.phone}
                onChange={e => setNewMember({ ...newMember, phone: e.target.value })}
                className="rounded border p-2"
              />
              <input
                type="text"
                placeholder="Address"
                value={newMember.address}
                onChange={e => setNewMember({ ...newMember, address: e.target.value })}
                className="rounded border p-2"
              />
            </div>
            <button
              type="submit"
              disabled={addMemberMutation.isPending}
              className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {addMemberMutation.isPending ? 'Adding...' : 'Add Member'}
            </button>
          </form>
        )}

        <div className="rounded-lg bg-white shadow">
          {membersLoading ? (
            <p className="p-6 text-gray-500">Loading...</p>
          ) : members.length === 0 ? (
            <p className="p-6 text-gray-500">No family members added yet.</p>
          ) : (
            <ul className="divide-y">
              {members.map(member => (
                <li key={member.id} className="flex items-center justify-between p-4">
                  <div>
                    <p className="font-medium">{member.name}</p>
                    <p className="text-sm text-gray-500">
                      {[member.email, member.phone].filter(Boolean).join(' | ') || 'No contact info'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-400">
                      {exposures.filter(e => e.family_member_id === member.id && e.status === 'detected').length} exposures
                    </span>
                    <button
                      onClick={() => deleteMemberMutation.mutate(member.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      {/* Exposures Section */}
      <section className="mt-8">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">
          Exposures ({exposures.length})
        </h2>
        <div className="rounded-lg bg-white shadow">
          {exposuresLoading ? (
            <p className="p-6 text-gray-500">Loading...</p>
          ) : exposures.length === 0 ? (
            <p className="p-6 text-gray-500">No exposures detected yet. Add family members and run a scan.</p>
          ) : (
            <ul className="divide-y">
              {exposures.slice(0, 20).map(exposure => (
                <li key={exposure.id} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{exposure.source_name}</span>
                        <span className={`rounded px-2 py-0.5 text-xs ${getStatusBadge(exposure.status)}`}>
                          {formatStatus(exposure.status)}
                        </span>
                        <span className="text-xs text-gray-400">
                          {exposure.source === 'breach' ? 'Data Breach' : 'People Search'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">
                        {getMemberName(exposure.family_member_id)}
                      </p>
                      {exposure.data_exposed && (
                        <p className="mt-1 text-xs text-gray-400">{exposure.data_exposed}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {exposure.source_url && (
                        <a
                          href={exposure.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:underline"
                        >
                          View
                        </a>
                      )}
                      {exposure.status === 'detected' && (
                        <button
                          onClick={() => requestRemovalMutation.mutate(exposure.id)}
                          className="text-sm text-orange-600 hover:underline"
                        >
                          Request Removal
                        </button>
                      )}
                      {(exposure.status === 'removal_requested' || exposure.status === 'removal_in_progress') && (
                        <button
                          onClick={() => markRemovedMutation.mutate(exposure.id)}
                          className="text-sm text-green-600 hover:underline"
                        >
                          Mark Removed
                        </button>
                      )}
                    </div>
                  </div>
                </li>
              ))}
              {exposures.length > 20 && (
                <li className="p-4 text-center text-gray-500">
                  And {exposures.length - 20} more exposures...
                </li>
              )}
            </ul>
          )}
        </div>
      </section>
    </div>
  )
}
