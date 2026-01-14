import React from 'react';

const EXCHANGE_COLORS = {
  binance: '#F0B90B',
  bybit: '#F7A600',
  hyperliquid: '#00D1FF',
  lighter: '#7C3AED',
};

export default function TopOpportunities({ opportunities, onSelect }) {
  if (!opportunities || opportunities.length === 0) {
    return (
      <div style={styles.empty}>
        <p>Loading opportunities...</p>
      </div>
    );
  }

  const formatPercent = (value) => {
    if (value === undefined || value === null) return '0.0000%';
    return `${(value * 100).toFixed(4)}%`;
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Top Arbitrage Opportunities</h2>
      <div style={styles.grid}>
        {opportunities.slice(0, 6).map((opp, index) => (
          <div
            key={`${opp.symbol}-${opp.long_exchange}-${opp.short_exchange}`}
            style={{
              ...styles.card,
              borderTop: `4px solid ${opp.estimated_apr > 0 ? '#10b981' : '#ef4444'}`,
            }}
            onClick={() => onSelect && onSelect(opp)}
          >
            <div style={styles.cardHeader}>
              <span style={styles.rank}>#{opp.rank || index + 1}</span>
              <span style={styles.symbol}>{opp.symbol?.replace('/USDT:USDT', '')}</span>
              <span style={{
                ...styles.apr,
                color: opp.estimated_apr > 0 ? '#10b981' : '#ef4444',
              }}>
                {opp.estimated_apr?.toFixed(2)}% APR
              </span>
            </div>

            <div style={styles.exchanges}>
              <div style={styles.exchangeItem}>
                <div style={{
                  ...styles.exchangeDot,
                  backgroundColor: EXCHANGE_COLORS[opp.long_exchange] || '#6b7280',
                }} />
                <span style={styles.exchangeLabel}>LONG</span>
                <span style={styles.exchangeName}>{opp.long_exchange?.toUpperCase()}</span>
              </div>
              <div style={styles.arrow}>→</div>
              <div style={styles.exchangeItem}>
                <div style={{
                  ...styles.exchangeDot,
                  backgroundColor: EXCHANGE_COLORS[opp.short_exchange] || '#6b7280',
                }} />
                <span style={styles.exchangeLabel}>SHORT</span>
                <span style={styles.exchangeName}>{opp.short_exchange?.toUpperCase()}</span>
              </div>
            </div>

            <div style={styles.rates}>
              <div style={styles.rateItem}>
                <span style={styles.rateLabel}>Funding Spread</span>
                <span style={styles.rateValue}>{formatPercent(opp.funding_spread)}</span>
              </div>
              <div style={styles.rateItem}>
                <span style={styles.rateLabel}>Long Rate</span>
                <span style={{
                  ...styles.rateValue,
                  color: opp.long_funding_rate >= 0 ? '#ef4444' : '#10b981',
                }}>
                  {formatPercent(opp.long_funding_rate)}
                </span>
              </div>
              <div style={styles.rateItem}>
                <span style={styles.rateLabel}>Short Rate</span>
                <span style={{
                  ...styles.rateValue,
                  color: opp.short_funding_rate >= 0 ? '#10b981' : '#ef4444',
                }}>
                  {formatPercent(opp.short_funding_rate)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: {
    marginBottom: '2rem',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '1rem',
  },
  empty: {
    textAlign: 'center',
    padding: '2rem',
    color: 'white',
    opacity: 0.8,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '1rem',
  },
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '1.25rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    marginBottom: '1rem',
  },
  rank: {
    fontSize: '0.75rem',
    fontWeight: 'bold',
    color: '#6b7280',
    background: '#f3f4f6',
    padding: '0.25rem 0.5rem',
    borderRadius: '4px',
  },
  symbol: {
    fontSize: '1.25rem',
    fontWeight: 'bold',
    color: '#1f2937',
    flex: 1,
  },
  apr: {
    fontSize: '1rem',
    fontWeight: 'bold',
  },
  exchanges: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0.75rem',
    background: '#f9fafb',
    borderRadius: '8px',
    marginBottom: '1rem',
  },
  exchangeItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '0.25rem',
  },
  exchangeDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  exchangeLabel: {
    fontSize: '0.625rem',
    color: '#9ca3af',
    textTransform: 'uppercase',
  },
  exchangeName: {
    fontSize: '0.875rem',
    fontWeight: '600',
    color: '#374151',
  },
  arrow: {
    fontSize: '1.25rem',
    color: '#9ca3af',
  },
  rates: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '0.5rem',
  },
  rateItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '0.125rem',
  },
  rateLabel: {
    fontSize: '0.625rem',
    color: '#9ca3af',
    textTransform: 'uppercase',
  },
  rateValue: {
    fontSize: '0.875rem',
    fontWeight: '600',
    color: '#374151',
  },
};
