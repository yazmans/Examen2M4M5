"""Panel de captura de parametros con validacion en vivo."""

import tkinter as tk
from tkinter import ttk

espaciado = 6
valoresEjemplo = {
    "trabajosMin": "20",
    "trabajosMax": "30",
    "unidades": "10,20,30",
    "maquinasMin": "3",
    "maquinasMax": "5",
    "rates": "5,10,15",
    "numReplicas": "20",
    "semilla": "",
}


def validarEnteroPositivo(texto, etiqueta, maximo=None):
    texto = texto.strip()
    if not texto:
        return None, "{}: el campo no puede quedar vacío.".format(etiqueta)
    if any(caracter < "0" or caracter > "9" for caracter in texto):
        return None, "{}: se esperaba un entero positivo, se escribió '{}'.".format(etiqueta, texto)
    if len(texto) > 18:
        return None, "{}: no se admiten más de 18 dígitos.".format(etiqueta)
    valor = int(texto.lstrip("0") or "0")
    if valor <= 0:
        return None, "{}: el valor debe ser mayor que cero.".format(etiqueta)
    if maximo is not None and valor > maximo:
        return None, "{}: el valor no puede ser mayor que {}.".format(etiqueta, maximo)
    return valor, None


def validarLista(texto, etiqueta, maximo=1000000):
    texto = texto.strip()
    if not texto:
        return None, "{}: la lista no puede quedar vacía.".format(etiqueta)
    valores = []
    for elemento in texto.split(","):
        elemento = elemento.strip()
        if not elemento or any(caracter < "0" or caracter > "9" for caracter in elemento):
            return None, "{}: solo se admiten enteros positivos separados por comas ('{}' no lo es).".format(
                etiqueta, elemento)
        if len(elemento) > 18:
            return None, "{}: no se admiten más de 18 dígitos por valor.".format(etiqueta)
        valor = int(elemento.lstrip("0") or "0")
        if valor <= 0:
            return None, "{}: cada valor debe ser mayor que cero ('{}').".format(etiqueta, elemento)
        if valor > maximo:
            return None, "{}: cada valor debe ser como máximo {} ('{}').".format(
                etiqueta, maximo, elemento)
        valores.append(valor)
    return valores, None


class PanelParametros(ttk.Frame):
    def __init__(self, contenedor, modo, alCambiar):
        super().__init__(contenedor, padding=(0, 0, espaciado * 2, 0))
        self.modo = modo
        self.alCambiar = alCambiar
        self.campos = {}
        self.entradas = []
        self._construir()

    def _agregarCampo(self, contenedor, fila, etiqueta, clave, valorInicial, unidad=""):
        ttk.Label(contenedor, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=espaciado // 2)
        variable = tk.StringVar(value=valorInicial)
        variable.trace_add("write", lambda *_: self.alCambiar())
        entrada = ttk.Entry(contenedor, textvariable=variable, width=16)
        entrada.grid(row=fila, column=1, sticky="w", padx=(espaciado, 0))
        self.entradas.append(entrada)
        if unidad:
            ttk.Label(contenedor, text=unidad, foreground="#555555").grid(
            row=fila, column=2, sticky="w", padx=(espaciado, 0))
        self.campos[clave] = variable
        return variable

    def _construir(self):
        grupoFactores = ttk.LabelFrame(self, text="Factores de la simulación", padding=espaciado * 2)
        grupoFactores.grid(row=0, column=0, sticky="ew")

        self._agregarCampo(grupoFactores, 0, "Trabajos, mínimo", "trabajosMin", "20", "trabajos")
        self._agregarCampo(grupoFactores, 1, "Trabajos, máximo", "trabajosMax", "30", "trabajos")
        self._agregarCampo(grupoFactores, 2, "Unidades por trabajo", "unidades", "10,20,30", "valores permitidos")
        self._agregarCampo(grupoFactores, 3, "Máquinas, mínimo", "maquinasMin", "3", "máquinas")
        self._agregarCampo(grupoFactores, 4, "Máquinas, máximo", "maquinasMax", "5", "máquinas")
        self._agregarCampo(grupoFactores, 5, "Tasas de proceso", "rates", "5,10,15", "unidades por hora")

        grupoCorrida = ttk.LabelFrame(self, text="Corrida", padding=espaciado * 2)
        grupoCorrida.grid(row=1, column=0, sticky="ew", pady=(espaciado * 2, 0))

        self._agregarCampo(grupoCorrida, 0, "Número de réplicas", "numReplicas", "20", "réplicas")
        self._agregarCampo(grupoCorrida, 1, "Semilla", "semilla", "", "opcional")

        self.etiquetaError = ttk.Label(self, text="", foreground="#9B1C1C", wraplength=280, justify="left")
        self.etiquetaError.grid(row=2, column=0, sticky="w", pady=(espaciado * 2, 0))

    def leerParametros(self):
        """Devuelve (parametros, mensajeError). Valida lo mismo que el nucleo."""
        valores = {}
        enteros = [
            ("trabajosMin", "Trabajos, mínimo", 100000),
            ("trabajosMax", "Trabajos, máximo", 100000),
            ("maquinasMin", "Máquinas, mínimo", 10000),
            ("maquinasMax", "Máquinas, máximo", 10000),
            ("numReplicas", "Número de réplicas", 100000),
        ]
        for clave, etiqueta, maximo in enteros:
            valor, error = validarEnteroPositivo(self.campos[clave].get(), etiqueta, maximo)
            if error:
                return None, error
            valores[clave] = valor

        for clave, etiqueta in [("unidades", "Unidades por trabajo"), ("rates", "Tasas de proceso")]:
            lista, error = validarLista(self.campos[clave].get(), etiqueta)
            if error:
                return None, error
            valores[clave] = lista

        textoSemilla = self.campos["semilla"].get().strip()
        if textoSemilla:
            semilla, error = validarEnteroPositivo(textoSemilla, "Semilla", 2147483647)
            if error:
                return None, error
            valores["semilla"] = semilla
        else:
            valores["semilla"] = None

        if valores["trabajosMin"] > valores["trabajosMax"]:
            return None, "El mínimo de trabajos ({}) no puede ser mayor que el máximo ({}).".format(
                valores["trabajosMin"], valores["trabajosMax"])
        if valores["maquinasMin"] > valores["maquinasMax"]:
            return None, "El mínimo de máquinas ({}) no puede ser mayor que el máximo ({}).".format(
                valores["maquinasMin"], valores["maquinasMax"])
        valores["modo"] = self.modo
        return valores, None

    def mostrarError(self, mensaje):
        self.etiquetaError.configure(text=mensaje or "")

    def restablecerValoresEjemplo(self):
        for clave, valor in valoresEjemplo.items():
            self.campos[clave].set(valor)

    def establecerHabilitado(self, habilitado):
        estado = "normal" if habilitado else "disabled"
        for entrada in self.entradas:
            entrada.configure(state=estado)
