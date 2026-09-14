import { useState } from 'react'
import { Mail, Lock, ArrowRight, Loader2, AlertCircle, X, UserRound, Leaf } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext.jsx'
import { useLanguage } from '../contexts/LanguageContext.jsx'

export default function AuthModal({ initialMode = 'signin', onClose, onSuccess }) {
  const [mode, setMode] = useState(initialMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { login, register } = useAuth()
  const { t } = useLanguage()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!email || !password || (mode === 'signup' && !confirmPassword)) {
      setError(t('auth.fillFields') || 'Please fill in all fields')
      return
    }

    if (mode === 'signup' && password !== confirmPassword) {
      setError(t('auth.passwordMismatch') || 'Passwords do not match')
      return
    }

    try {
      setError('')
      setLoading(true)
      
      await new Promise(resolve => setTimeout(resolve, 800))
      
      if (mode === 'signin') {
        login(email, password)
      } else {
        register(email, password)
      }
      
      onSuccess()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const changeMode = (nextMode) => {
    setError('')
    setMode(nextMode)
  }

  return (
    <div 
      className="fixed inset-0 z-[100] grid place-items-center bg-myanglow-navy/45 p-4 backdrop-blur-md" 
      onMouseDown={onClose}
    >
      <section
        role="dialog"
        aria-modal="true"
        className="relative w-full max-w-md overflow-hidden rounded-[2rem] border border-white/80 bg-white/95 p-6 shadow-[0_30px_100px_rgba(12,46,61,0.3)] backdrop-blur-xl sm:p-8"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-myanglow-lime/20 blur-2xl" />
        
        <button 
          type="button" 
          onClick={onClose} 
          className="absolute right-5 top-5 grid h-10 w-10 place-items-center rounded-xl text-slate-500 transition hover:bg-myanglow-sage/40 hover:text-myanglow-navy"
        >
          <X size={19} />
        </button>

        <div className="relative">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-myanglow-forest text-white shadow-lg shadow-myanglow-forest/20">
            <Leaf size={22} />
          </div>
          
          <h2 className="mt-5 text-3xl font-semibold text-myanglow-navy">
            {mode === 'signin' 
              ? (t('auth.welcomeBack') || 'Welcome Back') 
              : (t('auth.createAccount') || 'Create Account')}
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            {mode === 'signin' 
              ? (t('auth.loginSubtitle') || 'Sign in to access your AgroGuard dashboard')
              : (t('auth.registerSubtitle') || 'Join AgroGuard and start managing your farm')}
          </p>

          <div className="mt-6 grid grid-cols-2 rounded-2xl bg-myanglow-sage/35 p-1">
            <button 
              type="button" 
              onClick={() => changeMode('signin')} 
              className={`rounded-xl px-4 py-2.5 text-sm font-semibold transition ${mode === 'signin' ? 'bg-white text-myanglow-forest shadow-sm' : 'text-slate-500 hover:text-myanglow-navy'}`}
            >
              {t('auth.loginBtn') || 'Sign In'}
            </button>
            <button 
              type="button" 
              onClick={() => changeMode('signup')} 
              className={`rounded-xl px-4 py-2.5 text-sm font-semibold transition ${mode === 'signup' ? 'bg-white text-myanglow-forest shadow-sm' : 'text-slate-500 hover:text-myanglow-navy'}`}
            >
              {t('auth.registerBtn') || 'Sign Up'}
            </button>
          </div>

          {error && (
            <div className="mt-5 flex items-start gap-3 rounded-2xl bg-red-50 p-4 text-sm text-red-600 border border-red-100">
              <AlertCircle size={18} className="mt-0.5 shrink-0" />
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <label className="block text-sm font-semibold text-myanglow-navy">
              {t('auth.email') || 'Email Address'}
              <span className="mt-2 flex items-center gap-3 rounded-2xl border border-myanglow-sage bg-white px-4 focus-within:border-myanglow-medium focus-within:ring-4 focus-within:ring-myanglow-sage/30">
                <Mail size={17} className="text-myanglow-medium" />
                <input 
                  required 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="farmer@agroguard.com" 
                  className="w-full border-0 bg-transparent py-3.5 text-sm font-normal outline-none" 
                  disabled={loading}
                />
              </span>
            </label>

            <label className="block text-sm font-semibold text-myanglow-navy">
              {t('auth.password') || 'Password'}
              <span className="mt-2 flex items-center gap-3 rounded-2xl border border-myanglow-sage bg-white px-4 focus-within:border-myanglow-medium focus-within:ring-4 focus-within:ring-myanglow-sage/30">
                <Lock size={17} className="text-myanglow-medium" />
                <input 
                  required 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••" 
                  className="w-full border-0 bg-transparent py-3.5 text-sm font-normal outline-none" 
                  disabled={loading}
                />
              </span>
            </label>

            {mode === 'signup' && (
              <label className="block text-sm font-semibold text-myanglow-navy">
                {t('auth.confirmPassword') || 'Confirm Password'}
                <span className="mt-2 flex items-center gap-3 rounded-2xl border border-myanglow-sage bg-white px-4 focus-within:border-myanglow-medium focus-within:ring-4 focus-within:ring-myanglow-sage/30">
                  <Lock size={17} className="text-myanglow-medium" />
                  <input 
                    required 
                    type="password" 
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••" 
                    className="w-full border-0 bg-transparent py-3.5 text-sm font-normal outline-none" 
                    disabled={loading}
                  />
                </span>
              </label>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-2xl bg-myanglow-forest px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-myanglow-forest/20 transition hover:-translate-y-0.5 hover:bg-myanglow-medium disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : (
                mode === 'signin' ? (t('auth.loginBtn') || 'Sign In') : (t('auth.registerBtn') || 'Sign Up')
              )}
            </button>
          </form>
        </div>
      </section>
    </div>
  )
}
