// src/App.js
import React from 'react';
import styled from 'styled-components';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import Dashboard from './pages/Dashboard';
import './App.css';

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
`;

function App() {
  return (
    <AppContainer>
      <Sidebar />
      <MainContent>
        <TopBar />
        <Dashboard />
      </MainContent>
    </AppContainer>
  );
}

export default App;
