import { useState, useEffect, useCallback, useMemo } from 'react'
import { Line } from 'react-chartjs-2'
import { useLanguage } from '../contexts/LanguageContext.jsx'
import { API_BASE_URL, API_ENABLED } from '../api.js'
import WokwiSensorControls from './WokwiSensorControls.jsx'
import {
  Droplets,
  FlaskConical,
  Sun,
  RefreshCw,
  Timer,
} from 'lucide-react'

const HOURS = 12

function generateLabels() {
  const now = new Date()
  const labels = []
  for (let i = HOURS - 1; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 60 * 60000)
    labels.push(
      `${t.getHours().toString().padStart(2, '0')}:${t.getMinutes().toString().padStart(2, '0')}`
    )
  }
  return labels
}

function generateData(count, base, variance, min, max) {
  const data = []
  let val = base
  for (let i = 0; i < count; i++) {
    val += (Math.random() - 0.5) * variance
    val = Math.max(min, Math.min(max, val))
    data.push(Math.round(val * 10) / 10)
  }
  return data
}

function randomWalk(current, variance, min, max) {
  const val = current + (Math.random() - 0.5) * variance
  return Math.round(Math.max(min, Math.min(max, val)) * 10) / 10
}

function getSoilMoistureStatus(val, t) {
  if (val <= 34) return {
    label: t('iot.dry'),
    color: '#D97706',
    dotColor: 'bg-amber-500',
    badge: 'bg-amber-50 text-amber-700 border-amber-200/60',
    bar: 'linear-gradient(90deg, #D97706, #F59E0B)',
  }
  if (val <= 90) return {
    label: t('iot.normal'),
    color: '#2E7D32',
    dotColor: 'bg-emerald-500',
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200/60',
    bar: 'linear-gradient(90deg, #2E7D32, #4ADE80)',
  }
  return {
    label: t('iot.tooWet'),
    color: '#E11D48',
    dotColor: 'bg-rose-500',
    badge: 'bg-rose-50 text-rose-700 border-rose-200/60',
    bar: 'linear-gradient(90deg, #0EA5E9, #38BDF8)',
  }
}

function getPHStatus(val, t) {
  if (val < 5.5) return {
    label: t('iot.acidic'),
    color: '#D97706',
    dotColor: 'bg-amber-500',
    badge: 'bg-amber-50 text-amber-700 border-amber-200/60',
  }
  if (val <= 7.5) return {
    label: t('iot.suitable'),
    color: '#2E7D32',
    dotColor: 'bg-emerald-500',
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200/60',
  }
  return {
    label: t('iot.alkaline'),
    color: '#E11D48',
    dotColor: 'bg-rose-500',
    badge: 'bg-rose-50 text-rose-700 border-rose-200/60',
  }
}

function getLightStatus(val, t) {
  if (val <= 19) return {
    label: t('iot.lowLight'),
    color: '#D97706',
    dotColor: 'bg-amber-500',
    badge: 'bg-amber-50 text-amber-700 border-amber-200/60',
    bar: 'linear-gradient(90deg, #6B7280, #9CA3AF)',
  }
  if (val <= 85) return {
    label: t('iot.suitableLight'),
    color: '#2E7D32',
    dotColor: 'bg-emerald-500',
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200/60',
    bar: 'linear-gradient(90deg, #D97706, #FBBF24)',
  }
  return {
    label: t('iot.tooBright'),
    color: '#D97706',
    dotColor: 'bg-amber-500',
    badge: 'bg-amber-50 text-amber-700 border-amber-200/60',
    bar: 'linear-gradient(90deg, #D97706, #FBBF24)',
  }
}

