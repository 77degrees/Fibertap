'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface AuthStatus {
  microsoft: {
    connected: boolean
    email: string | null
    expires_at: string | null
  } | null
  smtp_configured: boolean
}

async function fetchAuthStatus(): Promise<AuthStatus> {
  const res = await fetch(`${API_BASE_URL}/auth/status`)
  if (!res.ok) throw new Error('Failed to fetch auth status')
  return res.json()
}

async function disconnectMicrosoft(): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/auth/microsoft/disconnect`, {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error('Failed to disconnect')
}

function SettingsContent() {
  const searchParams = useSearchParams()
  const queryClient = useQueryClient()
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // Check for OAuth callback params
  useEffect(() => {
    const connected = searchParams.get('connected')
    const email = searchParams.get('email')
    const error = searchParams.get('error')

    if (connected === 'microsoft' && email) {
      setMessage({ type: 'success', text: `Successfully connected: ${email}` })
      queryClient.invalidateQueries({ queryKey: ['authStatus'] })
    } else if (error) {
      setMessage({ type: 'error', text: error })
    }
  }, [searchParams, queryClient])

  const { data: authStatus, isLoading } = useQuery({
    queryKey: ['authStatus'],
    queryFn: fetchAuthStatus,
  })

  const disconnectMutation = useMutation({
    mutationFn: disconnectMicrosoft,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['authStatus'] })
      setMessage({ type: 'success', text: 'Successfully disconnected Outlook' })
    },
    onError: (err: Error) => {
      setMessage({ type: 'error', text: err.message })
    },
  })

  const handleConnectOutlook = () => {
    window.location.href = `${API_BASE_URL}/auth/microsoft/connect`
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
        <p className="text-gray-600">Configure email notifications and integrations</p>
      </header>

      {message && (
        <div
          className={`mb-6 rounded-lg p-4 ${
            message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}
        >
          {message.text}
          <button
            onClick={() => setMessage(null)}
            className="ml-4 text-sm underline"
          >
            Dismiss
          </button>
        </div>
      )}

      <section className="rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Email Notifications</h2>
        <p className="mb-6 text-gray-600">
          Connect your email account to receive alerts when new data exposures are detected.
        </p>

        {isLoading ? (
          <p className="text-gray-500">Loading...</p>
        ) : (
          <div className="space-y-4">
            {/* Microsoft/Outlook Connection */}
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                  <svg className="h-6 w-6 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21.17 2.06A1 1 0 0 0 20.25 2H8.5a1 1 0 0 0-.77.36l-6.5 8a1 1 0 0 0 0 1.28l6.5 8a1 1 0 0 0 .77.36h11.75a1 1 0 0 0 .92-.62 1 1 0 0 0 .08-.38V3a1 1 0 0 0-.08-.38 1 1 0 0 0-.17-.24zM20 18H9.25L4 12l5.25-6H20z"/>
                    <path d="M11 8h2v8h-2zm4 0h2v8h-2z"/>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Microsoft Outlook</h3>
                  {authStatus?.microsoft?.connected ? (
                    <p className="text-sm text-green-600">
                      Connected: {authStatus.microsoft.email}
                    </p>
                  ) : (
                    <p className="text-sm text-gray-500">
                      Sign in with your Microsoft account to send notifications via Outlook
                    </p>
                  )}
                </div>
              </div>
              <div>
                {authStatus?.microsoft?.connected ? (
                  <button
                    onClick={() => disconnectMutation.mutate()}
                    disabled={disconnectMutation.isPending}
                    className="rounded-md border border-red-300 px-4 py-2 text-red-600 hover:bg-red-50 disabled:opacity-50"
                  >
                    {disconnectMutation.isPending ? 'Disconnecting...' : 'Disconnect'}
                  </button>
                ) : (
                  <button
                    onClick={handleConnectOutlook}
                    className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                  >
                    Sign in with Outlook
                  </button>
                )}
              </div>
            </div>

            {/* Status Summary */}
            <div className="mt-6 rounded-lg bg-gray-50 p-4">
              <h3 className="font-medium text-gray-900">Notification Status</h3>
              {authStatus?.microsoft?.connected ? (
                <p className="mt-2 text-sm text-green-600">
                  Email notifications are enabled. Alerts will be sent to {authStatus.microsoft.email}.
                </p>
              ) : authStatus?.smtp_configured ? (
                <p className="mt-2 text-sm text-green-600">
                  Email notifications are enabled via SMTP configuration.
                </p>
              ) : (
                <p className="mt-2 text-sm text-yellow-600">
                  Email notifications are not configured. Connect your Outlook account above to receive alerts.
                </p>
              )}
            </div>
          </div>
        )}
      </section>

      <section className="mt-8 rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Azure App Setup</h2>
        <p className="text-sm text-gray-600">
          To use Microsoft/Outlook authentication, you need to register an app in Azure:
        </p>
        <ol className="mt-4 list-decimal space-y-2 pl-6 text-sm text-gray-600">
          <li>
            Go to{' '}
            <a
              href="https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Azure App Registrations
            </a>
          </li>
          <li>Click "New registration"</li>
          <li>Name it "Fibertap" (or any name you prefer)</li>
          <li>Select "Accounts in any organizational directory and personal Microsoft accounts"</li>
          <li>
            Add redirect URI: <code className="rounded bg-gray-100 px-1">http://localhost:8000/api/auth/microsoft/callback</code>
          </li>
          <li>After creating, go to "Certificates & secrets" and create a new client secret</li>
          <li>Copy the Application (client) ID and client secret to your <code className="rounded bg-gray-100 px-1">.env</code> file:
            <pre className="mt-2 rounded bg-gray-100 p-2">
{`MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret`}
            </pre>
          </li>
        </ol>
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
