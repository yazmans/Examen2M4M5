#ifndef ESCRITOR_CSV_H
#define ESCRITOR_CSV_H

#include <string>
#include <vector>

#include "Maquina.h"
#include "Simulador.h"

bool escribirSecuenciacion(const std::string& ruta, const std::vector<EntradaSecuencia>& secuencia,
                           std::string& mensajeError);

bool escribirReplicas(const std::string& ruta, const std::vector<ResultadoReplica>& resultados,
                      std::string& mensajeError);

#endif
