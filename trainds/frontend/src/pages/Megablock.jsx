import { useEffect, useState } from 'react'
import { megablockAPI } from '../api/client'
import { AlertTriangle, Calendar, Clock } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

const LINE_STYLES = {
  Western: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 border-blue-300',
  Central: 'bg-red-100  text-red-700  dark:bg-red-900/40  dark:text-red-300  border-red-300',
  Harbour: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300 border-green-300',
  'Trans Harbour': 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300 border-purple-300',
}

export default function Megablock() {
  const { t } = useLanguage()
  const [blocks,   setBlocks]   = useState([])
  const [filter,   setFilter]   = useState('All')
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    megablockAPI.getAll()
      .then((d) => setBlocks(d.megablocks || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const lines = ['All', 'Western', 'Central', 'Harbour', 'Trans Harbour']
  const visible = filter === 'All' ? blocks : blocks.filter((b) => b.line === filter)

  return (
    <div className="space-y-6 animate-slide-up">
      <h1 className="page-title flex items-center gap-2">
        <AlertTriangle size={24} className="text-orange-500" />
        {t('Megablock Alerts')}
      </h1>

      {/* Line filter */}
      <div className="flex gap-2 flex-wrap">
        {lines.map((l) => (
          <button
            key={l}
            onClick={() => setFilter(l)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors
              ${filter === l
                ? 'bg-brand-600 text-white'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
          >
            {t(l)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card h-24 animate-pulse bg-slate-100 dark:bg-slate-800" />
          ))}
        </div>
      ) : visible.length === 0 ? (
        <div className="card p-8 text-center">
          <AlertTriangle size={36} className="text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">{t('No megablocks scheduled for')} {t(filter)} {t('line')}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {visible.map((b, i) => (
            <div
              key={i}
              className={`card p-5 border-l-4 ${
                b.line === 'Western' ? 'border-blue-500' :
                b.line === 'Central' ? 'border-red-500'  :
                b.line === 'Trans Harbour' ? 'border-purple-500' : 'border-green-500'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="font-bold text-slate-800 dark:text-slate-100">{b.title}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{b.description}</p>
                  <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <Calendar size={12} /> {b.date}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock size={12} /> {b.time_range?.replace(/[^\x00-\x7F]/g, "-")}
                    </span>
                    {b.affected_section && (
                      <span>📍 {b.affected_section}</span>
                    )}
                  </div>
                  {b.alternative && (
                    <p className="mt-2 text-xs font-medium text-brand-600 dark:text-brand-400">
                      💡 Alternative: {b.alternative}
                    </p>
                  )}
                </div>
                <span className={`badge border ${LINE_STYLES[b.line] || 'bg-slate-100 text-slate-600'} shrink-0`}>
                  {b.line}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
