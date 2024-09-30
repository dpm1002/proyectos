import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import AddTask from './pages/AddTask';

function App() {
  return (
    <Router>
      <div>
        {/* Menú de navegación */}
        <nav>
          <ul>
            <li>
              <Link to="/">Inicio</Link>
            </li>
            <li>
              <Link to="/about">Acerca de</Link>
            </li>
            <li>
              <Link to="/add-task">Añadir tarea</Link> {/* Nuevo enlace */}
            </li>
          </ul>
        </nav>

        {/* Definición de rutas */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/add-task" element={<AddTask />} />  {/* Nueva ruta */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
