import matplotlib.pyplot as plt
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from UI import *
import itertools
from scipy import stats


class AppWin(QMainWindow, Ui_MainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        # Se genera la interfaz llamando al metodo setupUi
        self.setupUi(self)

        # Style de la tabla
        header1 = self.dataTableWidget.horizontalHeader()
        header1.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        # Declaracion de variables de la clase
        self.data = []
        self.fe = []
        self.cant = 0
        self.interv = 0

        # Conectando boton generar
        self.generatePushButton.clicked.connect(self.generate)
        self.cantLineEdit.returnPressed.connect(self.generate)
        self.generatePushButton.setAutoDefault(True)

        # Conectando boton limpiar datos
        self.limpiarPushButton.clicked.connect(self.limpiarDatos)
        self.limpiarPushButton.setAutoDefault(True)

        # CheckBox para habilitar cambio de valores
        self.modValues()
        self.modValuesCheckBox.stateChanged.connect(self.modValues)

        # Conectando boton para generar histograma
        self.histogramaPushButton.clicked.connect(self.genHistograma)
        self.histogramaPushButton.setAutoDefault(True)

        # Conectando boton para calcular varianza y media
        self.calcPushButton.clicked.connect(self.calcVarMed)
        self.calcPushButton.setAutoDefault(True)

    def generate(self):
        if self.cantLineEdit.text() == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Por favor ingrese la cantidad de numeros a generar")
            msg.setWindowTitle("Informacion incompleta")
            msg.exec_()
            return
        # Reinicio datos y tabla
        self.limpiarDatos()

        # Se convierten los textos validados a su int o float
        seed = float(self.semillaLineEdit.text())
        a = float(self.aLineEdit.text())
        c = float(self.cLineEdit.text())
        m = float(self.mLineEdit.text())
        self.cant = int(self.cantLineEdit.text())

        # Si el generador es multiplicativo se asigna c=0 y queda inhabilitado
        if self.tipoGenComboBox.currentIndex() == 1:
            self.cLineEdit.setEnabled(False)
            self.cLineEdit.setText("0")
            c = 0

        # Calcular subintervalos
        self.calcSubInterv()
        fo = [0] * (len(self.interv)-1)

        # Mostrar datos en tabla de numeros generados
        for i in range(0, self.cant):
            # Generamos un numero aleatorio
            rnd = ((a * seed) + c) % m
            seed = rnd
            rnd = rnd / m

            # truncamos a 4 decimales
            rnd = float("{:.4f}".format(rnd))

            # Se anexa el dato a la coleccion
            self.data.append(rnd)
            self.dataTableWidget.insertRow(i)
            self.dataTableWidget.setItem(i, 0, QTableWidgetItem(str(rnd)))

            # Frecuencias observadas colocadas en los subintervalos (contadores)
            for i in range(int(self.cantSubintervComboBox.currentText())):
                if self.interv[i] <= rnd < self.interv[i+1]:
                    fo[i] += 1

        # Calculo de la frecuencia esperada
        fe = [self.cant / (len(self.interv)-1)] * (len(self.interv)-1)

        for i in range(len(self.interv)-1):
            f = [self.interv[i]]*int((self.cant/(len(self.interv)-1)))
            self.fe.append(f)

        self.fe = list(itertools.chain(*self.fe))
 
        # Mostrar datos en tabla de Chi
        col4 = []
        col5 = []
        col6 = []
        for i in range(0, (len(self.interv)-1)):
            # Se muestran los intervalos en la tabla
            self.chiTableWidget.insertRow(i)
            intervItem = str(self.interv[i]) + ' - ' + str(self.interv[i+1])
            self.chiTableWidget.setItem(i, 0, QTableWidgetItem(intervItem))
            # Se muestran las frecuenias observadas en la tabla
            self.chiTableWidget.setItem(i, 1, QTableWidgetItem(str(fo[i])))
            # Se muestran las frecuencias esperadas en la tabla
            self.chiTableWidget.setItem(i, 2, QTableWidgetItem(str(fe[i])))
            # Calcular y mostrar 4ta columna en tabla
            col4.append((fo[i]-fe[i])**2)
            self.chiTableWidget.setItem(i, 3, QTableWidgetItem(str(col4[i])))
            # Calcular y mostrar 5ta columna en tabla
            col5.append(col4[i]/fe[i])
            self.chiTableWidget.setItem(i, 4, QTableWidgetItem(str(col5[i])))
            # Calcular y mostrar columna sumatoria
            if i == 0:
                col6.append(round(col5[i], 4))
            else:
                col6.append(round(col6[i-1] + col5[i], 4))
            self.chiTableWidget.setItem(i, 5, QTableWidgetItem(str(col6[i])))

        # Calculo de grado de libertad y generar hipotesis
        gradLibertad = int(self.cantSubintervComboBox.currentText()) - 1
        chitabulado = stats.chi2.ppf(1-.05, df=gradLibertad)
        self.chiTabuladoLineEdit.setText(str(chitabulado))
        self.sumaChiLineEdit.setText(str(col6[-1]))
        sumachi = col6[-1]
        
        if sumachi < chitabulado:
            self.resultadoLineEdit.setText("NO SE RECHAZA LA HIPOTESIS")
            self.resultadoLineEdit.setStyleSheet(
                """QLineEdit { background-color: green; color: white }""")
        else:
            self.resultadoLineEdit.setText("SE RECHAZA LA HIPOTESIS")
            self.resultadoLineEdit.setStyleSheet(
                """QLineEdit { background-color: red; color: white }""")

    # Limpiar los campos para volver a ingresar

    def limpiarDatos(self):
        self.cant = 0
        self.data = []
        self.fe = []
        self.interv = 0
        self.dataTableWidget.setRowCount(0)
        self.chiTableWidget.setRowCount(0)

    # Se calcula la media y la varianza a partir de nros generados
    def calcVarMed(self):
        if len(self.data) <= 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Por favor primero genere los datos para realizar el calculo")
            msg.setWindowTitle("Informacion incompleta")
            msg.exec_()
            return
        suma = 0
        for i in range(0, len(self.data)):
            suma = suma + self.data[i]
        media = suma / len(self.data)
        self.mediaLineEdit.setText(str(round(media, 8)))

        for i in range(0, len(self.data)):
            suma_var = (self.data[i] - media)**2
        varp = (suma_var / self.cant)
        self.varpLineEdit.setText(str(round(varp, 8)))

    # Se habilita o no la edicion de los valores a ingresar
    def modValues(self):
        if self.modValuesCheckBox.isChecked():
            self.semillaLineEdit.setEnabled(True)
            self.cLineEdit.setEnabled(True)
            self.mLineEdit.setEnabled(True)
            self.aLineEdit.setEnabled(True)
            self.tipoGenComboBox.setEnabled(True)
        else:
            self.semillaLineEdit.setEnabled(False)
            self.cLineEdit.setEnabled(False)
            self.mLineEdit.setEnabled(False)
            self.aLineEdit.setEnabled(False)
            self.tipoGenComboBox.setEnabled(False)

    # Generacion del histograma y style del mismo
    def genHistograma(self):
        if len(self.data) <= 0 or len(self.interv) <= 0 or len(self.fe) <= 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Por favor ingrese todos los parametros")
            msg.setWindowTitle("Informacion incompleta")
            msg.exec_()
            return
        plt.rcParams['toolbar'] = 'None'
        plt.hist(self.data, self.interv, histtype='bar',
                 rwidth=0.8, color="#9080ff")
        plt.hist(self.fe, self.interv, histtype='bar',
                 alpha=0.5, rwidth=0.4, color="#DC143C")
        plt.xticks(self.interv)

        plt.title("Histograma")
        plt.ylabel('Frecuencia obtenida')
        plt.xlabel('Intervalo')
        if len(self.interv) > 8:
            plt.xticks(fontsize=8)
        plt.show()

    # Funcion que calcula los xticks dependiendo del numero de intervalos ingresados
    def calcSubInterv(self):

        cantSubinterv = int(self.cantSubintervComboBox.currentText())
        rango = 1 / cantSubinterv
        self.interv = [float("{:.4f}".format(i * rango))
                       for i in range(cantSubinterv + 1)]


# Iniciar la pantalla y la app
if __name__ == '__main__':
    app = QApplication(sys.argv)
    appWin = AppWin()
    appWin.show()
    app.exec_()
