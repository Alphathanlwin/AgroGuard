import { useEffect, useMemo, useState } from 'react'
import { BarChart3, CloudRain, Leaf, MapPinned, Sprout, TrendingUp } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext.jsx'
import { API_BASE_URL, DEMO_FIELD_ID } from '../api.js'

const cropDistribution = [
	{ crop: 'Rice', percent: 42 },
	{ crop: 'Maize', percent: 23 },
	{ crop: 'Pulses', percent: 19 },
	{ crop: 'Sesame', percent: 16 },
]

const yieldByCrop = [
	{ crop: 'Rice', yield: 4.1 },
	{ crop: 'Maize', yield: 3.2 },
	{ crop: 'Pulses', yield: 2.6 },
	{ crop: 'Sesame', yield: 1.9 },
]

function Dashboard() {
	const { t } = useLanguage()
	const [stats, setStats] = useState(null)
	const [growth, setGrowth] = useState([])
	const [growthScenario, setGrowthScenario] = useState('healthy')

	useEffect(() => {
		let active = true
		Promise.all([
			fetch(`${API_BASE_URL}/dashboard/stats`).then((response) => response.ok ? response.json() : null),
			fetch(`${API_BASE_URL}/fields/${DEMO_FIELD_ID}/growth/timeline`).then((response) => response.ok ? response.json() : []),
		]).then(([nextStats, nextGrowth]) => {
			if (!active) return
			setStats(nextStats)
			setGrowth(nextGrowth || [])
		}).catch(() => {
			if (!active) return
			setStats(null)
			setGrowth([])
		})
		return () => { active = false }
	}, [])

	const overviewCards = useMemo(() => [
		{ key: 'dash.townships', value: stats ? String(stats.totalFields ?? stats.overview?.townships ?? 0) : '112', icon: MapPinned, accent: 'text-emerald-700', bg: 'bg-emerald-100' },
		{ key: 'dash.records', value: stats ? String(stats.totalAssessments ?? stats.overview?.records ?? 0) : '24,860', icon: BarChart3, accent: 'text-sky-700', bg: 'bg-sky-100' },
		{ key: 'dash.yield', value: stats?.overview?.yield && stats.overview.yield !== 'demo' ? `${stats.overview.yield} t/ha` : 'Demo rules', icon: Sprout, accent: 'text-amber-700', bg: 'bg-amber-100' },
		{ key: 'dash.rainfall', value: stats?.overview?.rainfall && stats.overview.rainfall !== 'seeded' ? `${stats.overview.rainfall} mm` : 'Seeded', icon: CloudRain, accent: 'text-indigo-700', bg: 'bg-indigo-100' },
	], [stats])
	const fieldStatus = stats?.fieldStatuses?.[0]
	const cropItems = stats?.cropDistribution?.length ? stats.cropDistribution : cropDistribution
	const yieldItems = stats?.yieldByCrop?.length ? stats.yieldByCrop : yieldByCrop

	const startGrowth = async () => {
		try {
			const response = await fetch(`${API_BASE_URL}/fields/${DEMO_FIELD_ID}/growth/start`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ scenario: growthScenario }),
			})
			if (response.ok) setGrowth(await response.json())
		} catch {
			// Keep the last replay visible when the optional API is unavailable.
		}
	}

	return (
		<div className="space-y-6">
			<section className="rounded-[2rem] border border-white/80 bg-white/90 p-6 shadow-[0_20px_60px_rgba(12,46,61,0.08)] backdrop-blur-xl">
				<div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
					<div>
						<p className="text-xs font-semibold uppercase tracking-[0.4em] text-myanglow-medium">
							AgroGuard Analytics
						</p>
						<h2 className="mt-3 text-3xl font-semibold text-myanglow-navy">{t('dash.title')}</h2>
						<p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600 sm:text-base">
							{t('dash.subtitle')}
						</p>
					</div>

					<div className="inline-flex items-center gap-2 rounded-full border border-myanglow-sage bg-myanglow-sage/40 px-4 py-2 text-sm font-medium text-myanglow-darkGreen">
						<TrendingUp size={16} />
						Last 30 days trend
					</div>
				</div>
			</section>

			<section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
				<article className="rounded-[1.8rem] border border-white/80 bg-white/90 p-6 shadow-[0_16px_50px_rgba(12,46,61,0.08)] backdrop-blur-xl">
					<div className="flex items-start justify-between gap-4">
						<div>
							<p className="text-xs font-semibold uppercase tracking-[0.3em] text-myanglow-medium">Live assessment</p>
							<h3 className="mt-2 text-xl font-semibold text-myanglow-navy">{fieldStatus?.fieldName || 'Demo field'}</h3>
						</div>
						<span className={`rounded-full px-3 py-1 text-xs font-semibold ${fieldStatus?.status === 'critical' ? 'bg-red-100 text-red-700' : fieldStatus?.status === 'warning' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
							{fieldStatus?.status || 'healthy'}
						</span>
					</div>
					<p className="mt-4 text-sm leading-6 text-slate-600">{fieldStatus?.recommendation || 'Assessment recommendation will appear when the backend is available.'}</p>
					{fieldStatus?.healthScore != null ? <p className="mt-4 text-sm font-semibold text-myanglow-forest">Health score: {fieldStatus.healthScore}/100</p> : null}
				</article>

				<article className="rounded-[1.8rem] border border-white/80 bg-white/90 p-6 shadow-[0_16px_50px_rgba(12,46,61,0.08)] backdrop-blur-xl">
					<div className="flex flex-wrap items-center justify-between gap-3">
						<div>
							<p className="text-xs font-semibold uppercase tracking-[0.3em] text-myanglow-medium">Growth comparison</p>
							<h3 className="mt-2 text-xl font-semibold text-myanglow-navy">Illustrative 12-month replay</h3>
						</div>
						<div className="flex gap-2">
							<select value={growthScenario} onChange={(event) => setGrowthScenario(event.target.value)} className="rounded-xl border border-myanglow-sage bg-white px-3 py-2 text-sm">
								<option value="healthy">Healthy</option>
								<option value="dry-soil">Dry soil</option>
								<option value="heat-stress">Heat stress</option>
							</select>
							<button type="button" onClick={startGrowth} className="rounded-xl bg-myanglow-forest px-3 py-2 text-sm font-semibold text-white">Replay</button>
						</div>
					</div>
					<div className="mt-4 grid gap-3 sm:grid-cols-2">
						{growth.map((simulation) => {
							const lastEvent = simulation.events?.[simulation.events.length - 1]
							return <div key={simulation.id} className="rounded-xl border border-myanglow-sage/60 bg-myanglow-sage/20 p-3"><p className="text-sm font-semibold text-myanglow-navy">{simulation.scenarioType.replace('_', ' ')}</p><p className="mt-1 text-xs text-slate-500">{simulation.isIllustrative ? 'Illustrative' : 'Measured'} · {lastEvent?.growthStage || 'Preparing'}</p><p className="mt-2 text-lg font-semibold text-myanglow-forest">{lastEvent?.healthIndex ?? '—'}/100</p></div>
						})}
					</div>
				</article>
			</section>

			<section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
				{overviewCards.map((card) => {
					const Icon = card.icon
					return (
						<article
							key={card.key}
							className="rounded-[1.6rem] border border-white/80 bg-white/90 p-5 shadow-[0_14px_40px_rgba(12,46,61,0.08)] backdrop-blur-xl"
						>
							<div className="flex items-center justify-between gap-3">
								<p className="text-sm font-medium text-slate-500">{t(card.key)}</p>
								<span className={`inline-flex h-10 w-10 items-center justify-center rounded-xl ${card.bg} ${card.accent}`}>
									<Icon size={18} />
								</span>
							</div>
							<p className="mt-4 text-3xl font-semibold text-myanglow-navy">{card.value}</p>
						</article>
					)
				})}
			</section>

			<section className="grid gap-6 xl:grid-cols-2">
				<article className="rounded-[1.8rem] border border-white/80 bg-white/90 p-6 shadow-[0_16px_50px_rgba(12,46,61,0.08)] backdrop-blur-xl">
					<div className="mb-5 flex items-center gap-2 text-myanglow-navy">
						<Leaf size={18} />
						<h3 className="text-lg font-semibold">{t('dash.cropDist')}</h3>
					</div>

					<div className="space-y-4">
						{cropItems.map((item) => (
							<div key={item.crop} className="space-y-1">
								<div className="flex items-center justify-between text-sm">
									<span className="font-medium text-slate-700">{item.crop}</span>
									<span className="text-slate-500">{item.percent}%</span>
								</div>
								<div className="h-2 rounded-full bg-myanglow-sage/35">
									<div
										className="h-2 rounded-full bg-myanglow-forest"
										style={{ width: `${item.percent}%` }}
									/>
								</div>
							</div>
						))}
					</div>
				</article>

				<article className="rounded-[1.8rem] border border-white/80 bg-white/90 p-6 shadow-[0_16px_50px_rgba(12,46,61,0.08)] backdrop-blur-xl">
					<div className="mb-5 flex items-center gap-2 text-myanglow-navy">
						<BarChart3 size={18} />
						<h3 className="text-lg font-semibold">{t('dash.avgYieldCrop')}</h3>
					</div>

					<div className="space-y-3">
						{yieldItems.map((item) => (
							<div
								key={item.crop}
								className="flex items-center justify-between rounded-xl border border-myanglow-sage/50 bg-myanglow-sage/20 px-4 py-3"
							>
								<span className="font-medium text-slate-700">{item.crop}</span>
								<span className="text-sm font-semibold text-myanglow-navy">{item.yield} t/ha</span>
							</div>
						))}
					</div>
				</article>
			</section>
		</div>
	)
}

export default Dashboard
