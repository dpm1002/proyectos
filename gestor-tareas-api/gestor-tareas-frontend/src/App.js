import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import AddTask from './pages/AddTask';
import DeleteTask from './pages/DeleteTask';
import { Navbar, Nav, Container } from 'react-bootstrap';  // Importamos componentes de Bootstrap

function App() {
  return (
    <Router>
      <div>
        {/* Barra de navegación de Bootstrap */}
        <Navbar bg="dark" variant="dark" expand="lg">
          <Container>
            <Navbar.Brand href="/">Gestor de Tareas</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="ml-auto">
                <Nav.Link as={Link} to="/">Inicio</Nav.Link>
                <Nav.Link as={Link} to="/about">Acerca de</Nav.Link>
                <Nav.Link as={Link} to="/add-task">Añadir Tarea</Nav.Link>
                <Nav.Link as={Link} to="/delete-task">Eliminar Tarea</Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        {/* Definición de rutas */}
        <Container className="mt-4">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/add-task" element={<AddTask />} />
            <Route path="/delete-task" element={<DeleteTask />} />
          </Routes>
        </Container>
      </div>
    </Router>
  );
}

export default App;
