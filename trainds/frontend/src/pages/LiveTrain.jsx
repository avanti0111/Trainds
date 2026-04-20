import { useState, useEffect, useRef } from 'react'
import { liveAPI } from '../api/client'
import StationSelect from '../components/StationSelect'
import TrainCard from '../components/TrainCard'
import { Radio, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { STATIONS } from '../data/stations'
import { useLanguage } from '../contexts/LanguageContext'

export default function LiveTrain() {
  const { t } = useLanguage()
  const [station, setStation] = useState('Kurla')
  const [trains,  setTrains]  = useState([])
  const [loading, setLoading] = useState(false)
  const [lastUpd, setLastUpd] = useState(null)
  const interval = useRef(null)

  const fetchTrains = async (st) => {
    if (!st) return
    setLoading(true)
    try {
      const data = await liveAPI.getTrains(st)
      setTrains(data.trains || [])
      setLastUpd(new Date())
    } catch (e) {
      toast.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTrains(station)
    interval.current = setInterval(() => fetchTrains(station), 30000)
    return () => clearInterval(interval.current)
  }, [station])

  return (
    <div className="space-y-6 animate-slide-up">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="page-title flex items-center gap-2">
          <Radio size={24} className="text-brand-600" />
          {t('Live Trains')}
        </h1>
        {lastUpd && (
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <RefreshCw size={11} />
            {t('Updated')} {lastUpd.toLocaleTimeString('en-IN')}
          </span>
        )}
      </div>

      <div className="card p-5 flex gap-3 items-end flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <StationSelect
            label={t('Station')}
            value={station}
            onChange={(v) => {
              if (!v) return
              setStation(v.name || v)   // works for object OR string
            }}
            stations={STATIONS}
          />
        </div>
        <button
          className="btn-secondary"
          onClick={() => fetchTrains(station)}
          disabled={loading}
        >
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
          {t('Refresh')}
        </button>
      </div>

      {loading && trains.length === 0 ? (
        <div className="grid md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-4 h-28 animate-pulse bg-slate-100 dark:bg-slate-800" />
          ))}
        </div>
      ) : trains.length > 0 ? (
        <div className="grid md:grid-cols-2 gap-4">
          {[...(trains || [])]
            .sort((a, b) => {
              const t1 = a?.time || ""
              const t2 = b?.time || ""
              return t1.localeCompare(t2)
            })
            .map((t, i) => (
              <TrainCard key={i} train={t} />
            ))}
        </div>
      ) : (
        <div className="card p-8 text-center text-slate-400">
          {t('No trains found for')} <strong>{station}</strong>
        </div>
      )}
    </div>
  )
}
