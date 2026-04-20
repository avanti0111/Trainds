import { Train, Clock, MapPin, ArrowRight } from 'lucide-react'

const statusColors = {
  'On Time':  'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
  'Delayed':  'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  'Cancelled':'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  'Early':    'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
}

export default function TrainCard({ train }) {
  const {
    train_no, name, from_station, to_station,
    departure, arrival, status, delay_min, line
  } = train

  const lineColor =
    line === 'Western'   ? 'bg-blue-500'  :
    line === 'Central'   ? 'bg-red-500'   :
    line === 'Harbour'   ? 'bg-green-500' : 
    line === 'Trans Harbour' ? 'bg-purple-500' : 'bg-slate-400'

  return (
    <div className="card p-4 hover:shadow-md transition-shadow animate-slide-up">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${lineColor}`} />
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            {line} Line · {train_no}
          </span>
        </div>
        <span className={`badge ${statusColors[status] || statusColors['On Time']}`}>
          {status}
          {delay_min > 0 && ` (+${delay_min}m)`}
        </span>
      </div>

      <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-3">
        {name || `Train ${train_no}`}
      </h3>

      <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
        <MapPin size={14} className="text-brand-500 shrink-0" />
        <span className="font-medium">{from_station}</span>
        <ArrowRight size={14} className="text-slate-400" />
        <span className="font-medium">{to_station}</span>
      </div>

      <div className="mt-3 flex items-center gap-4 text-sm">
        <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
          <Clock size={13} />
          <span>Dep: <strong className="text-slate-700 dark:text-slate-200">{departure}</strong></span>
        </div>
        <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
          <Clock size={13} />
          <span>Arr: <strong className="text-slate-700 dark:text-slate-200">{arrival}</strong></span>
        </div>
      </div>
    </div>
  )
}
