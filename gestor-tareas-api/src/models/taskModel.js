const mongoose = require('mongoose');

// Definimos el esquema de la tarea
const taskSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true  // El título es obligatorio
  },
  description: {
    type: String,
    required: false  // La descripción es opcional
  },
  completed: {
    type: Boolean,
    default: false  // Por defecto, la tarea no está completada
  },
  createdAt: {
    type: Date,
    default: Date.now  // Fecha de creación de la tarea
  }
});

// Creamos el modelo de tarea
const Task = mongoose.model('Task', taskSchema);

// Exportamos el modelo para poder usarlo en otros archivos
module.exports = Task;
