"""Trabajo Practico N° 1 - Analisis Numerico - Curso Tarela - Grupo 6"""

#Martes 09 de Octubre

#Integrantes:
#Julian Garcia Delfino - 100784
#Franco Giordano - 100608
#Agustin Yanuchausky - 99496

from decimal import Decimal
import matplotlib.pyplot as plt
import numpy as np
import math

def printIntegrantes():

	"""Imprime mensaje inicial"""

	print("Trabajo Practico N° 1 - Analisis Numerico - Curso Tarela - Grupo 6\n")
	print("Julian Garcia Delfino - 100784\nFranco Giordano - 100608\nAgustin Yanuchausky - 99496\n")

def crearMatrizK(n):

	"""Crea la matriz K de coeficientes provenientes de la ecuacion diferencial discretizada."""

	if n < 5:
		return [[0.0] * 5 for x in range(5)]

	dimension = n + 1

	K = [[0.0] * dimension for x in range(dimension)]

	K[0][0] = 1.0
	K[-1][-1] = 1.0

	#Como notamos un patron en las filas de la matriz K
	#Adopatmos un vector fijo que se va trasladando y modificando

	vectorFijo = [-4.0, 5.0, -4.0, 1.0]

	for i, p in enumerate(vectorFijo):

		K[1][i] = p
		K[-2][-i-1] = p

	vectorFijo2 = [1.0] + vectorFijo
	vectorFijo2[2] += 1

	for i in range(2, n - 1):

		offset = i - 2

		for j, e in enumerate(vectorFijo2):

			K[i][j + offset] = e

	return K

def q(x, grupo = 6.0):

	"""Calcula la carga, donde el parametro "grupo" es estatico."""

	#"grupo" se puede pasar opcionalmente.

	return grupo + grupo ** 2 * (x - x ** 2) 

def x(n, i, L = 1.0):

	"""Calcula el argumento de la funcion "q"."""

	return ((i * L) / n)

def f(n, i, k = 1.0, L = 1.0):

	"""Calcula los terminos independientes del vector F en base a la funcion x y q"""

	xi = x(n, i)

	return (q(xi) * (L / n) ** 4) / k

def crearF(n):

	"""Crear matriz F"""

	dimension = n + 1

	F = [0.0] * dimension

	for i in range(1, n):

		F[i] = f(n, i)

	return F

def SOR(K, F, anterior, w = 1.0):

	"""Calcula los vectores solucion mediante el metodo iterativo SOR"""

	respuesta = anterior[ : ]

	for posicion in range(len(respuesta)):

		iteracionGS = GaussSeidel(K, F, respuesta, posicion)

		respuesta[posicion] = (iteracionGS - respuesta[posicion]) * w + respuesta[posicion]

	return respuesta

def GaussSeidel(K, F, anterior, posicion):

	"""Metodo iterativo Gauss-Seidel implementado para su uso en el metodo SOR"""

	resultado = anterior[ : ]

	factor = 0.0

	for posicionI in range(len(K)):

		if posicionI != posicion:
			factor += (K[posicion][posicionI] * resultado[posicionI]) / K[posicion][posicion]

		resultado[posicion] = (F[posicion] / K[posicion][posicion]) - factor

	return resultado[posicion]

def normaInfinito(vector):

	"""Implementacion de la norma infinito"""

	return abs(max(vector, key = lambda x: abs(x)))

def criterioConvergencia(actual, anterior, tolerancia = 0.01):

	"""Implementacion del criterio de convergencia para el chequeo periodico en el ciclo SOR"""

	resta = [actual[i] - anterior[i] for i in range(len(actual))]

	normaResta = normaInfinito(resta)

	normaActual = normaInfinito(actual)

	return normaResta / normaActual <= tolerancia

def dumpLista(lista, dumpFile):

	"""Dump de los datos de la lista seleccionada, formateado para mejor exportacion y visualizacion"""

	for posicionElemento in range(len(lista)):

		if posicionElemento == 0:
			dumpFile.write("{:.4E}".format(Decimal(lista[posicionElemento])))

		else:
			dumpFile.write("	" + "{:.4E}".format(Decimal(lista[posicionElemento])))

	dumpFile.write("\n")

