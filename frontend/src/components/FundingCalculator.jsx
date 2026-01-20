import React, { useState, useEffect } from 'react';
import ExchangeSelector from './ExchangeSelector';

export default function FundingCalculator({ onCalculate, isLoading }) {
  const [symbols, setSymbols] = useState([]);
  const [inputs, setInputs] = useState({
    symbol: 'BTC/USDT:USDT',
    longExchange: 'binance',
    shortExchange: 'lighter',
    positionSize: 10000,
    leverage: 2,
    holdingHours: 24,
  });

  // API에서 심볼 목록 가져오기
  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/symbols');
        if (response.ok) {
          const data = await response.json();
          const symbolList = data.symbols.map(s => ({
            value: s,
            label: s.replace('/USDT:USDT', '')
          }));
          setSymbols(symbolList);
        }
      } catch (err) {
        console.error('Failed to fetch symbols:', err);
        // 폴백 심볼 리스트
        setSymbols([
          { value: 'BTC/USDT:USDT', label: 'BTC' },
          { value: 'ETH/USDT:USDT', label: 'ETH' },
        ]);
      }
    };
    fetchSymbols();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    onCalculate(inputs);
  };

  const updateInput = (key, value) => {
    setInputs(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Funding Arbitrage Calculator</h2>

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.row}>
          <div style={styles.field}>
            <label style={styles.label}>Trading Pair</label>
            <select
              value={inputs.symbol}
              onChange={(e) => updateInput('symbol', e.target.value)}
              style={styles.select}
            >
              {symbols.map(s => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div style={styles.row}>
          <div style={styles.field}>
            <ExchangeSelector
              label="Long Exchange"
              value={inputs.longExchange}
              onChange={(v) => updateInput('longExchange', v)}
              excludeValue={inputs.shortExchange}
            />
          </div>
          <div style={styles.field}>
            <ExchangeSelector
              label="Short Exchange"
              value={inputs.shortExchange}
              onChange={(v) => updateInput('shortExchange', v)}
              excludeValue={inputs.longExchange}
            />
          </div>
        </div>

        <div style={styles.row}>
          <div style={styles.field}>
            <label style={styles.label}>Position Size (USDT)</label>
            <input
              type="number"
              value={inputs.positionSize}
              onChange={(e) => updateInput('positionSize', parseFloat(e.target.value) || 0)}
              style={styles.input}
              min="100"
              step="100"
            />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Leverage</label>
            <input
              type="number"
              value={inputs.leverage}
              onChange={(e) => updateInput('leverage', parseFloat(e.target.value) || 1)}
              style={styles.input}
              min="1"
              max="50"
              step="1"
            />
          </div>
        </div>

        <div style={styles.row}>
          <div style={styles.field}>
            <label style={styles.label}>Holding Period (Hours)</label>
            <input
              type="number"
              value={inputs.holdingHours}
              onChange={(e) => updateInput('holdingHours', parseInt(e.target.value) || 1)}
              style={styles.input}
              min="1"
              step="1"
            />
          </div>
        </div>

        <button
          type="submit"
          style={{
            ...styles.button,
            opacity: isLoading ? 0.7 : 1,
          }}
          disabled={isLoading}
        >
          {isLoading ? 'Calculating...' : 'Calculate Arbitrage'}
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    background: 'white',
    borderRadius: '16px',
    padding: '2rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '1.5rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  row: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#374151',
  },
  select: {
    padding: '0.75rem 1rem',
    fontSize: '1rem',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    backgroundColor: 'white',
    cursor: 'pointer',
    outline: 'none',
  },
  input: {
    padding: '0.75rem 1rem',
    fontSize: '1rem',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    outline: 'none',
  },
  button: {
    padding: '1rem 2rem',
    fontSize: '1rem',
    fontWeight: '600',
    color: 'white',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
};
