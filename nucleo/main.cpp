#include <algorithm>
#include <chrono>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "EscritorCsv.h"
#include "GeneradorAleatorio.h"
#include "Parametros.h"
#include "Simulador.h"

namespace {

std::string rutaDe(const std::string& directorio, const std::string& nombre) {
    return (std::filesystem::path(directorio) / nombre).string();
}

std::string escaparJson(const std::string& texto) {
    std::string salida;
    for (char caracter : texto) {
        if (caracter == '\\' || caracter == '"') salida += '\\';
        salida += caracter;
    }
    return salida;
}

std::string numeroConCeros(int valor, int ancho) {
    std::ostringstream flujo;
    flujo << std::setw(ancho) << std::setfill('0') << valor;
    return flujo.str();
}

void ordenarSecuencia(std::vector<EntradaSecuencia>& secuencia) {
    std::sort(secuencia.begin(), secuencia.end(), [](const EntradaSecuencia& a, const EntradaSecuencia& b) {
        if (a.idMaquina != b.idMaquina) return a.idMaquina < b.idMaquina;
        return a.ordenSecuenciacion < b.ordenSecuenciacion;
    });
}

void imprimirResumen(const Parametros& parametros, const std::vector<ResultadoReplica>& resultados,
                     const std::string& archivoReplicas, const std::string& archivoSecuenciacion,
                     std::uint32_t semillaUsada) {
    double suma = 0.0;
    double maximo = resultados.front().makespan;
    double minimo = resultados.front().makespan;
    for (const ResultadoReplica& resultado : resultados) {
        suma += resultado.makespan;
        maximo = std::max(maximo, resultado.makespan);
        minimo = std::min(minimo, resultado.makespan);
    }
    const double promedio = suma / static_cast<double>(resultados.size());

    // En modo variable los factores cambian por replica: el resumen no puede dar un solo valor.
    const bool modoFija = parametros.modo == ModoSimulacion::Fija;
    const std::string trabajosResumen =
        modoFija ? std::to_string(resultados.front().numTrabajos) : std::string("null");
    const std::string maquinasResumen =
        modoFija ? std::to_string(resultados.front().numMaquinas) : std::string("null");

    std::cout << std::fixed << std::setprecision(4) << "{\"modo\":\""
              << (parametros.modo == ModoSimulacion::Fija ? "fija" : "variable") << "\",\"numReplicas\":"
              << parametros.numReplicas << ",\"semilla\":" << semillaUsada << ",\"promedioMakespan\":" << promedio
              << ",\"maximoMakespan\":" << maximo << ",\"minimoMakespan\":" << minimo
              << ",\"numTrabajos\":" << trabajosResumen << ",\"numMaquinas\":" << maquinasResumen
              << ",\"replicaDetalle\":" << parametros.replicaDetalle << ",\"archivoReplicas\":\"" << escaparJson(archivoReplicas)
              << "\",\"archivoSecuenciacion\":\"" << escaparJson(archivoSecuenciacion) << "\"}" << std::endl;
}

}  // namespace

int main(int argc, char* argv[]) {
    Parametros parametros;
    std::string mensajeError;
    if (!leerParametros(argc, argv, parametros, mensajeError)) {
        std::cerr << mensajeError << std::endl;
        return 1;
    }

    const std::uint32_t semillaUsada =
        parametros.tieneSemilla
            ? parametros.semilla
            : static_cast<std::uint32_t>(std::chrono::high_resolution_clock::now().time_since_epoch().count());

    std::error_code codigo;
    std::filesystem::create_directories(parametros.directorioSalida, codigo);
    if (codigo) {
        std::cerr << "No se pudo crear el carpeta de salida " << parametros.directorioSalida << "." << std::endl;
        return 1;
    }

    GeneradorAleatorio generador(semillaUsada);
    Simulador simulador(parametros);

    const bool modoFija = parametros.modo == ModoSimulacion::Fija;
    Instancia instanciaFija;
    if (modoFija) instanciaFija = simulador.sortearInstancia(generador);

    std::vector<ResultadoReplica> resultados;
    resultados.reserve(parametros.numReplicas);
    std::string archivoSecuenciacion;
    double sumaMakespan = 0.0;

    for (int numReplica = 1; numReplica <= parametros.numReplicas; ++numReplica) {
        // Cada replica corre con su propia semilla para poder reproducirla por separado.
        const std::uint32_t semillaReplica = generador.siguienteSemilla();
        GeneradorAleatorio generadorReplica(semillaReplica);

        // En modo variable se vuelven a sortear todos los factores en cada replica.
        const Instancia instanciaReplica =
            modoFija ? Instancia() : simulador.sortearInstancia(generadorReplica);
        const Instancia& instancia = modoFija ? instanciaFija : instanciaReplica;

        ResultadoReplica resultado = simulador.correrReplica(instancia, generadorReplica);
        resultado.numReplica = numReplica;
        resultado.semillaReplica = semillaReplica;
        sumaMakespan += resultado.makespan;
        resultado.promedioAcumulado = sumaMakespan / static_cast<double>(numReplica);
        ordenarSecuencia(resultado.secuencia);

        const bool escribirEsta =
            parametros.replicaDetalle == 0 || parametros.replicaDetalle == numReplica;
        if (escribirEsta) {
            const std::string nombre = parametros.replicaDetalle == 0
                                           ? "secuenciacion_r" + numeroConCeros(numReplica, 3) + ".csv"
                                           : "secuenciacion.csv";
            const std::string ruta = rutaDe(parametros.directorioSalida, nombre);
            if (!escribirSecuenciacion(ruta, resultado.secuencia, mensajeError)) {
                std::cerr << mensajeError << std::endl;
                return 1;
            }
            if (parametros.replicaDetalle != 0) archivoSecuenciacion = ruta;
        }

        resultado.secuencia.clear();
        resultado.secuencia.shrink_to_fit();
        resultados.push_back(std::move(resultado));
    }

    const std::string archivoReplicas = rutaDe(parametros.directorioSalida, "replicas.csv");
    if (!escribirReplicas(archivoReplicas, resultados, mensajeError)) {
        std::cerr << mensajeError << std::endl;
        return 1;
    }
    if (parametros.replicaDetalle == 0) {
        archivoSecuenciacion = rutaDe(parametros.directorioSalida, "secuenciacion_r001.csv");
    }

    imprimirResumen(parametros, resultados, archivoReplicas, archivoSecuenciacion, semillaUsada);
    return 0;
}