def dumpDatosGrafico(iteracionesTotalesPorW, factoresDeRelajacion, dumpFile, dumpWOptimos, n, wOptimo):

	"""Dump de los datos necesarios para graficar"""

	for posicionElemento in range(len(factoresDeRelajacion)):

		dumpFile.write("%d    %.2f\n" % (iteracionesTotalesPorW[posicionElemento], factoresDeRelajacion[posicionElemento]))

	dumpWOptimos.write("N = %d\n%.2f \n" % (n, wOptimo))

def distanciaSolucion(K, F, solucion):

	return np.linalg.norm(np.matmul(K, solucion) - np.asmatrix(F))

def restar(x, y):

	return [x[i] - y[i] for i in range(len(x))]

def calcularP(x0, x1, x2, x3):

	"""Calculo del nivel de convergencia"""

	deltax3 = normaInfinito(restar(x3, x2))
	deltax2 = normaInfinito(restar(x2, x1))
	deltax1 = normaInfinito(restar(x1, x0))

	return math.log(deltax3 / deltax2) / math.log(deltax2 / deltax1)

def plotearW(datosW, tolerancia):

	"""Funcion para los graficos mediante la libreria *matplotlib*"""

	wOptimo, sol = datosW[0], datosW[1][-1]

	plt.xlabel('Intervalos de discretizacion')
	plt.ylabel('Desviacion Y [m]')
	plt.title('Desviacion de la viga en funcion de posicion x.\nN = {} - wOptimo = {} - Tolerancia = {}.'.format(len(sol) - 1, wOptimo, tolerancia))
	plt.plot(sol, linestyle = '--', marker = 'o')
	plt.show()

def hallarWOptimo(tuplaN):

	"""Se implementa para buscar el factor de relajacion optimo en base a la cruza de datos entre"""
	"""las listas de factores de relajacion usados y la lista con la cantidad de iteraciones"""

	return min(tuplaN, key = lambda x: len(x[1]))

def resolverSistema(n, tuplaActual, dumpFile = None, iteracionesTotalesPorW = [], tolerancia = 0.01):

	"""Implementacion de la funcion que incluye el metodo SOR y las funciones vistas anteriormente"""
	"""para la resolucion del sistema"""

	dimension = n + 1

	K = crearMatrizK(n)

	F = crearF(n)

	anterior = [0.0] * dimension

	actual = SOR(K, F, anterior, w = tuplaActual[0])
	tuplaActual[1].append(actual)

	if dumpFile:
		dumpFile.write("Procesamiento del SEL con factor de relajacion = " + str(tuplaActual[0]) + "\n\n")
		dumpLista(actual, dumpFile)

	while not (criterioConvergencia(actual, anterior, tolerancia)):

		anterior = actual
		actual = SOR(K, F, anterior, tuplaActual[0])

		if dumpFile:
			dumpLista(actual, dumpFile)

		tuplaActual[1].append(actual)

	iteracionesTotales = len(tuplaActual[1])

	iteracionesTotalesPorW.append(iteracionesTotales)

	return iteracionesTotales

def resolverSistemaRefinado(n, w, dumpFile = None, iteracionesTotalesPorW = [], tolerancia = 0.01):

	"""Es como la funcion resolverSistema, pero esta se encarga de resolverlo para el refinamiento"""

	dimension = n + 1

	K = crearMatrizK(n)

	F = crearF(n)

	anterior = [0.0] * dimension

	actual = SOR(K, F, anterior, w)

	iteracionesTotales = 1

	while not (criterioConvergencia(actual, anterior, tolerancia)):

		anterior = actual
		actual = SOR(K, F, anterior, w)
		iteracionesTotales += 1

	iteracionesTotalesPorW.append(iteracionesTotales)

