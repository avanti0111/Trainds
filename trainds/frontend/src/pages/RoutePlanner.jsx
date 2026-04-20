import { useState } from 'react'
import { routeAPI } from '../api/client'
import StationSelect from '../components/StationSelect'
import { ArrowRight, ArrowLeftRight, Navigation, Clock, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import { STATIONS } from '../data/stations'
import { useLanguage } from '../contexts/LanguageContext'

export default function RoutePlanner() {
  const { lang, t } = useLanguage()
  const [from,     setFrom]     = useState('')
  const [to,       setTo]       = useState('')
  const [result,   setResult]   = useState(null)
  const [whatIf,   setWhatIf]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [loadingWI,setLoadingWI]= useState(false)

  const swap = () => { setFrom(to); setTo(from) }

  const handlePlan = async () => {
    if (!from || !to) return toast.error('Select both stations')
    const fromName = from.name || from
    const toName = to.name || to
    if (fromName === toName)  return toast.error('Origin and destination are the same')
    
    setLoading(true)
    setResult(null)
    setWhatIf(null)
    try {
      const data = await routeAPI.plan(fromName, toName)
      setResult(data)
    } catch (e) {
      toast.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleWhatIf = async () => {
    if (!from || !to) return toast.error('Plan a route first')
    const fromName = from.name || from
    const toName = to.name || to
    setLoadingWI(true)
    try {
      const data = await routeAPI.whatIf(fromName, toName)
      setWhatIf(data)
    } catch (e) {
      toast.error(e.message)
    } finally {
      setLoadingWI(false)
    }
  }

  return (
    <div className="space-y-6 animate-slide-up">
      <h1 className="page-title flex items-center gap-2">
        <Navigation size={24} className="text-brand-600" />
        {t('Route Planner')}
      </h1>

      {/* Input Card */}
      <div className="card p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <StationSelect label="From" value={from} onChange={setFrom} stations={STATIONS} />
          <StationSelect label="To"   value={to}   onChange={setTo}   stations={STATIONS} />
        </div>

        <div className="flex gap-3 flex-wrap">
          <button className="btn-secondary" onClick={swap}>
            <ArrowLeftRight size={15} /> {t('Swap')}
          </button>
          <button className="btn-primary" onClick={handlePlan} disabled={loading}>
            {loading ? t('Finding route…') : t('Find Route')}
          </button>
          {result && (
            <button className="btn-secondary" onClick={handleWhatIf} disabled={loadingWI}>
              <Zap size={15} />
              {loadingWI ? t('Comparing…') : t('What-If Analysis')}
            </button>
          )}
        </div>
      </div>

      {/* Result */}
      {result && <RouteResult data={result} />}

      {/* What-If */}
      {whatIf && <WhatIfResult data={whatIf} />}
    </div>
  )
}

function RouteResult({ data }) {
  const { t } = useLanguage()
  if (data.error) return (
    <div className="card p-5 border-l-4 border-red-400">
      <p className="text-red-600 dark:text-red-400 font-medium">{data.error}</p>
    </div>
  )

  const { route, changes, total_time_min, segments } = data

  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-bold text-slate-800 dark:text-slate-100 text-lg">
          {t('Best Route')}
        </h2>
        <span className="badge bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
          <Clock size={12} className="mr-1" /> ~{total_time_min} min
        </span>
      </div>

      {/* Route breadcrumb */}
      <div className="flex flex-wrap items-center gap-1.5">
        {route.map((station, i) => (
          <span key={i} className="flex items-center gap-1.5">
            <span className={`px-2.5 py-1 rounded-lg text-sm font-medium
              ${i === 0 || i === route.length - 1
                ? 'bg-brand-600 text-white'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200'}`}>
              {station}
            </span>
            {i < route.length - 1 && (
              <ArrowRight size={14} className="text-slate-400 shrink-0" />
            )}
          </span>
        ))}
      </div>

      {/* Segments */}
      {segments && segments.length > 0 && (
        <div className="space-y-2">
          <p className="section-label">{t('Journey Segments')}</p>
          {segments.map((seg, i) => (
            <div key={i}
              className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
              <div className="w-6 h-6 rounded-full bg-brand-600 text-white flex items-center
                              justify-center text-xs font-bold shrink-0 mt-0.5">
                {i + 1}
              </div>
              <div className="flex-1 text-sm">
                <p className="font-semibold text-slate-800 dark:text-slate-100">
                  {seg.from} → {seg.to}
                </p>
                <p className="text-slate-500 dark:text-slate-400 mt-0.5">
                  {seg.line} Line · ~{seg.time_min} min
                  {seg.change && (
                    <span className="ml-2 badge bg-yellow-100 text-yellow-700
                                     dark:bg-yellow-900/40 dark:text-yellow-300">
                      {t('Change here')}
                    </span>
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-sm text-slate-500 dark:text-slate-400">
        {changes === 0
          ? t('Direct journey – no changes required')
          : `🔄 ${changes} ${t(changes > 1 ? 'train changes required' : 'train change required')}`}
      </p>
    </div>
  )
}

function WhatIfResult({ data }) {
  const { t } = useLanguage()
  const { routes, decision } = data
  if (!routes || routes.length === 0) return null

  return (
    <div className="card p-5 space-y-4">
      <h2 className="font-bold text-slate-800 dark:text-slate-100 text-lg flex items-center gap-2">
        <Zap size={18} className="text-yellow-500" />
        {t('What-If Analysis')}
      </h2>
      
      {decision && (
        <div className="mb-4 p-4 rounded-xl bg-gradient-to-r from-brand-50 to-brand-100/50 dark:from-brand-900/30 dark:to-brand-800/10 border border-brand-200 dark:border-brand-800/50">
          <div className="flex items-center justify-between mb-3">
            <h3 className={`text-xl font-bold flex items-center gap-2 ${decision.recommendation === 'Leave Now' ? 'text-emerald-600 dark:text-emerald-400' : 'text-brand-600 dark:text-brand-400'}`}>
              {decision.recommendation === 'Leave Now' ? '✅' : '⏳'} {decision.recommendation}
            </h3>
            <div className="text-right">
              <p className="text-sm text-slate-500 font-medium">{t('Est. Departure')}</p>
              <p className="font-bold text-slate-800 dark:text-slate-100">{decision.departure_time}</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm mb-3 text-slate-700 dark:text-slate-300">
             <span className="flex items-center gap-1 font-medium"><Clock size={16} className="text-brand-500" /> {t('Total Time')}: {decision.estimated_total_time} mins</span>
          </div>
          <div className="space-y-1">
             <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">{t('Reasoning Analysis')}</p>
             {decision.reasoning.map((r, i) => (
                <p key={i} className="text-sm text-slate-600 dark:text-slate-300 flex items-center gap-1.5"><span className="w-1 h-1 rounded-full bg-slate-400 shrink-0"></span> {r}</p>
             ))}
          </div>
        </div>
      )}

      <div className="space-y-3">
        {routes.map((r, i) => (
          <div key={i}
            className={`p-4 rounded-xl border-2 transition-all
              ${i === 0
                ? 'border-brand-400 bg-brand-50 dark:bg-brand-900/20'
                : 'border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700/40'
              }`}>
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-slate-800 dark:text-slate-100">
                {t('Option')} {i + 1} {i === 0 && <span className="text-brand-600 text-xs ml-1">★ {t('Recommended')}</span>}
              </span>
              <div className="flex gap-2 flex-wrap justify-end">
                <span className="badge bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
                  {r.total_time_min} min
                </span>
                <span className={`badge ${
                  r.delay_risk === 'Low'    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300' :
                  r.delay_risk === 'Medium' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300' :
                  'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
                }`}>
                  {t(r.delay_risk)} {t('delay risk')}
                </span>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-1 text-sm text-slate-600 dark:text-slate-300">
              {r.route.map((s, j) => (
                <span key={j} className="flex items-center gap-1">
                  <span className="px-2 py-0.5 bg-white dark:bg-slate-700 rounded-md
                                   border border-slate-200 dark:border-slate-600">{s}</span>
                  {j < r.route.length - 1 && <ArrowRight size={12} className="text-slate-400" />}
                </span>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-2">{r.note}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
