import { useState, useRef, useEffect } from 'react'
import { MessageSquare, X, Send, Loader2, Bot, User } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

export default function Chatbot() {
  const { lang, t } = useLanguage()
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { text: t("Hi! I am the TRAiNDS Assistant. Ask me about routes, delays, or when to leave for your destination!"), sender: "bot" }
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const fetchHistory = async () => {
      const token = localStorage.getItem("token")
      if (!token) return
      try {
        const res = await fetch("http://127.0.0.1:5000/api/chat/history", {
          headers: { "Authorization": `Bearer ${token}` }
        })
        const data = await res.json()
        if (data.history && data.history.length > 0) {
          setMessages([
            { text: t("Hi! I am the TRAiNDS Assistant. Ask me about routes, delays, or when to leave for your destination!"), sender: "bot" },
            ...data.history
          ])
        }
      } catch (err) {
        console.error("History fetch failed:", err)
      }
    }
    if (isOpen) {
      fetchHistory()
    }
  }, [isOpen])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setMessages(prev => [...prev, { text: userMessage, sender: "user" }])
    setInput("")
    setIsLoading(true)

    const token = localStorage.getItem("token")
    const headers = { "Content-Type": "application/json" }
    if (token) headers["Authorization"] = `Bearer ${token}`

    try {
      const res = await fetch("http://127.0.0.1:5000/api/chat", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ message: userMessage, lang })
      })
      
      const data = await res.json()
      
      setMessages(prev => [...prev, { 
        text: data.reply || "Sorry, I am facing some internal logic errors.", 
        sender: "bot" 
      }])
    } catch (err) {
      setMessages(prev => [...prev, { 
        text: "Error reaching the backend. Please ensure the server is online.", 
        sender: "bot" 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 p-4 rounded-full shadow-lg bg-brand-600 text-white hover:scale-105 transition-transform z-50 ${isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}`}
      >
        <MessageSquare className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      <div 
        className={`fixed bottom-6 right-6 w-80 sm:w-96 bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 flex flex-col overflow-hidden transition-all duration-300 transform origin-bottom-right z-50 ${isOpen ? 'scale-100 opacity-100' : 'scale-0 opacity-0'}`}
        style={{ height: '500px', maxHeight: '80vh' }}
      >
        {/* Header */}
        <div className="bg-brand-600 text-white p-4 flex justify-between items-center shadow-md">
          <div className="flex items-center space-x-2">
            <Bot className="w-5 h-5" />
            <span className="font-semibold text-lg">{t('AI Assistant')}</span>
          </div>
          <button 
            onClick={() => setIsOpen(false)}
            className="hover:bg-brand-700 p-1 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 dark:bg-slate-900/50">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
              <div 
                className={`max-w-[80%] rounded-2xl p-3 shadow-sm ${
                  msg.sender === "user" 
                    ? "bg-brand-600 text-white rounded-tr-sm" 
                    : "bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 rounded-tl-sm border border-slate-100 dark:border-slate-600"
                }`}
              >
                <p className="text-sm leading-relaxed">{msg.text}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 rounded-2xl rounded-tl-sm p-3 shadow-sm border border-slate-100 dark:border-slate-600">
                <Loader2 className="w-5 h-5 animate-spin text-brand-600 dark:text-brand-400" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSend} className="p-3 bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("Ask about trains, delays...")}
              className="flex-1 bg-slate-100 dark:bg-slate-700 dark:text-white px-4 py-2.5 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="bg-brand-600 text-white p-2.5 rounded-full hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </>
  )
}
