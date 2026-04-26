import { createContext, useContext, useState, useEffect, useRef } from 'react'
import { translationAPI } from '../api/client'

const LanguageContext = createContext()

// Core Static Dictionary ensuring absolute 0ms latency!
const initialDictionary = {
  // Navigation & General
  "Dashboard": "डैशबोर्ड",
  "Route": "मार्ग",
  "Multi-Stop": "मल्टी-स्टॉप",
  "Delay AI": "देरी एआई",
  "Live": "लाइव",
  "Megablock": "मेगाब्लॉक",
  "SOS": "एसओएस (SOS)",
  "Log In": "लॉग इन",
  "Logout": "लॉगआउट",
  "Quick Access": "त्वरित पहुंच",
  
  // Dashboard
  "Mumbai Local": "मुंबई लोकल",
  "AI Assistant": "एआई सहायक",
  "Real-time routes · Delay prediction · Live tracking": "वास्तविक समय मार्ग · विलंब भविष्यवाणी · लाइव ट्रैकिंग",
  "Lines Active": "सक्रिय लाइनें",
  "Stations": "स्टेशन",
  "Trains / Day": "ट्रेनें / दिन",
  "Daily Riders": "दैनिक यात्री",
  "Across Mumbai network": "पूरे मुंबई नेटवर्क में",
  "Average daily services": "औसत दैनिक सेवाएँ",
  "Approximate commuters": "लगभग यात्री",
  "Mumbai": "मुंबई",

  // Route Planner
  "Route Planner": "रूट प्लानर",
  "From": "कहाँ से",
  "To": "कहाँ तक",
  "Swap": "अदला-बदली",
  "Find Route": "मार्ग खोजें",
  "Finding route…": "मार्ग खोज रहे हैं…",
  "Comparing…": "तुलना कर रहे हैं…",
  "What-If Analysis": "क्या-अगर विश्लेषण",
  "Best Route": "सबसे अच्छा मार्ग",
  "Journey Segments": "यात्रा के खंड",
  "Change here": "यहाँ बदलें",
  "Direct journey – no changes required": "✅ सीधी यात्रा – किसी बदलाव की आवश्यकता नहीं",
  "train change required": "ट्रेन बदलाव आवश्यक",
  "train changes required": "ट्रेन बदलाव आवश्यक",
  "Option": "विकल्प",
  "Recommended": "अनुशंसित",
  "Low": "कम",
  "Medium": "मध्यम",
  "High": "उच्च",
  "delay risk": "देरी का जोखिम",
  "Est. Departure": "अनुमानित प्रस्थान",
  "Total Time": "कुल समय",
  "Reasoning Analysis": "तर्क विश्लेषण",
  "Leave Now": "अभी निकलें",
  "Wait": "प्रतीक्षा करें",
  
  // Multi-Stop
  "Multi-Stop Journey": "मल्टी-स्टॉप यात्रा",
  "Plan complex travels across up to 4 stations simultaneously!": "एक साथ 4 स्टेशनों तक की जटिल यात्राओं की योजना बनाएं!",
  "Starting Station": "प्रारंभिक स्टेशन",
  "e.g. Dahanu Road": "उदा. दहानू रोड",
  "Destinations (Max 4)": "मंजिलें (अधिकतम 4)",
  "Add Stop": "स्टॉप जोड़ें",
  "Enter station...": "स्टेशन दर्ज करें...",
  "Strategy Mode": "रणनीति मोड",
  "Smart Optimize (Fastest)": "स्मार्ट ऑप्टिमाइज़ (सबसे तेज़)",
  "Strict Priority (Ordered)": "सख्त प्राथमिकता (क्रमबद्ध)",
  "Calculating Sequences...": "अनुक्रमों की गणना की जा रही है...",
  "Determine Best Route": "सबसे अच्छा मार्ग निर्धारित करें",
  "Recommendation": "अनुशंसा",
  "Optimal Sequence": "इष्टतम अनुक्रम",
  "Leg": "चरण",
  "stops": "स्टॉप",
  "mins": "मिनट",
  
  // Delay AI
  "Delay Prediction": "विलंब भविष्यवाणी",
  "Select Station": "स्टेशन चुनें",
  "Predict Delay": "विलंब की भविष्यवाणी करें",
  "Predicting...": "भविष्यवाणी की जा रही है...",
  "Arrival Time": "आगमन समय",
  "Predicted Delay": "अनुमानित विलंब",
  "Confidence": "विश्वास",
  
  // Chatbot
  "Assistant": "सहायक",
  "Type a message...": "संदेश टाइप करें...",
  "Ask about trains, delays...": "ट्रेनों, देरी के बारे में पूछें...",
  "Hi! I am the TRAiNDS Assistant. Ask me about routes, delays, or when to leave for your destination!": "नमस्ते! मैं TRAiNDS सहायक हूँ। मुझसे मार्ग, देरी, या अपनी मंजिल के लिए निकलने के समय के बारे में पूछें!",
  
  // SOS & Megablock
  "Emergency SOS": "आपातकालीन SOS",
  "Police": "पुलिस",
  "Ambulance": "एम्बुलेंस",
  "Railway Helpline": "रेलवे हेल्पलाइन",
  "Active Megablocks": "सक्रिय मेगाब्लॉक",
  "No active blocks reported": "कोई सक्रिय ब्लॉक नहीं",
  "Date": "तारीख",
  "Time": "समय",
  "Line": "लाइन",

  // Feedback & Common
  "Help us improve!": "सुधारने में हमारी मदद करें!",
  "Rate your experience": "अपने अनुभव का मूल्यांकन करें",
  "Submit Feedback": "प्रतिक्रिया जमा करें",
  "Tell us what you loved or what we could do better... (Optional)": "हमें बताएं आपको क्या पसंद आया या हम क्या बेहतर कर सकते हैं... (वैकल्पिक)",
  "⚠️ Active Megablocks": "⚠️ सक्रिय मेगाब्लॉक",
  "Submitting...": "जमा हो रहा है...",
  "Submit another review": "एक और समीक्षा जमा करें",
  "Plan Route": "मार्ग योजनाएं",
  "Delay Predictor": "विलंब भविष्यवाणी",
  "Live Trains": "लाइव ट्रेनें",
  "Megablocks": "मेगाब्लॉक",
  "SOS / Help": "एसओएस / मदद"
}

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(localStorage.getItem('lang') || 'en')
  
  const [dynamicDict, setDynamicDict] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('dynamicDict')) || {}
    } catch {
      return {}
    }
  })

  const pendingTranslations = useRef(new Set())
  const timeoutRef = useRef(null)

  useEffect(() => {
    localStorage.setItem('lang', lang)
  }, [lang])

  useEffect(() => {
    localStorage.setItem('dynamicDict', JSON.stringify(dynamicDict))
  }, [dynamicDict])

  const fetchTranslations = async () => {
    if (pendingTranslations.current.size === 0 || lang === 'en') return
    
    const textsToTranslate = Array.from(pendingTranslations.current)
    pendingTranslations.current.clear()

    try {
      const data = await translationAPI.translateTexts(textsToTranslate, lang)
      if (data.translations) {
        setDynamicDict(prev => ({ ...prev, ...data.translations }))
      }
    } catch (e) {
      console.error("Translation error", e)
    }
  }

  const convertNumerals = (str) => {
    if (lang !== 'hi' || !str) return str;
    const hindiNumerals = ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९'];
    return str.toString().replace(/[0-9]/g, (w) => hindiNumerals[+w]);
  }

  const t = (text) => {
    if (!text || typeof text !== 'string') return text;
    if (lang === 'en') return text;
    
    let result = text;

    // Check static dictionary first
    if (initialDictionary[text]) {
      result = initialDictionary[text];
    } else if (dynamicDict[text]) {
      // Check dynamic dictionary
      result = dynamicDict[text];
    } else {
      // If not found anywhere, queue it for translation
      if (!pendingTranslations.current.has(text)) {
        pendingTranslations.current.add(text)
        clearTimeout(timeoutRef.current)
        timeoutRef.current = setTimeout(fetchTranslations, 500)
      }
    }

    // Always convert numbers if in Hindi
    return convertNumerals(result);
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export const useLanguage = () => useContext(LanguageContext)
