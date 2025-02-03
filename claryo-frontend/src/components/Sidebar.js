// src/components/Sidebar.js
import React from 'react';
import styled from 'styled-components';

const SidebarContainer = styled.div`
  width: 80px;
  background-color: #444;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 1rem;
`;

const Logo = styled.div`
  width: 50px;
  height: 50px;
  background-color: #666;
  margin-bottom: 1rem;
`;

const CircleButton = styled.div`
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background-color: #888;
  margin: 0.5rem 0;
`;

export default function Sidebar() {
  return (
    <SidebarContainer>
      <Logo>LOGO</Logo>
      <CircleButton />
      <CircleButton />
    </SidebarContainer>
  );
}
