import { useState, useRef } from 'react';
import {
  CircleDollarSign,
  CircleCheck,
  Droplets,
  FlaskConical,
  LandPlot,
  Leaf,
  Lightbulb,
  MapPin,
  Satellite,
  Scale,
  Sparkles,
  Sprout,
  ThermometerSun,
  TriangleAlert,
  Wheat,
  X,
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { API_BASE_URL } from '../api';

const mockSuggestions = {
  Rice: { icon: '🌾', match: 94, marketRate: 1450, yieldPerAcre: 2100, reason: 'Warm temperatures, balanced soil pH, and strong rainfall make these conditions well suited for rice.' },
  Maize: { icon: '🌽', match: 89, marketRate: 980, yieldPerAcre: 1800, reason: 'The current temperature and soil conditions support strong maize establishment and healthy growth.' },
  Chickpea: { icon: '🌱', match: 86, marketRate: 3200, yieldPerAcre: 850, reason: 'Low rainfall and near-neutral soil favor chickpea, which performs well in relatively dry conditions.' },
};

const cropDetails = {
  ...mockSuggestions,
  Corn: { icon: '🌽', match: 89, marketRate: 980, yieldPerAcre: 1800, reason: 'The current conditions support strong corn establishment and healthy growth.' },
  Wheat: { icon: '🌾', match: 85, marketRate: 1250, yieldPerAcre: 1500, reason: 'Cooler temperatures make these conditions suitable for wheat.' },
  Beans: { icon: '🌱', match: 84, marketRate: 2600, yieldPerAcre: 900, reason: 'Moderate rainfall and temperature provide suitable growing conditions for beans.' },
  Sesame: { icon: '🌿', match: 88, marketRate: 3500, yieldPerAcre: 650, reason: 'Lower rainfall favors drought-tolerant sesame.' },
};

const cropIconMap = {
  Rice: Wheat,
  Wheat,
  Corn: Sprout,
  Beans: Leaf,
  Sesame: Leaf,
};

function CropIcon({ cropKey, size = 32 }) {
  const Icon = cropIconMap[cropKey] || Sprout;
  return <Icon size={size} strokeWidth={1.8} aria-hidden="true" />;
}

function AdvisoryIcon({ severity }) {
  if (severity === 'warning' || severity === 'danger') {
    return <TriangleAlert size={20} aria-hidden="true" />;
  }
  if (severity === 'success') {
    return <CircleCheck size={20} aria-hidden="true" />;
  }
  return <Lightbulb size={20} aria-hidden="true" />;
}

export default function CropSuggestion() {
  const { t, language } = useLanguage();
  
  // Form data — auto-filled by satellite or entered manually
  const [formData, setFormData] = useState({
    soil_pH: 6.5,
    rainfall_mm: 0,
    temperature_c: 28.0
  });
  
  // Location & weather state
  const [mode, setMode] = useState('auto'); // 'auto' or 'manual'
  const [locStatus, setLocStatus] = useState('idle'); // idle | detecting | fetching | done | error
  const [weatherData, setWeatherData] = useState(null);
  const [locError, setLocError] = useState(null);
  
  // ML prediction state
  const [suggestion, setSuggestion] = useState(null);
  const [predictionConfidence, setPredictionConfidence] = useState(null);
  const [predictionRecommendations, setPredictionRecommendations] = useState([]);
  const [selectedRecommendationIndex, setSelectedRecommendationIndex] = useState(0);
  const [explanation, setExplanation] = useState('');
  const [loading, setLoading] = useState(false);
  const [explaining, setExplaining] = useState(false);
  const [error, setError] = useState(null);
  const [marketWeight, setMarketWeight] = useState(100);
  const [farmAcreage, setFarmAcreage] = useState(1);
  
  const streamedTextRef = useRef('');

  const handleChange = (e) => {
    const value = e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value === '' ? '' : Number(value)
    });
  };

  // ─── Auto-Detect Location ──────────────────────────────────────
  const detectLocation = () => {
    if (!navigator.geolocation) {
      setLocError(t('loc.error'));
      setLocStatus('error');
      return;
    }

    setLocStatus('detecting');
    setLocError(null);
    setWeatherData(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        setLocStatus('fetching');

        try {
          const response = await axios.post(`${API_BASE_URL}/location-weather`, {
            latitude,
            longitude,
            language
          });

          const data = response.data;
          setWeatherData(data);

          // Auto-fill form with satellite data
          setFormData({
            soil_pH: data.current.soil_pH_estimate,
            rainfall_mm: data.current.rainfall_7d_mm,
            temperature_c: data.current.temperature_c
          });

          setLocStatus('done');
        } catch (err) {
          console.error('Weather fetch error:', err);
          setLocError(t('loc.error'));
          setLocStatus('error');
        }
      },
      (err) => {
        console.error('Geolocation error:', err);
        if (err.code === err.PERMISSION_DENIED) {
          setLocError(t('loc.permDenied'));
        } else {
          setLocError(t('loc.error'));
        }
        setLocStatus('error');
      },
      { enableHighAccuracy: true, timeout: 15000 }
    );
  };

  // ─── LLM Crop Explanation ─────────────────────────────────────
  const fetchExplanation = async (crop) => {
    setExplaining(true);
    setExplanation('');
    streamedTextRef.current = '';
    
    try {
      const response = await fetch(`${API_BASE_URL}/crop-explanation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, crop, language })
      });

      if (!response.body) throw new Error('ReadableStream not supported.');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      let buffer = '';
      let streamDone = false;
      
      while (!streamDone) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              if (data.content) {
                streamedTextRef.current += data.content;
                setExplanation(streamedTextRef.current);
              }
              if (data.done) streamDone = true;
            } catch (e) { /* skip */ }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setExplanation(t('chat.error'));
    } finally {
      setExplaining(false);
    }
  };

  // ─── Submit Prediction ────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuggestion(null);
    setPredictionRecommendations([]);
    setSelectedRecommendationIndex(0);
    setExplanation('');
    
    try {
      const payload = Object.fromEntries(
        Object.entries(formData).map(([key, value]) => [key, Number(value)])
      );
      if (Object.values(payload).some((value) => !Number.isFinite(value))) {
        setError('Please enter valid numbers for all crop conditions.');
        setLoading(false);
        return;
      }
      const response = await fetch(
        `${API_BASE_URL}/crop-suggestion`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...payload, language })
        }
      );
      const data = await response.json();
      const crop = data.crop;
      setSuggestion(crop);
      setPredictionConfidence(data.confidencePercent);
      setPredictionRecommendations(data.recommendations || []);
      setSelectedRecommendationIndex(0);
      setExplanation(
        data.recommendations?.[0]?.description
        || `${crop} is the best rule-based match for the supplied conditions.`
      );
      setLoading(false);
    } catch (err) {
      console.error('Crop prediction error:', err);
      setError('Unable to get a crop suggestion.');
      setLoading(false);
    }
  };

  const selectedRecommendation =
    predictionRecommendations[selectedRecommendationIndex] || null;

  const selectRecommendation = (recommendation, index) => {
    setSelectedRecommendationIndex(index);
    setSuggestion(recommendation.crop);
    setPredictionConfidence(recommendation.suitabilityPercent);
    setExplanation(recommendation.description);
  };

  return (
    <div className="crop-suggestion">
      <h2 className="m-0 text-xl font-semibold">{t('crop.title')}</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        {t('crop.subtitle')}
      </p>

      <div className="crop-input-layout">
        {/* ─── Left Panel: Location + Inputs ─── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', alignSelf: 'start' }}>

          {/* Mode Toggle */}
          <div className="mode-toggle">
            <button className={mode === 'auto' ? 'active' : ''} onClick={() => setMode('auto')}>
              <Satellite size={14} style={{display:'inline', marginRight:'0.4rem', verticalAlign:'text-bottom'}}/> {t('loc.autoMode')}
            </button>
            <button className={mode === 'manual' ? 'active' : ''} onClick={() => setMode('manual')}>
               {t('loc.manualMode')}
            </button>
          </div>

          {/* Auto Mode: Detect Location */}
          {mode === 'auto' && (
            <div className="glass-panel">
              <button 
                className="detect-btn"
                onClick={detectLocation}
                disabled={locStatus === 'detecting' || locStatus === 'fetching'}
              >
                {locStatus === 'detecting' && <><div className="spinner" /> {t('loc.detecting')}</>}
                {locStatus === 'fetching' && <><div className="spinner" /> {t('loc.fetchWeather')}</>}
                {(locStatus === 'idle' || locStatus === 'error' || locStatus === 'done') && (
                  <><div className="pulse-dot" /> {t('loc.detect')}</>
                )}
              </button>

              {locError && (
                <p style={{ color: 'var(--danger)', fontSize: '0.85rem', marginTop: '0.75rem', textAlign: 'center' }}>
                  {locError}
                </p>
              )}

              {/* Weather Data Cards */}
              {weatherData && (
                <div style={{ marginTop: '1.25rem', animation: 'fadeIn 0.5s ease' }}>
                  {/* Region Badge */}
                  <div className="region-badge">
                    <MapPin size={16} />
                    {language === 'my' ? weatherData.region.name_my : weatherData.region.name_en}
                  </div>

                  <div className="weather-grid">
                    <div className="weather-card">
                      <div className="weather-icon">🌡️</div>
                      <div className="weather-label">{t('loc.currentTemp')}</div>
                      <div className="weather-value">
                        {weatherData.current.temperature_c}<span className="weather-unit">°C</span>
                      </div>
                    </div>
                    <div className="weather-card">
                      <div className="weather-icon">🌧️</div>
                      <div className="weather-label">{t('loc.rain7d')}</div>
                      <div className="weather-value">
                        {weatherData.current.rainfall_7d_mm}<span className="weather-unit">mm</span>
                      </div>
                    </div>
                    {weatherData.current.humidity_pct && (
                      <div className="weather-card">
                        <div className="weather-icon">💧</div>
                        <div className="weather-label">{t('loc.humidity')}</div>
                        <div className="weather-value">
                          {weatherData.current.humidity_pct}<span className="weather-unit">%</span>
                        </div>
                      </div>
                    )}
                    <div className="weather-card">
                      <div className="weather-icon">🧪</div>
                      <div className="weather-label">{t('loc.soilPh')}</div>
                      <div className="weather-value">
                        {weatherData.current.soil_pH_estimate}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span className="data-source-tag">
                      <Satellite size={12} /> {t('loc.source')}
                    </span>
                  </div>

                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    {t('loc.phNote')}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* ─── Smart Advisories ─── */}
          {weatherData && weatherData.advisories && weatherData.advisories.length > 0 && mode === 'auto' && (
            <div className="glass-panel" style={{ animation: 'fadeIn 0.5s ease' }}>
              <h3 style={{ marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Lightbulb size={20} /> {t('loc.advisories')}
              </h3>
              <div className="advisories-container">
                {weatherData.advisories.map((adv, idx) => (
                  <div key={idx} className={`advisory-card ${adv.severity}`}>
                    <div className="advisory-icon">
                      <AdvisoryIcon severity={adv.severity} />
                    </div>
                    <div className="advisory-content">
                      <div className="advisory-title">
                        {language === 'my' ? adv.title_my : adv.title_en}
                      </div>
                      <div className="advisory-message">
                        {language === 'my' ? adv.message_my : adv.message_en}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ─── Input Form (always visible) ─── */}
          <form onSubmit={handleSubmit} className="glass-panel crop-suggestion-form">
            {mode === 'auto' && weatherData && (
              <p className="crop-form-note">
                {t('loc.override')}
              </p>
            )}
            <div className="form-group">
              <label><FlaskConical size={16} style={{display:'inline', marginRight:'0.5rem', verticalAlign:'text-bottom'}}/> {t('crop.soilPh')}</label>
              <input 
                type="number" 
                name="soil_pH" 
                step="0.1" 
                value={formData.soil_pH} 
                onChange={handleChange} 
                required 
              />
            </div>
            <div className="form-group">
              <label><Droplets size={16} style={{display:'inline', marginRight:'0.5rem', verticalAlign:'text-bottom'}}/> {t('crop.rainfall')}</label>
              <input 
                type="number" 
                name="rainfall_mm" 
                step="1" 
                value={formData.rainfall_mm} 
                onChange={handleChange} 
                required 
              />
            </div>
            <div className="form-group">
              <label><ThermometerSun size={16} style={{display:'inline', marginRight:'0.5rem', verticalAlign:'text-bottom'}}/> {t('crop.temp')}</label>
              <input 
                type="number" 
                name="temperature_c" 
                step="0.1" 
                value={formData.temperature_c} 
                onChange={handleChange} 
                required 
              />
            </div>
            <button type="submit" className="btn btn-primary crop-suggestion-submit" disabled={loading || explaining}>
              <Sprout size={18} />
              {loading ? t('crop.analyzing') : t('crop.suggestBtn')}
            </button>
            {error && (
              <p className="crop-suggestion-error" role="alert">
                {error}
              </p>
            )}
          </form>
        </div>
      </div>

      {suggestion && selectedRecommendation && (
        <div className="suggestion-modal-backdrop" onClick={() => setSuggestion(null)}>
          <section className="suggestion-pop-card" role="dialog" aria-modal="true" aria-label="Crop suggestion" onClick={(event) => event.stopPropagation()}>
            <button className="suggestion-close" type="button" aria-label="Close" onClick={() => setSuggestion(null)}>
              <X size={20} />
            </button>
            <div className="suggestion-crop-icon">
              <CropIcon cropKey={selectedRecommendation.cropKey} size={42} />
            </div>
            <p className="suggestion-eyebrow">{t('crop.recommended')}</p>
            <h2>{selectedRecommendation.crop}</h2>
            <span className="match-badge">{selectedRecommendation.suitabilityPercent}% suitable</span>
            <p className="suggestion-pop-reason">{selectedRecommendation.description}</p>

            {predictionRecommendations.length > 1 && (
              <div className="recommendation-options" aria-label="Choose a crop recommendation">
                {predictionRecommendations.map((recommendation, index) => (
                  <button
                    type="button"
                    key={recommendation.crop}
                    className={`recommendation-option ${selectedRecommendationIndex === index ? 'active' : ''}`}
                    aria-pressed={selectedRecommendationIndex === index}
                    onClick={() => selectRecommendation(recommendation, index)}
                  >
                    <span className="recommendation-option-name">
                      <span className="recommendation-option-icon">
                        <CropIcon cropKey={recommendation.cropKey} size={22} />
                      </span>
                      <span>
                        <small>Option {index + 1}</small>
                        <strong>{recommendation.crop}</strong>
                      </span>
                    </span>
                    <span className="recommendation-score">{recommendation.suitabilityPercent}%</span>
                  </button>
                ))}
              </div>
            )}

            <div className="crop-calculators">
              <div className="crop-calculator-card">
                <div className="calculator-heading">
                  <span><CircleDollarSign size={18} /> Market Value</span>
                  <small>{selectedRecommendation.marketPriceMmkPerKg.toLocaleString()} MMK/kg</small>
                </div>
                <label htmlFor="market-weight"><Scale size={14} /> Product weight (kg)</label>
                <input
                  id="market-weight"
                  type="number"
                  min="0"
                  step="1"
                  value={marketWeight}
                  onChange={(event) => setMarketWeight(Math.max(0, Number(event.target.value)))}
                />
                <p className="calculator-result">
                  <span>Estimated value</span>
                  <strong>{(marketWeight * selectedRecommendation.marketPriceMmkPerKg).toLocaleString()} MMK</strong>
                </p>
              </div>

              <div className="crop-calculator-card">
                <div className="calculator-heading">
                  <span><LandPlot size={18} /> Crop Yield</span>
                  <small>{selectedRecommendation.yieldPerAcreKg.toLocaleString()} kg/acre</small>
                </div>
                <label htmlFor="farm-acreage"><LandPlot size={14} /> Farm acreage</label>
                <input
                  id="farm-acreage"
                  type="number"
                  min="0"
                  step="0.1"
                  value={farmAcreage}
                  onChange={(event) => setFarmAcreage(Math.max(0, Number(event.target.value)))}
                />
                <p className="calculator-result">
                  <span>Expected production</span>
                  <strong>{(farmAcreage * selectedRecommendation.yieldPerAcreKg).toLocaleString()} kg</strong>
                </p>
              </div>
            </div>
            <button type="button" className="btn btn-primary" onClick={() => setSuggestion(null)}>Close</button>
          </section>
        </div>
      )}
    </div>
  );
}
