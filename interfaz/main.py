"""Interfaz de escritorio para el simulador FIFO."""

import csv
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

import puenteNucleo
from panelParametros import PanelParametros
from panelResultados import PanelResultados


espaciado = 12


class PaginaModo(ttk.Frame):
    def __init__(self, contenedor, aplicacion, modo):
        super().__init__(contenedor, padding=espaciado)
        self.aplicacion = aplicacion
        self.modo = modo
        self.directorioSalida = None
        self.replicaSeleccionada = 1
        self.guardarTodasReplicas = False
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.panelParametros = PanelParametros(
            self, modo, lambda: aplicacion._actualizarEstado(self))
        self.panelParametros.grid(row=0, column=0, sticky="new", padx=(0, espaciado))

        self.panelResultados = PanelResultados(
            self, lambda numReplica: aplicacion._seleccionarReplica(self, numReplica))
        self.panelResultados.grid(row=0, column=1, rowspan=2, sticky="nsew")

        self.botonEjecutar = ttk.Button(
            self, text="Ejecutar", command=lambda: aplicacion._ejecutar(self))
        self.botonEjecutar.grid(row=1, column=0, sticky="ew", pady=(espaciado, 0))

        self.botonRestablecer = ttk.Button(
            self, text="Restablecer valores de ejemplo",
            command=lambda: aplicacion._restablecerValoresEjemplo(self))
        self.botonRestablecer.grid(row=2, column=0, sticky="ew", pady=(espaciado, 0))

        self.guardarTodasVariable = tk.BooleanVar(value=False)
        self.casillaGuardarTodas = ttk.Checkbutton(
            self,
            text="Guardar detalle de todas las réplicas",
            variable=self.guardarTodasVariable)
        self.casillaGuardarTodas.grid(row=3, column=0, sticky="w", pady=(espaciado, 0))

        self.botonAbrir = ttk.Button(
            self, text="Abrir carpeta de CSV", command=lambda: aplicacion._abrirCsv(self), state="disabled")
        self.botonAbrir.grid(row=4, column=0, sticky="ew", pady=(espaciado, 0))

        self.botonExportar = ttk.Button(
            self, text="Exportar CSV", command=lambda: aplicacion._exportarCsv(self), state="disabled")
        self.botonExportar.grid(row=5, column=0, sticky="ew", pady=(espaciado, 0))

        self.etiquetaEstado = ttk.Label(self, text="Configuración válida.", wraplength=290, justify="left")
        self.etiquetaEstado.grid(row=6, column=0, sticky="w", pady=(espaciado, 0))


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador FIFO")
        self.geometry("1280x820")
        self.minsize(1000, 680)

        estilo = ttk.Style(self)
        temas = estilo.theme_names()
        if "vista" in temas:
            estilo.theme_use("vista")
        for nombreFuente in tkfont.names(self):
            tkfont.nametofont(nombreFuente, root=self).configure(family="Lucida Sans Unicode")
        self.paginas = []
        self.colaResultados = queue.Queue()
        self.ocupado = False

        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True)
        for modo, titulo in (("fija", "Instancia fija"), ("variable", "Instancia variable")):
            pagina = PaginaModo(cuaderno, self, modo)
            cuaderno.add(pagina, text=titulo)
            self.paginas.append(pagina)
        self.after(100, self._consultarResultados)

    def _actualizarEstado(self, pagina):
        _, error = pagina.panelParametros.leerParametros()
        pagina.panelParametros.mostrarError(error)
        if self.ocupado or error:
            pagina.botonEjecutar.configure(state="disabled")
        else:
            pagina.botonEjecutar.configure(state="normal")

    def _actualizarTodasLasPaginas(self):
        for pagina in self.paginas:
            pagina.panelParametros.establecerHabilitado(not self.ocupado)
            pagina.botonRestablecer.configure(state="disabled" if self.ocupado else "normal")
            pagina.casillaGuardarTodas.configure(state="disabled" if self.ocupado else "normal")
            self._actualizarEstado(pagina)

    def _restablecerValoresEjemplo(self, pagina):
        pagina.panelParametros.restablecerValoresEjemplo()
        pagina.panelParametros.mostrarError("")

    def _ejecutar(self, pagina):
        parametros, error = pagina.panelParametros.leerParametros()
        pagina.panelParametros.mostrarError(error)
        if error:
            return

        directorioBase = puenteNucleo.directorioSalidaPredeterminado()
        pagina.directorioSalida = os.path.join(directorioBase, pagina.modo)
        try:
            puenteNucleo.prepararDirectorioSalida(pagina.directorioSalida)
        except puenteNucleo.ErrorNucleo as errorDirectorio:
            messagebox.showerror("No se pudo preparar la corrida", str(errorDirectorio), parent=self)
            return

        pagina.botonAbrir.configure(state="disabled")
        pagina.botonExportar.configure(state="disabled")
        pagina.panelResultados.limpiar()
        pagina.etiquetaEstado.configure(text="Ejecutando simulación...")
        parametros["directorioSalida"] = pagina.directorioSalida
        parametros["guardarTodasReplicas"] = pagina.guardarTodasVariable.get()
        self.ocupado = True
        self._actualizarTodasLasPaginas()
        hilo = threading.Thread(
            target=self._ejecutarEnSegundoPlano, args=(pagina, parametros), daemon=True)
        hilo.start()

    def _ejecutarEnSegundoPlano(self, pagina, parametros):
        try:
            resumen = puenteNucleo.ejecutarSimulacion(parametros)
            replicas = puenteNucleo.leerReplicas(resumen["archivoReplicas"])
            if len(replicas) != resumen["numReplicas"]:
                raise puenteNucleo.ErrorNucleo(
                    "El CSV de réplicas no contiene la cantidad de filas esperada.")
            self.colaResultados.put((pagina, resumen, replicas, parametros))
        except (puenteNucleo.ErrorNucleo, OSError, ValueError, KeyError, csv.Error) as error:
            self.colaResultados.put((pagina, None, None, str(error)))

    def _consultarResultados(self):
        try:
            pagina, resumen, replicas, resultado = self.colaResultados.get_nowait()
        except queue.Empty:
            self.after(100, self._consultarResultados)
            return

        self.ocupado = False
        self._actualizarTodasLasPaginas()
        if isinstance(resultado, str):
            pagina.etiquetaEstado.configure(text="La simulación no se completó.")
            messagebox.showerror("Error de simulación", resultado, parent=self)
        else:
            pagina.replicas = replicas
            pagina.guardarTodasReplicas = resultado["guardarTodasReplicas"]
            pagina.panelResultados.mostrar(resumen, replicas, pagina.guardarTodasReplicas, resultado)
            pagina.botonAbrir.configure(state="normal")
            pagina.botonExportar.configure(state="normal")
            pagina.etiquetaEstado.configure(
                text="CSV guardados en:\n{}".format(pagina.directorioSalida))
        self.after(100, self._consultarResultados)

    def _seleccionarReplica(self, pagina, numReplica):
        if not pagina.directorioSalida:
            return
        if pagina.guardarTodasReplicas:
            nombreArchivo = "secuenciacion_r{:03d}.csv".format(numReplica)
        else:
            nombreArchivo = "secuenciacion.csv"
        ruta = os.path.join(pagina.directorioSalida, nombreArchivo)
        try:
            secuenciacion = puenteNucleo.leerSecuenciacion(ruta)
        except (OSError, ValueError, KeyError, csv.Error) as error:
            messagebox.showerror("No se pudo leer la secuenciación", str(error), parent=self)
            return
        pagina.replicaSeleccionada = numReplica
        numMaquinas = next(
            fila["numMaquinas"] for fila in pagina.replicas if fila["numReplica"] == numReplica)
        pagina.panelResultados.mostrarSecuenciacion(secuenciacion, numReplica, numMaquinas)

    def _abrirCsv(self, pagina):
        directorio = pagina.directorioSalida
        if not directorio or not os.path.isdir(directorio):
            messagebox.showerror("Carpeta no disponible", "No se encontró la carpeta de resultados.", parent=self)
            return
        try:
            if os.name == "nt":
                os.startfile(directorio)
            else:
                comando = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([comando, directorio])
        except OSError as error:
            messagebox.showerror("No se pudo abrir la carpeta", str(error), parent=self)

    def _exportarCsv(self, pagina):
        if not pagina.directorioSalida:
            return
        directorioDestino = filedialog.askdirectory(
            title="Seleccionar carpeta de destino para los CSV",
            initialdir=os.path.dirname(pagina.directorioSalida),
            mustexist=True,
            parent=self)
        if not directorioDestino:
            return
        try:
            rutas = puenteNucleo.exportarCsv(
                pagina.directorioSalida, directorioDestino, pagina.replicaSeleccionada,
                pagina.guardarTodasReplicas)
        except (puenteNucleo.ErrorNucleo, OSError) as error:
            messagebox.showerror("No se pudieron exportar los CSV", str(error), parent=self)
            return
        messagebox.showinfo(
            "Exportación completada",
            "Archivos exportados:\n{}".format("\n".join(rutas)),
            parent=self)


if __name__ == "__main__":
    Aplicacion().mainloop()
