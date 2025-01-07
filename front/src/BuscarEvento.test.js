import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import BuscarEventoPorNome from './BuscarEventoPorNome';

describe('BuscarEventoPorNome', () => {
  test('renders input and button', () => {
    render(<BuscarEventoPorNome />);
    
    const inputElement = screen.getByPlaceholderText(/Buscar evento por nome/i);
    const buttonElement = screen.getByText(/Buscar/i);
    
    expect(inputElement).toBeInTheDocument();
    expect(buttonElement).toBeInTheDocument();
  });

  test('updates input value on change', () => {
    render(<BuscarEventoPorNome />);
    
    const inputElement = screen.getByPlaceholderText(/Buscar evento por nome/i);
    fireEvent.change(inputElement, { target: { value: 'Conferência' } });
    
    expect(inputElement.value).toBe('Conferência');
  });

  test('fetches and displays events on button click', async () => {
    // Mock the fetch function
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({
          eventos: [
            { id: 1, nome: 'Conferência de Tecnologia', data: '2023-10-10', horario: '10:00', tipo: 'Conferência', local: 'Auditório', imagem: null, link: '', descricao: 'Uma conferência sobre tecnologia.' },
          ],
        }),
      })
    );

    render(<BuscarEventoPorNome />);
    
    const inputElement = screen.getByPlaceholderText(/Buscar evento por nome/i);
    const buttonElement = screen.getByText(/Buscar/i);
    
    fireEvent.change(inputElement, { target: { value: 'Conferência' } });
    fireEvent.click(buttonElement);
    
    const eventName = await screen.findByText(/Conferência de Tecnologia/i);
    
    expect(eventName).toBeInTheDocument();
    
    // Clean up mock
    global.fetch.mockClear();
  });

  test('displays no events found message', async () => {
    // Mock the fetch function
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ eventos: [] }),
      })
    );

    render(<BuscarEventoPorNome />);
    
    const inputElement = screen.getByPlaceholderText(/Buscar evento por nome/i);
    const buttonElement = screen.getByText(/Buscar/i);
    
    fireEvent.change(inputElement, { target: { value: 'Evento Inexistente' } });
    fireEvent.click(buttonElement);
    
    const noEventsMessage = await screen.findByText(/Nenhum evento encontrado/i);
    
    expect(noEventsMessage).toBeInTheDocument();
    
    // Clean up mock
    global.fetch.mockClear();
  });
});