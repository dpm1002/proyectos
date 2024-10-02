import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Table, Button, Alert } from 'react-bootstrap';

function DeleteTask() {
  const [tasks, setTasks] = useState([]);
  const [message, setMessage] = useState('');

  // Función para obtener todas las tareas
  useEffect(() => {
    axios.get('http://localhost:5000/api/tasks')
      .then(response => {
        setTasks(response.data);
      })
      .catch(error => {
        console.error('Error al obtener las tareas:', error);
      });
  }, []);

  // Función para eliminar una tarea
  const handleDelete = (id) => {
    axios.delete(`http://localhost:5000/api/tasks/${id}`)
      .then(response => {
        setMessage('Tarea eliminada con éxito');
        setTasks(tasks.filter(task => task._id !== id));  // Eliminar la tarea del estado
      })
      .catch(error => {
        setMessage('Error al eliminar la tarea');
        console.error('Error al eliminar la tarea:', error);
      });
  };

  return (
    <Container className="mt-5">
      <h1 className="mb-4">Eliminar Tareas</h1>

      {message && <Alert variant={message.includes('éxito') ? 'success' : 'danger'}>{message}</Alert>}

      <Table striped bordered hover>
        <thead>
          <tr>
            <th>#</th>
            <th>Tarea</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {tasks.length === 0 ? (
            <tr>
              <td colSpan="3">No hay tareas disponibles</td>
            </tr>
          ) : (
            tasks.map((task, index) => (
              <tr key={task._id}>
                <td>{index + 1}</td>
                <td>{task.title}</td>
                <td>
                  <Button variant="danger" onClick={() => handleDelete(task._id)}>Eliminar</Button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    </Container>
  );
}

export default DeleteTask;
