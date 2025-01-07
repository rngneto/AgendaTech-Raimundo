import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './Navbar';
import Eventos from './Eventos';
import RegisterUser from './RegisterUser';
import UserList from './UserList'; 
import About from './About';
import Footer from './Footer';
import ThemeToggle from './ThemeToggle';
import CreateEvent from './CreateEvent';
import DetalhesEvento from './DetalhesEvento';
import HelpCenter from './HelpCenter';
import DeadLink from './DeadLink';
import MinhaConta from './MinhaConta';
import LoginUser from './LoginUser';
import Filter from './Filter'; 
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import './App.css';

function App() {
  const [usuarioLogado, setUsuarioLogado] = useState(null);
  const [filtro, setFiltro] = useState({}); // Estado para o filtro

  useEffect(() => {
    const usuario = localStorage.getItem('usuarioLogado');
    if (usuario) {
      setUsuarioLogado(JSON.parse(usuario));
    }
  }, []);

  const handleLogin = (usuario) => {
    setUsuarioLogado(usuario);
    localStorage.setItem('usuarioLogado', JSON.stringify(usuario));
  };

  const handleLogout = () => {
    setUsuarioLogado(null);
    localStorage.removeItem('usuarioLogado');
  };

  const handleFilterChange = (novoFiltro) => {
    setFiltro(novoFiltro); // Atualiza o estado do filtro
  };

  return (
    <Router>
      <div className="App">
        <Navbar
          usuarioLogado={usuarioLogado}
          setUsuarioLogado={setUsuarioLogado}
          handleLogout={handleLogout}
        />
        
        {/* Define as rotas */}
        <Routes>          
          <Route 
            path="/" 
            element={
              <>
                <Eventos filtro={filtro} /> {/* Exibindo eventos primeiro */}
                <Filter onFilterChange={handleFilterChange} /> {/* Filtros abaixo dos eventos */}
              </>
            } 
          />
          <Route path="/create-event" element={<CreateEvent />} />
          <Route path="/eventos/:id" element={<DetalhesEvento />} />         
          <Route path="/register" element={<RegisterUser setUsuarioLogado={handleLogin} />} />
          <Route path="/login" element={<LoginUser setUsuarioLogado={handleLogin} />} />          
          <Route path="/usuarios" element={<UserList />} />
          <Route path="/about" element={<About />} />
          <Route path="/help" element={<HelpCenter />} />
          <Route path="/minha-conta" element={<MinhaConta usuario={usuarioLogado} />} />
          <Route path="*" element={<DeadLink />} />
        </Routes>
        
        {/* Componente Footer que será exibido em todas as páginas */}
        <Footer />
        <ThemeToggle />
      </div>
    </Router>
  );
}

export default App;
