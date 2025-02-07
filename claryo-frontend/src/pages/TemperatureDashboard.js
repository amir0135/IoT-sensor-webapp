// src/pages/TemperatureDashboard.js
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import ChartCard from '../components/ChartCard';
import FilterBar from '../components/FilterBar';

const DashboardContainer = styled.div`
  flex: 1;
  padding: 1rem;
  background-color: #eee;
`;

const SectionTitle = styled.h2`
  margin-top: 2rem;
  margin-bottom: 1rem;
`;

export default function TemperatureDashboard() {
  // Filter state
  const [dateRange, setDateRange] = useState("Last 7 Days");
  const [branch, setBranch] = useState("Branch 1");

  // Data state
  const [chartData, setChartData] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);

  // Function to fetch temperature data
  const fetchTemperatureData = () => {
    setLoading(true);
    axios
      .get("http://localhost:8000/sensors/temperature_summary", {
        params: { dateRange, branch },
      })
      .then((res) => {
        setChartData(res.data.chartData || []);
        setMetrics(res.data.metrics || []);
      })
      .catch((err) =>
        console.error("Error fetching temperature data:", err)
      )
      .finally(() => setLoading(false));
  };

  // Poll for new data every 10 seconds
  useEffect(() => {
    fetchTemperatureData();
    const interval = setInterval(fetchTemperatureData, 10000);
    return () => clearInterval(interval);
  }, [dateRange, branch]);

  // Configure the chart to use the average temperature value returned by the backend.
  // If your backend query uses a different alias (for example, "avgTemp"), update the dataKey here.
  const lines = [
    { dataKey: 'avgTemp', stroke: 'red', label: 'Avg Temperature (°C)' }
  ];

  return (
    <DashboardContainer>
      <FilterBar 
        dateRange={dateRange}
        branch={branch}
        onDateRangeChange={setDateRange}
        onBranchChange={setBranch}
      />
      <SectionTitle>Temperature Dashboard</SectionTitle>
      {loading ? (
        <p>Loading temperature data...</p>
      ) : (
        <ChartCard
          title="Temperature Dashboard"
          data={chartData}
          lines={lines}
          unitLabel="°C"
          metrics={metrics}
        />
      )}
    </DashboardContainer>
  );
}