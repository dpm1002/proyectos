document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('resource-form');
    const resourceList = document.getElementById('resource-list');
  
    document.getElementById('add-resource').addEventListener('click', () => {
      const inputResource = document.getElementById('input-resource').value;
      const inputOutput = document.getElementById('input-output').value;
      const inputRatio = document.getElementById('input-ratio').value;
  
      if (inputResource && inputOutput && inputRatio) {
        const listItem = document.createElement('li');
        listItem.textContent = `${inputResource} -> ${inputOutput} (Ratio: ${inputRatio})`;
        resourceList.appendChild(listItem);
  
        form.reset();
      } else {
        alert('Por favor, completa todos los campos');
      }
    });
  });
  