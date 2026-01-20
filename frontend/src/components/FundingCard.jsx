import React from 'react';

export default function FundingCard({ opportunity, onClick }) {
  const apr = opportunity.estimated_apr || 0;
  const isGoodApr = apr > 10;
  const profitColor = isGoodApr ? '#10b981' : apr > 0 ? '#f59e0b' : '#ef4444';

  const formatRate = (rate) => {
    if (rate === undefined || rate === null) return '0.0000%';
    return `${(rate * 100).toFixed(4)}%`;
  };

  const formatExchange = (exchange) => {
    if (!exchange) return 'Unknown';
    return exchange.charAt(0).toUpperCase() + exchange.slice(1);
  };

  const formatInterval = (hours) => {
    if (!hours) return '?h';
    return `${hours}h`;
  };

  return (
    <div
      style={{
        ...styles.card,
        borderLeft: `4px solid ${profitColor}`,
        cursor: onClick ? 'pointer' : 'default',
      }}
      onClick={onClick}
    >
      <div style={styles.cardHeader}>
        <div>
          <h3 style={styles.symbol}>{opportunity.symbol?.replace('/USDT:USDT', '').replace('/USDC:USDC', '')}</h3>
          <p style={styles.rank}>Rank #{opportunity.rank}</p>
        </div>
        <div style={styles.aprBadge}>
          <span style={{
            ...styles.aprValue,
            color: profitColor,
          }}>
            {apr.toFixed(2)}% APR
          </span>
        </div>
      </div>

      <div style={styles.strategyBox}>
        <span style={styles.strategyLabel}>Strategy:</span>
        <span style={styles.strategyValue}>
          Long on {formatExchange(opportunity.long_exchange)} / Short on {formatExchange(opportunity.short_exchange)}
        </span>
      </div>

      <div style={styles.rateGrid}>
        <div style={styles.rateItem}>
          <span style={styles.label}>
            {formatExchange(opportunity.long_exchange)} Funding
            <span style={styles.intervalBadge}>{formatInterval(opportunity.long_funding_interval)}</span>
          </span>
          <span style={{
            ...styles.value,
            color: opportunity.long_funding_rate < 0 ? '#10b981' : '#ef4444'
          }}>
            {formatRate(opportunity.long_funding_rate)}
          </span>
          <span style={styles.hourlyRate}>
            ({formatRate(opportunity.long_funding_rate_hourly)}/h)
          </span>
        </div>
        <div style={styles.rateItem}>
          <span style={styles.label}>
            {formatExchange(opportunity.short_exchange)} Funding
            <span style={styles.intervalBadge}>{formatInterval(opportunity.short_funding_interval)}</span>
          </span>
          <span style={{
            ...styles.value,
            color: opportunity.short_funding_rate > 0 ? '#10b981' : '#ef4444'
          }}>
            {formatRate(opportunity.short_funding_rate)}
          </span>
          <span style={styles.hourlyRate}>
            ({formatRate(opportunity.short_funding_rate_hourly)}/h)
          </span>
        </div>
        <div style={styles.rateItem}>
          <span style={styles.label}>Spread (Original)</span>
          <span style={{
            ...styles.value,
            color: '#667eea'
          }}>
            {formatRate(opportunity.funding_spread)}
          </span>
        </div>
        <div style={styles.rateItem}>
          <span style={styles.label}>Spread (Hourly)</span>
          <span style={{
            ...styles.value,
            color: '#667eea',
            fontWeight: 'bold'
          }}>
            {formatRate(opportunity.funding_spread_hourly)}
          </span>
        </div>
        <div style={{...styles.rateItem, gridColumn: 'span 2'}}>
          <span style={styles.label}>Est. APR (based on hourly spread)</span>
          <span style={{
            ...styles.value,
            color: profitColor,
            fontSize: '1.25rem'
          }}>
            {apr.toFixed(2)}%
          </span>
        </div>
      </div>

      <div style={styles.priceSection}>
        <div style={styles.priceItem}>
          <span style={styles.priceLabel}>Long Mark Price</span>
          <span style={styles.priceValue}>
            ${opportunity.long_mark_price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}
          </span>
        </div>
        <div style={styles.arrow}>vs</div>
        <div style={styles.priceItem}>
          <span style={styles.priceLabel}>Short Mark Price</span>
          <span style={styles.priceValue}>
            ${opportunity.short_mark_price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}
          </span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '1.5rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '1rem',
  },
  symbol: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '0.25rem',
  },
  rank: {
    fontSize: '0.875rem',
    color: '#6b7280',
  },
  aprBadge: {
    padding: '0.5rem 1rem',
    background: '#f3f4f6',
    borderRadius: '8px',
  },
  aprValue: {
    fontSize: '1.25rem',
    fontWeight: 'bold',
  },
  strategyBox: {
    padding: '1rem',
    background: '#eff6ff',
    borderRadius: '8px',
    marginBottom: '1rem',
    borderLeft: '3px solid #3b82f6',
  },
  strategyLabel: {
    fontSize: '0.75rem',
    color: '#3b82f6',
    textTransform: 'uppercase',
    fontWeight: '600',
    display: 'block',
    marginBottom: '0.25rem',
  },
  strategyValue: {
    fontSize: '0.875rem',
    color: '#1e40af',
    fontWeight: 'bold',
  },
  rateGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '1rem',
    marginBottom: '1rem',
    padding: '1rem',
    background: '#f9fafb',
    borderRadius: '8px',
  },
  rateItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
  },
  label: {
    fontSize: '0.75rem',
    color: '#6b7280',
    textTransform: 'uppercase',
    fontWeight: '500',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  intervalBadge: {
    display: 'inline-block',
    padding: '0.125rem 0.375rem',
    background: '#e0e7ff',
    color: '#4f46e5',
    borderRadius: '4px',
    fontSize: '0.625rem',
    fontWeight: '600',
    textTransform: 'none',
  },
  value: {
    fontSize: '1rem',
    fontWeight: '600',
  },
  hourlyRate: {
    fontSize: '0.75rem',
    color: '#9ca3af',
    fontWeight: '500',
  },
  priceSection: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '1rem',
    background: '#f9fafb',
    borderRadius: '8px',
  },
  priceItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
    flex: 1,
  },
  priceLabel: {
    fontSize: '0.75rem',
    color: '#6b7280',
    textTransform: 'uppercase',
  },
  priceValue: {
    fontSize: '1rem',
    color: '#1f2937',
    fontWeight: '600',
  },
  arrow: {
    fontSize: '1rem',
    color: '#667eea',
    fontWeight: 'bold',
    padding: '0 1rem',
  },
};
