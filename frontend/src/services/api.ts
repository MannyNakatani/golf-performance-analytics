const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000')
  .trim()
  .replace(/\/+$/, '')

export interface HealthResponse {
  status: 'healthy'
  service: 'golf-performance-api'
}

export async function getHealth(signal: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`, {
    signal: AbortSignal.any([signal, AbortSignal.timeout(8000)]),
    cache: 'no-store',
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw new Error(`The API returned HTTP ${response.status}.`)
  }

  const body: Partial<HealthResponse> | null = await response.json()

  if (body?.status !== 'healthy' || body.service !== 'golf-performance-api') {
    throw new Error('The API returned an unexpected health response.')
  }

  return { status: body.status, service: body.service }
}
