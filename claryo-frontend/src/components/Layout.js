// src/components/Layout.js
import React from 'react';
import styled from 'styled-components';
import TopBar from './TopBar';
import Sidebar from './Sidebar';

const PageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
`;

const ContentWrapper = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const MainContent = styled.div`
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background-color: #f0f2f5;
`;

export default function Layout({ children }) {
  return (
    <PageWrapper>
      <TopBar />
      <ContentWrapper>
        <Sidebar />
        <MainContent>
          {children}
        </MainContent>
      </ContentWrapper>
    </PageWrapper>
  );
}