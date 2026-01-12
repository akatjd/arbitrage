import React from 'react';

export default function ArbitrageCard({ opportunity }) {
  const isProfitable = opportunity.is_profitable && opportunity.profit_percent > 0;
  const profitColor = isProfitable ? '#10b981' : '#ef4444';

  // 순수 차익 색상
  const pureArbitrageColor = opportunity.pure_arbitrage_percent > 0 ? '#10b981' :
                             opportunity.pure_arbitrage_percent < 0 ? '#ef4444' : '#6b7280';

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
          <div style={{...styles.pureBadge, borderColor: pureArbitrageColor}}>
            <span style={{fontSize: '0.75rem', color: '#6b7280'}}>순수 차익: </span>
            <span style={{fontSize: '0.875rem', fontWeight: 'bold', color: pureArbitrageColor}}>
              {opportunity.pure_arbitrage_percent > 0 ? '+' : ''}{opportunity.pure_arbitrage_percent?.toFixed(4) || '0.0000'}%
            </span>
          </div>
        </div>
      </div>

      <div style={styles.priceGrid}>
        <div style={styles.priceItem}>
          <span style={styles.label}>Binance (USDT)</span>
          <span style={styles.value}>${opportunity.binance_price_usd.toLocaleString()}</span>
        </div>
        <div style={styles.priceItem}>
          <span style={styles.label}>Binance (KRW)</span>
          <span style={styles.value}>₩{opportunity.binance_price_krw.toLocaleString()}</span>
        </div>
        <div style={styles.priceItem}>
          <span style={styles.label}>Upbit (KRW)</span>
          <span style={styles.value}>₩{opportunity.upbit_price_krw.toLocaleString()}</span>
        </div>
        <div style={styles.priceItem}>
          <span style={styles.label}>Exchange Rate</span>
          <span style={styles.value}>₩{opportunity.exchange_rate.toLocaleString()}</span>
        </div>
      </div>

      <div style={styles.footer}>
        <div style={styles.footerItem}>
          <span style={styles.footerLabel}>Buy at</span>
          <span style={styles.footerValue}>₩{opportunity.buy_price.toLocaleString()}</span>
        </div>
        <div style={styles.arrow}>→</div>
        <div style={styles.footerItem}>
          <span style={styles.footerLabel}>Sell at</span>
          <span style={styles.footerValue}>₩{opportunity.sell_price.toLocaleString()}</span>
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
};
