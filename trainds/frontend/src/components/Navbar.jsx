import { NavLink } from 'react-router-dom'
import {
  Train, Map, Activity, Radio, AlertTriangle, Phone, Menu, X, Waypoints
} from 'lucide-react'
import { useState } from 'react'
import ThemeToggle from './ThemeToggle'
import { useLanguage } from '../contexts/LanguageContext'

const navItems = [
  { to: '/',          label: 'Dashboard',    icon: Activity    },
  { to: '/route',     label: 'Route',        icon: Map         },
  { to: '/multi',     label: 'Multi-Stop',   icon: Waypoints   },
  { to: '/delay',     label: 'Delay AI',     icon: Train       },
  { to: '/live',      label: 'Live',         icon: Radio       },
  { to: '/megablock', label: 'Megablock',    icon: AlertTriangle },
  { to: '/sos',       label: 'SOS',          icon: Phone       },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { lang, setLang, t } = useLanguage()

  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80
                    backdrop-blur border-b border-slate-200 dark:border-slate-700">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Brand */}
        <NavLink to="/" className="flex items-center gap-2 font-extrabold
                                    text-brand-600 dark:text-brand-400 text-xl">
          <Train size={22} />
          TRAiNDS
        </NavLink>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium
                 transition-colors duration-150
                 ${isActive
                   ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300'
                   : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                 }`
              }
            >
              <Icon size={16} />
              {t(label)}
            </NavLink>
          ))}
          
          <div className="ml-2 border-l border-slate-200 dark:border-slate-700 pl-3 flex items-center space-x-2">
            <button 
              onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
              className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-lg text-xs font-bold text-brand-600 dark:text-brand-400 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              {lang === 'en' ? 'हिंदी' : 'EN'}
            </button>
            <ThemeToggle />
          </div>
          
          {/* Auth Toggles */}
          <div className="ml-2 flex items-center">
            {localStorage.getItem('token') ? (
              <button 
                onClick={() => { localStorage.removeItem('token'); localStorage.removeItem('username'); window.location.reload(); }}
                className="text-sm font-medium text-slate-600 hover:text-red-500 dark:text-slate-300 dark:hover:text-red-400 transition-colors"
              >
                {t('Logout')}
              </button>
            ) : (
              <NavLink to="/login" className="px-4 py-1.5 rounded-full bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium transition-colors">
                {t('Log In')}
              </NavLink>
            )}
          </div>
        </div>

        {/* Mobile controls */}
        <div className="flex md:hidden items-center gap-2">
          {localStorage.getItem('token') ? (
            <button 
              onClick={() => { localStorage.removeItem('token'); localStorage.removeItem('username'); window.location.reload(); }}
              className="text-xs font-medium text-red-500 mr-2"
            >{t('Logout')}</button>
          ) : (
            <NavLink to="/login" className="text-xs font-medium text-brand-600 dark:text-brand-400 mr-2">{t('Log In')}</NavLink>
          )}
          <button 
            onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
            className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-lg text-xs font-bold text-brand-600 dark:text-brand-400 transition-colors"
          >
            {lang === 'en' ? 'हिंदी' : 'EN'}
          </button>
          <ThemeToggle />
          <button
            onClick={() => setOpen(!open)}
            className="p-2 rounded-lg text-slate-600 dark:text-slate-300
                       hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      {open && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-700
                        bg-white dark:bg-slate-900 px-4 py-3 flex flex-col gap-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium
                 transition-colors
                 ${isActive
                   ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300'
                   : 'text-slate-600 dark:text-slate-300'
                 }`
              }
            >
              <Icon size={16} />
              {t(label)}
            </NavLink>
          ))}
        </div>
      )}
    </nav>
  )
}
