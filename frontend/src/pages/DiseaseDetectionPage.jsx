import { useEffect, useMemo, useRef, useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  ImagePlus,
  Loader2,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  UploadCloud,
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext.jsx'

const acceptedTypes = ['image/jpeg', 'image/png', 'image/webp']
const maxFileSize = 8 * 1024 * 1024

import { API_BASE_URL } from '../api.js'

const workflowStages = ['Upload', 'Validate', 'Analyze', 'Review']

function SectionCard({ title, children, className = '' }) {
  return (
    <section
      className={`rounded-[2rem] border border-white/80 bg-white/90 p-5 shadow-[0_20px_60px_rgba(12,46,61,0.08)] backdrop-blur-xl sm:p-6 ${className}`}
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-myanglow-navy sm:text-xl">{title}</h2>
      </div>
      {children}
    </section>
  )
}

function DiseaseDetectionPage() {
  const { t, language } = useLanguage()
  const inputRef = useRef(null)
  const timerRef = useRef(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [validationError, setValidationError] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [statusText, setStatusText] = useState('Upload a plant or leaf image to begin.')

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl('')
      return undefined
    }

    const nextPreview = URL.createObjectURL(selectedFile)
    setPreviewUrl(nextPreview)
    setAnalysisResult(null)
    setStatusText('Preview ready. Analyze the plant when you are ready.')

    return () => {
      URL.revokeObjectURL(nextPreview)
    }
  }, [selectedFile])

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        window.clearTimeout(timerRef.current)
      }
    }
  }, [])

  const currentStage = useMemo(() => {
    if (analysisResult) return 3
    if (isAnalyzing) return 2
    if (previewUrl) return 1
    return 0
  }, [analysisResult, isAnalyzing, previewUrl])

  const handleFileChange = (event) => {
    const nextFile = event.target.files?.[0]

    if (!nextFile) {
      return
    }

    if (!acceptedTypes.includes(nextFile.type)) {
      setValidationError('Please upload a JPG, PNG, or WEBP plant image.')
      setSelectedFile(null)
      event.target.value = ''
      return
    }

    if (nextFile.size > maxFileSize) {
      setValidationError('Please choose an image smaller than 8 MB.')
      setSelectedFile(null)
      event.target.value = ''
      return
    }

    setValidationError('')
    setSelectedFile(nextFile)
    setAnalysisResult(null)
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setValidationError('Upload an image before analyzing the plant.')
      return
    }

    setValidationError('')
    setIsAnalyzing(true)
    setAnalysisResult(null)
    setStatusText('Analyzing the selected plant image...')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(`${API_BASE_URL}/disease-detect`, {
        method: 'POST',
        headers: {
          'Accept-Language': language
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error('Failed to analyze image')
      }

      const data = await response.json()
      setAnalysisResult(data)
      setStatusText('Analysis complete. Review the plant health recommendations below.')
    } catch (error) {
      console.error('Analysis error:', error)
      setValidationError('Failed to analyze the image. Please try again.')
      setStatusText('Analysis failed.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    if (timerRef.current) {
      window.clearTimeout(timerRef.current)
    }

    setSelectedFile(null)
    setPreviewUrl('')
    setValidationError('')
    setIsAnalyzing(false)
    setAnalysisResult(null)
    setStatusText('Upload a plant or leaf image to begin.')

    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  const scoreGradient = analysisResult
    ? {
        background: `conic-gradient(#9ad64c 0 ${analysisResult.healthScore}%, rgba(161, 188, 178, 0.35) ${analysisResult.healthScore}% 100%)`,
      }
    : undefined

  return (
    <div className="space-y-6">
      <section className="rounded-[2rem] border border-white/80 bg-white/85 p-5 shadow-[0_20px_60px_rgba(12,46,61,0.08)] backdrop-blur-xl sm:p-6 lg:p-7">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.45em] text-myanglow-medium">
              {t('disease.title')}
            </p>
            <h2 className="mt-3 text-3xl font-semibold leading-tight text-myanglow-navy sm:text-4xl">
              {t('disease.hero')}
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600 sm:text-base">
              {t('disease.subtitle')}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {workflowStages.map((stage, index) => {
            const isDone = currentStage > index
            const isActive = currentStage === index

            return (
              <div
                key={stage}
                className={`rounded-2xl border px-4 py-3 transition ${
                  isDone
                    ? 'border-myanglow-soft bg-myanglow-sage/35 text-myanglow-navy'
                    : isActive
                      ? 'border-myanglow-lime bg-white text-myanglow-navy shadow-sm'
                      : 'border-white bg-white/70 text-slate-500'
                }`}
              >
                <p className="text-[0.7rem] font-semibold uppercase tracking-[0.35em]">
                  Step {index + 1}
                </p>
                <p className="mt-2 text-sm font-semibold">{stage}</p>
              </div>
            )
          })}
        </div>
      </section>

      <section className="grid items-stretch gap-6 xl:grid-cols-2">
        <div className="h-full w-full">
          <SectionCard title={t('disease.upload')} className="h-full">
            <div className="grid gap-5 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
              <label
                htmlFor="plant-image"
                className="group flex cursor-pointer flex-col items-center justify-center rounded-[1.5rem] border-2 border-dashed border-myanglow-sage bg-gradient-to-br from-white to-myanglow-sage/20 p-6 text-center transition hover:border-myanglow-medium hover:bg-myanglow-sage/30"
              >
                <input
                  ref={inputRef}
                  id="plant-image"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-myanglow-forest/10 text-myanglow-forest transition group-hover:bg-myanglow-forest/15">
                  <ImagePlus size={28} />
                </div>
                <p className="mt-4 text-lg font-semibold text-myanglow-navy">
                  {t('disease.uploadPrompt')}
                </p>
                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-600">
                  {t('disease.formats')}
                </p>
                <span className="mt-5 inline-flex items-center gap-2 rounded-full bg-myanglow-forest px-4 py-2 text-sm font-semibold text-white transition group-hover:bg-myanglow-medium">
                  <UploadCloud size={16} />
                  {t('disease.choose')}
                </span>
              </label>

              <div className="overflow-hidden rounded-[1.5rem] border border-myanglow-sage/70 bg-white p-4">
                <div className="flex items-center justify-between gap-3 border-b border-myanglow-sage/60 pb-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.35em] text-myanglow-medium">
                      {t('disease.preview')}
                    </p>
                    <p className="mt-2 text-sm text-slate-500">
                      {selectedFile ? selectedFile.name : t('disease.noImage')}
                    </p>
                  </div>
                  <span className="rounded-full bg-myanglow-sage/50 px-3 py-1 text-xs font-semibold text-myanglow-darkGreen">
                    {selectedFile ? t('disease.ready') : t('disease.waiting')}
                  </span>
                </div>

                <div className="mt-4 flex min-h-[18rem] items-center justify-center rounded-[1.3rem] bg-gradient-to-br from-white to-myanglow-sage/25 p-3">
                  {previewUrl ? (
                    <img
                      src={previewUrl}
                      alt="Plant preview"
                      className="max-h-[18rem] w-full rounded-[1rem] object-cover shadow-lg"
                    />
                  ) : (
                    <div className="flex max-w-sm flex-col items-center text-center text-slate-500">
                      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white text-myanglow-medium shadow-sm">
                        <ScanSearch size={28} />
                      </div>
                      <p className="mt-4 text-lg font-semibold text-myanglow-navy">
                        {t('disease.previewHere')}
                      </p>
                      <p className="mt-2 text-sm leading-6">
                        {t('disease.previewHelp')}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {validationError ? (
              <div className="mt-4 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                <AlertTriangle size={18} className="mt-0.5 shrink-0" />
                <p>{validationError}</p>
              </div>
            ) : null}

            <div className="mt-5 flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={!selectedFile || isAnalyzing}
                className="inline-flex items-center justify-center gap-2 rounded-2xl bg-myanglow-forest px-5 py-3 text-sm font-semibold text-white transition hover:bg-myanglow-medium disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isAnalyzing ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} />}
                {t('disease.analyze')}
              </button>

              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-myanglow-sage bg-white px-5 py-3 text-sm font-semibold text-myanglow-navy transition hover:border-myanglow-soft hover:bg-myanglow-sage/40"
              >
                {t('disease.reset')}
              </button>
            </div>

            <p className="mt-4 text-sm text-slate-500" aria-live="polite">
              {statusText}
            </p>
          </SectionCard>
        </div>

        <div className="h-full w-full">
          <SectionCard title={t('disease.result')} className="h-full">
            {isAnalyzing ? (
              <div className="flex min-h-[18rem] flex-col items-center justify-center rounded-[1.5rem] border border-myanglow-sage/70 bg-myanglow-sage/20 px-6 py-10 text-center">
                <Loader2 size={34} className="animate-spin text-myanglow-forest" />
                <p className="mt-4 text-lg font-semibold text-myanglow-navy">
                  {t('disease.analyzing')}
                </p>
                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-600">
                  The app is processing the image and preparing the disease
                  diagnosis result.
                </p>
              </div>
            ) : analysisResult ? (
              <div className="space-y-5">
                <div className="flex flex-col gap-5 rounded-[1.5rem] border border-myanglow-sage/70 bg-white p-4 sm:flex-row sm:items-center">
                  <div className="flex shrink-0 items-center justify-center">
                    <div className="relative flex h-40 w-40 items-center justify-center rounded-full p-3" style={scoreGradient}>
                      <div className="flex h-28 w-28 flex-col items-center justify-center rounded-full bg-white shadow-inner shadow-myanglow-sage/40">
                        <span className="text-4xl font-semibold text-myanglow-navy">
                          {analysisResult.healthScore}
                        </span>
                        <span className="mt-1 text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-slate-500">
                          Health
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex-1 space-y-3 text-center sm:text-left">
                    <p className="text-xs font-semibold uppercase tracking-[0.35em] text-myanglow-medium">
                      Health Summary
                    </p>
                    <h3 className="text-2xl font-semibold text-myanglow-navy">
                      {analysisResult.plantName}
                    </h3>
                    <p className="text-sm italic text-slate-500">{analysisResult.scientificName}</p>
                    <div className="flex flex-wrap justify-center gap-2 sm:justify-start">
                      <span className="rounded-full bg-myanglow-sage/60 px-3 py-1 text-xs font-semibold text-myanglow-darkGreen">
                        {analysisResult.healthStatus}
                      </span>
                      <span className="rounded-full bg-myanglow-lime/20 px-3 py-1 text-xs font-semibold text-myanglow-forest">
                        Disease: {analysisResult.detectedDisease}
                      </span>
                      <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-myanglow-navy ring-1 ring-myanglow-sage">
                        Confidence {analysisResult.confidenceScore}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <InfoCard label="Disease severity" value={analysisResult.diseaseSeverity} />
                  <InfoCard label="Affected area" value={analysisResult.estimatedAffectedArea} />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <DetailPanel
                    title="Visible symptoms"
                    items={analysisResult.visibleSymptoms}
                    accent="text-myanglow-forest"
                  />
                  <DetailPanel
                    title="Possible causes"
                    items={analysisResult.possibleCauses}
                    accent="text-myanglow-darkGreen"
                  />
                  <DetailPanel
                    title="Treatment recommendations"
                    items={analysisResult.treatmentRecommendations}
                    accent="text-myanglow-medium"
                  />
                  <DetailPanel
                    title="Prevention recommendations"
                    items={analysisResult.preventionRecommendations}
                    accent="text-myanglow-muted"
                  />
                </div>
              </div>
            ) : (
              <div className="flex min-h-[18rem] flex-col items-center justify-center rounded-[1.5rem] border border-dashed border-myanglow-sage bg-myanglow-sage/15 px-6 py-10 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white text-myanglow-forest shadow-sm">
                  <ShieldCheck size={28} />
                </div>
                <p className="mt-4 text-lg font-semibold text-myanglow-navy">
                  {t('disease.noAnalysis')}
                </p>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
                  {t('disease.noAnalysisHelp')}
                </p>
              </div>
            )}
          </SectionCard>

        </div>
      </section>
    </div>
  )
}

function InfoCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-myanglow-sage/70 bg-white px-4 py-3">
      <p className="text-[0.7rem] font-semibold uppercase tracking-[0.35em] text-myanglow-medium">
        {label}
      </p>
      <p className="mt-2 text-sm font-semibold text-myanglow-navy">{value}</p>
    </div>
  )
}

function DetailPanel({ title, items, accent }) {
  return (
    <section className="rounded-2xl border border-myanglow-sage/70 bg-white p-4">
      <p className={`text-sm font-semibold ${accent}`}>{title}</p>
      <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-600">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <CheckCircle2 size={16} className={`mt-1 shrink-0 ${accent}`} />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}

export default DiseaseDetectionPage
