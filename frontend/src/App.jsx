import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import Header from './components/Header';
import ArbitrageCard from './components/ArbitrageCard';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

function App() {
  const { data, isConnected, error } = useWebSocket('ws://localhost:8000/ws');
  const [opportunities, setOpportunities] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [avgKimchiPremium, setAvgKimchiPremium] = useState(0);

  useEffect(() => {
    if (data && data.type === 'arbitrage_update') {
      setOpportunities(data.data || []);
      setAvgKimchiPremium(data.avg_kimchi_premium || 0);
      setLastUpdate(new Date(data.timestamp));
    }
  }, [data]);

  return (
    <div className="app">
      <Header isConnected={isConnected} />

      <main style={styles.main}>
        <div style={styles.container}>
          {error && (
            <div style={styles.error}>
              <p>{error}</p>
            </div>
          )}

          {!isConnected && !error && <LoadingSpinner />}

          {isConnected && opportunities.length === 0 && (
            <div style={styles.noData}>
              <p>Waiting for arbitrage data...</p>
            </div>
          )}

          {isConnected && opportunities.length > 0 && (
            <>
              <div style={styles.statsBar}>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Total Pairs</span>
                  <span style={styles.statValue}>{opportunities.length}</span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Profitable</span>
                  <span style={{
                    ...styles.statValue,
                    color: '#10b981'
                  }}>
                    {opportunities.filter(o => o.is_profitable).length}
                  </span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>평균 김치 프리미엄</span>
                  <span style={{
                    ...styles.statValue,
                    color: avgKimchiPremium > 0 ? '#f59e0b' : '#ef4444'
                  }}>
                    {avgKimchiPremium > 0 ? '+' : ''}{avgKimchiPremium.toFixed(4)}%
                  </span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Best Opportunity</span>
                  <span style={{
                    ...styles.statValue,
                    color: '#667eea'
                  }}>
                    {opportunities[0]?.profit_percent.toFixed(4)}%
                  </span>
                </div>
                {lastUpdate && (
                  <div style={styles.stat}>
                    <span style={styles.statLabel}>Last Update</span>
                    <span style={styles.statValue}>
                      {lastUpdate.toLocaleTimeString()}
                    </span>
                  </div>
                )}
              </div>

              <div style={styles.grid}>
                {opportunities.map((opportunity, index) => (
                  <ArbitrageCard key={`${opportunity.symbol}-${index}`} opportunity={opportunity} />
                ))}
              </div>
            </>
          )}
        </div>
      </main>

      <footer style={styles.footer}>
        <p>Crypto Arbitrage Monitor - Real-time price tracking for Binance & Upbit</p>
      </footer>
    </div>
  );
}

const styles = {
  main: {
    flex: 1,
    padding: '2rem',
  },
  container: {
    maxWidth: '1400px',
    margin: '0 auto',
  },
  error: {
    background: '#fee2e2',
    border: '1px solid #ef4444',
    borderRadius: '8px',
    padding: '1rem',
    marginBottom: '1rem',
    color: '#b91c1c',
  },
  noData: {
    textAlign: 'center',
    padding: '4rem',
    color: 'white',
    fontSize: '1.125rem',
  },
  statsBar: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
    marginBottom: '2rem',
  },
  stat: {
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    padding: '1.5rem',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  statLabel: {
    fontSize: '0.875rem',
    color: '#6b7280',
    textTransform: 'uppercase',
    fontWeight: '500',
  },
  statValue: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1f2937',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
    gap: '1.5rem',
  },
  footer: {
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    padding: '1.5rem',
    textAlign: 'center',
    color: '#6b7280',
    fontSize: '0.875rem',
  },
};

export default App;
