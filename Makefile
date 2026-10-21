CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra
FUENTES = nucleo/main.cpp nucleo/Maquina.cpp nucleo/Parametros.cpp \
          nucleo/Simulador.cpp nucleo/GeneradorAleatorio.cpp nucleo/EscritorCsv.cpp
SALIDA = nucleo/bin/simulador.exe

all: $(SALIDA)

$(SALIDA): $(FUENTES)
	@mkdir -p nucleo/bin
	$(CXX) $(CXXFLAGS) -static -o $(SALIDA) $(FUENTES)

clean:
	rm -f $(SALIDA)

.PHONY: all clean
