// Importamos Express para usar su sistema de rutas
const express = require('express');
const router = express.Router();  // Usamos el router de Express para manejar rutas

// Definimos una ruta GET para obtener todas las tareas
router.get('/tasks', (req, res) => {
  res.json({ message: 'Listado de tareas' });
});

// Exportamos el router para usarlo en otros archivos
module.exports = router;