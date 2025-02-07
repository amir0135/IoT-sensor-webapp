// src/pages/FlowDashboard.js
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

export default function FlowDashboard() {
  // Filter state
  const [dateRange, setDateRange] = useState("Last 7 Days");
  const [branch, setBranch] = useState("Branch 1");

  // Data state
  const [chartData, setChartData] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);

  // Function to fetch flow data
  useEffect(() => {
    async function fetchFlowData() {
      try {
        setLoading(true);
        const res = await axios.get("http://localhost:8000/sensors/flow_summary", {
          params: { dateRange, branch },
        });
        setChartData(res.data.chartData || []);
        setMetrics(res.data.metrics || []);
      } catch (err) {
        console.error("Error fetching flow data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchFlowData();
    const interval = setInterval(fetchFlowData, 10000);
    return () => clearInterval(interval);
  }, [dateRange, branch]);

  // Configure a single line for flow using the average value from the backend
  const lines = [
    { dataKey: 'avgFlow', stroke: 'green', label: 'Avg Flow (nm³/min)' }
  ];

  return (
    <DashboardContainer>
      <FilterBar 
        dateRange={dateRange}
        branch={branch}
        onDateRangeChange={setDateRange}
        onBranchChange={setBranch}
      />
      <SectionTitle>Flow Dashboard</SectionTitle>
      {loading ? (
        <p>Loading flow data...</p>
      ) : (
        <ChartCard
          title="Flow Dashboard"
          data={chartData}
          lines={lines}
          unitLabel="nm³/min"
          metrics={metrics}
        />
      )}
    </DashboardContainer>
  );
}