import { useState, useEffect, useRef } from 'react';

export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    const connect = () => {
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          if (isMounted) {
            setIsConnected(true);
            setError(null);
            console.log('WebSocket connected');
          }
        };

        ws.onmessage = (event) => {
          if (isMounted) {
            try {
              const message = JSON.parse(event.data);
              setData(message);
            } catch (err) {
              console.error('Error parsing WebSocket message:', err);
            }
          }
        };

        ws.onerror = (event) => {
          if (isMounted) {
            setError('WebSocket error occurred');
            console.error('WebSocket error:', event);
          }
        };

        ws.onclose = () => {
          if (isMounted) {
            setIsConnected(false);
            console.log('WebSocket disconnected');

            // 자동 재연결 (3초 후)
            reconnectTimeoutRef.current = setTimeout(() => {
              if (isMounted) {
                console.log('Attempting to reconnect...');
                connect();
              }
            }, 3000);
          }
        };
      } catch (err) {
        if (isMounted) {
          setError(`Failed to connect: ${err.message}`);
          console.error('WebSocket connection error:', err);
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  return { data, isConnected, error };
}
