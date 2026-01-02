import React, { useState, useEffect } from 'react';
import axios from 'axios';

const StorageManager = () => {
  const [storageInfo, setStorageInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cleanupAge, setCleanupAge] = useState(24);
  const [message, setMessage] = useState('');

  const fetchStorageInfo = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:7860/storage/info');
      setStorageInfo(response.data);
      setMessage('');
    } catch (error) {
      console.error('Error fetching storage info:', error);
      setMessage('Failed to fetch storage info');
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:7860/storage/cleanup?max_age_hours=${cleanupAge}`);
      setMessage(response.data.message);
      fetchStorageInfo(); // Refresh info after cleanup
    } catch (error) {
      console.error('Error cleaning up storage:', error);
      setMessage('Failed to cleanup storage');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStorageInfo();
  }, []);

  return (
    <div className="storage-manager" style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px', marginTop: '20px' }}>
      <h3>📦 Storage Management</h3>
      
      {message && <div className="message" style={{ padding: '10px', backgroundColor: '#f0f0f0', marginBottom: '10px', borderRadius: '4px' }}>{message}</div>}

      <div className="storage-info-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
        {storageInfo && Object.entries(storageInfo).map(([key, info]) => (
          <div key={key} className="storage-card" style={{ padding: '15px', border: '1px solid #eee', borderRadius: '6px', backgroundColor: '#fafafa' }}>
            <h4 style={{ textTransform: 'capitalize', marginTop: 0 }}>{key.replace('_', ' ')}</h4>
            <p><strong>Files:</strong> {info.file_count !== undefined ? info.file_count : 'N/A'}</p>
            <p><strong>Size:</strong> {info.size_mb} MB</p>
            {info.cleanup_policy && <p style={{ fontSize: '0.9em', color: '#666' }}>ℹ️ {info.cleanup_policy}</p>}
            {info.note && <p style={{ fontSize: '0.9em', color: '#666' }}>ℹ️ {info.note}</p>}
          </div>
        ))}
      </div>

      <div className="cleanup-controls" style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '15px', backgroundColor: '#fff0f0', borderRadius: '6px' }}>
        <span>🧹 <strong>Cleanup Temporary Files:</strong></span>
        <label>
          Older than:
          <input 
            type="number" 
            value={cleanupAge} 
            onChange={(e) => setCleanupAge(e.target.value)}
            style={{ width: '60px', marginLeft: '5px', marginRight: '5px' }}
            min="1"
          />
          hours
        </label>
        <button 
          onClick={handleCleanup} 
          disabled={loading}
          style={{ padding: '5px 15px', backgroundColor: '#ff4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          {loading ? 'Cleaning...' : 'Run Cleanup'}
        </button>
      </div>
      
      <div style={{ marginTop: '10px', textAlign: 'right' }}>
        <button onClick={fetchStorageInfo} style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}>
          Refresh Info
        </button>
      </div>
    </div>
  );
};

export default StorageManager;
