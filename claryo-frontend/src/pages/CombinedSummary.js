// src/pages/CombinedSummary.js
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import ChartCard from '../components/ChartCard';

const SectionTitle = styled.h2`
  margin-top: 2rem;
  margin-bottom: 1rem;
`;

export default function CombinedSummary() {
  const [latestSensors, setLatestSensors] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchLatestData = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${process.env.REACT_APP_API_URL}/sensors/latest`);
      setLatestSensors(res.data || []);
    } catch (error) {
      console.error("Error fetching latest sensor data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestData();
  }, []);

  const chartData = latestSensors.map((s) => ({
    date: new Date(s.timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    avgPressure: s.avgPressure || s.pressure,
    avgFlow: s.avgFlow || s.flowRate,
    avgTemperature: s.avgTemperature || s.temperature,
  }));

  const lines = [
    { dataKey: 'avgPressure', stroke: 'blue', label: 'Avg Pressure (bar)' },
    { dataKey: 'avgFlow', stroke: 'green', label: 'Avg Flow (nm³/min)' },
    { dataKey: 'avgTemperature', stroke: 'red', label: 'Avg Temperature (°C)' },
  ];

  const pressures = latestSensors.map((s) => s.pressure);
  const minP = pressures.length ? Math.min(...pressures).toFixed(2) : '-';
  const maxP = pressures.length ? Math.max(...pressures).toFixed(2) : '-';
  const currentP = pressures.length ? pressures[0].toFixed(2) : '-';
  const metrics = [{ label: 'Pressure', current: currentP, min: minP, max: maxP }];

  return (
    <div>
      <SectionTitle>Combined Sensor Summary</SectionTitle>
      {loading ? (
        <p>Loading sensor data...</p>
      ) : (
        <ChartCard
          title="Combined Sensor Data"
          data={chartData}
          lines={lines}
          unitLabel=""
          metrics={metrics}
        />
      )}
    </div>
  );
}