// Importamos Express y el modelo de tarea
const express = require('express');
const router = express.Router();
const Task = require('../models/taskModel');  // Importamos el modelo de tarea

// Ruta para obtener todas las tareas
router.get('/tasks', async (req, res) => {
  try {
    const tasks = await Task.find();  // Encontrar todas las tareas en la base de datos
    res.json(tasks);  // Devolver las tareas como JSON
  } catch (error) {
    res.status(500).json({ message: 'Error al obtener las tareas' });  // Si hay un error, devolvemos un mensaje de error
  }
});

module.exports = router;
