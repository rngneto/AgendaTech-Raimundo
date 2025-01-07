import React, { useState } from 'react';
import './Filter.css'; 

const Filter = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    tipo: '',
    data: '',
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const updatedFilters = { ...filters, [name]: value };
    setFilters(updatedFilters);
    onFilterChange(updatedFilters); 
  };

  return (
    <div className="filter-container">
      <select name="tipo" value={filters.tipo} onChange={handleInputChange}>
        <option value="">Todos os tipos</option>
        <option value="presencial">Presencial</option>
        <option value="online">Online</option>
        <option value="hibrido">Híbrido</option>
      </select>

      <select name="data" value={filters.data} onChange={handleInputChange}>
        <option value="">Todas as datas</option>
        <option value="semana">Esta semana</option>
        <option value="mes">Este mês</option>
      </select>
    </div>
  );
};

export default Filter;
