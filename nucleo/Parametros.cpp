#include "Parametros.h"

#include <cstdlib>
#include <sstream>
#include <string>

namespace {

// Validación de enteros positivos.
bool esEnteroPositivo(const std::string& texto, long long& valor) {
    if (texto.empty()) return false;
    for (char caracter : texto) {
        if (caracter < '0' || caracter > '9') return false;
    }
    if (texto.size() > 18) return false;
    valor = std::stoll(texto);
    return valor > 0;
}

bool leerEnteroPositivo(const std::string& nombre, const std::string& texto, int limiteSuperior,
                        int& destino, std::string& mensajeError) {
    long long valor = 0;
    if (!esEnteroPositivo(texto, valor)) {
        mensajeError = "El parametro " + nombre + " debe ser un entero positivo. Se recibio: '" + texto + "'.";
        return false;
    }
    if (valor > limiteSuperior) {
        mensajeError = "El parametro " + nombre + " no puede ser mayor que " + std::to_string(limiteSuperior) + ".";
        return false;
    }
    destino = static_cast<int>(valor);
    return true;
}

bool leerLista(const std::string& nombre, const std::string& texto, std::vector<int>& destino,
               std::string& mensajeError) {
    std::vector<int> valores;
    std::stringstream flujo(texto);
    std::string elemento;
    while (std::getline(flujo, elemento, ',')) {
        long long valor = 0;
        if (!esEnteroPositivo(elemento, valor) || valor > 1000000) {
            mensajeError = "La lista " + nombre + " solo admite enteros positivos separados por comas. Se recibio: '" +
                           elemento + "'.";
            return false;
        }
        valores.push_back(static_cast<int>(valor));
    }
    if (valores.empty()) {
        mensajeError = "La lista " + nombre + " no puede estar vacia.";
        return false;
    }
    destino = valores;
    return true;
}

}  // namespace

std::string textoAyuda() {
    return "Uso: simulador --modo fija|variable [opciones]\n"
           "  --numReplicas N        replicas a simular (entero positivo, predeterminado 20)\n"
           "  --semilla N            semilla para reproducibilidad (entero positivo, opcional)\n"
           "  --trabajosMin N        minimo de trabajos (predeterminado 20)\n"
           "  --trabajosMax N        maximo de trabajos (predeterminado 30)\n"
           "  --unidades a,b,c       unidades de trabajo permitidas (predeterminado 10,20,30)\n"
           "  --maquinasMin N        minimo de maquinas (predeterminado 3)\n"
           "  --maquinasMax N        maximo de maquinas (predeterminado 5)\n"
           "  --rates a,b,c          rates en unidades por hora (predeterminado 5,10,15)\n"
           "  --replicaDetalle N     replica a detallar; 0 escribe una por replica (predeterminado 1)\n"
           "  --directorioSalida RUTA  carpeta donde se escriben los CSV\n";
}

bool leerParametros(int argc, char* argv[], Parametros& parametros, std::string& mensajeError) {
    for (int indice = 1; indice < argc; ++indice) {
        std::string bandera = argv[indice];
        if (bandera == "--ayuda" || bandera == "--help") {
            mensajeError = textoAyuda();
            return false;
        }
        if (indice + 1 >= argc) {
            mensajeError = "Falta el valor del parametro " + bandera + ".";
            return false;
        }
        std::string valor = argv[++indice];
        if (valor.rfind("--", 0) == 0) {
            mensajeError = "Falta el valor del parametro " + bandera + "; se encontro '" + valor + "'.";
            return false;
        }

        if (bandera == "--modo") {
            if (valor == "fija") {
                parametros.modo = ModoSimulacion::Fija;
            } else if (valor == "variable") {
                parametros.modo = ModoSimulacion::Variable;
            } else {
                mensajeError = "El parametro --modo solo admite 'fija' o 'variable'. Se recibio: '" + valor + "'.";
                return false;
            }
        } else if (bandera == "--numReplicas") {
            if (!leerEnteroPositivo("--numReplicas", valor, 100000, parametros.numReplicas, mensajeError)) return false;
        } else if (bandera == "--semilla") {
            int semilla = 0;
            if (!leerEnteroPositivo("--semilla", valor, 2147483647, semilla, mensajeError)) return false;
            parametros.semilla = static_cast<std::uint32_t>(semilla);
            parametros.tieneSemilla = true;
        } else if (bandera == "--trabajosMin") {
            if (!leerEnteroPositivo("--trabajosMin", valor, 100000, parametros.trabajosMin, mensajeError)) return false;
        } else if (bandera == "--trabajosMax") {
            if (!leerEnteroPositivo("--trabajosMax", valor, 100000, parametros.trabajosMax, mensajeError)) return false;
        } else if (bandera == "--maquinasMin") {
            if (!leerEnteroPositivo("--maquinasMin", valor, 10000, parametros.maquinasMin, mensajeError)) return false;
        } else if (bandera == "--maquinasMax") {
            if (!leerEnteroPositivo("--maquinasMax", valor, 10000, parametros.maquinasMax, mensajeError)) return false;
        } else if (bandera == "--unidades") {
            if (!leerLista("--unidades", valor, parametros.unidades, mensajeError)) return false;
        } else if (bandera == "--rates") {
            if (!leerLista("--rates", valor, parametros.rates, mensajeError)) return false;
        } else if (bandera == "--replicaDetalle") {
            if (valor == "0") {
                parametros.replicaDetalle = 0;
            } else if (!leerEnteroPositivo("--replicaDetalle", valor, 100000, parametros.replicaDetalle, mensajeError)) {
                return false;
            }
        } else if (bandera == "--directorioSalida") {
            if (valor.empty()) {
                mensajeError = "El parametro --directorioSalida no puede estar vacio.";
                return false;
            }
            parametros.directorioSalida = valor;
        } else {
            mensajeError = "Parametro no reconocido: '" + bandera + "'.\n" + textoAyuda();
            return false;
        }
    }

    if (parametros.trabajosMin > parametros.trabajosMax) {
        mensajeError = "El minimo de trabajos (" + std::to_string(parametros.trabajosMin) +
                       ") no puede ser mayor que el maximo (" + std::to_string(parametros.trabajosMax) + ").";
        return false;
    }
    if (parametros.maquinasMin > parametros.maquinasMax) {
        mensajeError = "El minimo de maquinas (" + std::to_string(parametros.maquinasMin) +
                       ") no puede ser mayor que el maximo (" + std::to_string(parametros.maquinasMax) + ").";
        return false;
    }
    if (parametros.replicaDetalle > parametros.numReplicas) {
        mensajeError = "La replica a detallar (" + std::to_string(parametros.replicaDetalle) +
                       ") no puede ser mayor que el numero de replicas (" + std::to_string(parametros.numReplicas) + ").";
        return false;
    }
    return true;
}
