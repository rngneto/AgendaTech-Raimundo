import React from 'react';
import { Link } from 'react-router-dom';
import './UserDropdown.css';

const UserDropdown = ({ usuarioLogado, handleLogout }) => {
  if (!usuarioLogado) {
    return null; // Se o usuário não estiver logado, não exibe o dropdown
  }

  return (
    <div className="dropdown">
      <a
        href="#"
        className="d-block link-body-emphasis text-decoration-none"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        <img
          src={usuarioLogado.imagem ? `http://localhost:8000${usuarioLogado.imagem}` : '/assets/user-icon.png'}
          alt={usuarioLogado.nome || 'Usuário'}
          width="42"
          height="42"
          className="rounded-circle"
        />
      </a>
      <ul className="dropdown-menu text-small shadow">
        <li>
          <Link className="dropdown-item" to="/create-event">
            Criar Evento
          </Link>
        </li>
        <li>
          <a className="dropdown-item" href="#meus-desejos">
            Lista de desejos
          </a>
        </li>
        <li>
          <Link className="dropdown-item" to="/minha-conta">
            Minha Conta
          </Link>
        </li>
        <li>
          <Link className="dropdown-item" to="/help">
            Central de ajuda
          </Link>
        </li>
        <li>
          <hr className="dropdown-divider" />
        </li>
        <li>
          <a className="dropdown-item" href="#" onClick={handleLogout}>
            Sair
          </a>
        </li>
      </ul>
    </div>
  );
};

export default UserDropdown;
