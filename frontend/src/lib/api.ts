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
  source: string
  source_name: string
  source_url: string | null
  data_exposed: string | null
  status: string
  incogni_request_id: string | null
  detected_at: string
  updated_at: string
}

export const api = {
  familyMembers: {
    list: () => fetchApi<FamilyMember[]>('/family-members'),
    get: (id: number) => fetchApi<FamilyMember>(`/family-members/${id}`),
    create: (data: Partial<FamilyMember>) =>
      fetchApi<FamilyMember>('/family-members', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    delete: (id: number) =>
      fetchApi(`/family-members/${id}`, { method: 'DELETE' }),
  },
  exposures: {
    list: (memberId?: number) =>
      fetchApi<Exposure[]>(`/exposures${memberId ? `?member_id=${memberId}` : ''}`),
    get: (id: number) => fetchApi<Exposure>(`/exposures/${id}`),
    requestRemoval: (id: number) =>
      fetchApi(`/exposures/${id}/request-removal`, { method: 'POST' }),
  },
  scans: {
    trigger: (scanType = 'full') =>
      fetchApi('/scans', {
        method: 'POST',
        body: JSON.stringify({ scan_type: scanType }),
      }),
  },
}
