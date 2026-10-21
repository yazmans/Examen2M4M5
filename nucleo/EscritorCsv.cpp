#include "EscritorCsv.h"

#include <fstream>
#include <iomanip>

namespace {

// La secuenciacion se ordena por maquina y luego por orden de atencion 
void escribirFila(std::ofstream& archivo, const EntradaSecuencia& entrada) {
    archivo << entrada.idMaquina << ',' << entrada.idTrabajo << ',' << std::fixed << std::setprecision(4)
            << entrada.fechaHoraInicio << ',' << entrada.fechaHoraFin << ',' << entrada.ordenSecuenciacion << ','
            << entrada.idProducto << '\n';
}

}  // namespace

bool escribirSecuenciacion(const std::string& ruta, const std::vector<EntradaSecuencia>& secuencia,
                           std::string& mensajeError) {
    std::ofstream archivo(ruta);
    if (!archivo) {
        mensajeError = "No se pudo escribir el archivo " + ruta + ".";
        return false;
    }
    archivo << "Maquina,idTrabajo,fechaHoraInicio,fechaHoraFin,OrdenSecuenciacion,IdProducto\n";
    for (const EntradaSecuencia& entrada : secuencia) escribirFila(archivo, entrada);
    return true;
}

bool escribirReplicas(const std::string& ruta, const std::vector<ResultadoReplica>& resultados,
                      std::string& mensajeError) {
    std::ofstream archivo(ruta);
    if (!archivo) {
        mensajeError = "No se pudo escribir el archivo " + ruta + ".";
        return false;
    }
    archivo << "numReplica,makespan,promedioAcumulado,numTrabajos,numMaquinas,semillaReplica,unidadesTotales\n";
    for (const ResultadoReplica& resultado : resultados) {
        archivo << resultado.numReplica << ',' << std::fixed << std::setprecision(4) << resultado.makespan << ','
                << resultado.promedioAcumulado << ',' << resultado.numTrabajos << ',' << resultado.numMaquinas << ','
                << resultado.semillaReplica << ',' << resultado.unidadesTotales << '\n';
    }
    return true;
}
