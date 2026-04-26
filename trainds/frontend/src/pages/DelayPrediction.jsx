import { useState } from 'react'
import { delayAPI, weatherAPI } from '../api/client'
import StationSelect from '../components/StationSelect'
import { TrendingUp, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import { STATIONS } from '../data/stations'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { useLanguage } from '../contexts/LanguageContext'


const WEATHER = ['Clear', 'Clouds', 'Rain', 'Thunderstorm', 'Mist', 'Haze']

export default function DelayPrediction() {
  const { t } = useLanguage()
  const now = new Date()
  const [form, setForm] = useState({
    station: null,
    hour: now.getHours(),
    day_of_week: now.getDay(),
    weather: '',
    rainfall_mm: '',
  })
  const [result,  setResult]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [hourlyData, setHourlyData] = useState([])

  const set = (k, v) => setForm((p) => ({ ...p, [k]: v }))

  const handlePredict = async () => {
  if (!form.station) {
    toast.error("Please select a station")
    return
  }

  setLoading(true)
  setResult(null)

  try {
    // detect line from station
    
    const payload = {
      station: form.station?.name,
      line: form.station?.line,
      hour: form.hour,
      day_of_week: form.day_of_week,
    }
    if (form.weather) {
      payload.weather = form.weather
      payload.rainfall_mm = form.rainfall_mm === '' ? 0 : form.rainfall_mm
    }

    const data = await delayAPI.predict(payload)
    setResult(data)

    const hours = [5,7,9,11,13,15,17,19,21,23]

    const hourly = await Promise.all(
      hours.map(async (h) => {
        const r = await delayAPI.predict({
          ...payload,
          hour: h
        })

        return {
          hour: `${h}:00`,
          delay: r.predicted_delay_min
        }
      })
    )

    setHourlyData(hourly)

  } catch (e) {
    toast.error(e.message)
  } finally {
    setLoading(false)
  }
}

  const riskColor =
    !result ? '' :
    result.risk_level === 'Low'    ? 'border-emerald-400 bg-emerald-50 dark:bg-emerald-900/20' :
    result.risk_level === 'Medium' ? 'border-yellow-400  bg-yellow-50  dark:bg-yellow-900/20'  :
    'border-red-400 bg-red-50 dark:bg-red-900/20'

  return (
    <div className="space-y-6 animate-slide-up">
      <h1 className="page-title flex items-center gap-2">
        <TrendingUp size={24} className="text-brand-600" />
        {t('Delay Prediction')}
      </h1>

      <div className={`flex flex-col md:flex-row gap-6 transition-all duration-500 ease-in-out ${result ? '' : 'justify-center'}`}>
        {/* Form */}
        <div className={`card p-6 space-y-6 transition-all duration-500 ${result ? 'w-full md:w-1/2' : 'w-full max-w-xl'}`}>
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 pb-3">
             <p className="section-label mb-0 text-brand-600 dark:text-brand-400">{t('Prediction Parameters')}</p>
          </div>

          <div className="space-y-1">
            <StationSelect
              label={t('Station')}
              value={form.station}
              onChange={(v) => set('station', v)}
              stations={STATIONS}
            />
            {form.station && (
              <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 pl-1">
                Line: {form.station?.line}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded-xl border border-slate-200 dark:border-slate-700">
              <label className="section-label mb-2 block">{t('Hour of Day')}</label>
              <input
                type="range" min={0} max={23} value={form.hour}
                onChange={(e) => set('hour', +e.target.value)}
                className="w-full accent-brand-600"
              />
              <p className="text-sm text-center text-slate-700 dark:text-slate-300 mt-2 font-bold font-mono">
                {form.hour.toString().padStart(2, '0')}:00
              </p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded-xl border border-slate-200 dark:border-slate-700">
              <label className="section-label mb-2 block">{t('Day of Week')}</label>
              <select
                value={form.day_of_week}
                onChange={(e) => set('day_of_week', +e.target.value)}
                className="input-base bg-white dark:bg-slate-800"
              >
                {['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'].map((d, i) => (
                  <option key={d} value={i}>{d}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700 space-y-4">
            <label className="section-label block text-brand-600 dark:text-brand-400">{t('Simulate Weather Conditions')}</label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-500 block mb-1">{t('Weather')}</label>
                <select
                  value={form.weather}
                  onChange={(e) => set('weather', e.target.value)}
                  className="input-base py-2 text-sm bg-white dark:bg-slate-800"
                >
                  <option value="">{t('Live Weather (Auto)')}</option>
                  {WEATHER.map(w => <option key={w} value={w}>{t(w)}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 block mb-1">{t('Rainfall (mm)')}</label>
                <input
                  type="number" min={0} max={300} value={form.rainfall_mm}
                  onChange={(e) => set('rainfall_mm', +e.target.value)}
                  className="input-base py-2 text-sm bg-white dark:bg-slate-800 disabled:opacity-50"
                  disabled={!form.weather}
                  placeholder={!form.weather ? 'Auto' : '0'}
                />
              </div>
            </div>
          </div>

          <button className="btn-primary w-full py-3.5 text-lg shadow-md hover:shadow-lg transition-all" onClick={handlePredict} disabled={loading}>
            {loading ? t('Predicting...') : t('Predict Delay')}
          </button>
        </div>

        {/* Result */}
        {result && (
          <div className="w-full md:w-1/2 space-y-4 animate-fade-in">
            <div className={`card p-6 border-l-4 shadow-lg ${riskColor}`}>
              <div className="flex items-center gap-2 mb-3">
                {result.risk_level === 'Low'
                  ? <CheckCircle size={20} className="text-emerald-500" />
                  : <AlertCircle size={20} className={
                      result.risk_level === 'Medium' ? 'text-yellow-500' : 'text-red-500'
                    } />
                }
                <h2 className="font-bold text-slate-800 dark:text-slate-100 text-lg">
                  {t('Prediction Result')}
                </h2>
              </div>
              
              {result.weather_used && (
                <div className="mb-4 bg-slate-100 dark:bg-slate-800 rounded-lg p-3 flex justify-between items-center text-sm">
                  <div className="flex flex-col">
                     <span className="text-slate-500 font-semibold mb-0.5">
                       {result.weather_used.is_simulated ? t('Simulated Weather') : t('Live Weather')}
                     </span>
                     <span className="font-bold text-brand-700 dark:text-brand-400">{t(result.weather_used.condition)}</span>
                  </div>
                  <div className="flex flex-col text-right">
                     <span className="text-slate-500 font-semibold mb-0.5">{t('Rainfall')}</span>
                     <span className="font-bold text-blue-600 dark:text-blue-400">{result.weather_used.rainfall} mm</span>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="section-label">{t('Expected Delay')}</p>
                  <p className="text-3xl font-extrabold text-slate-800 dark:text-slate-100">
                    {Number(result.predicted_delay_min).toFixed(1)}
                    <span className="text-lg font-medium ml-1 text-slate-500">min</span>
                  </p>
                </div>
                <div>
                  <p className="section-label">{t('Risk Level')}</p>
                  <p className={`text-2xl font-bold mt-1
                    ${result.risk_level === 'Low'    ? 'text-emerald-600' :
                      result.risk_level === 'Medium' ? 'text-yellow-600'  : 'text-red-600'}`}>
                    {t(result.risk_level)}
                  </p>
                </div>
              </div>

              <div className="mt-3 space-y-1">
                {result.factors && result.factors.map((f, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-brand-500 shrink-0" />
                    {f}
                  </div>
                ))}
              </div>

              <p className="mt-3 text-sm font-medium text-slate-500 dark:text-slate-400">
                <Clock size={13} className="inline mr-1" />
                Model: {result.model}
              </p>
            </div>

            {hourlyData.length > 0 && (
              <div className="card p-5">
                <p className="section-label mb-3">{t('Delay Forecast – Key Hours')}</p>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={hourlyData} barSize={20}>
                    <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} unit="m" />
                    <Tooltip
                      formatter={(v) => [`${v} min`, 'Delay']}
                      contentStyle={{ fontSize: 12 }}
                    />
                    <Bar dataKey="delay" radius={[4, 4, 0, 0]}>
                      {hourlyData.map((e, i) => (
                        <Cell
                          key={i}
                          fill={e.delay <= 3 ? '#10b981' : e.delay <= 7 ? '#f59e0b' : '#ef4444'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

