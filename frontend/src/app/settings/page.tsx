'use client'

import { Suspense, useState } from 'react'
import Link from 'next/link'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface AuthStatus {
  microsoft: {
    connected: boolean
    email: string | null
  } | null
  smtp_configured: boolean
  smtp_email: string | null
  notification_email: string | null
}

async function fetchAuthStatus(): Promise<AuthStatus> {
  const res = await fetch(`${API_BASE_URL}/auth/status`)
  if (!res.ok) throw new Error('Failed to fetch auth status')
  return res.json()
}

async function configureSmtp(data: {
  smtp_user: string
  smtp_password: string
  notification_email: string
}): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/auth/smtp/configure`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      smtp_host: 'smtp.gmail.com',
      smtp_port: 587,
      ...data,
    }),
  })
  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || 'Failed to configure')
  }
}

async function testSmtp(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE_URL}/auth/smtp/test`, { method: 'POST' })
  return res.json()
}

async function disconnectSmtp(): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/auth/smtp/disconnect`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to disconnect')
}

function SettingsContent() {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    smtp_user: '',
    smtp_password: '',
    notification_email: '',
  })

  const { data: authStatus, isLoading } = useQuery({
    queryKey: ['authStatus'],
    queryFn: fetchAuthStatus,
  })

  const configureMutation = useMutation({
    mutationFn: configureSmtp,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['authStatus'] })
      setMessage({ type: 'success', text: 'Gmail configured successfully!' })
      setShowForm(false)
      setFormData({ smtp_user: '', smtp_password: '', notification_email: '' })
    },
    onError: (err: Error) => {
      setMessage({ type: 'error', text: err.message })
    },
  })

  const testMutation = useMutation({
    mutationFn: testSmtp,
    onSuccess: (data) => {
      if (data.status === 'success') {
        setMessage({ type: 'success', text: 'Test email sent! Check your inbox.' })
      } else {
        setMessage({ type: 'error', text: data.message })
      }
    },
    onError: (err: Error) => {
      setMessage({ type: 'error', text: err.message })
    },
  })

  const disconnectMutation = useMutation({
    mutationFn: disconnectSmtp,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['authStatus'] })
      setMessage({ type: 'success', text: 'Email disconnected' })
    },
    onError: (err: Error) => {
      setMessage({ type: 'error', text: err.message })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    configureMutation.mutate(formData)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <div className="flex items-center gap-4">
          <Link href="/" className="text-blue-600 hover:underline">
            &larr; Back to Dashboard
          </Link>
        </div>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Configure email notifications</p>
      </header>

      {message && (
        <div
          className={`mb-6 rounded-lg p-4 ${
            message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}
        >
          {message.text}
          <button onClick={() => setMessage(null)} className="ml-4 text-sm underline">
            Dismiss
          </button>
        </div>
      )}

      <section className="rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Email Notifications</h2>
        <p className="mb-6 text-gray-600">
          Get alerts when new data exposures are detected for your family members.
        </p>

        {isLoading ? (
          <p className="text-gray-500">Loading...</p>
        ) : authStatus?.smtp_configured ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between rounded-lg border border-green-200 bg-green-50 p-4">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Gmail Connected</h3>
                  <p className="text-sm text-gray-600">
                    Sending from: {authStatus.smtp_email}
                  </p>
                  <p className="text-sm text-gray-600">
                    Alerts sent to: {authStatus.notification_email}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => testMutation.mutate()}
                  disabled={testMutation.isPending}
                  className="rounded-md border border-blue-300 px-4 py-2 text-blue-600 hover:bg-blue-50 disabled:opacity-50"
                >
                  {testMutation.isPending ? 'Sending...' : 'Send Test'}
                </button>
                <button
                  onClick={() => disconnectMutation.mutate()}
                  disabled={disconnectMutation.isPending}
                  className="rounded-md border border-red-300 px-4 py-2 text-red-600 hover:bg-red-50 disabled:opacity-50"
                >
                  {disconnectMutation.isPending ? 'Removing...' : 'Remove'}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {!showForm ? (
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-100">
                    <svg className="h-6 w-6 text-red-600" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">Gmail</h3>
                    <p className="text-sm text-gray-500">
                      Use your Gmail account to send notification emails
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowForm(true)}
                  className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                >
                  Set Up Gmail
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="rounded-lg border p-4">
                <h3 className="mb-4 font-medium text-gray-900">Gmail Setup</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Gmail Address
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.smtp_user}
                      onChange={(e) => setFormData({ ...formData, smtp_user: e.target.value })}
                      placeholder="your-email@gmail.com"
                      className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      App Password
                    </label>
                    <input
                      type="password"
                      required
                      value={formData.smtp_password}
                      onChange={(e) => setFormData({ ...formData, smtp_password: e.target.value })}
                      placeholder="xxxx xxxx xxxx xxxx"
                      className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      Not your regular password. See instructions below.
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Send Alerts To
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.notification_email}
                      onChange={(e) => setFormData({ ...formData, notification_email: e.target.value })}
                      placeholder="alerts@example.com"
                      className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="submit"
                      disabled={configureMutation.isPending}
                      className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                    >
                      {configureMutation.isPending ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowForm(false)}
                      className="rounded-md border px-4 py-2 text-gray-600 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>
        )}
      </section>

      <section className="mt-8 rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">How to Get a Gmail App Password</h2>
        <ol className="list-decimal space-y-3 pl-6 text-sm text-gray-600">
          <li>
            Go to your{' '}
            <a
              href="https://myaccount.google.com/security"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Google Account Security
            </a>
          </li>
          <li>
            Make sure <strong>2-Step Verification</strong> is turned ON (required for app passwords)
          </li>
          <li>
            Go to{' '}
            <a
              href="https://myaccount.google.com/apppasswords"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              App Passwords
            </a>
          </li>
          <li>Select app: "Mail" and device: "Other (Custom name)"</li>
          <li>Enter "Fibertap" as the name and click Generate</li>
          <li>Copy the 16-character password (spaces are fine) and paste it above</li>
        </ol>
        <div className="mt-4 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800">
          <strong>Note:</strong> App passwords are different from your regular Google password.
          They provide secure access for apps without exposing your main password.
        </div>
      </section>
    </div>
  )
}

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="container mx-auto px-4 py-8">Loading...</div>}>
      <SettingsContent />
    </Suspense>
  )
}
