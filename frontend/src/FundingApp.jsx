import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import Header from './components/Header';
import TopOpportunities from './components/TopOpportunities';
import FundingCalculator from './components/FundingCalculator';
import FundingResult from './components/FundingResult';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

function FundingApp() {
  const { data, isConnected, error } = useWebSocket('ws://localhost:8000/ws');
  const [opportunities, setOpportunities] = useState([]);
  const [calculationResult, setCalculationResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [stats, setStats] = useState({
    totalOpportunities: 0,
    profitableCount: 0,
    bestAPR: 0,
  });

  useEffect(() => {
    if (data && data.type === 'funding_update') {
      const opps = data.data || [];
      setOpportunities(opps);
      setLastUpdate(new Date(data.timestamp));

      // Calculate statistics
      const profitable = opps.filter(o => o.estimated_apr > 0);
      const bestAPR = opps.length > 0 ? Math.max(...opps.map(o => o.estimated_apr)) : 0;

      setStats({
        totalOpportunities: opps.length,
        profitableCount: profitable.length,
        bestAPR: bestAPR,
      });
    }
  }, [data]);

  const handleCalculate = async (inputs) => {
    setIsCalculating(true);
    setCalculationResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/funding-arbitrage/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: inputs.symbol,
          long_exchange: inputs.longExchange,
          short_exchange: inputs.shortExchange,
          position_size_usdt: inputs.positionSize,
          leverage: inputs.leverage,
          holding_hours: inputs.holdingHours,
        }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('선택한 거래소에서 해당 거래쌍을 지원하지 않습니다.\n다른 거래소 또는 거래쌍을 선택해 주세요.');
        }
        throw new Error(`오류가 발생했습니다. (코드: ${response.status})`);
      }

      const result = await response.json();
      setCalculationResult(result);
    } catch (err) {
      console.error('Calculation error:', err);
      alert(err.message);
    } finally {
      setIsCalculating(false);
    }
  };

  const handleSelectOpportunity = (opp) => {
    // Auto-fill calculator with selected opportunity
    const inputs = {
      symbol: opp.symbol,
      longExchange: opp.long_exchange,
      shortExchange: opp.short_exchange,
      positionSize: 10000,
      leverage: 2,
      holdingHours: 24,
    };
    handleCalculate(inputs);

    // Scroll to calculator
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app">
      <Header isConnected={isConnected} title="Funding Rate Arbitrage Monitor" />

      <main style={styles.main}>
        <div style={styles.container}>
          {error && (
            <div style={styles.error}>
              <p>{error}</p>
            </div>
          )}

          {!isConnected && !error && <LoadingSpinner />}

          {isConnected && (
            <>
              {/* Statistics Bar */}
              <div style={styles.statsBar}>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Connection Status</span>
                  <span style={{
                    ...styles.statValue,
                    color: '#10b981',
                  }}>
                    LIVE
                  </span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Total Opportunities</span>
                  <span style={styles.statValue}>{stats.totalOpportunities}</span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Profitable</span>
                  <span style={{
                    ...styles.statValue,
                    color: '#10b981',
                  }}>
                    {stats.profitableCount}
                  </span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Best APR</span>
                  <span style={{
                    ...styles.statValue,
                    color: '#667eea',
                  }}>
                    {stats.bestAPR.toFixed(2)}%
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

              {/* Calculator Section */}
              <div style={styles.section}>
                <FundingCalculator
                  onCalculate={handleCalculate}
                  isLoading={isCalculating}
                />
              </div>

              {/* Calculation Result */}
              {calculationResult && (
                <div style={styles.section}>
                  <FundingResult result={calculationResult} />
                </div>
              )}

              {/* Top Opportunities */}
              {opportunities.length > 0 && (
                <div style={styles.section}>
                  <TopOpportunities
                    opportunities={opportunities}
                    onSelect={handleSelectOpportunity}
                  />
                </div>
              )}

              {opportunities.length === 0 && (
                <div style={styles.noData}>
                  <p>Waiting for funding rate data...</p>
                  <p style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                    The system is collecting funding rates from multiple exchanges.
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <footer style={styles.footer}>
        <p>Funding Rate Arbitrage Monitor - Real-time tracking across Binance, Bybit, Hyperliquid & more</p>
        <p style={{ fontSize: '0.75rem', marginTop: '0.5rem', opacity: 0.7 }}>
          Data updates every 60 seconds | Funding rates updated every 8 hours
        </p>
      </footer>
    </div>
  );
}

const styles = {
  main: {
    flex: 1,
    padding: '2rem',
    minHeight: 'calc(100vh - 200px)',
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
  section: {
    marginBottom: '2rem',
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
  footer: {
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    padding: '1.5rem',
    textAlign: 'center',
    color: '#6b7280',
    fontSize: '0.875rem',
  },
};

export default FundingApp;
