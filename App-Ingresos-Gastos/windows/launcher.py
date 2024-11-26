import sys
import threading
from PyQt5.QtCore import QUrl  # Importar QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
import subprocess

# Inicia el servidor Flask como un subproceso
def start_flask():
    subprocess.Popen(["python", "app.py"])

# Ventana principal PyQt5
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Ingresos y Gastos")
        self.setGeometry(100, 100, 1024, 768)

        # Navegador embebido
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:5000"))

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

if __name__ == "__main__":
    # Iniciar Flask en un hilo separado
    threading.Thread(target=start_flask, daemon=True).start()

    # Iniciar PyQt5
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
