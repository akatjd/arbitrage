import React from 'react';

export default function Header({ isConnected, title = 'Crypto Arbitrage Monitor' }) {
  return (
    <header style={styles.header}>
      <div style={styles.container}>
        <h1 style={styles.title}>{title}</h1>
        <div style={styles.status}>
          <div style={{
            ...styles.statusDot,
            backgroundColor: isConnected ? '#10b981' : '#ef4444'
          }}></div>
          <span style={styles.statusText}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </header>
  );
}

const styles = {
  header: {
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    padding: '1.5rem 2rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
  },
  container: {
    maxWidth: '1400px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '1.75rem',
    fontWeight: 'bold',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  status: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  statusDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    animation: 'pulse 2s infinite',
  },
  statusText: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#6b7280',
  },
};
