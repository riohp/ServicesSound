# ServicesSoundAlexa

Un sistema que te permite usar tu dispositivo Alexa como altavoz para tu PC, transmitiendo audio a través de tu red local.

## Características

- Transmite audio del PC a dispositivos Alexa en tu red local
- Interfaz gráfica simple para controlar la transmisión de audio
- Descubrimiento automático de servicios usando Zeroconf
- Control de volumen y procesamiento de audio
- Monitoreo de estado y gestión de conexiones

## Requisitos

- Python 3.11
- Dispositivo Alexa compatible en la misma red
- Los siguientes paquetes de Python:
  - PyAudio
  - Flask
  - NumPy
  - Zeroconf
  - netifaces

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/carloshenao/ServicesSoundAlexa.git
   cd ServicesSoundAlexa
   ```

2. Crea y activa el entorno Conda:
   ```
   conda env create -f environment.yml
   conda activate ServicesSoundAlexa


   ```
3. ver dependencias 
   ```
   conda list
   ```
## Uso

1. Ejecuta la aplicación:
   ```
   python -m src.main
   ```

2. En la interfaz gráfica, haz clic en el botón "Iniciar Transmisión" para comenzar a transmitir audio

3. En tu dispositivo Alexa, di "Alexa, conectar a PC Audio" o busca "ServicesSound" en la aplicación de Alexa

4. Ahora deberías escuchar el audio de tu PC reproduciéndose a través de tu dispositivo Alexa

## Cómo Funciona

La aplicación captura la salida de audio de tu PC, la procesa y la pone disponible como un servicio de streaming en tu red local. Los dispositivos Alexa pueden descubrir y conectarse a este servicio usando el protocolo Zeroconf/mDNS.

## Estructura del Proyecto

```
└── riohp-servicessound/
    ├── readme.md  
    ├── environment.yml             # Este archivo
    ├── requirements.txt       # Requisitos de paquetes
    ├── setup.py               # Configuración de instalación del paquete
    ├── config/                # Archivos de configuración
    │   ├── __init__.py
    │   ├── logging_config.py  # Configuración de logging
    │   └── settings.py        # Configuraciones de la aplicación
    ├── logs/                  # Directorio de archivos de log
    ├── src/                   # Código fuente
    │   ├── main.py            # Punto de entrada principal de la aplicación
    |   ├── __init__.py        # Inicializador del paquete
    │   ├── audio/             # Componentes de procesamiento de audio
    │   │   ├── audio_config.py    # Configuración de audio
    │   │   ├── audio_processor.py # Procesamiento de señales de audio
    │   │   └── audio_server.py    # Servidor de streaming de audio
    │   ├── gui/               # Componentes de interfaz gráfica
    │   │   ├── main_window.py     # Ventana principal de la GUI
    │   │   ├── components/          # Componentes de la GUI
    │   │   │   ├── __init__.py
    │   │   │   ├── control_panel.py  # Panel de control
    │   │   │   └── status_panel.py   # Panel de estado
    │   │   └── styles/            # Estilos de la GUI
    │   │       └── __init__.py
    │   │       └── theme.py       # Tema de la aplicación
    │   ├── network/           # Componentes de red
    │   │   ├── connection_manager.py # Gestión de conexiones de clientes
    │   │   └── service_discovery.py  # Registro de servicios Zeroconf
    │   └── utils/             # Funciones de utilidad
    │       ├── __init__.py
    │       ├── helpers.py         # Funciones auxiliares
    │       └── logger.py          # Configuración de logging
    └── test/                  # Pruebas unitarias
        ├── test_audio_server.py   # Pruebas del servidor de audio
        ├── test_gui.py            # Pruebas de la GUI
        └── test_network.py        # Pruebas de red
```

## Solución de Problemas

- **"No se escucha sonido desde Alexa"**: Asegúrate de que tu PC y dispositivo Alexa estén en la misma red, verifica la configuración del firewall
- **"El audio se corta"**: Intenta reducir la frecuencia de muestreo en la configuración, asegúrate de tener buena señal WiFi
- **"No se puede descubrir el servicio"**: Asegúrate de que tu router permita tráfico mDNS

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.

## Reconocimientos

- Carlos Henao (@carloshenao) - Autor original
- Contribuyentes a los proyectos PyAudio, Flask y Zeroconf

