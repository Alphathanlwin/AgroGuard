import {
  ArrowRight,
  Activity,
  Bot,
  CheckCircle2,
  ChevronDown,
  Leaf,
  LineChart,
  LockKeyhole,
  Mail,
  Radar,
  RadioTower,
  ScanSearch,
  Sparkles,
  Sprout,
  TimerReset,
  TrendingUp,
  UserRound,
  X,
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

import AuthModal from './components/AuthModal.jsx'
import { useAuth } from './contexts/AuthContext.jsx'

const capabilities = [
  {
    icon: Radar,
    title: 'Satellite crop intelligence',
    description: 'Turn NDVI vegetation signals into clear field-health insights and seasonal trends.',
  },
  {
    icon: Sprout,
    title: 'Smart crop recommendations',
    description: 'Match soil, rainfall, and temperature conditions with suitable crops and yield estimates.',
  },
  {
    icon: ScanSearch,
    title: 'Plant disease detection',
    description: 'Upload a leaf image and receive an easy-to-understand health assessment and guidance.',
  },
  {
    icon: Bot,
    title: 'Agriculture AI assistant',
    description: 'Give farmers one place to ask questions and make confident, data-supported decisions.',
  },
  {
    icon: RadioTower,
    title: 'IoT sensor simulation',
    description: 'Monitor simulated soil moisture, pH, and light readings through live charts and sensor status updates.',
  },
]

const signals = [
  { label: 'Vegetation health', value: '0.71', icon: Leaf },
  { label: 'Crop condition match', value: '94%', icon: Sparkles },
  { label: 'Field insights', value: 'Live', icon: LineChart },
]

const impactHighlights = [
  {
    icon: Activity,
    title: 'Earlier field awareness',
    description: 'Bring satellite, sensor, and crop-health signals together so changes are easier to notice and understand.',
  },
  {
    icon: TimerReset,
    title: 'Faster daily decisions',
    description: 'Replace scattered checks with one clear workspace for recommendations, diagnosis, and practical next steps.',
  },
  {
    icon: TrendingUp,
    title: 'Stronger growing plans',
    description: 'Use regional history and live field indicators to plan crops with more context and confidence.',
  },
]

function LandingPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { currentUser } = useAuth()
  const [authMode, setAuthMode] = useState(null)

  // Open modal automatically if redirected from protected route
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const mode = params.get('auth')
    if (mode === 'signin' || mode === 'signup') {
      setAuthMode(mode)
    }
  }, [location])

  const openAuth = (mode = 'signin') => {
    if (currentUser) {
      navigate('/dashboard')
    } else {
      setAuthMode(mode)
    }
  }

  const closeAuth = () => {
    setAuthMode(null)
    // Remove the ?auth= param from the URL if present
    if (location.search.includes('auth=')) {
      navigate('/', { replace: true })
    }
  }

  return (
    <main className="min-h-screen overflow-hidden bg-gradient-to-br from-myanglow-sage via-white to-myanglow-soft/40 text-myanglow-navy">
      <section className="relative min-h-screen">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgba(154,214,76,0.28),transparent_25%),radial-gradient(circle_at_88%_12%,rgba(90,176,63,0.18),transparent_24%),radial-gradient(circle_at_65%_88%,rgba(161,188,178,0.28),transparent_30%)]" />
        <div className="absolute -left-20 top-52 h-56 w-56 rounded-full border border-myanglow-soft/30" />
        <div className="absolute -left-12 top-60 h-40 w-40 rounded-full border border-myanglow-soft/30" />

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <nav className="flex min-h-28 w-full items-center justify-between py-8 sm:py-9">
            <div className="flex items-center gap-4">
              <div className="grid h-14 w-14 place-items-center rounded-[1.2rem] bg-myanglow-forest text-white shadow-lg shadow-myanglow-forest/20">
                <Leaf size={26} />
              </div>
              <div>
                <p
                  className="text-[1.15rem] font-semibold tracking-[0.14em] text-myanglow-medium"
                  style={{ fontFamily: 'Trebuchet MS, "Segoe UI", sans-serif' }}
                >
                  AgroGuard
                </p>
                <p className="mt-1 text-sm text-slate-500">Intelligence for every field</p>
              </div>
            </div>

            <div className="hidden items-center gap-9 text-base font-medium text-slate-600 md:flex lg:gap-11">
              <a href="#capabilities" className="transition hover:text-myanglow-forest">Capabilities</a>
              <a href="#impact" className="transition hover:text-myanglow-forest">Impact</a>
              <button type="button" onClick={() => openAuth('signin')} className="rounded-2xl bg-myanglow-forest px-6 py-3.5 text-base font-semibold text-white shadow-lg shadow-myanglow-forest/15 transition hover:bg-myanglow-medium">
                {currentUser ? 'Dashboard' : 'Sign in'}
              </button>
            </div>
          </nav>

          <div className="grid items-center gap-12 pb-14 pt-5 lg:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)] lg:pb-16 lg:pt-7">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-myanglow-sage bg-white/75 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-myanglow-forest shadow-sm backdrop-blur">
                <Sparkles size={14} />
                Built for smarter farming
              </div>

              <h1 className="mt-7 text-5xl font-semibold leading-[1.05] tracking-tight text-myanglow-navy sm:text-6xl lg:text-7xl">
                From field data to
                <span className="mt-2 block text-myanglow-forest">better harvests.</span>
              </h1>

              <p className="mt-7 max-w-xl text-base leading-8 text-slate-600 sm:text-lg">
                One intelligent workspace that combines satellite monitoring, crop recommendations,
                disease detection, market calculations, and practical AI guidance for farmers.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <button
                  type="button"
                  onClick={() => openAuth('signup')}
                  className="inline-flex items-center justify-center gap-2 rounded-2xl bg-myanglow-forest px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-myanglow-forest/20 transition hover:-translate-y-0.5 hover:bg-myanglow-medium"
                >
                  {currentUser ? 'Go to Dashboard' : 'Start your farm'}
                </button>
                <a
                  href="#capabilities"
                  className="inline-flex items-center justify-center gap-2 rounded-2xl border border-myanglow-sage bg-white/85 px-6 py-3.5 text-sm font-semibold text-myanglow-navy transition hover:bg-myanglow-sage/35"
                >
                  See how it works <ChevronDown size={17} />
                </a>
              </div>

              <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-slate-600">
                {['Farmer focused', 'Data informed', 'Mobile ready'].map((item) => (
                  <span key={item} className="inline-flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-myanglow-medium" /> {item}
                  </span>
                ))}
              </div>
            </div>

            <div className="relative mx-auto w-full max-w-2xl lg:mx-0">
              <div className="absolute -inset-5 rounded-[2.5rem] bg-myanglow-lime/15 blur-2xl" />
              <div className="relative rounded-[2rem] border border-white/90 bg-white/80 p-4 shadow-[0_35px_90px_rgba(12,46,61,0.14)] backdrop-blur-xl sm:p-6">
                <div className="flex items-center justify-between border-b border-myanglow-sage/60 pb-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-myanglow-medium">Field intelligence</p>
                    <h2 className="mt-2 text-xl font-semibold text-myanglow-navy">Farm overview</h2>
                  </div>
                  <span className="inline-flex items-center gap-2 rounded-full bg-myanglow-sage/50 px-3 py-1.5 text-xs font-semibold text-myanglow-darkGreen">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-myanglow-brightLime" /> Active
                  </span>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  {signals.map(({ label, value, icon: Icon }) => (
                    <div key={label} className="rounded-2xl border border-myanglow-sage/70 bg-white p-4 shadow-sm">
                      <div className="flex items-center justify-between text-myanglow-forest">
                        <Icon size={18} />
                        <span className="text-[0.65rem] font-semibold uppercase tracking-wider text-slate-400">Insight</span>
                      </div>
                      <p className="mt-5 text-2xl font-semibold text-myanglow-navy">{value}</p>
                      <p className="mt-1 text-xs text-slate-500">{label}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-4 grid gap-4 sm:grid-cols-[1.25fr_0.75fr]">
                  <div className="overflow-hidden rounded-2xl border border-myanglow-sage/70 bg-gradient-to-br from-myanglow-sage/60 to-white p-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-myanglow-medium">Vegetation trend</p>
                        <p className="mt-2 text-sm text-slate-600">Healthy growth over six months</p>
                      </div>
                      <Radar size={24} className="text-myanglow-forest" />
                    </div>
                    <div className="mt-7 flex h-24 items-end gap-2">
                      {[38, 47, 43, 61, 72, 84, 78, 92].map((height, index) => (
                        <div key={index} className="flex-1 rounded-t-md bg-myanglow-forest/80" style={{ height: `${height}%` }} />
                      ))}
                    </div>
                  </div>

                  <div className="rounded-2xl bg-myanglow-navy p-5 text-white">
                    <Sprout size={25} className="text-myanglow-brightLime" />
                    <p className="mt-7 text-xs uppercase tracking-[0.2em] text-myanglow-grayGreen">Recommended</p>
                    <p className="mt-2 text-3xl font-semibold">Rice</p>
                    <p className="mt-2 text-sm text-myanglow-sage">94% field match</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="capabilities" className="relative flex min-h-screen scroll-mt-0 items-center bg-white/80 py-12 sm:py-14">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-myanglow-medium">One connected platform</p>
            <h2 className="mt-4 text-3xl font-semibold leading-tight text-myanglow-navy sm:text-4xl">Everything needed to understand the field and act faster.</h2>
          </div>

          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {capabilities.map(({ icon: Icon, title, description }, index) => (
              <article key={title} className="group rounded-[1.6rem] border border-myanglow-sage/80 bg-white p-6 shadow-[0_14px_40px_rgba(12,46,61,0.06)] transition hover:-translate-y-1 hover:shadow-[0_20px_50px_rgba(12,46,61,0.1)]">
                <div className="flex items-center justify-between">
                  <span className="grid h-12 w-12 place-items-center rounded-2xl bg-myanglow-sage/45 text-myanglow-forest transition group-hover:bg-myanglow-forest group-hover:text-white">
                    <Icon size={22} />
                  </span>
                  <span className="text-xs font-semibold text-myanglow-grayGreen">0{index + 1}</span>
                </div>
                <h3 className="mt-6 text-lg font-semibold text-myanglow-navy">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-500">{description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="impact" className="flex min-h-screen scroll-mt-0 items-center py-8 sm:py-10">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="impact-panel relative overflow-hidden rounded-[2rem] bg-myanglow-navy px-6 py-8 text-white shadow-[0_30px_80px_rgba(12,46,61,0.2)] sm:px-8 lg:px-10 lg:py-9">
            <div className="impact-orb absolute -right-20 -top-24 h-72 w-72 rounded-full bg-myanglow-lime/15 blur-3xl" />
            <div className="impact-orb impact-orb-delayed absolute -bottom-28 left-1/3 h-64 w-64 rounded-full bg-myanglow-soft/10 blur-3xl" />

            <div className="relative grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
              <div className="impact-reveal max-w-2xl">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-myanglow-brightLime">Connected field impact</p>
                <h2 className="mt-3 text-3xl font-semibold leading-tight sm:text-4xl">Turn field signals into confident action.</h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-myanglow-sage sm:text-base">AgroGuard combines monitoring, recommendations, disease support, and simulated sensor readings in one approachable platform.</p>
              </div>

              <div className="impact-reveal impact-reveal-delayed grid grid-cols-3 gap-3">
                {[
                  ['5', 'connected tools'],
                  ['24/7', 'field visibility'],
                  ['1', 'simple workspace'],
                ].map(([value, label]) => (
                  <div key={label} className="rounded-2xl border border-white/10 bg-white/10 p-3 text-center backdrop-blur-sm">
                    <p className="text-xl font-semibold text-myanglow-brightLime sm:text-2xl">{value}</p>
                    <p className="mt-1 text-xs leading-5 text-myanglow-sage">{label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative mt-6 grid gap-3 md:grid-cols-3">
              {impactHighlights.map(({ icon: Icon, title, description }, index) => (
                <article key={title} className="impact-card rounded-[1.25rem] border border-white/10 bg-white/[0.07] p-4 backdrop-blur-sm" style={{ animationDelay: `${180 + index * 120}ms` }}>
                  <div className="grid h-10 w-10 place-items-center rounded-xl bg-myanglow-brightLime text-myanglow-navy">
                    <Icon size={19} />
                  </div>
                  <h3 className="mt-3 text-base font-semibold">{title}</h3>
                  <p className="mt-1.5 text-xs leading-5 text-myanglow-sage sm:text-sm">{description}</p>
                </article>
              ))}
            </div>

            <div className="impact-reveal impact-reveal-delayed relative mt-6 flex flex-col gap-3 border-t border-white/10 pt-5 sm:flex-row sm:items-center sm:justify-between">
              <p className="max-w-xl text-sm leading-6 text-myanglow-sage">Start with your field overview, then explore the tools that matter most for today’s farming decisions.</p>
              <button type="button" onClick={() => openAuth('signup')} className="inline-flex shrink-0 items-center justify-center gap-2 rounded-2xl bg-myanglow-brightLime px-6 py-3.5 text-sm font-semibold text-myanglow-navy transition hover:-translate-y-1 hover:bg-white">
                Launch dashboard
              </button>
            </div>
          </div>
        </div>
      </section>
      
      {authMode && (
        <AuthModal 
          initialMode={authMode} 
          onClose={closeAuth} 
          onSuccess={() => navigate('/dashboard')} 
        />
      )}
    </main>
  )
}

export default LandingPage
