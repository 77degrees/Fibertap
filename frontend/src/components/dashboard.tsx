'use client'

export function Dashboard() {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Fibertap</h1>
        <p className="text-gray-600">Personal data privacy monitoring</p>
      </header>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Stats Cards */}
        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-sm font-medium text-gray-500">Family Members</h2>
          <p className="mt-2 text-3xl font-semibold text-gray-900">0</p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-sm font-medium text-gray-500">Active Exposures</h2>
          <p className="mt-2 text-3xl font-semibold text-red-600">0</p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-sm font-medium text-gray-500">Removals In Progress</h2>
          <p className="mt-2 text-3xl font-semibold text-yellow-600">0</p>
        </div>
      </div>

      <section className="mt-8">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Recent Exposures</h2>
        <div className="rounded-lg bg-white p-6 shadow">
          <p className="text-gray-500">No exposures detected yet. Add family members to start monitoring.</p>
        </div>
      </section>

      <section className="mt-8">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Family Members</h2>
        <div className="rounded-lg bg-white p-6 shadow">
          <p className="text-gray-500">No family members added yet.</p>
          <button className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
            Add Family Member
          </button>
        </div>
      </section>
    </div>
  )
}
