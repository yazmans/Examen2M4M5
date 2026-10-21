#include "GeneradorAleatorio.h"

GeneradorAleatorio::GeneradorAleatorio(std::uint32_t semilla) : motor(semilla) {}

int GeneradorAleatorio::enteroEntre(int minimo, int maximo) {
    std::uniform_int_distribution<int> distribucion(minimo, maximo);
    return distribucion(motor);
}

int GeneradorAleatorio::valorDeLista(const std::vector<int>& valores) {
    std::uniform_int_distribution<std::size_t> distribucion(0, valores.size() - 1);
    return valores[distribucion(motor)];
}

std::uint32_t GeneradorAleatorio::siguienteSemilla() {
    std::uniform_int_distribution<std::uint32_t> distribucion(1, 4294967295u);
    return distribucion(motor);
}
