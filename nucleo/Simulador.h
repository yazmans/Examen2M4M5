#ifndef SIMULADOR_H
#define SIMULADOR_H

#include <cstdint>
#include <vector>

#include "GeneradorAleatorio.h"
#include "Maquina.h"
#include "Parametros.h"
#include "Trabajo.h"

// Sorteo de factores.
struct Instancia {
    int numTrabajos = 0;
    int numMaquinas = 0;
    std::vector<Trabajo> trabajos;
    std::vector<std::vector<int>> rates;  

    int unidadesTotales() const;
};

struct ResultadoReplica {
    int numReplica = 0;
    double makespan = 0.0;
    double promedioAcumulado = 0.0;
    int numTrabajos = 0;
    int numMaquinas = 0;
    std::uint32_t semillaReplica = 0;
    int unidadesTotales = 0;
    std::vector<EntradaSecuencia> secuencia;
};

class Simulador {
public:
    explicit Simulador(const Parametros& parametros);

    Instancia sortearInstancia(GeneradorAleatorio& generador) const;
    ResultadoReplica correrReplica(const Instancia& instancia, GeneradorAleatorio& generador) const;

private:
    const Parametros& parametros;
};

double calcularMakespan(const std::vector<Maquina>& maquinas);

#endif
