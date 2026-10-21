"""Puente hacia el ejecutable de C++. No contiene logica de simulacion."""

import csv
import json
import os
import shutil
import subprocess
import sys


class ErrorNucleo(Exception):
    """El ejecutable rechazó los parámetros o falló durante la corrida."""


def rutaEjecutable():
    # Al empaquetar con PyInstaller el binario viaja junto al ejecutable.
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "simulador.exe")
    raizProyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(raizProyecto, "nucleo", "bin", "simulador.exe")


def directorioSalidaPredeterminado():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.expanduser("~"), "Documents", "Simulador", "salidas")
    raizProyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(raizProyecto, "salidas")


def prepararDirectorioSalida(directorio):
    try:
        os.makedirs(directorio, exist_ok=True)
        for nombre in os.listdir(directorio):
            if nombre in ("replicas.csv", "secuenciacion.csv"):
                archivoCsv = True
            elif nombre.startswith("secuenciacion_r") and nombre.endswith(".csv"):
                numeroReplica = nombre[len("secuenciacion_r"):-len(".csv")]
                archivoCsv = bool(numeroReplica) and numeroReplica.isdigit()
            else:
                archivoCsv = False

            if not archivoCsv:
                continue

            ruta = os.path.join(directorio, nombre)
            if os.path.islink(ruta) or os.path.isfile(ruta):
                os.remove(ruta)
            else:
                raise ErrorNucleo(
                    "No se puede reemplazar el resultado porque la ruta no es un archivo:\n{}".format(ruta))
    except OSError as error:
        raise ErrorNucleo("No se pudo limpiar la carpeta de resultados:\n{}".format(error))


def construirArgumentos(parametros):
    argumentos = [
        "--modo", parametros["modo"],
        "--numReplicas", str(parametros["numReplicas"]),
        "--trabajosMin", str(parametros["trabajosMin"]),
        "--trabajosMax", str(parametros["trabajosMax"]),
        "--unidades", ",".join(str(v) for v in parametros["unidades"]),
        "--maquinasMin", str(parametros["maquinasMin"]),
        "--maquinasMax", str(parametros["maquinasMax"]),
        "--rates", ",".join(str(v) for v in parametros["rates"]),
        "--replicaDetalle", "0" if parametros.get("guardarTodasReplicas", False) else "1",
        "--directorioSalida", parametros["directorioSalida"],
    ]
    if parametros.get("semilla"):
        argumentos += ["--semilla", str(parametros["semilla"])]
    return argumentos


def ejecutarSimulacion(parametros):
    ejecutable = rutaEjecutable()
    if not os.path.exists(ejecutable):
        raise ErrorNucleo("No se encontró el ejecutable del núcleo en:\n{}".format(ejecutable))

    banderas = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    proceso = subprocess.run([ejecutable] + construirArgumentos(parametros),
                             capture_output=True, text=True, creationflags=banderas)
    if proceso.returncode != 0:
        mensaje = proceso.stderr.strip() or "El núcleo terminó con código {}.".format(proceso.returncode)
        raise ErrorNucleo(mensaje)
    try:
        return json.loads(proceso.stdout)
    except json.JSONDecodeError:
        raise ErrorNucleo("No se pudo interpretar la salida del núcleo:\n{}".format(proceso.stdout[:500]))


def leerCsv(ruta):
    with open(ruta, newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def leerReplicas(ruta):
    filas = []
    for fila in leerCsv(ruta):
        filas.append({
            "numReplica": int(fila["numReplica"]),
            "makespan": float(fila["makespan"]),
            "promedioAcumulado": float(fila["promedioAcumulado"]),
            "numTrabajos": int(fila["numTrabajos"]),
            "numMaquinas": int(fila["numMaquinas"]),
            "semillaReplica": fila["semillaReplica"],
            "unidadesTotales": int(fila["unidadesTotales"]),
        })
    return filas


def leerSecuenciacion(ruta):
    filas = []
    for fila in leerCsv(ruta):
        filas.append({
            "maquina": int(fila["Maquina"]),
            "idTrabajo": int(fila["idTrabajo"]),
            "fechaHoraInicio": float(fila["fechaHoraInicio"]),
            "fechaHoraFin": float(fila["fechaHoraFin"]),
            "ordenSecuenciacion": int(fila["OrdenSecuenciacion"]),
            "idProducto": int(fila["IdProducto"]),
        })
    return filas


def exportarCsv(directorioOrigen, directorioDestino, numReplica, guardarTodasReplicas=False):
    if guardarTodasReplicas:
        nombreSecuenciacion = "secuenciacion_r{:03d}.csv".format(numReplica)
    else:
        nombreSecuenciacion = "secuenciacion.csv"
    nombres = ["replicas.csv", nombreSecuenciacion]
    rutasExportadas = []
    for nombre in nombres:
        rutaOrigen = os.path.join(directorioOrigen, nombre)
        if not os.path.isfile(rutaOrigen):
            raise ErrorNucleo("No se encontró el archivo CSV esperado:\n{}".format(rutaOrigen))
        rutaDestino = os.path.join(directorioDestino, nombre)
        if os.path.normcase(os.path.abspath(rutaOrigen)) == os.path.normcase(os.path.abspath(rutaDestino)):
            raise ErrorNucleo("La carpeta de destino debe ser distinta de la de resultados.")
        if os.path.exists(rutaDestino):
            raise ErrorNucleo("Ya existe un archivo con este nombre en el destino:\n{}".format(rutaDestino))
        rutasExportadas.append((rutaOrigen, rutaDestino))

    for rutaOrigen, rutaDestino in rutasExportadas:
        shutil.copy2(rutaOrigen, rutaDestino)
    return [rutaDestino for _, rutaDestino in rutasExportadas]
