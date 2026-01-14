import React from 'react';

export default function ArbitrageCard({ opportunity }) {
  const isProfitable = opportunity.is_profitable && opportunity.profit_percent > 0;
  const profitColor = isProfitable ? '#10b981' : '#ef4444';

  return (
    <div style={{
      ...styles.card,
      borderLeft: `4px solid ${profitColor}`,
    }}>
      <div style={styles.cardHeader}>
        <div>
          <h3 style={styles.symbol}>{opportunity.symbol.replace('/USDT', '')}</h3>
          <p style={styles.direction}>{opportunity.direction}</p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-end' }}>
          <div style={styles.profitBadge}>
            <span style={{
              ...styles.profitPercent,
              color: profitColor,
            }}>
              {opportunity.profit_percent > 0 ? '+' : ''}{opportunity.profit_percent.toFixed(4)}%
            </span>
          </div>
        </div>
      </div>

      <div style={styles.actionBox}>
        <span style={styles.actionLabel}>Trading Strategy:</span>
        <span style={styles.actionValue}>{opportunity.action}</span>
      </div>

      <div style={styles.priceGrid}>
        <div style={styles.priceItem}>
          <span style={styles.label}>{opportunity.buy_exchange} (Buy)</span>
          <span style={styles.value}>${opportunity.buy_price_usd.toLocaleString()}</span>
        </div>
        <div style={styles.priceItem}>
          <span style={styles.label}>{opportunity.sell_exchange} (Sell)</span>
          <span style={styles.value}>${opportunity.sell_price_usd.toLocaleString()}</span>
        </div>
        <div style={styles.priceItem}>
          <span style={styles.label}>Price Difference</span>
          <span style={styles.value}>${opportunity.price_difference_usd?.toLocaleString() ?? '0'}</span>
        </div>
        <div style={styles.priceItem}>
          <span style={styles.label}>Spread</span>
          <span style={styles.value}>{opportunity.raw_premium_percent.toFixed(4)}%</span>
        </div>
        <div style={styles.priceItem}>
          <span style={styles.label}>Net Profit (fee incl.)</span>
          <span style={{
            ...styles.value,
            color: opportunity.profit_usd > 0 ? '#10b981' : '#ef4444'
          }}>${opportunity.profit_usd.toLocaleString()}</span>
        </div>
      </div>

      <div style={styles.footer}>
        <div style={styles.footerItem}>
          <span style={styles.footerLabel}>Buy Cost (fee incl.)</span>
          <span style={styles.footerValue}>${opportunity.buy_cost_usd.toLocaleString()}</span>
        </div>
        <div style={styles.arrow}>→</div>
        <div style={styles.footerItem}>
          <span style={styles.footerLabel}>Sell Revenue (fee incl.)</span>
          <span style={styles.footerValue}>${opportunity.sell_revenue_usd.toLocaleString()}</span>
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
    cursor: 'pointer',
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
  direction: {
    fontSize: '0.875rem',
    color: '#6b7280',
  },
  profitBadge: {
    padding: '0.5rem 1rem',
    background: '#f3f4f6',
    borderRadius: '8px',
  },
  pureBadge: {
    padding: '0.375rem 0.75rem',
    background: 'white',
    borderRadius: '6px',
    border: '2px solid',
    display: 'flex',
    gap: '0.25rem',
    alignItems: 'center',
  },
  profitPercent: {
    fontSize: '1.25rem',
    fontWeight: 'bold',
  },
  priceGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '1rem',
    marginBottom: '1rem',
    padding: '1rem',
    background: '#f9fafb',
    borderRadius: '8px',
  },
  priceItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
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
  footer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '1rem',
    background: '#f9fafb',
    borderRadius: '8px',
  },
  footerItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
    flex: 1,
  },
  footerLabel: {
    fontSize: '0.75rem',
    color: '#6b7280',
    textTransform: 'uppercase',
  },
  footerValue: {
    fontSize: '1rem',
    color: '#1f2937',
    fontWeight: '600',
  },
  arrow: {
    fontSize: '1.5rem',
    color: '#667eea',
    fontWeight: 'bold',
    padding: '0 1rem',
  },
  actionBox: {
    padding: '1rem',
    background: '#eff6ff',
    borderRadius: '8px',
    marginBottom: '1rem',
    borderLeft: '3px solid #3b82f6',
  },
  actionLabel: {
    fontSize: '0.75rem',
    color: '#3b82f6',
    textTransform: 'uppercase',
    fontWeight: '600',
    display: 'block',
    marginBottom: '0.25rem',
  },
  actionValue: {
    fontSize: '0.875rem',
    color: '#1e40af',
    fontWeight: 'bold',
  },
};
