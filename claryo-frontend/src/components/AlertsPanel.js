// src/components/AlertsPanel.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';

// Styled container for the alerts panel.
const AlertContainer = styled.div`
  background-color: #ffe6e6;
  border: 1px solid #ff0000;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
`;

// Styled component for error messages.
const ErrorMessage = styled.div`
  color: red;
  margin: 1rem 0;
`;

export default function AlertsPanel({ threshold = 12.0, pollingInterval = 10000 }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Function to fetch alerts from the API.
  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get("http://localhost:8000/sensors/check_alerts", {
        params: { threshold }
      });
      if (response.status === 200) {
        // The API returns an object with "alerts_triggered".
        setAlerts(response.data.alerts_triggered || []);
      } else {
        setError("Failed to fetch alerts");
      }
    } catch (err) {
      setError("Error fetching alerts: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Poll the alerts endpoint at the specified interval.
  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, pollingInterval);
    return () => clearInterval(interval);
  }, [threshold, pollingInterval]);

  return (
    <div>
      {loading && <div>Loading alerts...</div>}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {alerts.length > 0 ? (
        <AlertContainer>
          <h3>Alerts Triggered</h3>
          <ul>
            {alerts.map((alert, index) => (
              <li key={index}>
                Sensor {alert.sensorId} reported pressure {alert.pressure} at {alert.timestamp}
              </li>
            ))}
          </ul>
        </AlertContainer>
      ) : (
        !loading && <div>No alerts at this time.</div>
      )}
    </div>
  );
}