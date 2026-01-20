import React, { useState, useEffect } from 'react';

export default function FundingDetailModal({ symbol, onClose }) {
  const [loading, setLoading] = useState(true);
  const [rates, setRates] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAllRates = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/api/v1/funding-rates/all/${encodeURIComponent(symbol)}`);
        if (response.ok) {
          const data = await response.json();
          setRates(data.rates || {});
        } else {
          setError('Failed to fetch funding rates');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchAllRates();
  }, [symbol]);

  const formatRate = (rate) => {
    if (rate === undefined || rate === null) return '-';
    return `${(rate * 100).toFixed(4)}%`;
  };

  const formatRateHourly = (rate, interval) => {
    if (rate === undefined || rate === null || !interval) return '-';
    const hourlyRate = rate / interval;
    return `${(hourlyRate * 100).toFixed(4)}%`;
  };

  const formatPrice = (price) => {
    if (!price) return '-';
    return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}`;
  };

  const getExchangeColor = (exchange) => {
    const colors = {
      binance: '#F0B90B',
      bybit: '#F7A600',
      lighter: '#7C3AED',
      hyperliquid: '#00D1FF',
    };
    return colors[exchange] || '#6b7280';
  };

  const formatExchangeName = (exchange) => {
    return exchange.charAt(0).toUpperCase() + exchange.slice(1);
  };

  // 펀딩 레이트 기준 정렬 (낮은 순 = 롱에 유리)
  const sortedRates = Object.entries(rates).sort((a, b) => {
    return (a[1]?.funding_rate || 0) - (b[1]?.funding_rate || 0);
  });

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.header}>
          <h2 style={styles.title}>
            {symbol.replace('/USDT:USDT', '')} Funding Rates
          </h2>
          <button style={styles.closeBtn} onClick={onClose}>×</button>
        </div>

        {loading && (
          <div style={styles.loading}>Loading...</div>
        )}

        {error && (
          <div style={styles.error}>{error}</div>
        )}

        {!loading && !error && (
          <>
            <div style={styles.legend}>
              <div style={styles.legendItem}>
                <span style={{...styles.legendDot, background: '#10b981'}}></span>
                <span>음수 = Long 포지션에 유리 (펀딩피 수령)</span>
              </div>
              <div style={styles.legendItem}>
                <span style={{...styles.legendDot, background: '#ef4444'}}></span>
                <span>양수 = Short 포지션에 유리 (펀딩피 수령)</span>
              </div>
            </div>

            <div style={styles.tableWrapper}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>거래소</th>
                    <th style={styles.th}>펀딩 주기</th>
                    <th style={styles.th}>펀딩 레이트</th>
                    <th style={styles.th}>시간당 환산</th>
                    <th style={styles.th}>Mark Price</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedRates.map(([exchange, data]) => (
                    <tr key={exchange} style={styles.tr}>
                      <td style={styles.td}>
                        <div style={styles.exchangeCell}>
                          <span
                            style={{
                              ...styles.exchangeDot,
                              background: getExchangeColor(exchange)
                            }}
                          ></span>
                          <span style={styles.exchangeName}>
                            {formatExchangeName(exchange)}
                          </span>
                        </div>
                      </td>
                      <td style={styles.td}>
                        <span style={styles.intervalBadge}>
                          {data?.funding_interval_hours || '?'}h
                        </span>
                      </td>
                      <td style={{
                        ...styles.td,
                        ...styles.rateCell,
                        color: data?.funding_rate < 0 ? '#10b981' : data?.funding_rate > 0 ? '#ef4444' : '#6b7280'
                      }}>
                        {formatRate(data?.funding_rate)}
                      </td>
                      <td style={{
                        ...styles.td,
                        color: '#6b7280',
                        fontSize: '0.875rem'
                      }}>
                        {formatRateHourly(data?.funding_rate, data?.funding_interval_hours)}/h
                      </td>
                      <td style={styles.td}>
                        {formatPrice(data?.mark_price)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {sortedRates.length === 0 && (
              <div style={styles.noData}>
                No funding rate data available for this symbol.
              </div>
            )}

            {sortedRates.length >= 2 && (
              <div style={styles.suggestion}>
                <h4 style={styles.suggestionTitle}>💡 추천 전략</h4>
                <p style={styles.suggestionText}>
                  <strong>{formatExchangeName(sortedRates[0][0])}</strong>에서 Long,
                  <strong> {formatExchangeName(sortedRates[sortedRates.length - 1][0])}</strong>에서 Short
                </p>
                <p style={styles.suggestionDetail}>
                  스프레드: {formatRate((sortedRates[sortedRates.length - 1][1]?.funding_rate || 0) - (sortedRates[0][1]?.funding_rate || 0))}
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.6)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '1rem',
  },
  modal: {
    background: 'white',
    borderRadius: '16px',
    maxWidth: '700px',
    width: '100%',
    maxHeight: '80vh',
    overflow: 'auto',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.5rem',
    borderBottom: '1px solid #e5e7eb',
    position: 'sticky',
    top: 0,
    background: 'white',
    zIndex: 10,
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    fontSize: '2rem',
    cursor: 'pointer',
    color: '#6b7280',
    lineHeight: 1,
    padding: '0.5rem',
  },
  legend: {
    padding: '1rem 1.5rem',
    background: '#f9fafb',
    display: 'flex',
    gap: '1.5rem',
    flexWrap: 'wrap',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    fontSize: '0.75rem',
    color: '#6b7280',
  },
  legendDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
  },
  tableWrapper: {
    padding: '1rem 1.5rem',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    textAlign: 'left',
    padding: '0.75rem',
    borderBottom: '2px solid #e5e7eb',
    fontSize: '0.75rem',
    fontWeight: '600',
    color: '#6b7280',
    textTransform: 'uppercase',
  },
  tr: {
    borderBottom: '1px solid #f3f4f6',
  },
  td: {
    padding: '0.75rem',
    fontSize: '0.875rem',
  },
  exchangeCell: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  exchangeDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
  },
  exchangeName: {
    fontWeight: '600',
    color: '#1f2937',
  },
  intervalBadge: {
    display: 'inline-block',
    padding: '0.25rem 0.5rem',
    background: '#e0e7ff',
    color: '#4f46e5',
    borderRadius: '4px',
    fontSize: '0.75rem',
    fontWeight: '600',
  },
  rateCell: {
    fontWeight: '600',
    fontSize: '1rem',
  },
  loading: {
    padding: '3rem',
    textAlign: 'center',
    color: '#6b7280',
  },
  error: {
    padding: '1.5rem',
    background: '#fee2e2',
    color: '#b91c1c',
    margin: '1rem 1.5rem',
    borderRadius: '8px',
  },
  noData: {
    padding: '2rem',
    textAlign: 'center',
    color: '#6b7280',
  },
  suggestion: {
    margin: '1rem 1.5rem 1.5rem',
    padding: '1rem',
    background: 'linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%)',
    borderRadius: '12px',
    border: '1px solid #bfdbfe',
  },
  suggestionTitle: {
    margin: '0 0 0.5rem 0',
    fontSize: '1rem',
    color: '#1e40af',
  },
  suggestionText: {
    margin: '0 0 0.25rem 0',
    fontSize: '0.875rem',
    color: '#1f2937',
  },
  suggestionDetail: {
    margin: 0,
    fontSize: '0.875rem',
    color: '#6b7280',
  },
};
