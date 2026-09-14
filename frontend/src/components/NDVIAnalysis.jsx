import { useEffect, useState } from 'react';
import { Satellite, Leaf, TrendingUp, Info } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import { useLanguage, pcodeMap } from '../contexts/LanguageContext';
import { API_BASE_URL } from '../api';

export default function NDVIAnalysis() {
  const { t, language } = useLanguage();
  const [regions, setRegions] = useState([]);
  const [selectedPcode, setSelectedPcode] = useState('');
  const [ndviData, setNdviData] = useState({ labels: [], vim: [], viq: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();

    const loadRegions = async () => {
      try {
        setError('');
        const response = await fetch(
          `${API_BASE_URL}/analytics/ndvi-regions`,
          { signal: controller.signal }
        );
        const availableRegions = await response.json();
        setRegions(availableRegions);
        setSelectedPcode((current) => current || availableRegions[0]?.PCODE || '');
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('NDVI regions error:', err);
          setError('Unable to load NDVI regions.');
          setLoading(false);
        }
      }
    };

    loadRegions();
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!selectedPcode) return undefined;
    const controller = new AbortController();

    const loadNdvi = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await fetch(
          `${API_BASE_URL}/ndvi/${encodeURIComponent(selectedPcode)}`,
          { signal: controller.signal }
        );
        setNdviData(await response.json());
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('NDVI data error:', err);
          setError('Unable to load NDVI measurements for this region.');
          setNdviData({ labels: [], vim: [], viq: [] });
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    };

    loadNdvi();
    return () => controller.abort();
  }, [selectedPcode]);

  const chartData = {
    labels: ndviData?.labels || [],
    datasets: [
      {
        label: t('ndvi.latestVim'),
        data: ndviData?.vim || [],
        borderColor: '#2ecc71',
        backgroundColor: 'rgba(46, 204, 113, 0.2)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y'
      },
      {
        label: t('ndvi.latestViq'),
        data: ndviData?.viq || [],
        borderColor: '#f59e0b',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        tension: 0.4,
        yAxisID: 'y1'
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        labels: {
          color: '#334155',
          font: { size: 13, weight: '600' },
          padding: 18,
          usePointStyle: true,
        }
      }
    },
    scales: {
      x: { ticks: { color: '#475569' }, grid: { color: 'rgba(148,163,184,0.18)' } },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: { display: true, text: t('ndvi.latestVim'), color: '#2ecc71' },
        ticks: { color: '#475569' },
        grid: { color: 'rgba(148,163,184,0.18)' }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: { display: true, text: t('ndvi.latestViq'), color: '#f59e0b' },
        grid: { drawOnChartArea: false },
        ticks: { color: '#475569' }
      },
    },
  };

  const getRegionName = (pcode, adm_id) => {
    // If it's in our mapping (e.g. MMR001), use the mapped name.
    // If it's a district (like MMR001D001), fallback to the original PCODE or adm_id
    if (pcodeMap[language] && pcodeMap[language][pcode]) {
      return pcodeMap[language][pcode];
    }
    // Attempt to extract the state part for districts (e.g. MMR001 from MMR001D001)
    if (pcode && pcode.length > 6) {
      const statePcode = pcode.substring(0, 6);
      if (pcodeMap[language] && pcodeMap[language][statePcode]) {
        return `${pcodeMap[language][statePcode]} (${pcode})`;
      }
    }
    return `${adm_id} (${pcode})`;
  };

  return (
    <div className="ndvi-analysis">
      <h2 className="m-0 text-xl font-semibold"><Satellite size={28} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '10px' }}/> {t('ndvi.title')}</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        {t('ndvi.subtitle')}
      </p>

      {/* Simple explanation box */}
      <div className="glass-panel" style={{ marginBottom: '2rem', background: 'rgba(52, 152, 219, 0.1)', border: '1px solid rgba(52, 152, 219, 0.3)' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#3498db', fontSize: '1.1rem', marginBottom: '0.5rem' }}>
          <Info size={18} /> {t('ndvi.whatIsNdvi')}
        </h3>
        <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <li><strong>{t('ndvi.vimDesc')}</strong></li>
          <li><strong>{t('ndvi.viqDesc')}</strong></li>
        </ul>
      </div>

      <div className="ndvi-controls glass-panel">
        <label style={{ margin: 0 }}>{t('ndvi.selectRegion')}</label>
        <select 
          value={selectedPcode} 
          onChange={(e) => setSelectedPcode(e.target.value)}
          disabled={loading && regions.length === 0}
        >
          {regions.map((r) => (
            <option key={`${r.PCODE}-${r.adm_id}`} value={r.PCODE}>{getRegionName(r.PCODE, r.adm_id)}</option>
          ))}
        </select>
      </div>

      {error && <p className="crop-suggestion-error" role="alert">{error}</p>}
      {loading && <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>Loading NDVI data…</p>}

      <div className="grid grid-cols-3" style={{ gap: '1rem', marginBottom: '2rem' }}>
        <div className="glass-panel">
          <h3><Leaf size={18} style={{ display: 'inline', verticalAlign: 'text-bottom' }}/> {t('ndvi.latestVim')}</h3>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary)' }}>
             {ndviData?.vim?.length ? ndviData.vim[ndviData.vim.length-1].toFixed(3) : '-'}
          </div>
        </div>
        <div className="glass-panel">
          <h3>{t('ndvi.avgVim')}</h3>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--secondary)' }}>
             {ndviData?.vim?.length ? (ndviData.vim.reduce((a,b)=>a+b,0)/ndviData.vim.length).toFixed(3) : '-'}
          </div>
        </div>
        <div className="glass-panel">
          <h3><TrendingUp size={18} style={{ display: 'inline', verticalAlign: 'text-bottom' }}/> {t('ndvi.latestViq')}</h3>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--warning)' }}>
             {ndviData?.viq?.length ? ndviData.viq[ndviData.viq.length-1].toFixed(1) : '-'}
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ height: '400px' }}>
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}
