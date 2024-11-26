document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('resource-form');
    const resourceList = document.getElementById('resource-list');
    const resources = []; // Array para almacenar los datos
  
    // Función para calcular producción por segundo y tiempo ajustado
    const calculateProduction = (ratio, time, constructors) => {
      const adjustedTime = time / constructors; // Tiempo ajustado por número de constructores
      const productionPerSecond = (constructors * ratio) / time; // Producción por segundo
      return { productionPerSecond: productionPerSecond.toFixed(2), adjustedTime: adjustedTime.toFixed(2) };
    };
  
    document.getElementById('add-resource').addEventListener('click', () => {
      // Obtener valores de los inputs
      const inputResource = document.getElementById('input-resource').value;
      const inputOutput = document.getElementById('input-output').value;
      const inputRatio = parseFloat(document.getElementById('input-ratio').value);
      const inputTime = parseFloat(document.getElementById('input-time').value);
      const inputConstructors = parseInt(document.getElementById('input-constructors').value, 10);
      const inputMachine = document.getElementById('input-machine').value;
  
      if (inputResource && inputOutput && inputRatio && inputTime && inputConstructors && inputMachine) {
        const resourceData = {
          input: inputResource,
          output: inputOutput,
          ratio: inputRatio,
          time: inputTime,
          constructors: inputConstructors,
          machine: inputMachine
        };
  
        resources.push(resourceData); // Guardar en el array de recursos
  
        // Calcular producción y tiempo ajustado
        const { productionPerSecond, adjustedTime } = calculateProduction(inputRatio, inputTime, inputConstructors);
  
        // Mostrar en la lista
        const listItem = document.createElement('li');
        listItem.textContent = `${inputResource} -> ${inputOutput} | Máquina: ${inputMachine}, Ratio: ${inputRatio}, Tiempo Ajustado: ${adjustedTime}s, Constructores: ${inputConstructors}, Producción/s: ${productionPerSecond}`;
        resourceList.appendChild(listItem);
  
        form.reset(); // Reiniciar formulario
      } else {
        alert('Por favor, completa todos los campos');
      }
    });
  
    // Exportar los datos a JSON para guardarlos
    document.getElementById('export-json').addEventListener('click', () => {
      const jsonData = JSON.stringify({ resources }, null, 2); // Convertir a JSON con formato
      const blob = new Blob([jsonData], { type: 'application/json' }); // Crear un archivo Blob
      const url = URL.createObjectURL(blob);
  
      // Crear un enlace de descarga
      const a = document.createElement('a');
      a.href = url;
      a.download = 'resources.json'; // Nombre del archivo
      a.click(); // Simular el clic para descargar
      URL.revokeObjectURL(url); // Limpiar la URL del objeto
    });
  });
  