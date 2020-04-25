"""
1. Пошук файлів формату HTML за кількома введеними користувачем словами (врахувати можливість розриву слова тегами HTML).
2. Виділення із файлу HTML-формату частини тексту у новий файл із переміщенням зображень виділеної частини до нового каталогу.
3. Видалити з кожного рядка файлу надлишкові пробіли та всі табуляції, а також видаляти рядки, що цілком складаються із пробілів і табуляцій.
"""
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.Qt import QApplication, QClipboard
from PyQt5 import QtWidgets
from PyQt5 import QtPrintSupport
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QLineEdit


class Main(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.filename = ""
        self.changesSaved = True
        self.initUI()

    def initToolbar(self):
        # створення панелі інструментів

        # Створити
        self.newAction = QtWidgets.QAction(QtGui.QIcon("icons/new.png"), "Створити", self)
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.setStatusTip("Create a new document from scratch.")
        self.newAction.triggered.connect(self.new)

        # Відкрити
        self.openAction = QtWidgets.QAction(QtGui.QIcon("icons/open.png"), "Відкрити", self)
        self.openAction.setStatusTip("Open existing document")
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.open)

        # Зберегти
        self.saveAction = QtWidgets.QAction(QtGui.QIcon("icons/save.png"), "Зберегти", self)
        self.saveAction.setStatusTip("Save document")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.save)

        # Друкувати
        self.printAction = QtWidgets.QAction(QtGui.QIcon("icons/print.png"), "Друкувати", self)
        self.printAction.setStatusTip("Print document")
        self.printAction.setShortcut("Ctrl+P")
        self.printAction.triggered.connect(self.printHandler)

        # Форматувати (видалити всы таби і пробіли)
        self.formatAction = QtWidgets.QAction(QtGui.QIcon("icons/preview.png"), "Форматувати теги", self)
        self.formatAction.setStatusTip("Delete all tabs and spaces.")
        self.formatAction.triggered.connect(self.format_text)

        # Перегляд
        self.html_viewAction = QtWidgets.QAction(QtGui.QIcon("icons/preview.png"), "Переглянути HTML сторінку", self)
        self.html_viewAction.setStatusTip("Preview html page.")
        self.html_viewAction.triggered.connect(self.open_html)

        # Вирізати
        self.cutAction = QtWidgets.QAction(QtGui.QIcon("icons/cut.png"), "Вирізати", self)
        self.cutAction.setStatusTip("Delete and copy text to clipboard")
        self.cutAction.setShortcut("Ctrl+X")
        self.cutAction.triggered.connect(self.text.cut)

        # Копіювати
        self.copyAction = QtWidgets.QAction(QtGui.QIcon("icons/copy.png"), "Копіювати", self)
        self.copyAction.setStatusTip("Copy text to clipboard")
        self.copyAction.setShortcut("Ctrl+C")
        self.copyAction.triggered.connect(self.text.copy)

        # Вставити
        self.pasteAction = QtWidgets.QAction(QtGui.QIcon("icons/paste.png"), "Вставити", self)
        self.pasteAction.setStatusTip("Paste text from clipboard")
        self.pasteAction.setShortcut("Ctrl+V")
        self.pasteAction.triggered.connect(self.text.paste)

        # Зробити крок назад
        self.undoAction = QtWidgets.QAction(QtGui.QIcon("icons/undo.png"), "Крок назад", self)
        self.undoAction.setStatusTip("Undo last action")
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(self.text.undo)

        # Зробити крок вперед
        self.redoAction = QtWidgets.QAction(QtGui.QIcon("icons/redo.png"), "Крок вперед", self)
        self.redoAction.setStatusTip("Redo last undone thing")
        self.redoAction.setShortcut("Ctrl+Y")
        self.redoAction.triggered.connect(self.text.redo)

        # знайти
        self.searchAction = QtWidgets.QAction(QtGui.QIcon("icons/find.png"), "Знайти", self)
        self.searchAction.setStatusTip("Search through files.")
        self.searchAction.triggered.connect(self.search)

        # Відомості про програму
        self.aboutAction = QtWidgets.QAction(QtGui.QIcon("icons/about.png"), "Про програму", self)
        self.aboutAction.setShortcut("Ctrl+I")
        self.aboutAction.setStatusTip("Details about program.")
        self.aboutAction.triggered.connect(self.about)

        # Завдання: copy + new + paste
        self.cnpAction = QtWidgets.QAction(QtGui.QIcon("icons/cnp.png"), "Скопіювати + Створити + Додати", self)
        self.cnpAction.setShortcut("Ctrl+Alt+N")
        self.cnpAction.setStatusTip("Task: copy + new + paste")
        self.cnpAction.triggered.connect(self.copy_new_paste)

        # Вставити (створити список)
        bulletAction = QtWidgets.QAction(QtGui.QIcon("icons/bullet.png"), "Вставити список", self)
        bulletAction.setStatusTip("Insert bullet list")
        bulletAction.setShortcut("Ctrl+Shift+B")
        bulletAction.triggered.connect(self.bulletList)

        # Вставити (створити нумерований список)
        numberedAction = QtWidgets.QAction(QtGui.QIcon("icons/number.png"), "Вставити нумерований список", self)
        numberedAction.setStatusTip("Insert numbered list")
        numberedAction.setShortcut("Ctrl+Shift+L")
        numberedAction.triggered.connect(self.numberList)

        # Вставити зображення
        imageAction = QtWidgets.QAction(QtGui.QIcon("icons/image.png"), "Вставити зображення", self)
        imageAction.setStatusTip("Insert image")
        imageAction.setShortcut("Ctrl+Shift+I")
        imageAction.triggered.connect(self.insertImage)

        # Ярликова панель інструментів з розмежуваннями
        self.toolbar = self.addToolBar("Options")

        self.toolbar.addAction(self.newAction)
        self.toolbar.addAction(self.openAction)
        self.toolbar.addAction(self.saveAction)

        self.toolbar.addSeparator()  # Розмежуваннями

        self.toolbar.addAction(self.printAction)
        self.toolbar.addAction(self.html_viewAction)

        self.toolbar.addSeparator()  # Розмежуваннями

        self.toolbar.addAction(self.cutAction)
        self.toolbar.addAction(self.copyAction)
        self.toolbar.addAction(self.pasteAction)
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)

        self.toolbar.addSeparator()  # Розмежуваннями

        self.toolbar.addAction(bulletAction)
        self.toolbar.addAction(numberedAction)

        self.toolbar.addAction(imageAction)


        # Makes the next toolbar appear underneath this one
        self.addToolBarBreak()

    def initFormatbar(self):

      self.formatbar = self.addToolBar("Format")


    def initMenubar(self):

      menubar = self.menuBar()

      file = menubar.addMenu("Файл")
      edit = menubar.addMenu("Редагувати")
      search = menubar.addMenu("Пошук")
      task = menubar.addMenu("Задання")
      about = menubar.addMenu("Про програму")

      file.addAction(self.newAction)
      file.addAction(self.openAction)
      file.addAction(self.saveAction)
      file.addAction(self.printAction)
      file.addAction(self.html_viewAction)

      edit.addAction(self.formatAction)
      edit.addAction(self.undoAction)
      edit.addAction(self.redoAction)
      edit.addAction(self.cutAction)
      edit.addAction(self.copyAction)
      edit.addAction(self.pasteAction)

      about.addAction(self.aboutAction)

      search.addAction(self.searchAction)

      task.addAction(self.cnpAction)


    def initUI(self):

        self.text = QtWidgets.QTextEdit(self)

        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        # Set the tab stop width to around 33 pixels which is
        # about 8 spaces
        self.text.setTabStopWidth(33)

        self.setCentralWidget(self.text)

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        # If the cursor position changes, call the function that displays
        # the line and column number
        self.text.cursorPositionChanged.connect(self.cursorPosition)

        # x and y coordinates on the screen, width, height
        self.setGeometry(500, 100, 1030, 800)

        self.setWindowTitle("Текстовий редактор")

        self.setWindowIcon(QtGui.QIcon("icons/icon.png"))

        self.text.textChanged.connect(self.changed)


    def new(self):

        spawn = Main(self)
        spawn.raise_()
        spawn.activateWindow()
        spawn.show()
        return spawn

    def open(self):

        # Get filename and show only .writer files
        #PYQT5 Returns a tuple in PyQt5, we only need the filename
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', ".", "(*.html);;(*.txt)")[0]
        try:
            if self.filename:
                with open(self.filename, "rt") as file:
                    self.text.setPlainText(file.read())
        except:
            print("Error: File does not exist or contain non-text elements.")

    def open_html(self):
        with open(self.filename, "rt") as file:
            self.text.setText(file.read())

    def save(self):
        if not self.filename:
          self.filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', ".", "(*.html);;(*.txt)")[0]

        if self.filename:
            # Append extension if not there yet
            if not self.filename.endswith(".txt"):
              self.filename += ".txt"

            # We just store the contents of the text file along with the
            # format in html, which Qt does in a very nice way for us
            with open(self.filename, "wt") as file:
                file.write(self.text.toHtml())

            self.changesSaved = True

    def preview(self):

        # Open preview dialog
        preview = QtPrintSupport.QPrintPreviewDialog()

        # If a print is requested, open print dialog
        preview.paintRequested.connect(lambda p: self.text.print_(p))

        preview.exec_()

    def printHandler(self):

        # Open printing dialog
        dialog = QtPrintSupport.QPrintDialog()

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.text.document().print_(dialog.printer())


    def cursorPosition(self):

        cursor = self.text.textCursor()

        # Mortals like 1-indexed things
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()

        self.statusbar.showMessage("Line: {} | Column: {}".format(line, col))

    def bulletList(self):

        cursor = self.text.textCursor()

        # Insert bulleted list
        cursor.insertList(QtGui.QTextListFormat.ListDisc)

    def numberList(self):

        cursor = self.text.textCursor()

        # Insert list with numbers
        cursor.insertList(QtGui.QTextListFormat.ListDecimal)

    def insertImage(self):

        filename = \
        QtWidgets.QFileDialog.getOpenFileName(self, 'Insert image', ".", "Images (*.png *.xpm *.jpg *.bmp *.gif)")[0]

        if filename:

            # Create image object
            image = QtGui.QImage(filename)

            # Error if unloadable
            if image.isNull():

                popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical,
                                              "Image load error",
                                              "Could not load image file!",
                                              QtWidgets.QMessageBox.Ok,
                                              self)
                popup.show()

            else:

                cursor = self.text.textCursor()

                cursor.insertImage(image, filename)


    def about(self):
        popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.about(self, "Відомості про програму",
                                          "Програма:     Текстовий редактор\nАвтор:            Чіома Еста\nОпис:\n"
                                          "Текстовий редактор - це комп'ютерна програма-застосунок, призначений для "
                                          "створення й зміни текстових файлів формату html (вставки, видалення та "
                                          "копіювання тексту, заміни змісту, сортування та редагування), а також їх"
                                          " їх перегляду, виводу на друк."))
        popup.show()


    def copy_new_paste(self):

        self.text.copy()
        n = self.new()
        n.text.paste()


    def getText(self):
        self.wordLabel = QtWidgets.QLabel(self)
        self.wordLabel.setText('Text (some words):')
        self.line = QLineEdit(self)

        self.line.move(80, 20)
        self.line.resize(200, 32)
        self.wordLabel.move(20, 20)

        pybutton = QtWidgets.QPushButton('OK', self)
        pybutton.clicked.connect(self.clickMethod)
        pybutton.resize(200, 32)
        pybutton.move(80, 60)
        return self.wordLabel

    def clickMethod(self):
        print('Your name: ' + self.line.text())


    def search(self):
        self.library = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                         'Choose a directory'
                                                         'Library')
        user_input = self.getText()
        directory = os.listdir(self.library)

        search_string = self.getText()

        for fname in directory:
            try:
                if os.path.isfile(user_input + os.sep + fname):
                    # Full path
                    f = open(user_input + os.sep + fname, 'rt')

                    if search_string in f.read():
                        print('found string in file %s' % fname)
                    else:
                        print('string not found')
                    f.close()
            except:
                print("Error: File does not exist or contain non-text elements.")


    def format_text(self):
        plaintext = QtWidgets.QTextEdit.toPlainText(self.text)
        for i in (2, 100):
            plaintext = plaintext.replace("\t", "", i)
            plaintext = plaintext.replace("\n", "", 2)
            plaintext = plaintext.replace(' ', '', i)
            QtWidgets.QTextEdit.setPlainText(self.text, plaintext)


    def changed(self):
        self.changesSaved = False


    def closeEvent(self, event):

        if self.changesSaved:

            event.accept()

        else:

            popup = QtWidgets.QMessageBox(self)

            popup.setIcon(QtWidgets.QMessageBox.Warning)

            popup.setText("Документ було змінено")

            popup.setInformativeText("Чи хочете ви зберегти зміни?")

            popup.setStandardButtons(QtWidgets.QMessageBox.Save |
                                     QtWidgets.QMessageBox.Cancel |
                                     QtWidgets.QMessageBox.Discard)

            popup.setDefaultButton(QtWidgets.QMessageBox.Save)

            answer = popup.exec_()

            if answer == QtWidgets.QMessageBox.Save:
                self.save()

            elif answer == QtWidgets.QMessageBox.Discard:
                event.accept()

            else:
                event.ignore()


def main():

    app = QtWidgets.QApplication(sys.argv)

    main = Main()
    main.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
