import React, { useState } from 'react';
import axios from 'axios';

function AddTask() {
  // Estado para manejar los datos del formulario
  const [task, setTask] = useState({
    title: '',
    description: ''
  });

  const [message, setMessage] = useState('');

  // Función para manejar los cambios en los inputs
  const handleChange = (e) => {
    const { name, value } = e.target;
    setTask({
      ...task,
      [name]: value
    });
  };

  // Función para manejar el envío del formulario
  const handleSubmit = (e) => {
    e.preventDefault(); // Evita que el formulario recargue la página
    axios.post('http://localhost:5000/api/tasks', task)
      .then(response => {
        setMessage('¡Tarea creada con éxito!');
        setTask({ title: '', description: '' });  // Reseteamos el formulario
      })
      .catch(error => {
        console.error('Error al crear la tarea:', error);
        setMessage('Hubo un error al crear la tarea');
      });
  };

  return (
    <div>
      <h1>Añadir Nueva Tarea</h1>

      {message && <p>{message}</p>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Título:</label>
          <input
            type="text"
            id="title"
            name="title"
            value={task.title}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="description">Descripción:</label>
          <textarea
            id="description"
            name="description"
            value={task.description}
            onChange={handleChange}
          ></textarea>
        </div>
        <button type="submit">Añadir Tarea</button>
      </form>
    </div>
  );
}

export default AddTask;
