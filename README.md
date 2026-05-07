# Exopierna 3D Configurator

Aplicación interactiva para la visualización y configuración en tiempo real de prótesis mecánicas/exopiernas. Utiliza un motor de renderizado por software optimizado con Numba y una interfaz moderna en Pygame.

## Características
- **Renderizado 3D por Software:** Optimizado con NumPy y Numba (JIT).
- **Cinemática en Tiempo Real:** Configuración de flexión de rodilla, extensión de varilla y abducción.
- **Telemetría Médica:** Cálculo dinámico de torque, fuerza de carga y consumo de batería.
- **Estética Cyberpunk:** Interfaz de usuario oscura con alto contraste.

## Requisitos
- Python 3.12+
- Dependencias listadas en `requirements.txt`

## Instalación Local
1. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## Uso con Docker (X11 Forwarding)
Para ejecutar la aplicación en un contenedor Docker, asegúrate de tener un servidor X (como VcXsrv en Windows o XQuartz en macOS) ejecutándose.

1. Construir la imagen:
   ```bash
   docker build -t exopierna-app .
   ```
2. Ejecutar el contenedor (Windows/PowerShell con VcXsrv):
   ```powershell
   # Asegúrate de que el servidor X permita conexiones de red
   $DISPLAY = "$(ipconfig | select-string 'IPv4' | select-object -first 1 | % { $_.ToString().Split(':')[-1].Trim() }):0"
   docker run -it --rm -e DISPLAY=$DISPLAY -v ${PWD}/models:/app/models exopierna-app
   ```

## Desarrollo y Estándares
- **Git Commit Types:**
  - `feat`: Nueva funcionalidad.
  - `fix`: Corrección de errores.
  - `refactor`: Mejora de código sin cambio funcional.
  - `docs`: Cambios en documentación.
- **Arquitectura:** Modular dividida en Motor (`engine_3d`), Cargador (`loader`), UI (`ui_components`) y Punto de Entrada (`main`).