def refinarW(n, tuplaActual, iteracionesTotalesPorW):

	"""Genera los datos de salida del refinamiento que se hace sobre el w optimo encontrado previamente"""

	iteracionesRefinamiento = []

	wOptimo = int(hallarWOptimo(tuplaActual)[0] * 100.0)

	if wOptimo == 100:

		rangoRefinamiento = [(x / 100.0) for x in range(wOptimo, wOptimo + 5, 1) if x > 0 and x != wOptimo]

		for i in range(len(rangoRefinamiento)):
			if i == 0:
				resolverSistemaRefinado(n, rangoRefinamiento[i], None, iteracionesRefinamiento)
				posicionMinimo = i

			else:
				resolverSistemaRefinado(n, rangoRefinamiento[i], None, iteracionesRefinamiento)

				if iteracionesRefinamiento[i] < iteracionesRefinamiento[posicionMinimo]:
					posicionMinimo = i

		wOptimo = rangoRefinamiento[posicionMinimo]

	else:

		rangoRefinamiento = [(x / 100.0) for x in range(wOptimo - 4, wOptimo + 5, 1) if x > 0 and x != wOptimo]

		for i in range(len(rangoRefinamiento)):
			if i == 0:
				resolverSistemaRefinado(n, rangoRefinamiento[i], None, iteracionesRefinamiento)
				posicionMinimo = i

			else:
				resolverSistemaRefinado(n, rangoRefinamiento[i], None, iteracionesRefinamiento)

				if iteracionesRefinamiento[i] < iteracionesRefinamiento[posicionMinimo]:
					posicionMinimo = i

		wOptimo = rangoRefinamiento[posicionMinimo]

	return [rangoRefinamiento, iteracionesRefinamiento, wOptimo]

def main():

	"""Funcion main donde se ejecutara todo el programa previamente descrito en el informe"""

	tomarIntervalos = True
	dictDatos = {}

	factoresDeRelajacion = [x / 100.0 for x in range(100, 200, 5)]
	
	dumpWOptimos = open("WOptimos.txt", "w")

	printIntegrantes()

	while tomarIntervalos:

		aux = int(input("Ingrese un intervalo mayor a 4, caso contrario finaliza lectura: "))

		if aux > 4:
			dictDatos[aux] = [(factor, []) for factor in factoresDeRelajacion]

		else:
			tomarIntervalos = False

	if dictDatos:
		print("Se ejecutara el programa para los siguientes intervalos: {} ".format(list(dictDatos.keys())))


	for n, tuplaActual in dictDatos.items():

		dumpFile = open("Intervalos_" + str(n) + ".txt", "w")

		iteracionesTotalesPorW = []

		for t in tuplaActual:

			iteracionesTotales = resolverSistema(n, t, dumpFile, iteracionesTotalesPorW)

			dumpFile.write("\n" + "Iteraciones totales: " + str(iteracionesTotales) + "\n\n")
			dumpFile.write("----------------------------------------------------- \n\n")

		datosRefinamiento = refinarW(n, tuplaActual, iteracionesTotalesPorW)

		dumpDatosGrafico(iteracionesTotalesPorW, factoresDeRelajacion, dumpFile, dumpWOptimos, n, datosRefinamiento[2])

		plt.title('W vs. cantidad de iteraciones.\nN = {} - Tolerancia = {}'.format(n, 0.01))
		plt.plot(factoresDeRelajacion, iteracionesTotalesPorW, marker = 'o')
		plt.plot(datosRefinamiento[0], datosRefinamiento[1], marker = 'o')
		plt.show()

		dumpFile.close()

	dumpWOptimos.close()

	dumpWOptimos = open("WOptimos.txt", "r")

	dictDatos2 = {}

	for key in dictDatos.keys():

		for line in dumpWOptimos:

			if line == ("N = " + str(key) + "\n"):
				dictDatos2[key] = (float(dumpWOptimos.readline()), [])
				break

	dumpWOptimos.close()

	for n, tuplaActual in dictDatos2.items():

		dumpFile = open("Intervalos_definitivo_" + str(n) + ".txt", "w")

		iteracionesTotalesPorW = []

		iteracionesTotales = resolverSistema(n, tuplaActual, dumpFile, iteracionesTotalesPorW, 0.0001)

		dumpFile.write("\n" + "Iteraciones totales: " + str(iteracionesTotales) + "\n\n")
		dumpFile.write("----------------------------------------------------- \n\n")

		sols = tuplaActual[1]

		print("Orden de convergencia experimental: %.4f\n" % (float(calcularP(sols[-1], sols[-2], sols[-3], sols[-4]))))

		plotearW(tuplaActual, 0.0001)

		dumpFile.close()


main()
