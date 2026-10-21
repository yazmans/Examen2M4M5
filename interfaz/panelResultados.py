"""Tablas y graficas de resultados."""

import tkinter as tk
from tkinter import ttk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.rcParams["font.family"] = "Lucida Sans Unicode"

espaciado = 6
colorLinea = "#1F4E79"
gris = '#777777'


class PanelResultados(ttk.Frame):
    def __init__(self, contenedor, alSeleccionarReplica):
        super().__init__(contenedor)
        self.alSeleccionarReplica = alSeleccionarReplica
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._construir()

    def _construir(self):
        grupoResumen = ttk.LabelFrame(self, text="Resumen del makespan", padding=espaciado * 2)
        grupoResumen.grid(row=0, column=0, sticky="ew")
        grupoResumen.columnconfigure(0, weight=1)

        self.tablaResumen = ttk.Treeview(grupoResumen, columns=("medida", "valor"), show="headings", height=4)
        self.tablaResumen.heading("medida", text="Medida")
        self.tablaResumen.heading("valor", text="Valor")
        self.tablaResumen.column("medida", width=260, anchor="w")
        self.tablaResumen.column("valor", width=140, anchor="e")
        self.tablaResumen.grid(row=0, column=0, sticky="ew")

        self.etiquetaParametros = ttk.Label(grupoResumen, text="", foreground=gris, wraplength=640,
                                            justify="left")
        self.etiquetaParametros.grid(row=1, column=0, sticky="w", pady=(espaciado, 0))

        cuaderno = ttk.Notebook(self)
        cuaderno.grid(row=2, column=0, sticky="nsew", pady=(espaciado * 2, 0))

        marcoReplicas = ttk.Frame(cuaderno, padding=espaciado)
        marcoReplicas.columnconfigure(0, weight=1)
        marcoReplicas.rowconfigure(0, weight=1)
        columnas = ("numReplica", "makespan", "promedioAcumulado", "numTrabajos", "numMaquinas",
                    "unidadesTotales", "semillaReplica")
        titulos = ("Réplica", "Makespan (h)", "Promedio acum. (h)", "Trabajos", "Máquinas",
                   "Unidades totales", "Semilla")
        anchos = (70, 110, 140, 80, 80, 120, 110)
        self.tablaReplicas = ttk.Treeview(marcoReplicas, columns=columnas, show="headings")
        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            self.tablaReplicas.heading(columna, text=titulo)
            self.tablaReplicas.column(columna, width=ancho, anchor="e")
        self.tablaReplicas.column("numReplica", anchor="center")
        self.tablaReplicas.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(marcoReplicas, orient="vertical", command=self.tablaReplicas.yview)
        self.tablaReplicas.configure(yscrollcommand=barra.set)
        barra.grid(row=0, column=1, sticky="ns")
        cuaderno.add(marcoReplicas, text="Réplicas")

        self.figuraConvergencia = Figure(figsize=(6.2, 3.6), dpi=100)
        self.ejeConvergencia = self.figuraConvergencia.add_subplot(111)
        marcoConvergencia = ttk.Frame(cuaderno)
        self.lienzoConvergencia = FigureCanvasTkAgg(self.figuraConvergencia, master=marcoConvergencia)
        self.lienzoConvergencia.get_tk_widget().pack(fill="both", expand=True)
        cuaderno.add(marcoConvergencia, text="Promedio acumulado (convergencia)")

        self.figuraMakespan = Figure(figsize=(6.2, 3.6), dpi=100)
        self.ejeMakespan = self.figuraMakespan.add_subplot(111)
        marcoMakespan = ttk.Frame(cuaderno)
        self.lienzoMakespan = FigureCanvasTkAgg(self.figuraMakespan, master=marcoMakespan)
        self.lienzoMakespan.get_tk_widget().pack(fill="both", expand=True)
        cuaderno.add(marcoMakespan, text="Makespan por réplica")

        self.figuraGantt = Figure(figsize=(6.2, 3.6), dpi=100)
        self.ejeGantt = self.figuraGantt.add_subplot(111)
        marcoGantt = ttk.Frame(cuaderno)
        marcoSeleccion = ttk.Frame(marcoGantt, padding=(espaciado, espaciado, espaciado, 0))
        marcoSeleccion.pack(fill="x")
        ttk.Label(marcoSeleccion, text="Replica:").pack(side="left")
        self.variableReplica = tk.StringVar()
        self.selectorReplica = ttk.Combobox(
            marcoSeleccion, textvariable=self.variableReplica, state="readonly", width=12)
        self.selectorReplica.pack(side="left", padx=(espaciado, 0))
        self.selectorReplica.bind("<<ComboboxSelected>>", self._alCambiarReplica)
        self.etiquetaDetalle = ttk.Label(marcoSeleccion, foreground=gris)
        self.etiquetaDetalle.pack(side="left", padx=(espaciado, 0))
        self.lienzoGantt = FigureCanvasTkAgg(self.figuraGantt, master=marcoGantt)
        self.lienzoGantt.get_tk_widget().pack(fill="both", expand=True)
        cuaderno.add(marcoGantt, text="Diagrama de Gantt")

        self._limpiarEjes()

    def _limpiarEjes(self):
        for eje, titulo in ((self.ejeConvergencia, "Convergencia del makespan"),
                            (self.ejeGantt, "Secuenciación por máquina")):
            eje.clear()
            eje.set_title(titulo, fontsize=10)
            eje.text(0.5, 0.5, "Sin datos. Ejecute una simulación.", ha="center", va="center",
                     transform=eje.transAxes, color=gris, fontsize=9)
            eje.set_xticks([])
            eje.set_yticks([])
        self.figuraConvergencia.tight_layout()
        self.ejeMakespan.clear()
        self.ejeMakespan.set_title("Makespan por réplica", fontsize=10)
        self.ejeMakespan.text(0.5, 0.5, "Sin datos. Ejecute una simulación.", ha="center", va="center",
                              transform=self.ejeMakespan.transAxes, color=gris, fontsize=9)
        self.ejeMakespan.set_xticks([])
        self.ejeMakespan.set_yticks([])
        self.figuraMakespan.tight_layout()
        self.figuraGantt.tight_layout()
        self.lienzoConvergencia.draw()
        self.lienzoMakespan.draw()
        self.lienzoGantt.draw()

    def limpiar(self):
        for tabla in (self.tablaResumen, self.tablaReplicas):
            for elemento in tabla.get_children():
                tabla.delete(elemento)
        self.etiquetaParametros.configure(text="")
        self.selectorReplica["values"] = []
        self.variableReplica.set("")
        self.ejeConvergencia.clear()
        self.ejeConvergencia.set_title("Promedio acumulado del makespan", fontsize=10)
        self.ejeConvergencia.text(
            0.5, 0.5, "Sin datos. Ejecute una simulación.", ha="center", va="center",
            transform=self.ejeConvergencia.transAxes, color=gris, fontsize=9)
        self.ejeConvergencia.set_xticks([])
        self.ejeConvergencia.set_yticks([])
        self.figuraConvergencia.tight_layout()
        self.lienzoConvergencia.draw()
        self._limpiarEjes()

    def mostrar(self, resumen, replicas, guardarTodasReplicas, parametros):
        self._mostrarResumen(resumen, parametros)
        self._mostrarReplicas(replicas)
        self._dibujarConvergencia(replicas)
        self._dibujarMakespan(replicas)
        replicasConDetalle = replicas if guardarTodasReplicas else replicas[:1]
        self.selectorReplica["values"] = [
            "Réplica {}".format(fila["numReplica"]) for fila in replicasConDetalle]
        if guardarTodasReplicas:
            replicaInicial = min(replicas, key=lambda fila: fila["makespan"])["numReplica"]
        else:
            replicaInicial = 1
        self.variableReplica.set("Réplica {}".format(replicaInicial))
        if guardarTodasReplicas:
            self.etiquetaDetalle.configure(text="")
        else:
            self.etiquetaDetalle.configure(text="Detalle guardado solo para la réplica 1.")
        self.alSeleccionarReplica(replicaInicial)

    def _alCambiarReplica(self, _evento):
        textoReplica = self.variableReplica.get()
        try:
            numReplica = int(textoReplica.split()[-1])
        except (ValueError, IndexError):
            return
        self.alSeleccionarReplica(numReplica)

    def mostrarSecuenciacion(self, secuenciacion, numReplica, numMaquinas):
        self._dibujarGantt(secuenciacion, numReplica, numMaquinas)

    def _mostrarResumen(self, resumen, parametros):
        for elemento in self.tablaResumen.get_children():
            self.tablaResumen.delete(elemento)
        filas = [
            ("Promedio del makespan", "{:.4f} h".format(resumen["promedioMakespan"])),
            ("Máximo del makespan", "{:.4f} h".format(resumen["maximoMakespan"])),
            ("Mínimo del makespan", "{:.4f} h".format(resumen["minimoMakespan"])),
            ("Réplicas simuladas", str(resumen["numReplicas"])),
        ]
        for fila in filas:
            self.tablaResumen.insert("", "end", values=fila)

        if resumen.get("numTrabajos") is None:
            descripcionInstancia = "factores generados en cada réplica"
        else:
            descripcionInstancia = "{} trabajos, {} máquinas".format(
                resumen["numTrabajos"], resumen["numMaquinas"])
        self.etiquetaParametros.configure(text=(
            "Modo: {} ({}).  Unidades: {}.  Tasas: {} unidades por hora.  "
            "Trabajos: {} a {}.  Máquinas: {} a {}.  Semilla: {}."
        ).format(
            "instancia fija" if resumen["modo"] == "fija" else "instancia variable",
            descripcionInstancia,
            ", ".join(str(v) for v in parametros["unidades"]),
            ", ".join(str(v) for v in parametros["rates"]),
            parametros["trabajosMin"], parametros["trabajosMax"],
            parametros["maquinasMin"], parametros["maquinasMax"],
            resumen["semilla"]))

    def _mostrarReplicas(self, replicas):
        for elemento in self.tablaReplicas.get_children():
            self.tablaReplicas.delete(elemento)
        for fila in replicas:
            self.tablaReplicas.insert("", "end", values=(
                fila["numReplica"],
                "{:.4f}".format(fila["makespan"]),
                "{:.4f}".format(fila["promedioAcumulado"]),
                fila["numTrabajos"],
                fila["numMaquinas"],
                fila["unidadesTotales"],
                fila["semillaReplica"]))

    def _dibujarConvergencia(self, replicas):
        eje = self.ejeConvergencia
        eje.clear()
        numeros = [fila["numReplica"] for fila in replicas]
        promedios = [fila["promedioAcumulado"] for fila in replicas]
        eje.plot(numeros, promedios, color=colorLinea, linewidth=1.4)
        eje.set_xlabel("Número de réplica")
        eje.set_ylabel("Makespan promedio acumulado (horas)")
        eje.set_title("Promedio acumulado del makespan", fontsize=10)
        eje.grid(True, linewidth=0.4, alpha=0.5)
        if len(numeros) <= 20:
            eje.set_xticks(numeros)
        self.figuraConvergencia.tight_layout()
        self.lienzoConvergencia.draw()

    def _dibujarMakespan(self, replicas):
        eje = self.ejeMakespan
        eje.clear()
        numeros = [fila["numReplica"] for fila in replicas]
        makespanPorReplica = [fila["makespan"] for fila in replicas]
        eje.plot(numeros, makespanPorReplica, color=colorLinea, linewidth=1.4, marker="o", markersize=3)
        eje.set_xlabel("Número de réplica")
        eje.set_ylabel("Makespan (horas)")
        eje.set_title("Makespan por réplica", fontsize=10)
        eje.grid(True, linewidth=0.4, alpha=0.5)
        if len(numeros) <= 20:
            eje.set_xticks(numeros)
        self.figuraMakespan.tight_layout()
        self.lienzoMakespan.draw()

    def _dibujarGantt(self, secuenciacion, numReplica, numMaquinas):
        eje = self.ejeGantt
        eje.clear()
        if not secuenciacion:
            eje.set_title("Secuenciación por máquina", fontsize=10)
            eje.text(0.5, 0.5, "No hay datos para la réplica seleccionada.", ha="center", va="center",
                     transform=eje.transAxes, color=gris, fontsize=9)
            eje.set_xticks([])
            eje.set_yticks([])
            self.figuraGantt.tight_layout()
            self.lienzoGantt.draw()
            return

        maquinas = range(1, numMaquinas + 1)
        posiciones = {maquina: indice for indice, maquina in enumerate(maquinas)}
        trabajos = sorted({fila["idTrabajo"] for fila in secuenciacion})
        paleta = matplotlib.colormaps["tab20"].resampled(len(trabajos))
        colorPorTrabajo = {idTrabajo: paleta(indice % paleta.N)
                           for indice, idTrabajo in enumerate(trabajos)}

        for fila in secuenciacion:
            duracion = fila["fechaHoraFin"] - fila["fechaHoraInicio"]
            eje.barh(posiciones[fila["maquina"]], duracion, left=fila["fechaHoraInicio"], height=0.6,
                     color=colorPorTrabajo[fila["idTrabajo"]], edgecolor="white", linewidth=0.5)
            if duracion > 0.8:
                eje.text(fila["fechaHoraInicio"] + duracion / 2, posiciones[fila["maquina"]],
                         str(fila["idTrabajo"]), ha="center", va="center", fontsize=7, color="black")

        eje.set_yticks(list(posiciones.values()))
        eje.set_yticklabels(["Máquina {}".format(maquina) for maquina in maquinas])
        eje.invert_yaxis()
        eje.set_xlabel("Tiempo (horas desde 0)")
        eje.set_ylabel("Máquina")
        eje.set_title("Secuenciación FIFO, réplica {}".format(numReplica), fontsize=10)
        eje.grid(True, axis="x", linewidth=0.4, alpha=0.5)
        self.figuraGantt.tight_layout()
        self.lienzoGantt.draw()
