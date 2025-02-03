// src/components/ChartCard.js
import React from 'react';
import styled from 'styled-components';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid,
} from 'recharts';

const CardContainer = styled.div`
  background-color: #fff;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: row;
`;

const ChartWrapper = styled.div`
  flex: 2;
  min-width: 0;
`;

const MetricsWrapper = styled.div`
  flex: 1;
  margin-left: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

const MetricTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  td {
    padding: 0.25rem 0;
  }
  th {
    text-align: left;
  }
`;

export default function ChartCard({
  title,
  dataKey,
  data,
  lines, // array of { dataKey: string, stroke: string, label: string }
  unitLabel,
  metrics = [],
}) {
  return (
    <CardContainer>
      <ChartWrapper>
        <h2>{title}</h2>
        <LineChart
          width={500}
          height={300}
          data={data}
          margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
        >
          <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          {lines.map((lineCfg) => (
            <Line
              key={lineCfg.dataKey}
              type="monotone"
              dataKey={lineCfg.dataKey}
              stroke={lineCfg.stroke}
              name={lineCfg.label}
            />
          ))}
        </LineChart>
      </ChartWrapper>
      <MetricsWrapper>
        <MetricTable>
          <thead>
            <tr>
              <th colSpan="4">Measurements</th>
            </tr>
            <tr>
              <th>Line</th>
              <th>Current</th>
              <th>Min</th>
              <th>Max</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => (
              <tr key={m.label}>
                <td>{m.label}</td>
                <td>{m.current} {unitLabel}</td>
                <td>{m.min} {unitLabel}</td>
                <td>{m.max} {unitLabel}</td>
              </tr>
            ))}
          </tbody>
        </MetricTable>
      </MetricsWrapper>
    </CardContainer>
  );
}
