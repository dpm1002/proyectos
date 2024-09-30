// Importamos las librerías necesarias para el servidor
const express = require('express');  // Framework que nos permite crear el servidor y definir rutas
const cors = require('cors');  // Middleware que nos permite evitar problemas de seguridad al consumir la API desde otro dominio

// Creamos una aplicación de Express
const app = express();

// Middleware
app.use(cors());  // Habilitamos CORS para permitir solicitudes desde otros dominios
app.use(express.json());  // Middleware para que Express entienda JSON en las solicitudes que recibe

// Definimos un puerto para nuestro servidor
const PORT = process.env.PORT || 5000;

// Arrancamos el servidor
app.listen(PORT, () => {
    console.log(`Servidor corriendo en el puerto ${PORT}`);
  });

// Definimos la primera ruta: 'GET /'
app.get('/', (req, res) => {
    res.send('Bienvenido a la API del Gestor de Tareas');
  });