import { useState } from 'react'
import { Map, Plus, Minus, Settings2, Clock, CheckCircle } from 'lucide-react'
import { routeAPI } from '../api/client'
import { useLanguage } from '../contexts/LanguageContext'
import { STATIONS } from '../data/stations'
import StationSelect from '../components/StationSelect'

export default function MultiRoute() {
  const { lang, t } = useLanguage()
  const [source, setSource] = useState(null)
  const [destinations, setDestinations] = useState([null])
  const [mode, setMode] = useState('optimize')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAddDestination = () => {
    if (destinations.length < 4) {
      setDestinations([...destinations, null])
    }
  }

  const handleRemoveDestination = (idx) => {
    setDestinations(destinations.filter((_, i) => i !== idx))
  }

  const handleDestChange = (val, idx) => {
    const newDests = [...destinations]
    newDests[idx] = val
    setDestinations(newDests)
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    setError('')
    setResult(null)
    const validDests = destinations.filter(d => d !== null).map(d => d.name)
    const sourceName = source ? source.name : null
    if (!sourceName || validDests.length === 0) {
      setError("Please provide a source and at least 1 destination.")
      return
    }

    setLoading(true)
    try {
      const data = await routeAPI.multiRoute(sourceName, validDests, mode)
      setResult(data)
    } catch (err) {
      setError(err.message || "Failed to calculate multi-route.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center p-3 sm:p-4 bg-brand-100 dark:bg-brand-900/40 rounded-full mb-2">
          <Map className="w-8 h-8 sm:w-10 sm:h-10 text-brand-600 dark:text-brand-400" />
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-800 dark:text-white pb-1">
          {t('Multi-Stop Journey')}
        </h1>
        <p className="text-base sm:text-lg text-slate-500 dark:text-slate-400 max-w-2xl mx-auto px-4">
          {t('Plan complex travels across up to 4 stations simultaneously!')}
        </p>
      </div>

      <div className="bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700">
        <form onSubmit={handleSearch} className="space-y-6">
          {/* Source Box */}
          <div>
            <StationSelect
              label={t('Starting Station')}
              value={source}
              onChange={(v) => setSource(v)}
              stations={STATIONS}
            />
          </div>

          <div className="border-t border-slate-200 dark:border-slate-700 py-4">
            <div className="flex justify-between items-center mb-4">
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300">{t('Destinations (Max 4)')}</label>
              {destinations.length < 4 && (
                <button type="button" onClick={handleAddDestination} className="text-sm font-medium text-brand-600 dark:text-brand-400 hover:text-brand-700 flex items-center space-x-1">
                  <Plus size={16}/> <span>{t('Add Stop')}</span>
                </button>
              )}
            </div>

            <div className="space-y-3">
              {destinations.map((dest, idx) => (
                <div key={idx} className="flex items-center space-x-2">
                  <span className="flex-none bg-slate-100 dark:bg-slate-700 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-slate-500 dark:text-slate-300">
                    {idx + 1}
                  </span>
                  <div className="flex-1">
                    <StationSelect
                      value={dest}
                      onChange={(v) => handleDestChange(v, idx)}
                      stations={STATIONS}
                    />
                  </div>
                  {destinations.length > 1 && (
                    <button type="button" onClick={() => handleRemoveDestination(idx)} className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors">
                      <Minus size={18} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-2">
              <Settings2 size={16} /> {t('Strategy Mode')}
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center space-x-2 text-slate-700 dark:text-slate-300 cursor-pointer">
                <input 
                  type="radio" 
                  name="mode" 
                  value="optimize" 
                  checked={mode === 'optimize'} 
                  onChange={() => setMode('optimize')} 
                  className="w-4 h-4 text-brand-600 focus:ring-brand-500 border-slate-300"
                />
                <span className="text-sm font-medium">{t('Smart Optimize (Fastest)')}</span>
              </label>
              <label className="flex items-center space-x-2 text-slate-700 dark:text-slate-300 cursor-pointer">
                <input 
                  type="radio" 
                  name="mode" 
                  value="priority" 
                  checked={mode === 'priority'} 
                  onChange={() => setMode('priority')} 
                  className="w-4 h-4 text-brand-600 focus:ring-brand-500 border-slate-300"
                />
                <span className="text-sm font-medium">{t('Strict Priority (Ordered)')}</span>
              </label>
            </div>
          </div>

          {error && <p className="text-red-500 font-medium text-center">{error}</p>}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-3.5 rounded-xl transition-all shadow-md hover:shadow-lg disabled:opacity-50"
          >
            {loading ? t("Calculating Sequences...") : t("Determine Best Route")}
          </button>
        </form>
      </div>

      {result && (
        <div className="space-y-6 animate-slide-up">
          <div className="bg-gradient-to-r from-brand-600 to-indigo-600 p-6 rounded-2xl shadow-xl text-white">
             <div className="flex items-center space-x-2 mb-2 opacity-90">
                <CheckCircle className="w-5 h-5" />
                <span className="font-semibold text-sm tracking-wider uppercase">{t('Recommendation')}</span>
             </div>
             <h2 className="text-3xl font-extrabold mb-2">{result.decision.recommendation}</h2>
             <div className="flex items-center space-x-4 text-brand-50 text-sm font-medium">
               <span>{t('Optimal Sequence')}: {source?.name} → {result.optimized_order.join(" → ")}</span>
             </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.journey_plan.map((segment, idx) => (
              <div key={idx} className="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-md border border-slate-200 dark:border-slate-700 space-y-4 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-center border-b border-slate-100 dark:border-slate-700 pb-3">
                  <div className="font-semibold text-slate-800 dark:text-white">
                    {t('Leg')} {idx + 1}: <span className="text-brand-600">{segment.from}</span>
                  </div>
                  <Clock className="w-5 h-5 text-slate-400" />
                </div>
                <div className="text-slate-600 dark:text-slate-400">
                  {t('To')} <span className="font-bold text-slate-800 dark:text-slate-200">{segment.to}</span>
                </div>
                <div className="flex justify-between items-center bg-slate-50 dark:bg-slate-900/50 p-3 rounded-lg text-sm">
                   <span className="text-slate-500 font-medium">{segment.route.length} {t('stops')}</span>
                   <span className="font-bold text-brand-600 dark:text-brand-400">{segment.time} {t('mins')}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
