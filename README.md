# Proyecto Final Pierna V2 - Configuración de Exopierna

Este proyecto es un simulador 3D interactivo desarrollado en Python para la visualización y control cinemático de una prótesis de pierna (Exopierna). Utiliza `pygame` para el renderizado y `numba` para optimizar los cálculos matemáticos de alto rendimiento.

## Cómo funciona el proyecto paso a paso

El funcionamiento del sistema se divide en las siguientes etapas secuenciales:

### 1. Inicialización y Carga de Modelos
Al ejecutar `main.py`, el sistema:
*   Inicia el entorno gráfico con **Pygame** en modo pantalla completa.
*   Utiliza el módulo `loader.py` para escanear el directorio `models/` en busca de archivos `.stl`.
*   Carga la geometría de cada pieza, convirtiendo los datos binarios del STL en arreglos de vértices (NumPy).

### 2. Procesamiento y Categorización de Piezas
Una vez cargados los vértices, el script principal:
*   Identifica si las piezas pertenecen al lado **izquierdo** o **derecho** basándose en el nombre del archivo.
*   Clasifica cada pieza en un **rol cinemático**:
    *   **TOP (Cadera/Base):** Piezas estáticas o base.
    *   **MID (Muslo):** Piezas que rotan desde la cadera (Abducción).
    *   **BOT (Rodilla/Pie):** Piezas que rotan desde la rodilla y permiten extensión.
*   Realiza una **corrección de ejes** para alinear el modelo (Z-up a Y-up) y escala el conjunto para que quepa perfectamente en la pantalla.

### 3. Motor de Cálculo Cinemático (`engine_3d.py`)
El "cerebro" matemático del proyecto aplica transformaciones en tiempo real:
*   **Cinemática Directa:** Calcula la posición de cada vértice basándose en los ángulos de flexión de rodilla, abducción de cadera y ajuste de altura.
*   **Optimización con Numba:** Los cálculos de rotación y traslación están decorados con `@njit`, lo que permite procesar miles de triángulos con una latencia mínima (60 FPS estables).
*   **Pivotes Dinámicos:** Las rotaciones se realizan sobre puntos específicos (eje de rodilla y eje de cadera) calculados automáticamente según la geometría del modelo.

### 4. Proyección 3D y Renderizado
Como el motor es un desarrollo propio (no usa OpenGL):
*   Se aplica una **proyección de perspectiva** para convertir las coordenadas 3D a coordenadas de pantalla 2D.
*   El renderizado se realiza en modo **wireframe (malla de alambre)** de alta fidelidad, con colores diferenciados para cada lado de la exopierna.
*   Se incluye una cámara orbital que permite rotar y hacer zoom sobre el modelo usando el mouse.

### 5. Interfaz de Usuario y Telemetría (`ui_components.py`)
El usuario interactúa con la simulación a través de:
*   **Sliders:** Control manual de la flexión, abducción y extensión.
*   **Panel de Telemetría:** Muestra datos en tiempo real (estado de batería simulado, ángulos exactos, modo de operación).
*   **Gráficas en Tiempo Real:** Visualizan la dinámica del movimiento de la rodilla y la cadera.
*   **Modo Demo:** Al presionar la tecla `D`, el sistema entra en un ciclo de exhibición automática donde la pierna realiza movimientos cíclicos.

## Requisitos Técnicos
*   Python 3.x
*   Pygame
*   NumPy
*   Numba (para la aceleración por hardware de los cálculos 3D)

## Instalación
1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el simulador:
   ```bash
   python main.py
   ```
