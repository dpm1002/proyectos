import React, { useState } from 'react';
import axios from 'axios';
import { Container, Form, Button, Alert } from 'react-bootstrap';  // Importamos componentes de Bootstrap

function AddTask() {
  const [task, setTask] = useState({ title: '', description: '' });
  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setTask({ ...task, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/api/tasks', task)
      .then(response => {
        setMessage('¡Tarea creada con éxito!');
        setTask({ title: '', description: '' });
      })
      .catch(error => {
        setMessage('Hubo un error al crear la tarea');
      });
  };

  return (
    <Container className="mt-5">
      <h1 className="mb-4">Añadir Nueva Tarea</h1>

      {/* Mostramos un mensaje de éxito o error */}
      {message && <Alert variant={message.includes('éxito') ? 'success' : 'danger'}>{message}</Alert>}

      <Form onSubmit={handleSubmit}>
        <Form.Group controlId="formTitle">
          <Form.Label>Título</Form.Label>
          <Form.Control
            type="text"
            name="title"
            value={task.title}
            onChange={handleChange}
            placeholder="Introduce el título de la tarea"
            required
          />
        </Form.Group>

        <Form.Group controlId="formDescription" className="mt-3">
          <Form.Label>Descripción</Form.Label>
          <Form.Control
            as="textarea"
            rows={3}
            name="description"
            value={task.description}
            onChange={handleChange}
            placeholder="Descripción de la tarea (opcional)"
          />
        </Form.Group>

        <Button variant="primary" type="submit" className="mt-3">
          Añadir Tarea
        </Button>
      </Form>
    </Container>
  );
}

export default AddTask;
