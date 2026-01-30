const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`)
  }

  // Handle 204 No Content
  if (res.status === 204) {
    return null as T
  }

  return res.json()
}

export interface FamilyMember {
  id: number
  name: string
  email: string | null
  phone: string | null
  address: string | null
  date_of_birth: string | null
  created_at: string
  updated_at: string
}

export interface Exposure {
  id: number
  family_member_id: number
  source: 'breach' | 'people_search' | 'data_broker' | 'other'
  source_name: string
  source_url: string | null
  data_exposed: string | null
  status: 'detected' | 'removal_requested' | 'removal_in_progress' | 'removed' | 'removal_failed'
  incogni_request_id: string | null
  detected_at: string
  updated_at: string
}

export interface Scan {
  id: number
  scan_type: 'full' | 'breach' | 'data_broker'
  status: 'pending' | 'running' | 'completed' | 'failed'
  exposures_found: number
  error_message: string | null
  started_at: string
  completed_at: string | null
}

export const api = {
  familyMembers: {
    list: () => fetchApi<FamilyMember[]>('/family-members/'),
    get: (id: number) => fetchApi<FamilyMember>(`/family-members/${id}`),
    create: (data: Partial<FamilyMember>) =>
      fetchApi<FamilyMember>('/family-members/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: number, data: Partial<FamilyMember>) =>
      fetchApi<FamilyMember>(`/family-members/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: number) =>
      fetchApi<null>(`/family-members/${id}`, { method: 'DELETE' }),
  },
  exposures: {
    list: (memberId?: number, status?: string) => {
      const params = new URLSearchParams()
      if (memberId) params.append('member_id', memberId.toString())
      if (status) params.append('status', status)
      const query = params.toString()
      return fetchApi<Exposure[]>(`/exposures/${query ? `?${query}` : ''}`)
    },
    get: (id: number) => fetchApi<Exposure>(`/exposures/${id}`),
    requestRemoval: (id: number) =>
      fetchApi<Exposure>(`/exposures/${id}/request-removal`, { method: 'POST' }),
    markRemoved: (id: number) =>
      fetchApi<Exposure>(`/exposures/${id}/mark-removed`, { method: 'POST' }),
    delete: (id: number) =>
      fetchApi<null>(`/exposures/${id}`, { method: 'DELETE' }),
  },
  scans: {
    list: () => fetchApi<Scan[]>('/scans/'),
    get: (id: number) => fetchApi<Scan>(`/scans/${id}`),
    trigger: (scanType: 'full' | 'breach' | 'data_broker' = 'full', familyMemberIds?: number[]) =>
      fetchApi<Scan>('/scans/', {
        method: 'POST',
        body: JSON.stringify({ scan_type: scanType, family_member_ids: familyMemberIds }),
      }),
  },
}
