#ifndef GENERADOR_ALEATORIO_H
#define GENERADOR_ALEATORIO_H

#include <cstdint>
#include <random>
#include <vector>


class GeneradorAleatorio {
public:
    explicit GeneradorAleatorio(std::uint32_t semilla);

    int enteroEntre(int minimo, int maximo);
    int valorDeLista(const std::vector<int>& valores);
    std::uint32_t siguienteSemilla();

private:
    std::mt19937 motor;
};

#endif
