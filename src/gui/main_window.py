import tkinter as tk
from tkinter import ttk
import logging

from .components.control_panel import ControlPanel
from .components.status_panel import StatusPanel
from .styles.theme import apply_theme

class MainWindow:
    
    
    def __init__(self):
        """
        Constructor que inicializa toda la ventana y sus componentes.
        
        Piensa en esto como preparar un escenario antes de una obra de teatro:
        se configuran las luces, se colocan los decorados, y se prepara todo
        para que la función pueda comenzar.
        """
        # Crear el logger para esta clase específicamente
        self.logger = logging.getLogger(__name__)
        
        # Crear la ventana principal de tkinter
        self.root = tk.Tk()
        
        # Configurar las propiedades básicas de la ventana
        self.setup_window()
        
        # Aplicar el tema visual para que se vea moderno
        apply_theme(self.root)
        
        # Crear todos los componentes (paneles, botones, etc.)
        self.create_components()
        
        # Configurar qué hacer cuando el usuario cierre la ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Registrar en el log que todo se inicializó correctamente
        self.logger.info("Ventana principal inicializada correctamente")
    
    def setup_window(self):
        """
        Configura las propiedades básicas de la ventana.
        
        Esta función es como decorar y amueblar una habitación:
        define el tamaño, el título, y dónde aparecerá en la pantalla.
        """
        self.root.title("PC to Alexa Audio - ServicesSoundAlexa")
        self.root.geometry("600x400")  # Ancho x Alto en píxeles
        self.root.minsize(500, 350)    # Tamaño mínimo para que no se vea mal
        
        # Centrar la ventana en la pantalla
        self.center_window()
        
        # Configurar cómo se comporta el grid principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def center_window(self):
        """
        Centra la ventana en la pantalla del usuario.
        
        Es como colgar un cuadro en la pared - calculas el centro
        para que se vea equilibrado y profesional.
        """
        self.root.update_idletasks()  # Asegurar que tkinter conoce el tamaño real
        
        # Obtener dimensiones de la ventana y la pantalla
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcular posición central
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Aplicar la nueva posición
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_components(self):
        """
        Crea y organiza todos los componentes de la interfaz.
        
        Esta función es como organizar los muebles en una sala:
        coloca cada elemento en su lugar apropiado para que
        todo funcione bien y se vea ordenado.
        """
        # Crear un marco principal que contenga todo
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar cómo se expanden los elementos dentro del marco
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Crear el panel de control (botones, controles)
        self.control_panel = ControlPanel(main_frame)
        self.control_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Crear el panel de estado (información del sistema)
        self.status_panel = StatusPanel(main_frame)
        self.status_panel.grid(row=1, column=0, sticky="nsew")
    
    def on_closing(self):
        """
        Función que se ejecuta cuando el usuario cierra la ventana.
        
        Esta función es como apagar todas las luces y cerrar con llave
        cuando te vas de casa - se asegura de que todo quede limpio y ordenado.
        """
        self.logger.info("Usuario cerró la aplicación")
        
        # Aquí podrías agregar código para:
        # - Guardar configuraciones
        # - Detener servidores
        # - Limpiar archivos temporales
        
        # Cerrar la ventana y terminar la aplicación
        self.root.destroy()
    
    def run(self):
        """
        Inicia el bucle principal de la interfaz gráfica.
        
        Esta función es como abrir las puertas de un teatro y comenzar
        la función. Una vez que se ejecuta, la aplicación queda "viva"
        y responde a las acciones del usuario hasta que la cierre.
        """
        self.logger.info("Iniciando interfaz gráfica...")
        
        # Este comando bloquea la ejecución aquí hasta que se cierre la ventana
        self.root.mainloop()
        
        self.logger.info("Interfaz gráfica cerrada")