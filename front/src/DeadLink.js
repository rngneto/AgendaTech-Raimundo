import React from 'react';
import { Link } from 'react-router-dom';
import './DeadLink.css';
import deadLinkImage from './assets/dead-link.png';

const DeadLink = () => {
  return (
    <div className="dead-link-container">
      <h1>Parece que você encontrou um</h1>
      <h2>LINK MORTO!</h2>
      <img src={deadLinkImage} alt="Dead Link" className="dead-link-image" />
      <p>
        Volte para a <Link to="/" className="home-link">página inicial</Link> ou<br />
        reporte o erro no nosso e-mail: <strong>agendatech@es2ufpi.com</strong>
      </p>
    </div>
  );
};

export default DeadLink;
