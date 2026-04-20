import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Train, Map, Activity, AlertTriangle,
  Phone, Cloud, Clock, TrendingUp
} from 'lucide-react'
import { weatherAPI, megablockAPI } from '../api/client'
import Feedback from '../components/Feedback'
import { useLanguage } from '../contexts/LanguageContext'



export default function Dashboard() {
  const [weather, setWeather]     = useState(null)
  const [megablock, setMegablock] = useState([])
  const [time, setTime]           = useState(new Date())
  const { t } = useLanguage()

  const quickLinks = [
    { to: '/route',     label: t('Plan Route'),      icon: Map,          color: 'text-blue-500',   bg: 'bg-blue-50 dark:bg-blue-900/20'   },
    { to: '/delay',     label: t('Delay Predictor'), icon: TrendingUp,   color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-900/20' },
    { to: '/live',      label: t('Live Trains'),     icon: Activity,     color: 'text-emerald-500',bg: 'bg-emerald-50 dark:bg-emerald-900/20' },
    { to: '/megablock', label: t('Megablocks'),      icon: AlertTriangle,color: 'text-orange-500', bg: 'bg-orange-50 dark:bg-orange-900/20'  },
    { to: '/sos',       label: t('SOS / Help'),      icon: Phone,        color: 'text-red-500',    bg: 'bg-red-50 dark:bg-red-900/20'       },
  ]
  const statCards = [
    { label: 'Lines Active',   value: '4',    sub: 'Western · Central · Harbour · Trans Harbour' },
    { label: 'Stations',       value: '120+', sub: 'Across Mumbai network'       },
    { label: 'Trains / Day',   value: '2,900',sub: 'Average daily services'      },
    { label: 'Daily Riders',   value: '7.5M', sub: 'Approximate commuters'       },
  ]

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    weatherAPI.get().then(setWeather).catch(() => {})
    megablockAPI.getAll().then((d) => setMegablock(d.megablocks || [])).catch(() => {})
    return () => clearInterval(t)
  }, [])

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Hero */}
      <div className="card p-6 bg-gradient-to-br from-brand-600 to-brand-800
                      dark:from-brand-800 dark:to-slate-900 text-white border-0">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Train size={20} />
              <span className="text-brand-200 text-sm font-medium">TRAiNDS</span>
            </div>
            <h1 className="text-3xl font-extrabold leading-tight">
              {t('Mumbai Local')}<br />{t('AI Assistant')}
            </h1>
            <p className="text-brand-200 mt-2 text-sm">
              {t('Real-time routes · Delay prediction · Live tracking')}
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-mono font-bold">
              {time.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
            </p>
            <p className="text-brand-200 text-sm mt-0.5">
              {time.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}
            </p>
          </div>
        </div>

        {weather && (
          <div className="mt-4 flex items-center gap-2 bg-white/10 rounded-xl px-4 py-2 w-fit">
            <Cloud size={16} />
            <span className="text-sm font-medium">
              Mumbai · {weather.temperature}°C · {weather.description}
            </span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s) => (
          <div key={s.label} className="card p-4">
            <p className="text-2xl font-extrabold text-brand-600 dark:text-brand-400">{t(s.value)}</p>
            <p className="font-semibold text-slate-700 dark:text-slate-200 text-sm mt-0.5">{t(s.label)}</p>
            <p className="text-xs text-slate-400 mt-0.5">{t(s.sub)}</p>
          </div>
        ))}
      </div>

      {/* Quick links */}
      <div>
        <p className="section-label mb-3">{t('Quick Access')}</p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {quickLinks.map(({ to, label, icon: Icon, color, bg }) => (
            <Link
              key={to}
              to={to}
              className="card p-4 flex flex-col items-center gap-2 hover:shadow-md
                         active:scale-95 transition-all duration-150 cursor-pointer"
            >
              <div className={`p-3 rounded-xl ${bg}`}>
                <Icon size={22} className={color} />
              </div>
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-200 text-center">
                {label}
              </span>
            </Link>
          ))}
        </div>
      </div>

      {/* Active megablocks */}
      {megablock.length > 0 && (
        <div>
          <p className="section-label mb-3">⚠️ Active Megablocks</p>
          <div className="space-y-2">
            {megablock.slice(1,10).map((m, i) => (
              <div key={i} className="card p-4 border-l-4 border-orange-400">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-100">{m.title}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{m.description}</p>
                  </div>
                  <span className="badge bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300 shrink-0 ml-2">
                    {m.line}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  <Clock size={11} className="inline mr-1" />
                  {m.date} · {m.time_range}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Internal Feedback Module */}
      <Feedback />

    </div>
  )
}
