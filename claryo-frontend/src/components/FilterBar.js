// src/components/FilterBar.js
import React from 'react';
import styled from 'styled-components';

const FilterContainer = styled.div`
  background-color: #fff;
  padding: 1rem;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const FilterGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

export default function FilterBar({ dateRange, branch, onDateRangeChange, onBranchChange }) {
  return (
    <FilterContainer>
      <FilterGroup>
        <label htmlFor="dateRange">Date Range:</label>
        <select
          id="dateRange"
          value={dateRange}
          onChange={(e) => onDateRangeChange(e.target.value)}
        >
          <option value="Last 7 Days">Last 7 Days</option>
          <option value="Last Month">Last Month</option>
          {/* Add more options if needed */}
        </select>
      </FilterGroup>
      <FilterGroup>
        <label htmlFor="branch">Branch:</label>
        <select
          id="branch"
          value={branch}
          onChange={(e) => onBranchChange(e.target.value)}
        >
          <option value="Branch 1">Branch 1</option>
          <option value="Branch 2">Branch 2</option>
          <option value="Branch 3">Branch 3</option>
          {/* Add more options if needed */}
        </select>
      </FilterGroup>
    </FilterContainer>
  );
}