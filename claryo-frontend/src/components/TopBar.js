// src/components/TopBar.js
import React from 'react';
import styled from 'styled-components';

const TopBarContainer = styled.div`
  background-color: #ccc;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Title = styled.h1`
  margin: 0;
`;

const SelectContainer = styled.div`
  display: flex;
  gap: 1rem;
`;

export default function TopBar() {
  return (
    <TopBarContainer>
      <Title>Dashboard</Title>
      <SelectContainer>
        <select defaultValue="Last Month">
          <option>This Week</option>
          <option>This Month</option>
          <option>Last Month</option>
        </select>
        <select defaultValue="Branch 1">
          <option>Branch 1</option>
          <option>Branch 2</option>
          <option>Branch 3</option>
        </select>
      </SelectContainer>
    </TopBarContainer>
  );
}
