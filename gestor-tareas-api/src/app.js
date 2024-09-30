// Importamos las librerías necesarias
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');  // Mongoose para conectarnos a MongoDB

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Conectar a MongoDB
mongoose.connect('mongodb://localhost/gestor-tareas', {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('Conectado a MongoDB'))
.catch(err => console.log('Error al conectar con MongoDB:', err));

// Importamos las rutas
const taskRoutes = require('./routes/taskRoutes');
app.use('/api', taskRoutes);

// Definir puerto y arrancar servidor
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en el puerto ${PORT}`);
});
