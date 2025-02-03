// src/pages/Dashboard.js
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import ChartCard from '../components/ChartCard';

const DashboardContainer = styled.div`
  flex: 1;
  padding: 1rem;
  background-color: #eee;
`;

export default function Dashboard() {
  // State to hold fetched sensor data
  const [latestSensors, setLatestSensors] = useState([]);
  const [avgPressure, setAvgPressure] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch data from your FastAPI backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // 1) Get the 10 most recent rows
        const latestRes = await axios.get("http://localhost:8000/sensors/latest");
        setLatestSensors(latestRes.data || []);

        // 2) Get the average pressure
        const avgRes = await axios.get("http://localhost:8000/sensors/average_pressure_latest");
        // The endpoint returns something like [{ "avgPressure": 7.15 }]
        if (avgRes.data && avgRes.data.length > 0) {
          setAvgPressure(avgRes.data[0].avgPressure);
        }

      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Transform `latestSensors` into chart-friendly data
  // For example, Recharts typically needs an array of objects:
  // [ { date: 'Mar 17', pressure: 7.2, flow: 300 }, ... ]
  // We can parse the timestamp for the x-axis label, etc.
  const chartData = latestSensors.map((s) => ({
    date: new Date(s.timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    pressure: s.pressure,
    flow: s.flowRate,    // updated property name
    temperature: s.temperature,
  }));

  // For multi-line chart, define line configs
  const lines = [
    { dataKey: 'pressure', stroke: 'blue', label: 'Pressure' },
    { dataKey: 'flow', stroke: 'green', label: 'Flow' },
    { dataKey: 'temperature', stroke: 'red', label: 'Temperature' },
  ];

  // Example metrics array (current, min, max) – if you only have 10 rows,
  // you might compute min/max on the front end for demonstration.
  const pressures = latestSensors.map((s) => s.pressure);
  const minP = pressures.length ? Math.min(...pressures).toFixed(2) : '-';
  const maxP = pressures.length ? Math.max(...pressures).toFixed(2) : '-';
  const currentP = pressures.length ? pressures[0].toFixed(2) : '-';

  const metrics = [
    {
      label: 'Pressure',
      current: currentP,
      min: minP,
      max: maxP,
    },
  ];

  return (
    <DashboardContainer>
      {loading ? <p>Loading data...</p> : null}

      {/* Example ChartCard that shows Pressure, Flow, Temperature on one chart */}
      <ChartCard
        title="Latest Sensor Data"
        dataKey="pressure" // or whichever is your primary
        data={chartData}
        lines={lines}
        unitLabel=""
        metrics={metrics}
      />

      {/* Display average pressure from the second endpoint, if desired */}
      {avgPressure && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Average Pressure (Latest): {avgPressure.toFixed(2)} bar</h3>
        </div>
      )}
    </DashboardContainer>
  );
}
