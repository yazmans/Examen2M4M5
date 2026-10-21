#include "Maquina.h"

Maquina::Maquina(int idMaquina) : idMaquina(idMaquina) {}

void Maquina::agregarTrabajo(int idTrabajo, int idProducto, double duracion) {
    EntradaSecuencia entrada;
    entrada.idMaquina = idMaquina;
    entrada.idTrabajo = idTrabajo;
    entrada.idProducto = idProducto;
    entrada.ordenSecuenciacion = static_cast<int>(entradas.size()) + 1;
    entrada.fechaHoraInicio = tiempoLibre;
    entrada.fechaHoraFin = tiempoLibre + duracion;
    tiempoLibre = entrada.fechaHoraFin;
    entradas.push_back(entrada);
}
