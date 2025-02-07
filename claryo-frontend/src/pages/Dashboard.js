// src/pages/Dashboard.js
import React from 'react';
import styled from 'styled-components';
import { Outlet, Link } from 'react-router-dom';
import CombinedSummary from './CombinedSummary';
import AlertsPanel from '../components/AlertsPanel';

const HubContainer = styled.div`
  flex: 1;
  padding: 1rem;
  background-color: #eee;
`;

const NavSection = styled.div`
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
`;

const NavButton = styled(Link)`
  background-color: #444;
  color: #fff;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  border-radius: 4px;
  &:hover {
    background-color: #666;
  }
`;

export default function Dashboard() {
  return (
    <HubContainer>
      {/* Always visible combined sensor summary at the top */}
      <CombinedSummary />

      {/* Real-time alerts panel */}
      <AlertsPanel threshold={12.0} pollingInterval={10000} />

      {/* Navigation bar for dedicated dashboards */}
      <NavSection>
        <NavButton to="/dashboard/temperature">Temperature Dashboard</NavButton>
        <NavButton to="/dashboard/pressure">Pressure Dashboard</NavButton>
        <NavButton to="/dashboard/flow">Flow Dashboard</NavButton>
      </NavSection>

      {/* Outlet renders the dedicated dashboard content below */}
      <Outlet />
    </HubContainer>
  );
}