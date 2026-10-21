#include "Simulador.h"

#include <algorithm>

int Instancia::unidadesTotales() const {
    int total = 0;
    for (const Trabajo& trabajo : trabajos) total += trabajo.unidadesTrabajo;
    return total;
}

Simulador::Simulador(const Parametros& parametros) : parametros(parametros) {}

Instancia Simulador::sortearInstancia(GeneradorAleatorio& generador) const {
    Instancia instancia;
    instancia.numTrabajos = generador.enteroEntre(parametros.trabajosMin, parametros.trabajosMax);
    instancia.numMaquinas = generador.enteroEntre(parametros.maquinasMin, parametros.maquinasMax);

    instancia.trabajos.reserve(instancia.numTrabajos);
    for (int indice = 0; indice < instancia.numTrabajos; ++indice) {
        Trabajo trabajo;
        trabajo.idTrabajo = indice + 1;
        trabajo.idProducto = indice + 1;
        trabajo.unidadesTrabajo = generador.valorDeLista(parametros.unidades);
        instancia.trabajos.push_back(trabajo);
    }

    instancia.rates.assign(instancia.numTrabajos, std::vector<int>(instancia.numMaquinas, 0));
    for (int indiceTrabajo = 0; indiceTrabajo < instancia.numTrabajos; ++indiceTrabajo) {
        for (int indiceMaquina = 0; indiceMaquina < instancia.numMaquinas; ++indiceMaquina) {
            instancia.rates[indiceTrabajo][indiceMaquina] = generador.valorDeLista(parametros.rates);
        }
    }
    return instancia;
}

ResultadoReplica Simulador::correrReplica(const Instancia& instancia, GeneradorAleatorio& generador) const {
    std::vector<Maquina> maquinas;
    maquinas.reserve(instancia.numMaquinas);
    for (int indice = 0; indice < instancia.numMaquinas; ++indice) maquinas.emplace_back(indice + 1);

    for (int indiceTrabajo = 0; indiceTrabajo < instancia.numTrabajos; ++indiceTrabajo) {
        const int indiceMaquina = generador.enteroEntre(0, instancia.numMaquinas - 1);
        const Trabajo& trabajo = instancia.trabajos[indiceTrabajo];
        const double duracion = static_cast<double>(trabajo.unidadesTrabajo) /
                                static_cast<double>(instancia.rates[indiceTrabajo][indiceMaquina]);
        maquinas[indiceMaquina].agregarTrabajo(trabajo.idTrabajo, trabajo.idProducto, duracion);
    }

    ResultadoReplica resultado;
    resultado.makespan = calcularMakespan(maquinas);
    resultado.numTrabajos = instancia.numTrabajos;
    resultado.numMaquinas = instancia.numMaquinas;
    resultado.unidadesTotales = instancia.unidadesTotales();
    for (const Maquina& maquina : maquinas) {
        const std::vector<EntradaSecuencia>& entradas = maquina.secuencia();
        resultado.secuencia.insert(resultado.secuencia.end(), entradas.begin(), entradas.end());
    }
    return resultado;
}

double calcularMakespan(const std::vector<Maquina>& maquinas) {
    double maximo = 0.0;
    for (const Maquina& maquina : maquinas) maximo = std::max(maximo, maquina.tiempoFinalizacion());
    return maximo;
}
