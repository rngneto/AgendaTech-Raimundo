import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginUser.css';

const LoginUser = ({ setUsuarioLogado }) => {
  const [formData, setFormData] = useState({
    username: '',
    senha: '',
  });
  const navigate = useNavigate(); // Hook para redirecionar
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    try {
      const response = await fetch('http://127.0.0.1:8000/api/login_usuario/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
  
      if (response.ok) {
        const data = await response.json();
        setUsuarioLogado(data); // Define o estado global com os dados do usuário
        alert('Login realizado com sucesso!');
        navigate('/'); // Redireciona para a página inicial após o cadastro
      } else {
        const errorData = await response.json();
        setError(errorData.erro || 'Erro ao realizar login.');
      }
    } catch (error) {
      console.error('Erro ao enviar dados:', error);
      setError('Erro ao realizar login. Verifique sua conexão.');
    }
  };
  

  return (
    <div className="login-container">
      <h2>Acesse sua Conta</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Nome de Usuário</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Senha</label>
          <input
            type="password"
            name="senha"
            value={formData.senha}
            onChange={handleChange}
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit">Entrar</button>
      </form>
    </div>
  );
};

export default LoginUser;
