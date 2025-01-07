import React, { useEffect, useState } from 'react';
import './Eventos.css';

const Eventos = ({ filtro }) => {
  const [eventos, setEventos] = useState([]);
  const [eventosFiltrados, setEventosFiltrados] = useState([]);
  const [paginaAtual, setPaginaAtual] = useState(1);
  const [totalPaginas, setTotalPaginas] = useState(1);

  useEffect(() => {
    const carregarEventos = async () => {
      try {
        const resposta = await fetch(`http://localhost:8000/api/listar_eventos?page=${paginaAtual}`);
        const dados = await resposta.json();

        setEventos(dados.eventos || []);
        setEventosFiltrados(dados.eventos || []); // Inicialmente, exibe todos os eventos
        setTotalPaginas(dados.total_paginas || 1);
      } catch (erro) {
        console.error('Erro ao carregar eventos:', erro);
        setEventos([]);
        setEventosFiltrados([]);
      }
    };

    carregarEventos();
  }, [paginaAtual]);

  // Atualiza a lista de eventos filtrados ao mudar o filtro
  useEffect(() => {
    if (filtro) {
      let eventosAtualizados = eventos;

      // Filtro por tipo
      if (filtro.tipo) {
        eventosAtualizados = eventosAtualizados.filter((evento) => evento.tipo === filtro.tipo);
      }

      // Filtro por data
      if (filtro.data) {
        const now = new Date();
        if (filtro.data === 'semana') {
          const semanaFim = new Date();
          semanaFim.setDate(now.getDate() + 7);

          eventosAtualizados = eventosAtualizados.filter((evento) => {
            const eventoData = new Date(evento.data);
            return eventoData >= now && eventoData <= semanaFim;
          });
        } else if (filtro.data === 'mes') {
          const mesFim = new Date();
          mesFim.setMonth(now.getMonth() + 1);

          eventosAtualizados = eventosAtualizados.filter((evento) => {
            const eventoData = new Date(evento.data);
            return eventoData >= now && eventoData <= mesFim;
          });
        }
      }

      setEventosFiltrados(eventosAtualizados);
    } else {
      setEventosFiltrados(eventos);
    }
  }, [filtro, eventos]);

  const mudarPagina = (novaPagina) => {
    if (novaPagina > 0 && novaPagina <= totalPaginas) {
      setPaginaAtual(novaPagina);
    }
  };

  return (
    <main>
      <section className="py-5 text-center container">
        <h1>Eventos</h1>
        <p className="lead text-muted">
          Página {paginaAtual} de {totalPaginas}
        </p>
      </section>

      <div className="album py-5 bg-body-tertiary">
        <div className="container">
          <div className="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4">
            {eventosFiltrados.map((evento) => (
              <div className="col" key={evento.id}>
                <div className="card shadow-sm evento-card">
                  {evento.imagem && (
                    <img
                      src={`http://localhost:8000${evento.imagem}`}
                      alt={evento.nome}
                      className="card-img-top"
                    />
                  )}
                  <div className="card-body">
                    <h5 className="card-title">{evento.nome}</h5>
                    <p className="card-text">
                      <strong>Data:</strong> {evento.data || '---'}
                      <br />
                      <strong>Horário:</strong> {evento.horario || '---'}
                      <br />
                      <strong>Tipo:</strong> {evento.tipo || '---'}
                      <br />
                      <strong>Local:</strong> {evento.local || '---'}
                    </p>
                    <a
                      href={`/eventos/${evento.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary mt-2"
                    >
                      Saiba mais
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="d-flex justify-content-between align-items-center mt-4">
            <button
              className="btn btn-primary"
              onClick={() => mudarPagina(paginaAtual - 1)}
              disabled={paginaAtual === 1}
            >
              Anterior
            </button>
            <button
              className="btn btn-primary"
              onClick={() => mudarPagina(paginaAtual + 1)}
              disabled={paginaAtual === totalPaginas}
            >
              Próxima
            </button>
          </div>
        </div>
      </div>
    </main>
  );
};

export default Eventos;
