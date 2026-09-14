import { useEffect, useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { API_BASE_URL, DEMO_FIELD_ID } from '../api';

export default function HealthUpdates() {
  const { t } = useLanguage();
  const [updates, setUpdates] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  
  const [formData, setFormData] = useState({
    township: '',
    crop_type: '',
    health_status: 'Healthy',
    disease_details: '',
    reported_by: ''
  });

  useEffect(() => {
    let active = true;
    fetch(`${API_BASE_URL}/fields/${DEMO_FIELD_ID}/alerts`)
      .then((response) => response.ok ? response.json() : [])
      .then((data) => {
        if (active) setAlerts(data);
      })
      .catch(() => {
        if (active) setAlerts([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false };
  }, []);

  const updateAlert = async (id, action) => {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/${id}/${action}`, { method: 'PATCH' });
      if (response.ok) {
        const updated = await response.json();
        setAlerts((current) => current.map((alert) => alert.id === id ? updated : alert));
      }
    } catch (error) {
      console.error('Error updating alert:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        setUpdates(current => current.map(item => item.id === editingId
          ? { ...item, ...formData }
          : item));
      } else {
        setUpdates(current => [{
          ...formData,
          id: Date.now(),
          reported_at: new Date().toISOString(),
        }, ...current]);
      }
      setFormData({
        township: '',
        crop_type: '',
        health_status: 'Healthy',
        disease_details: '',
        reported_by: ''
      });
      setEditingId(null);
    } catch (error) {
      console.error("Error saving update:", error);
    }
  };

  const handleEdit = (update) => {
    setEditingId(update.id);
    setFormData({
      township: update.township,
      crop_type: update.crop_type,
      health_status: update.health_status,
      disease_details: update.disease_details || '',
      reported_by: update.reported_by
    });
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this report?")) {
      setUpdates(current => current.filter(item => item.id !== id));
    }
  };

  const translateStatus = (status) => {
    if (status === 'Healthy') return t('status.healthy');
    if (status === 'Diseased') return t('status.diseased');
    if (status === 'Pest Infested') return t('status.pest');
    if (status === 'Drought Stressed') return t('status.drought');
    return status;
  };

  return (
    <div className="health-updates">
      <h2 className="m-0 text-xl font-semibold">{t('health.title')}</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
        {t('health.subtitle')}
      </p>

      <div className="grid grid-cols-2" style={{ gap: '2rem' }}>
        <div className="glass-panel" style={{ alignSelf: 'start' }}>
          <h2>{editingId ? t('health.edit') : t('health.new')}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>{t('health.township')}</label>
              <input type="text" name="township" value={formData.township} onChange={handleChange} required />
            </div>
            
            <div className="form-group">
              <label>{t('health.cropType')}</label>
              <input type="text" name="crop_type" value={formData.crop_type} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label>{t('health.status')}</label>
              <select name="health_status" value={formData.health_status} onChange={handleChange}>
                <option value="Healthy">{t('status.healthy')}</option>
                <option value="Diseased">{t('status.diseased')}</option>
                <option value="Pest Infested">{t('status.pest')}</option>
                <option value="Drought Stressed">{t('status.drought')}</option>
              </select>
            </div>

            <div className="form-group">
              <label>{t('health.details')}</label>
              <textarea name="disease_details" value={formData.disease_details} onChange={handleChange} rows="3" />
            </div>

            <div className="form-group">
              <label>{t('health.reportedBy')}</label>
              <input type="text" name="reported_by" value={formData.reported_by} onChange={handleChange} required />
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                {editingId ? t('health.update') : t('health.submit')}
              </button>
              {editingId && (
                <button type="button" className="btn btn-outline" onClick={() => {
                  setEditingId(null);
                  setFormData({
                    township: '',
                    crop_type: '',
                    health_status: 'Healthy',
                    disease_details: '',
                    reported_by: ''
                  });
                }}>
                  {t('health.cancel')}
                </button>
              )}
            </div>
          </form>
        </div>

        <div>
          {alerts.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h2>Field alerts</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {alerts.map((alert) => (
                  <div key={alert.id} className="glass-panel" style={{ padding: '1rem', borderLeft: `4px solid ${alert.severity === 'critical' ? '#ef4444' : '#f59e0b'}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                      <strong>{alert.severity.toUpperCase()} · {alert.riskType}</strong>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{alert.status}</span>
                    </div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '0.5rem 0 0.75rem' }}>{alert.message}</p>
                    {alert.status !== 'resolved' && (
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {alert.status === 'open' && <button type="button" className="btn btn-outline" onClick={() => updateAlert(alert.id, 'acknowledge')}>Acknowledge</button>}
                        <button type="button" className="btn btn-primary" onClick={() => updateAlert(alert.id, 'resolve')}>Resolve</button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          <h2>{t('health.recent')}</h2>
          {loading ? (
            <p>{t('health.loading')}</p>
          ) : updates.length === 0 ? (
            <div className="glass-panel" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
              {t('health.noReports')}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {updates.map(update => (
                <div key={update.id} className="glass-panel" style={{ padding: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <h3 style={{ margin: 0 }}>{update.township} - {update.crop_type}</h3>
                    <span style={{ 
                      padding: '0.25rem 0.75rem', 
                      borderRadius: '1rem', 
                      fontSize: '0.85rem',
                      background: update.health_status === 'Healthy' ? 'rgba(46, 204, 113, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                      color: update.health_status === 'Healthy' ? '#2ecc71' : '#ef4444'
                    }}>
                      {translateStatus(update.health_status)}
                    </span>
                  </div>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                    {update.disease_details || 'No details provided.'}
                  </p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    <span>By: {update.reported_by} | {new Date(update.reported_at).toLocaleDateString()}</span>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => handleEdit(update)} style={{ background: 'transparent', border: 'none', color: 'var(--secondary)', cursor: 'pointer' }}>Edit</button>
                      <button onClick={() => handleDelete(update.id)} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}>Delete</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