export default function IoTSimulation() {
  const { t, language } = useLanguage()
  const [labels, setLabels] = useState(generateLabels)
  const [soilHistory, setSoilHistory] = useState(() => generateData(HOURS, 60, 14, 10, 95))
  const [phActualHistory, setPhActualHistory] = useState(() => generateData(HOURS, 6.5, 1.5, 3, 9))
  const [lightHistory, setLightHistory] = useState(() => generateData(HOURS, 55, 12, 5, 95))
  const [soilMoisture, setSoilMoisture] = useState(62.3)
  const [soilPH, setSoilPH] = useState(6.8)
  const [lightIntensity, setLightIntensity] = useState(55.7)
  const [temperature, setTemperature] = useState(28)
  const [humidity, setHumidity] = useState(65)
  const [isSimulating, setIsSimulating] = useState(true)
  const [networkMode, setNetworkMode] = useState('lorawan')
  const [isApplying, setIsApplying] = useState(false)
  const [syncStatus, setSyncStatus] = useState('')
  const [draft, setDraft] = useState({
    soilMoisture: 62.3,
    soilPH: 6.8,
    lightIntensity: 55.7,
    temperature: 28,
    humidity: 65,
  })

  const addDataPoint = useCallback(() => {
    const now = new Date()
    const label =
      `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

    const newSoil = randomWalk(soilMoisture, 6, 5, 95)
    const newPH = randomWalk(soilPH, 0.4, 3.5, 9.0)
    const newLight = randomWalk(lightIntensity, 7, 0, 100)
    const newTemperature = randomWalk(temperature, 1.5, 8, 42)
    const newHumidity = randomWalk(humidity, 4, 15, 98)

    setLabels(prev => [...prev.slice(1), label])
    setSoilHistory(prev => [...prev.slice(1), newSoil])
    setPhActualHistory(prev => [...prev.slice(1), newPH])
    setLightHistory(prev => [...prev.slice(1), newLight])
    setSoilMoisture(newSoil)
    setSoilPH(newPH)
    setLightIntensity(newLight)
    setTemperature(newTemperature)
    setHumidity(newHumidity)
    setDraft({
      soilMoisture: newSoil,
      soilPH: newPH,
      lightIntensity: newLight,
      temperature: newTemperature,
      humidity: newHumidity,
    })
    setSyncStatus('')
  }, [soilMoisture, soilPH, lightIntensity, temperature, humidity])

  useEffect(() => {
    if (!isSimulating) return
    const interval = setInterval(addDataPoint, 5000)
    return () => clearInterval(interval)
  }, [isSimulating, addDataPoint])

  const chartData = useMemo(() => ({
    labels,
    datasets: [
      {
        label: t('iot.soilMoisture'),
        data: soilHistory,
        borderColor: '#2E7D32',
        backgroundColor: 'rgba(46, 125, 50, 0.10)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 6,
        pointBackgroundColor: '#2E7D32',
      },
      {
        label: t('iot.soilPh'),
        data: phHistory,
        borderColor: '#8E44AD',
        backgroundColor: 'rgba(142, 68, 173, 0.08)',
        borderWidth: 2.5,
        borderDash: [5, 3],
        fill: true,
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 6,
        pointBackgroundColor: '#8E44AD',
      },
      {
        label: t('iot.light'),
        data: lightHistory,
        borderColor: '#F39C12',
        backgroundColor: 'rgba(243, 156, 18, 0.08)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 6,
        pointBackgroundColor: '#F39C12',
      },
    ],
  }), [labels, soilHistory, phHistory, lightHistory, language])

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 400 },
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        align: 'end',
        labels: {
          usePointStyle: true,
          padding: 16,
          font: { family: 'Outfit, sans-serif', size: 11 },
          color: '#374151',
        },
      },
      tooltip: {
        backgroundColor: '#0B252C',
        titleFont: { family: 'Outfit, sans-serif' },
        bodyFont: { family: 'Outfit, sans-serif' },
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
        ticks: {
          font: { family: 'Outfit, sans-serif', size: 10 },
          color: '#6B7280',
          maxTicksLimit: 8,
          autoSkip: true,
          maxRotation: 0,
        },
      },
      y: {
        min: 0,
        max: 100,
        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
        ticks: {
          font: { family: 'Outfit, sans-serif', size: 11 },
          color: '#6B7280',
          stepSize: 10,
          callback: (v) => v + '%',
        },
        title: {
          display: true,
          text: t('iot.percentage'),
          font: { family: 'Outfit, sans-serif', size: 11 },
          color: '#374151',
        },
      },
    },
  }), [language])

  const smStatus = getSoilMoistureStatus(soilMoisture, t)
  const phStatus = getPHStatus(soilPH, t)
  const ltStatus = getLightStatus(lightIntensity, t)

  const updateDraft = (key, value) => {
    setIsSimulating(false)
    setSyncStatus('')
    setDraft((current) => ({ ...current, [key]: value }))
  }

  const updateNetworkMode = (mode) => {
    setIsSimulating(false)
    setSyncStatus('')
    setNetworkMode(mode)
  }

  const applyDraftReading = async () => {
    setIsSimulating(false)
    setIsApplying(true)

    const now = new Date()
    const label =
      `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

    setLabels((previous) => [...previous.slice(1), label])
    setSoilHistory((previous) => [...previous.slice(1), draft.soilMoisture])
    setPhActualHistory((previous) => [...previous.slice(1), draft.soilPH])
    setLightHistory((previous) => [...previous.slice(1), draft.lightIntensity])
    setSoilMoisture(draft.soilMoisture)
    setSoilPH(draft.soilPH)
    setLightIntensity(draft.lightIntensity)
    setTemperature(draft.temperature)
    setHumidity(draft.humidity)

    if (!API_ENABLED) {
      setSyncStatus('local')
      setIsApplying(false)
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/observations/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: Number(import.meta.env.VITE_WOKWI_DEVICE_ID || 1),
          event_id: `dashboard-${networkMode}-${Date.now()}`,
          temperature: draft.temperature,
          humidity: draft.humidity,
          soil_moisture: draft.soilMoisture,
          ph: draft.soilPH,
          light: draft.lightIntensity,
          recorded_at: now.toISOString(),
        }),
      })

      if (!response.ok) {
        throw new Error(`Observation upload failed with ${response.status}`)
      }
      setSyncStatus('backend')
    } catch {
      setSyncStatus('local')
    } finally {
      setIsApplying(false)
    }
  }

  return (
    <section className="iot-simulation">
      <div className="max-w-7xl mx-auto flex flex-col gap-4 lg:gap-5">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-xl lg:text-2xl font-semibold m-0" style={{ color: '#1E5E3A' }}>
              {t('iot.title')}
            </h2>
            <p className="text-slate-500 mt-0.5 text-xs lg:text-sm">
              {t('iot.subtitle')}
            </p>
          </div>
          <div className="flex items-center gap-2.5">
            <div
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${
                isSimulating
                  ? 'bg-emerald-50 border-emerald-200/60 text-emerald-700'
                  : 'bg-rose-50 border-rose-200/60 text-rose-700'
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${isSimulating ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}
              />
              {isSimulating ? t('iot.live') : t('iot.paused')}
            </div>
            <button
              onClick={() => setIsSimulating((s) => !s)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border border-slate-200 bg-white text-slate-700 hover:border-emerald-300 hover:text-emerald-700 transition-all cursor-pointer"
              style={{ fontFamily: 'Outfit, sans-serif' }}
            >
              <RefreshCw size={13} />
              {isSimulating ? t('iot.pause') : t('iot.resume')}
            </button>
          </div>
        </div>

        <WokwiSensorControls
          draft={draft}
          networkMode={networkMode}
          onChange={updateDraft}
          onNetworkModeChange={updateNetworkMode}
          onApply={applyDraftReading}
          isApplying={isApplying}
          syncStatus={syncStatus}
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200 border border-slate-100">
            <div className="flex items-center gap-3 mb-1">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 bg-blue-50">
                <Droplets size={20} className="text-blue-600" />
              </div>
            </div>
            <div className="text-sm font-medium text-slate-500 mb-1">{t('iot.soilMoisture')}</div>
            <div className="text-3xl font-extrabold text-slate-800 tracking-tight">
              {soilMoisture.toFixed(1)}<span className="text-lg font-medium text-slate-400 ml-0.5">%</span>
            </div>
            <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold border my-4 ${smStatus.badge}`}>
              <span className={`w-2 h-2 rounded-full animate-pulse mr-2 ${smStatus.dotColor}`} />
              {smStatus.label}
            </div>
            <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${soilMoisture}%`, background: smStatus.bar }}
              />
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200 border border-slate-100">
            <div className="flex items-center gap-3 mb-1">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 bg-purple-50">
                <FlaskConical size={20} className="text-purple-600" />
              </div>
            </div>
            <div className="text-sm font-medium text-slate-500 mb-1">{t('iot.soilPh')}</div>
            <div className="text-3xl font-extrabold text-slate-800 tracking-tight">
              {soilPH.toFixed(1)}
              <span className="text-lg font-medium text-slate-400 ml-0.5">pH</span>
            </div>
            <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold border my-4 ${phStatus.badge}`}>
              <span className={`w-2 h-2 rounded-full animate-pulse mr-2 ${phStatus.dotColor}`} />
              {phStatus.label}
            </div>
            <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500 relative"
                style={{
                  width: `${(soilPH / 14) * 100}%`,
                  background: `linear-gradient(90deg,
                    rgba(217,119,6,0.35) 0%,
                    rgba(217,119,6,0.35) 39.3%,
                    rgba(46,125,50,0.35) 39.3%,
                    rgba(46,125,50,0.35) 53.6%,
                    rgba(225,29,72,0.35) 53.6%,
                    rgba(225,29,72,0.35) 100%)`,
                }}
              />
              <div
                className="h-full rounded-full transition-all duration-500 relative"
                style={{
                  width: `${(soilPH / 14) * 100}%`,
                  background: phStatus.color,
                }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-400 mt-0.5 px-0.5">
              <span>0</span>
              <span>5.5</span>
              <span>7.5</span>
              <span>14</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200 border border-slate-100">
            <div className="flex items-center gap-3 mb-1">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 bg-amber-50">
                <Sun size={20} className="text-amber-600" />
              </div>
            </div>
            <div className="text-sm font-medium text-slate-500 mb-1">{t('iot.light')}</div>
            <div className="text-3xl font-extrabold text-slate-800 tracking-tight">
              {lightIntensity.toFixed(1)}<span className="text-lg font-medium text-slate-400 ml-0.5">%</span>
            </div>
            <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold border my-4 ${ltStatus.badge}`}>
              <span className={`w-2 h-2 rounded-full animate-pulse mr-2 ${ltStatus.dotColor}`} />
              {ltStatus.label}
            </div>
            <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${lightIntensity}%`, background: ltStatus.bar }}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 lg:p-6 lg:pb-4 w-full">
          <div className="mb-3">
            <h2 className="m-0 text-base font-bold text-slate-800">{t('iot.chartTitle')}</h2>
            <p className="mb-0 mt-0.5 text-xs text-slate-500">{t('iot.chartSubtitle')}</p>
          </div>
          <div className="h-[300px] lg:h-[360px]">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-emerald-50/50 border border-emerald-100 text-sm text-[#1C5D39]">
          <Timer size={15} className="shrink-0" />
          {t('iot.refresh')}{' '}
          <strong>{labels[labels.length - 1]}</strong>
        </div>
      </div>
    </section>
  )
}
