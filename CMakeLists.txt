cmake_minimum_required(VERSION 3.15)
project(SimuladorFifo CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(simulador
    nucleo/main.cpp
    nucleo/Maquina.cpp
    nucleo/Parametros.cpp
    nucleo/Simulador.cpp
    nucleo/GeneradorAleatorio.cpp
    nucleo/EscritorCsv.cpp
)

set_target_properties(simulador PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/nucleo/bin
)
