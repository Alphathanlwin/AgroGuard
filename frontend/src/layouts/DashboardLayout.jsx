import { useEffect, useState } from 'react'
import { Menu } from 'lucide-react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from '../components/Sidebar.jsx'

function DashboardLayout() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    setMobileSidebarOpen(false)
  }, [location.pathname])

  return (
    <div className="min-h-screen bg-gradient-to-br from-myanglow-sage/35 via-white to-myanglow-soft/25 text-slate-900">
      <Sidebar
        mobileSidebarOpen={mobileSidebarOpen}
        onClose={() => setMobileSidebarOpen(false)}
      />

      {mobileSidebarOpen ? (
        <button
          type="button"
          aria-label="Close sidebar"
          className="fixed inset-0 z-30 bg-slate-900/20 backdrop-blur-[1px] lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      ) : null}

      <div className="lg:pl-72">
        <button
          type="button"
          aria-label="Open sidebar"
          className="fixed left-4 top-4 z-20 inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-myanglow-sage bg-white text-myanglow-navy shadow-sm transition hover:border-myanglow-soft hover:bg-myanglow-sage/40 lg:hidden"
          onClick={() => setMobileSidebarOpen(true)}
        >
          <Menu size={20} />
        </button>

        <main className="px-4 pb-6 pt-20 sm:px-6 lg:px-8 lg:py-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
