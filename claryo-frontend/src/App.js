// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TemperatureDashboard from './pages/TemperatureDashboard';
import PressureDashboard from './pages/PressureDashboard';
import FlowDashboard from './pages/FlowDashboard';
import CombinedSummary from './pages/CombinedSummary';
import styled from 'styled-components';
import './App.css';

const NavBar = styled.nav`
  padding: 1rem;
  background-color: #222;
  a {
    color: #fff;
    margin-right: 1rem;
    text-decoration: none;
  }
`;

function App() {
  return (
    <Router>
      <NavBar>
        <Link to="/">Home</Link>
      </NavBar>
      <Routes>
        {/* Hub route with nested routes */}
        <Route path="/dashboard" element={<Dashboard />}>
          {/* Default nested route: render nothing extra */}
          <Route index element={<></>} />
          <Route path="temperature" element={<TemperatureDashboard />} />
          <Route path="pressure" element={<PressureDashboard />} />
          <Route path="flow" element={<FlowDashboard />} />
          {/* If you have a detailed combined view, add it here */}
          <Route path="combined" element={<CombinedSummary />} />
        </Route>
        {/* Default landing page */}
        <Route path="/" element={<div>Welcome! Go to the <Link to="/dashboard">Dashboard</Link>.</div>} />
      </Routes>
    </Router>
  );
}

export default App;