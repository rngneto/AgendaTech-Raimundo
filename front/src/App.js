import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './Navbar';
import About from './About';
import ThemeToggle from './ThemeToggle';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Barra de navegação */}
        <Navbar />

        {/* Definição das rotas */}
        <Routes>
          {/* Página inicial com informações */}
          <Route path="/" element={<About />} />
        </Routes>

        {/* Alternador de tema global */}
        <ThemeToggle />
      </div>
    </Router>
  );
}

export default App;
