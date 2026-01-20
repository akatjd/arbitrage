import React from 'react';

const EXCHANGES = [
  { id: 'binance', name: 'Binance', color: '#F0B90B' },
  { id: 'bybit', name: 'Bybit', color: '#F7A600' },
  { id: 'lighter', name: 'Lighter', color: '#7C3AED' },
];

export default function ExchangeSelector({ value, onChange, label, excludeValue }) {
  const filteredExchanges = excludeValue
    ? EXCHANGES.filter(ex => ex.id !== excludeValue)
    : EXCHANGES;

  return (
    <div style={styles.container}>
      {label && <label style={styles.label}>{label}</label>}
      <div style={styles.selectWrapper}>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          style={styles.select}
        >
          {filteredExchanges.map(exchange => (
            <option key={exchange.id} value={exchange.id}>
              {exchange.name}
            </option>
          ))}
        </select>
        <div
          style={{
            ...styles.indicator,
            backgroundColor: EXCHANGES.find(e => e.id === value)?.color || '#6b7280'
          }}
        />
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#374151',
  },
  selectWrapper: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  select: {
    width: '100%',
    padding: '0.75rem 1rem',
    paddingLeft: '2rem',
    fontSize: '1rem',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    backgroundColor: 'white',
    cursor: 'pointer',
    appearance: 'none',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  indicator: {
    position: 'absolute',
    left: '0.75rem',
    width: '12px',
    height: '12px',
    borderRadius: '50%',
  },
};
