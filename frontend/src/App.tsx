import { useEffect, useState } from 'react'
import { getHealth, type HealthResponse } from './api'

type Connection =
  | { state: 'loading' }
  | { state: 'connected'; health: HealthResponse }
  | { state: 'error' }

const statusLabels = {
  loading: 'Checking connection…',
  connected: 'Connected',
  error: 'Connection error',
}

const statusColors = {
  loading: 'bg-amber-500',
  connected: 'bg-emerald-600',
  error: 'bg-red-700',
}

export default function App() {
  const [attempt, setAttempt] = useState(0)
  const [connection, setConnection] = useState<Connection>({ state: 'loading' })

  useEffect(() => {
    const controller = new AbortController()

    void getHealth(controller.signal)
      .then((health) => {
        if (!controller.signal.aborted) setConnection({ state: 'connected', health })
      })
      .catch(() => {
        if (!controller.signal.aborted) setConnection({ state: 'error' })
      })

    return () => controller.abort()
  }, [attempt])

  function retry() {
    setConnection({ state: 'loading' })
    setAttempt((previous) => previous + 1)
  }

  return (
    <main className="mx-auto flex min-h-dvh max-w-6xl flex-col justify-center gap-12 px-5 py-12 sm:px-10">
      <section className="hero relative isolate overflow-hidden rounded-[2rem] bg-[#153829] px-6 py-14 text-[#f8f7ef] sm:px-12 sm:py-20">
        <div className="course-lines absolute inset-0 -z-10" aria-hidden="true" />
        <h1 className="max-w-xl font-serif text-5xl leading-[0.98] tracking-tight sm:text-7xl">
          AI Golf Performance Intelligence
        </h1>
        <p className="mt-6 max-w-sm text-base leading-relaxed text-[#e1ebdb] sm:text-lg">
          A platform for understanding your performance on the course.
        </p>
      </section>

      <section aria-labelledby="api-heading" className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-[#d8ded4] bg-white p-6 sm:px-8">
        <div>
          <h2 id="api-heading" className="text-lg font-semibold">API connection</h2>
          <div role="status" aria-atomic="true" className="mt-2 text-sm text-[#3c5245]">
            <p className="flex items-center gap-2 font-medium">
              <span aria-hidden="true" className={`size-2.5 rounded-full ${statusColors[connection.state]}`} />
              {statusLabels[connection.state]}
            </p>
            {connection.state === 'connected' && <p className="mt-1">{connection.health.service}</p>}
            {connection.state === 'error' && <p className="mt-1">Check that the API is running, then try again.</p>}
          </div>
        </div>
        {connection.state === 'error' && (
          <button
            type="button"
            onClick={retry}
            className="min-h-11 rounded-lg bg-[#153829] px-4 text-sm font-semibold text-white hover:bg-[#25523b] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#153829]"
          >
            Retry connection
          </button>
        )}
      </section>
    </main>
  )
}
