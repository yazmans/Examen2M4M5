#ifndef MAQUINA_H
#define MAQUINA_H

#include <vector>

// Una entrada de la secuencia = un trabajo ya colocado en una maquina.
struct EntradaSecuencia {
    int idMaquina = 0;
    int idTrabajo = 0;
    int idProducto = 0;
    int ordenSecuenciacion = 0;
    double fechaHoraInicio = 0.0;
    double fechaHoraFin = 0.0;
};

// Agrega trabajos FIFO
class Maquina {
public:
    explicit Maquina(int idMaquina);

    void agregarTrabajo(int idTrabajo, int idProducto, double duracion);
    double tiempoFinalizacion() const { return tiempoLibre; }
    const std::vector<EntradaSecuencia>& secuencia() const { return entradas; }

private:
    int idMaquina;
    double tiempoLibre = 0.0;
    std::vector<EntradaSecuencia> entradas;
};

#endif
