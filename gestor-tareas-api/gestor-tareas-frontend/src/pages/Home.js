import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Home() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    // Hacer la solicitud GET al backend para obtener las tareas
    axios.get('http://localhost:5000/api/tasks')
      .then(response => {
        setTasks(response.data);  // Guardamos las tareas en el estado
      })
      .catch(error => {
        console.error('Error al obtener las tareas:', error);
      });
  }, []);  // El array vacío [] significa que el efecto solo se ejecutará una vez al cargar el componente

  return (
    <div>
      <h1>Tareas</h1>
      {tasks.length === 0 ? (
        <p>No hay tareas disponibles.</p>
      ) : (
        <ul>
          {tasks.map(task => (
            <li key={task._id}>{task.title}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Home;
