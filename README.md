# EXAMEN-2-M4-M5

Jazmin Padilla Ramos A01735947

# Instrucciones para crear archivo ejecutable

## Compilar el núcleo

Desde la terminal con el repositorio del proyecto abierto:

```powershell
g++ -std=c++17 -O2 -Wall -Wextra -static -o nucleo\bin\simulador.exe nucleo\main.cpp nucleo\Maquina.cpp nucleo\Parametros.cpp nucleo\Simulador.cpp nucleo\GeneradorAleatorio.cpp nucleo\EscritorCsv.cpp
```

## Ejecutar la interfaz

Instalación de dependencias y ejecución de la interfaz:

```powershell
python -m pip install -r requirements.txt
python interfaz\main.py
```

## Empaquetar para Windows

Con el núcleo compilado, genere un ejecutable único que incluye los algoritmos de C++:

```powershell
python empaquetado\crearEjecutable.py
```

# Descripción del proyecto

El proyecto presenta la simulación de la calendarización de tareas en máquinas. 

## Tecnologías utilizadas

| Tecnología | Uso en el proyecto |
| --- | --- |
| C++17 | Implementa el núcleo de simulación: genera instancias, asigna trabajos a máquinas y calcula el makespan. |
| Python 3 | Ejecuta la interfaz, valida parámetros, invoca el núcleo y presenta sus resultados. |
| Tkinter y ttk | Construyen la ventana de escritorio, las pestañas, los formularios, las tablas y los controles. |
| `subprocess` y JSON | La interfaz ejecuta el programa C++ como un proceso externo y recibe su resumen estructurado. |
| CSV | Guarda los resultados por réplica y la secuenciación usada para los diagramas de Gantt. |
| Matplotlib | Dibuja los diagramas de Gantt, la curva de makespan por réplica y el promedio acumulado. |
| PyInstaller | Empaqueta la interfaz Python y el ejecutable C++ en `Simulador.exe` para Windows. |
| g++ (MinGW-w64) | Compila el núcleo C++ en Windows. |
| CMake y Make | Ofrecen alternativas para configurar y compilar el núcleo, además del comando directo con g++. |
| `unittest` | Ejecuta las pruebas de validación de parámetros y del puente entre la interfaz y el núcleo. |

Tkinter, `subprocess`, JSON, CSV y `unittest` forman parte de la biblioteca estándar de Python. Las dependencias externas de Python están listadas en `requirements.txt`.

Factores: 

- Número de trabajos o tareas en un rango parametrizable.

- Cantidad de elementos de un trabajo, toma una opción entre valores parametrizables.

- Número de máquinas en un rango parametrizable.

- Rates pada cada par trabajo-máquina, toma una opción entre valores parametrizables. 

Parámetro:

- Número de simulaciones.

- Semilla opcional para replicar simulaciones.

Variables aleatorias:

- Asignación de una tarea a una máquina.

La interfaz presenta dos opciones de simulación:

1. Instancia fija: Los factores se sortean al principio y la asignación de tareas varía por simulación.

2. Instancia variable: Los factores y las asignaciones se sortean por simulación. 

Como resultado se grafica el makespan de cada simulación y el promedio acumulado donde se observa la convergencia. La casilla «Guardar detalle de todas las réplicas» está desactivada inicialmente: se guarda el resumen y el detalle de la primera réplica. Al activarla, se guarda un CSV de secuenciación por réplica y el Gantt inicial corresponde a la réplica con menor makespan. Los CSV se escriben en las carpetas `salidas\fija` y `salidas\variable`, reemplazando los archivos de la corrida anterior.

Al crear el ejecutable, se genera `empaquetado\dist\Simulador.exe`. Las corridas empaquetadas guardan sus CSV en `Documentos\Simulador\salidas\fija` y `Documentos\Simulador\salidas\variable`.
