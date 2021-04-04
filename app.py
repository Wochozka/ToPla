#!/usr/bin/env python3
# -*- coding: utf-8 -*-

version = "1.1.0"

#imports:
import argparse                 #parsing arguments
import codecs                   #file encoding
from bs4 import UnicodeDammit   #encoding detector
import csv                      #file read as csv and proccess
import os                       #file operations
from PyQt5 import QtWidgets, QtGui, QtCore          #GUI
from PyQt5.QtWidgets import QMessageBox             # GUI MessageBox
import sys                                          #GUI (exit)

#GUI:
class Form(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        super(Form,self).__init__(**kwargs)

        self.setWindowTitle("ABO to ABO-K")
        self.setFixedSize(500,200)

        self.init_gui()
        self.show()

    def init_gui(self):
        #Form layout
        form = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout()
        form.setLayout(grid)
        self.setCentralWidget(form)

        ### input file ###
        #Label
        self.input_label = QtWidgets.QLabel("Vstupní soubor:")
        self.input_label.setFont(QtGui.QFont("Arial", 14))
        grid.addWidget(self.input_label, 0,0, QtCore.Qt.AlignRight)

        #Path
        self.input_path = QtWidgets.QLineEdit()
        self.input_path.setFont(QtGui.QFont("Arial", 14))
        self.input_path.setAlignment(QtCore.Qt.AlignLeft)
        grid.addWidget(self.input_path, 0,1, QtCore.Qt.AlignCenter)

        #Find_Button
        self.input_button = QtWidgets.QPushButton("Procházet...")
        self.input_button.setFixedSize(85,35)
        self.input_button.clicked.connect(self.fileOpenDialog)
        grid.addWidget(self.input_button,0,2, QtCore.Qt.AlignLeft)

        ### output file ###
        #Label
        self.output_label = QtWidgets.QLabel("Výstupní soubor:")
        self.output_label.setFont(QtGui.QFont("Arial", 14))
        grid.addWidget(self.output_label, 1,0, QtCore.Qt.AlignRight)

        #Path
        self.output_path = QtWidgets.QLineEdit()
        self.output_path.setFont(QtGui.QFont("Arial", 14))
        self.output_path.setAlignment(QtCore.Qt.AlignLeft)
        grid.addWidget(self.output_path, 1,1, QtCore.Qt.AlignCenter)

        #Find_Button
        self.output_button = QtWidgets.QPushButton("Procházet...")
        self.output_button.setFixedSize(85,35)
        self.output_button.clicked.connect(self.fileSaveDialog)
        grid.addWidget(self.output_button,1,2, QtCore.Qt.AlignLeft)

        ### dosage ###
        #Label
        self.dosage_label = QtWidgets.QLabel("Číslo dávky:")
        self.dosage_label.setFont(QtGui.QFont("Arial", 14))
        grid.addWidget(self.dosage_label, 2,0, QtCore.Qt.AlignLeft)

        #SpinBox
        self.dosage = QtWidgets.QSpinBox()
        self.dosage.setFont(QtGui.QFont("Arial", 14))
        self.dosage.setFixedSize(120,30)
        self.dosage.setValue(20)
        grid.addWidget(self.dosage, 2,1, QtCore.Qt.AlignLeft)

        ### Others ###
        #TransferButton
        self.transfer_button = QtWidgets.QPushButton("Převést")
        self.transfer_button.setFont(QtGui.QFont("Arial", 14))
        self.transfer_button.setFixedSize(85,35)
        self.transfer_button.clicked.connect(self.transferButton)
        grid.addWidget(self.transfer_button, 3,2,1,2, QtCore.Qt.AlignRight)

        #About
        self.about = QtWidgets.QLabel("Made by Wochozka, (c) All Rights Reserved")
        self.about.setFont(QtGui.QFont("Times New Roman", 8))
        grid.addWidget(self.about, 3,0,1,2, QtCore.Qt.AlignBottom)

    #FileOpenDialog
    def fileOpenDialog(self):
        self.input_dialog = QtWidgets.QFileDialog.Options()
        self.input_dialog |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Open KPC file", "","KPC Files (*.kpc);;All Files (*)", options=self.input_dialog)
        if fileName:
            self.input_path.setText(fileName)
    
    #FileSaveDialog
    def fileSaveDialog(self):
        self.output_dialog = QtWidgets.QFileDialog.Options()
        self.output_dialog |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save PLA file to","","PLA Files (*.pla);;Text Files (*.txt);;All Files (*)", options=self.output_dialog)
        if fileName:
            self.output_path.setText(fileName)
    
    #transferButton
    def transferButton(self):
        transfer(self.input_path.text(), self.output_path.text(), self.dosage.value(), gui=True)

def transfer(inputFile, outputFile, dosage, gui):
    
    #if outputFile is not set, create filename automaticly
    if (outputFile == None or outputFile == ""):
        outputFile = inputFile[:-3] + "pla"
    
    #input file is not set - this should not happen 
    if (inputFile == ""):
        print("Input file must be set.")
        return 

    #check encoding and fileexist
    try:
        with open(inputFile, 'rb') as myfile:
            content = myfile.read()
    except:
        print("Input file is corrupted or not exist:", sys.exc_info()[0])

    suggestion = UnicodeDammit(content)
    if suggestion.original_encoding != "utf-8":
        #Change encoding
        BLOCKSIZE = 1048576 # or some other, desired size in bytes
        #create auxiliary file with correct encoding
        targetFileName = inputFile + ".utf"
        with codecs.open(inputFile, "r", "cp1250") as sourceFile:
            with codecs.open(targetFileName, "w", "utf-8") as targetFile:
                while True:
                    contents = sourceFile.read(BLOCKSIZE)
                    if not contents:
                        break
                    targetFile.write(contents)
        #change input file from original with bad encoding to auxiliary file with proper encoding
        inputFile = targetFileName

    #read input file
    with open(inputFile, newline='') as pohodaFile:
        inputList = list(csv.reader(pohodaFile, delimiter=' '))

    #init outputList
    outputList = []

    currentDate = inputList[0][0][4:10]                 #first line of input file, getDate
    payersAccount = inputList[2][1].replace("-", "")    #third line, getPayersAccount
    dueDate = inputList[2][3]                           #third line, getDueDate
    totalAmount = inputList[2][2][:-2]                  #third line, getTotalAmount
    while totalAmount[0] == "0":                        #remove left zeroes
        totalAmount = totalAmount[1:]
    totalAmountSup = inputList[2][2][-2:]               #third line, getTotalAmount /pennies (marked 'sup' as supplemental)

    outputList = [f"FS5;P248;{currentDate};{dosage};K;0;B;\n"]      #first line, HARD SET FOR NEEDS TEXTILNISKOLA.cz
    
    #format: inputList[lineInInputFile][groupSeparatedBySpace][subStingInGroup]
    for item in range(1, (len(inputList)-4)):                       #items parsing
        beneficiarysAccount = inputList[item+2][0].replace("-", "") #beneficiary's accounts
        bankCode = inputList[item+2][3][:-4]                        #bank codes
        amount = inputList[item+2][1][:-2]                          #amount (int)
        while amount[0] == "0":                                     #remove left zeroes
            amount = amount[1:]
        amountSup = inputList[item+2][1][-2:]                       #amount /pennies (marked 'sup' as supplemental)
        variableSym = inputList[item+2][2]                          #variable symbol
        constantSym = inputList[item+2][3][-4:]                     #constant symbol

        outputList.append(f"PRT;{item};;U;{payersAccount};{beneficiarysAccount};{bankCode};{amount},{amountSup};CZK;{dueDate};{variableSym};{constantSym};;;\n")
    
    outputList.append(f"KON;{len(inputList)-5};{totalAmount},{totalAmountSup};\n")

    #save file
    with open(outputFile, 'w', newline='\n') as abokFile:
        for line in outputList:
            abokFile.write(line)
    #if GUI was used, launch MsgBox
    if gui: msgBox()
    
    sys.exit()

def msgBox():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Prevod byl dokoncen.")
        msg.setWindowTitle("ABO to ABO-K")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prevod Multicash formatu KPC z Pohody do CNB formatu ABO-K FS5.")
    parser.add_argument("-i", "--input", help="Vstupni soubor ve formatu .kpc z Pohody. Pokud neni zadan, spusti se GUI.")
    parser.add_argument("-o", "--output", help="Nazev souboru pro vystup, ktery bude slouzit pro CNB ABO-K jako FS5 verze.")
    parser.add_argument("-d", "--dosage", help="Cislo davky (vychozi = 20).", default="20")
    parser.add_argument("-v", "--version", help="Vypise aktualini verzi programu.", action="store_true")

    #parse arguments
    args = parser.parse_args()
    inputFile = args.input
    outputFile = args.output
    dosage = args.dosage
    
    if args.version:
        print(version)
        exit()

    #if argument -i is set (input file) transfer it on bash/cmd, otherwise GUI 
    if (inputFile == None):
        #run GUI
        aplikace = QtWidgets.QApplication(sys.argv)
        okno = Form()
        sys.exit(aplikace.exec_())

    else:
        #make transfer via bash/cmd
        transfer(inputFile, outputFile, dosage, gui=False)