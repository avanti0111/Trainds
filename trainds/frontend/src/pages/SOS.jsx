import { Phone, MapPin, AlertCircle, Info, ExternalLink } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

const EMERGENCY = [
  { name: 'Railway Police (RPF)',  number: '182',    color: 'bg-red-500',     desc: 'Security emergencies on trains/platforms' },
  { name: 'Government Railway Police', number: '1512', color: 'bg-orange-500', desc: 'Crime, missing persons on railways' },
  { name: 'Medical Emergency',    number: '108',    color: 'bg-emerald-500', desc: 'Ambulance service'                        },
  { name: 'Police',               number: '100',    color: 'bg-blue-500',    desc: 'General police emergency'                 },
  { name: 'Fire Brigade',         number: '101',    color: 'bg-red-600',     desc: 'Fire emergencies'                         },
  { name: 'Women Helpline',       number: '1091',   color: 'bg-pink-500',    desc: 'Women safety helpline'                    },
  { name: 'Child Helpline',       number: '1098',   color: 'bg-purple-500',  desc: 'Child safety & welfare'                   },
  { name: 'CR Helpline',          number: '022-22694040', color: 'bg-slate-600', desc: 'Central Railway helpline'             },
  { name: 'WR Helpline',          number: '022-23077000', color: 'bg-slate-600', desc: 'Western Railway helpline'             },
]

const SAFETY_TIPS = [
  'Use designated ladies\' compartments during peak hours',
  'Report suspicious objects – call 182 immediately',
  'Stand behind yellow line on platforms',
  'Use overcrowding alerts during peak hours (8–10 AM, 6–8 PM)',
  'Keep valuables secured, especially in crowded trains',
  'Download UTS/IRCTC apps for ticketing assistance',
  'Note your train number and coach number when boarding',
  'Emergency chain pulls are for genuine emergencies only – misuse is punishable',
]

const LOST_FOUND = [
  { label: 'CR Lost & Found (CSMT)', contact: '022-22694040' },
  { label: 'WR Lost & Found (Churchgate)', contact: '022-22075711' },
  { label: 'Railway Claims Tribunal', contact: '022-22693636' },
]

export default function SOS() {
  const { t } = useLanguage()

  return (
    <div className="space-y-6 animate-slide-up">
      <div className="card p-5 bg-gradient-to-r from-red-600 to-red-800 border-0 text-white">
        <div className="flex items-center gap-2 mb-1">
          <AlertCircle size={20} />
          <h1 className="text-xl font-extrabold">{t('SOS & Emergency')}</h1>
        </div>
        <p className="text-red-200 text-sm">
          {t('Quick access to railway emergency contacts and safety information')}
        </p>
      </div>

      {/* Emergency contacts */}
      <div>
        <p className="section-label mb-3">{t('Emergency Contacts')}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {EMERGENCY.map((e) => (
            <a
              key={e.number}
              href={`tel:${e.number}`}
              className="card p-4 hover:shadow-md active:scale-95 transition-all flex items-center gap-3"
            >
              <div className={`${e.color} text-white rounded-xl p-2.5 shrink-0`}>
                <Phone size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm truncate">
                  {t(e.name)}
                </p>
                <p className="font-mono font-bold text-brand-600 dark:text-brand-400">
                  {e.number}
                </p>
                <p className="text-xs text-slate-400 truncate">{t(e.desc)}</p>
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* Safety tips */}
      <div className="card p-5">
        <p className="section-label mb-3 flex items-center gap-1.5">
          <Info size={14} /> {t('Safety Tips')}
        </p>
        <ul className="space-y-2">
          {SAFETY_TIPS.map((tip, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-300">
              <span className="text-brand-500 font-bold mt-0.5 shrink-0">{i + 1}.</span>
              {t(tip)}
            </li>
          ))}
        </ul>
      </div>

      {/* Lost & Found */}
      <div>
        <p className="section-label mb-3 flex items-center gap-1.5">
          <MapPin size={14} /> {t('Lost & Found')}
        </p>
        <div className="grid sm:grid-cols-3 gap-3">
          {LOST_FOUND.map((l) => (
            <div key={l.label} className="card p-4">
              <p className="font-semibold text-slate-700 dark:text-slate-200 text-sm">{t(l.label)}</p>
              <a
                href={`tel:${l.contact}`}
                className="font-mono text-brand-600 dark:text-brand-400 text-sm hover:underline flex items-center gap-1 mt-1"
              >
                {l.contact} <ExternalLink size={12} />
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
