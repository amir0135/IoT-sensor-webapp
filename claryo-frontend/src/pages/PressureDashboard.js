// src/pages/PressureDashboard.js
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

export default function PressureDashboard() {
  // Filter state
  const [dateRange, setDateRange] = useState("Last 7 Days");
  const [branch, setBranch] = useState("Branch 1");

  // Data state
  const [chartData, setChartData] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);

  // Function to fetch pressure data
  const fetchPressureData = () => {
    setLoading(true);
    axios
      .get("http://localhost:8000/sensors/pressure_summary", {
        params: { dateRange, branch },
      })
      .then((res) => {
        setChartData(res.data.chartData || []);
        setMetrics(res.data.metrics || []);
      })
      .catch((err) =>
        console.error("Error fetching pressure data:", err)
      )
      .finally(() => setLoading(false));
  };

  // Poll for new data every 10 seconds
  useEffect(() => {
    fetchPressureData();
    const interval = setInterval(fetchPressureData, 10000);
    return () => clearInterval(interval);
  }, [dateRange, branch]);

  // Configure a single line for pressure using the average value from the backend
  const lines = [
    { dataKey: 'avgPressure', stroke: 'blue', label: 'Avg Pressure (bar)' }
  ];

  return (
    <DashboardContainer>
      <FilterBar 
        dateRange={dateRange}
        branch={branch}
        onDateRangeChange={setDateRange}
        onBranchChange={setBranch}
      />
      <SectionTitle>Pressure Dashboard</SectionTitle>
      {loading ? (
        <p>Loading pressure data...</p>
      ) : (
        <ChartCard
          title="Pressure Dashboard"
          data={chartData}
          lines={lines}
          unitLabel="bar"
          metrics={metrics}
        />
      )}
    </DashboardContainer>
  );
}