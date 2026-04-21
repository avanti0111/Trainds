import { useState } from 'react'
import { Star, MessageSquareQuote } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import API_BASE_URL from '../api/apiConfig'


export default function Feedback() {
  const [rating, setRating] = useState(0)
  const [hoverRating, setHoverRating] = useState(0)
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const { t } = useLanguage()

  // Conditionally render only if user is logged in
  const token = localStorage.getItem('token')
  if (!token) return null

  const emojis = ['😕', '😐', '🙂', '😊', '😍']

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (rating === 0) {
      setError("Please select a rating!")
      return
    }

    setLoading(true)
    setError('')
    setMessage('')

    try {
      const res = await fetch(`${API_BASE_URL}/feedback`, {

        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}` 
        },
        body: JSON.stringify({ rating, comment })
      })

      const data = await res.json()
      if (res.ok) {
        setMessage(t("Thank you for your feedback!") + " " + emojis[rating-1])
        setRating(0)
        setComment('')
      } else {
        setError(data.error || "Failed to submit feedback.")
      }
    } catch {
      setError("Network error hitting the feedback endpoint.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-md border border-slate-200 dark:border-slate-700 max-w-2xl mx-auto my-8">
      <div className="flex items-center gap-2 mb-4">
        <MessageSquareQuote className="w-5 h-5 text-brand-600 dark:text-brand-400" />
        <h3 className="text-xl font-bold text-slate-800 dark:text-white">{t('Help us improve!')}</h3>
      </div>
      
      {!message ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex flex-col items-center space-y-2 py-4 bg-slate-50 dark:bg-slate-900/50 rounded-xl">
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">{t('Rate your experience')}</span>
            <div className="flex flex-row space-x-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                  onClick={() => setRating(star)}
                  className="p-1 focus:outline-none transition-transform hover:scale-110"
                >
                  <Star 
                    className={`w-8 h-8 ${star <= (hoverRating || rating) ? "text-yellow-400 fill-yellow-400" : "text-slate-300 dark:text-slate-600"}`} 
                  />
                </button>
              ))}
            </div>
            {(hoverRating || rating) > 0 && (
              <span className="text-2xl animate-bounce pt-1">
                {emojis[(hoverRating || rating) - 1]}
              </span>
            )}
          </div>

          <div>
            <textarea 
              rows="3"
              placeholder={t("Tell us what you loved or what we could do better... (Optional)")}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full input-base resize-none"
            ></textarea>
          </div>

          {error && <p className="text-red-500 text-sm font-medium">{error}</p>}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50"
          >
            {loading ? t("Submitting...") : t("Submit Feedback")}
          </button>
        </form>
      ) : (
        <div className="text-center py-6 bg-brand-50 dark:bg-brand-900/30 rounded-xl border border-brand-100 dark:border-brand-800 animate-fade-in">
          <p className="text-lg font-bold text-brand-700 dark:text-brand-300">{message}</p>
          <button 
            onClick={() => setMessage('')} 
            className="mt-4 text-sm font-medium text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 underline"
          >
            {t("Submit another review")}
          </button>
        </div>
      )}
    </div>
  )
}
