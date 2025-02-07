// src/components/TopBar.js
import React from 'react';
import styled from 'styled-components';

const TopBarContainer = styled.div`
  background-color: #444;
  padding: 1rem;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
`;

const IconsContainer = styled.div`
  /* Styles for additional icons (e.g., user profile) */
`;

export default function TopBar() {
  return (
    <TopBarContainer>
      <Logo>Claryo</Logo>
      <IconsContainer>
        {/* Example user icon */}
        <span role="img" aria-label="user">👤</span>
      </IconsContainer>
    </TopBarContainer>
  );
}