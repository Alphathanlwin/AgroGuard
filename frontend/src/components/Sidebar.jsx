import { Home, LayoutDashboard, Radar, Sprout, ScanSearch, Bot, HeartPulse, Languages, RadioTower, LogOut } from 'lucide-react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useLanguage } from '../contexts/LanguageContext.jsx'
import { useAuth } from '../contexts/AuthContext.jsx'

const navItems = [
  { key: 'nav.landing', icon: Home, path: '/' },
  { key: 'nav.dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { key: 'nav.ndvi', icon: Radar, path: '/ndvi-analysis' },
  { key: 'nav.suggestion', icon: Sprout, path: '/crop-suggestion' },
  { key: 'nav.disease', icon: ScanSearch, path: '/disease-detection' },
  { key: 'nav.chat', icon: Bot, path: '/ai-chat' },
  { key: 'nav.iot', icon: RadioTower, path: '/iot-simulation' },
  { key: 'nav.updates', icon: HeartPulse, path: '/health-updates' },
]

function Sidebar({ mobileSidebarOpen, onClose }) {
  const { language, setLanguage, t } = useLanguage()
  const { currentUser, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-white/70 bg-white/90 backdrop-blur-xl transition-transform duration-300 ease-out lg:translate-x-0 ${
        mobileSidebarOpen ? 'translate-x-0 shadow-2xl shadow-myanglow-navy/10' : '-translate-x-full'
      }`}
    >
      <div className="flex items-start justify-between border-b border-myanglow-sage/70 px-6 py-6">
        <div>
          <p
            className="text-[1.25rem] font-semibold tracking-[0.14em] text-myanglow-medium"
            style={{ fontFamily: 'Trebuchet MS, "Segoe UI", sans-serif' }}
          >
            AgroGuard
          </p>
          <h2 className="mt-2 text-[1.15rem] font-semibold text-myanglow-navy">{t('sidebar.title')}</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            {t('sidebar.subtitle')}
          </p>
        </div>

        <button
          type="button"
          aria-label="Close sidebar"
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-myanglow-sage text-myanglow-navy transition hover:bg-myanglow-sage/40 lg:hidden"
          onClick={onClose}
        >
          ×
        </button>
      </div>

      <nav className="flex-1 space-y-2 px-4 py-5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.key}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-myanglow-forest text-white shadow-lg shadow-myanglow-forest/20'
                    : 'text-slate-600 hover:bg-myanglow-sage/60 hover:text-myanglow-navy',
                ].join(' ')
              }
            >
              <Icon size={18} />
              <span>{t(item.key)}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="border-t border-myanglow-sage/70 p-4 space-y-3">
        {currentUser && (
          <div className="flex items-center justify-between rounded-2xl bg-myanglow-sage/20 px-4 py-3">
            <div className="overflow-hidden">
              <p className="truncate text-sm font-semibold text-myanglow-navy">{currentUser.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="ml-2 shrink-0 rounded-xl bg-white p-2 text-red-500 transition hover:bg-red-50"
              title={t('auth.logout') || 'Log Out'}
            >
              <LogOut size={16} />
            </button>
          </div>
        )}

        <div className="flex items-center gap-1 rounded-2xl border border-myanglow-sage bg-white p-1">
          <Languages size={16} className="ml-2 shrink-0 text-myanglow-navy" />
          {['en', 'my'].map((code) => (
            <button
              key={code}
              type="button"
              onClick={() => setLanguage(code)}
              className={`flex-1 rounded-xl px-2 py-2 text-xs font-semibold transition ${language === code ? 'bg-myanglow-forest text-white' : 'text-slate-600 hover:bg-myanglow-sage/40'}`}
            >
              {t(code === 'en' ? 'language.english' : 'language.burmese')}
            </button>
          ))}
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
