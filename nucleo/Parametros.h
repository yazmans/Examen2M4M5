#ifndef PARAMETROS_H
#define PARAMETROS_H

#include <cstdint>
#include <string>
#include <vector>

enum class ModoSimulacion { Fija, Variable };

struct Parametros {
    ModoSimulacion modo = ModoSimulacion::Fija;
    int numReplicas = 20;
    bool tieneSemilla = false;
    std::uint32_t semilla = 0;

    int trabajosMin = 20;
    int trabajosMax = 30;
    std::vector<int> unidades{10, 20, 30};
    int maquinasMin = 3;
    int maquinasMax = 5;
    std::vector<int> rates{5, 10, 15};

    int replicaDetalle = 1;  
    std::string directorioSalida = "salidas";
};

// Devuelve true si argv es valido, si no, deja el motivo en mensajeError.
bool leerParametros(int argc, char* argv[], Parametros& parametros, std::string& mensajeError);

std::string textoAyuda();

#endif
