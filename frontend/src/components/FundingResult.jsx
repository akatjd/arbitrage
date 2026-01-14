import React from 'react';

export default function FundingResult({ result }) {
  if (!result) return null;

  const formatPercent = (value) => {
    if (value === undefined || value === null) return '0.0000%';
    return `${value >= 0 ? '+' : ''}${(value * 100).toFixed(4)}%`;
  };

  const formatUSD = (value) => {
    if (value === undefined || value === null) return '$0.00';
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
  };

  const isProfitable = result.apr > 0;

  return (
    <div style={{
      ...styles.container,
      borderLeft: `4px solid ${isProfitable ? '#10b981' : '#ef4444'}`,
    }}>
      <div style={styles.header}>
        <div>
          <h3 style={styles.symbol}>{result.symbol?.replace('/USDT:USDT', '') || 'N/A'}</h3>
          <p style={styles.direction}>
            LONG @ {result.long_exchange?.toUpperCase()} / SHORT @ {result.short_exchange?.toUpperCase()}
          </p>
        </div>
        <div style={{
          ...styles.aprBadge,
          background: isProfitable ? '#d1fae5' : '#fee2e2',
          color: isProfitable ? '#065f46' : '#991b1b',
        }}>
          <span style={styles.aprLabel}>APR</span>
          <span style={styles.aprValue}>{result.apr?.toFixed(2) || '0.00'}%</span>
        </div>
      </div>

      <div style={styles.grid}>
        <div style={styles.item}>
          <span style={styles.label}>Funding Rate Spread</span>
          <span style={styles.value}>{formatPercent(result.funding_rate_spread)}</span>
        </div>
        <div style={styles.item}>
          <span style={styles.label}>Price Spread</span>
          <span style={styles.value}>{result.price_spread_percent?.toFixed(4) || '0.0000'}%</span>
        </div>
        <div style={styles.item}>
          <span style={styles.label}>Per Funding Profit</span>
          <span style={styles.value}>{formatUSD(result.per_funding_profit_usdt)}</span>
        </div>
        <div style={styles.item}>
          <span style={styles.label}>Total Funding Count</span>
          <span style={styles.value}>{result.total_funding_count || 0}</span>
        </div>
        <div style={{...styles.item, ...styles.highlight}}>
          <span style={styles.label}>Estimated Total Profit</span>
          <span style={{
            ...styles.value,
            color: isProfitable ? '#10b981' : '#ef4444',
            fontSize: '1.25rem',
          }}>
            {formatUSD(result.estimated_total_profit_usdt)}
          </span>
        </div>
        <div style={styles.item}>
          <span style={styles.label}>Profit Rate</span>
          <span style={styles.value}>{result.estimated_profit_percent?.toFixed(4) || '0.0000'}%</span>
        </div>
        <div style={styles.item}>
          <span style={styles.label}>Required Margin</span>
          <span style={styles.value}>{formatUSD(result.required_margin_usdt)}</span>
        </div>
        <div style={styles.item}>
          <span style={styles.label}>Position Size</span>
          <span style={styles.value}>{formatUSD(result.position_size_usdt)}</span>
        </div>
      </div>

      <div style={styles.fundingDetails}>
        <div style={styles.detailRow}>
          <span>Long ({result.long_exchange}) Funding Rate:</span>
          <span style={{ color: result.long_funding_rate >= 0 ? '#ef4444' : '#10b981' }}>
            {formatPercent(result.long_funding_rate)}
          </span>
        </div>
        <div style={styles.detailRow}>
          <span>Short ({result.short_exchange}) Funding Rate:</span>
          <span style={{ color: result.short_funding_rate >= 0 ? '#10b981' : '#ef4444' }}>
            {formatPercent(result.short_funding_rate)}
          </span>
        </div>
        <div style={styles.detailRow}>
          <span>Long Mark Price:</span>
          <span>{formatUSD(result.long_mark_price)}</span>
        </div>
        <div style={styles.detailRow}>
          <span>Short Mark Price:</span>
          <span>{formatUSD(result.short_mark_price)}</span>
        </div>
      </div>
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '1.5rem',
  },
  symbol: {
    fontSize: '1.75rem',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '0.25rem',
  },
  direction: {
    fontSize: '0.875rem',
    color: '#6b7280',
  },
  aprBadge: {
    padding: '0.75rem 1.25rem',
    borderRadius: '12px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  aprLabel: {
    fontSize: '0.75rem',
    fontWeight: '500',
    textTransform: 'uppercase',
  },
  aprValue: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '1rem',
    marginBottom: '1.5rem',
    padding: '1rem',
    background: '#f9fafb',
    borderRadius: '12px',
  },
  item: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
  },
  highlight: {
    gridColumn: 'span 2',
  },
  label: {
    fontSize: '0.75rem',
    color: '#6b7280',
    textTransform: 'uppercase',
    fontWeight: '500',
  },
  value: {
    fontSize: '1rem',
    color: '#1f2937',
    fontWeight: '600',
  },
  fundingDetails: {
    padding: '1rem',
    background: '#eff6ff',
    borderRadius: '12px',
    borderLeft: '3px solid #3b82f6',
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '0.5rem 0',
    fontSize: '0.875rem',
    borderBottom: '1px solid #dbeafe',
  },
};
