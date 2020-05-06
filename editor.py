"""
1. Пошук файлів формату HTML за кількома введеними користувачем словами (врахувати можливість розриву слова тегами HTML).
2. Виділення із файлу HTML-формату частини тексту у новий файл із переміщенням зображень виділеної частини до нового каталогу.
3. Видалити з кожного рядка файлу надлишкові пробіли та всі табуляції, а також видаляти рядки, що цілком складаються із пробілів і табуляцій.
"""
# -*- coding: utf-8 -*-

import sys
import os
import glob
import re
from PyQt5 import QtWidgets
from PyQt5 import QtPrintSupport
from PyQt5 import QtGui
from PyQt5.QtWidgets import QInputDialog


class Editor(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.filename = ""
        self.changes_saved = True
        self.initUI()

    def initToolbar(self):  # створення панелі інструментів

        # Create
        self.actionNew = QtWidgets.QAction(QtGui.QIcon("icons/new.png"),
                                           "Створити", self)
        self.actionNew.setShortcut("Ctrl+N")
        self.actionNew.setStatusTip("Create a new document from scratch.")
        self.actionNew.triggered.connect(self.new_file)

        # Open
        self.actionOpen = QtWidgets.QAction(QtGui.QIcon("icons/open.png"),
                                            "Відкрити", self)
        self.actionOpen.setStatusTip("Open existing document")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionOpen.triggered.connect(self.open_file)

        # Save
        self.actionSave = QtWidgets.QAction(QtGui.QIcon("icons/save.png"),
                                            "Зберегти", self)
        self.actionSave.setStatusTip("Save document")
        self.actionSave.setShortcut("Ctrl+S")
        self.actionSave.triggered.connect(self.save_file)

        # Print
        self.actionPrint = QtWidgets.QAction(QtGui.QIcon("icons/print.png"),
                                             "Друкувати", self)
        self.actionPrint.setStatusTip("Print document")
        self.actionPrint.setShortcut("Ctrl+P")
        self.actionPrint.triggered.connect(self.preview_file)

        # Edit (delete all tabs and extra spaces)
        self.actionFormat = QtWidgets.QAction(QtGui.QIcon("icons/preview.png"),
                                              "Форматувати таби і пробіли", self)
        self.actionFormat.setStatusTip("Delete all tabs and spaces.")
        self.actionFormat.triggered.connect(self.format_text)

        # View HTML
        self.actionViewHtml = QtWidgets.QAction(QtGui.QIcon("icons/preview.png"),
                                                "Переглянути HTML сторінку", self)
        self.actionViewHtml.setStatusTip("Preview html page.")
        self.actionViewHtml.triggered.connect(self.open_html_file)

        # Cut
        self.actionCut = QtWidgets.QAction(QtGui.QIcon("icons/cut.png"),
                                           "Вирізати", self)
        self.actionCut.setStatusTip("Delete and copy text to clipboard")
        self.actionCut.setShortcut("Ctrl+X")
        self.actionCut.triggered.connect(self.text_field.cut)

        # Copy
        self.actionCopy = QtWidgets.QAction(QtGui.QIcon("icons/copy.png"),
                                            "Копіювати", self)
        self.actionCopy.setStatusTip("Copy text to clipboard")
        self.actionCopy.setShortcut("Ctrl+C")
        self.actionCopy.triggered.connect(self.text_field.copy)

        # Paste
        self.actionPaste = QtWidgets.QAction(QtGui.QIcon("icons/paste.png"),
                                             "Вставити", self)
        self.actionPaste.setStatusTip("Paste text from clipboard")
        self.actionPaste.setShortcut("Ctrl+V")
        self.actionPaste.triggered.connect(self.text_field.paste)

        # Undo
        self.actionUndo = QtWidgets.QAction(QtGui.QIcon("icons/undo.png"),
                                            "Крок назад", self)
        self.actionUndo.setStatusTip("Undo last action")
        self.actionUndo.setShortcut("Ctrl+Z")
        self.actionUndo.triggered.connect(self.text_field.undo)

        # Redo
        self.actionRedo = QtWidgets.QAction(QtGui.QIcon("icons/redo.png"),
                                            "Крок вперед", self)
        self.actionRedo.setStatusTip("Redo last undone thing")
        self.actionRedo.setShortcut("Ctrl+Y")
        self.actionRedo.triggered.connect(self.text_field.redo)

        # Find
        self.actionFind = QtWidgets.QAction(QtGui.QIcon("icons/find.png"),
                                            "Знайти", self)
        self.actionFind.setStatusTip("Search through files.")
        self.actionFind.triggered.connect(self.search)

        # About program
        self.actionAbout = QtWidgets.QAction(QtGui.QIcon("icons/about.png"),
                                             "Про програму", self)
        self.actionAbout.setShortcut("Ctrl+I")
        self.actionAbout.setStatusTip("Details about program.")
        self.actionAbout.triggered.connect(self.about_program)

        # Task: copy + new + paste
        self.actionCNP = QtWidgets.QAction(QtGui.QIcon("icons/cnp.png"),
                                           "Скопіювати + Створити + Додати", self)
        self.actionCNP.setShortcut("Ctrl+Alt+N")
        self.actionCNP.setStatusTip("Task: copy + new + paste")
        self.actionCNP.triggered.connect(self.copy_new_paste)

        # Insert bullet list
        actionBulletList = QtWidgets.QAction(QtGui.QIcon("icons/bullet.png"),
                                             "Вставити список", self)
        actionBulletList.setStatusTip("Insert bullet list")
        actionBulletList.setShortcut("Ctrl+Shift+B")
        actionBulletList.triggered.connect(self.insertBulletList)

        # Insert number list
        actionNumberedList = QtWidgets.QAction(QtGui.QIcon("icons/number.png"),
                                               "Вставити нумерований список", self)
        actionNumberedList.setStatusTip("Insert numbered list")
        actionNumberedList.setShortcut("Ctrl+Shift+L")
        actionNumberedList.triggered.connect(self.insertNumberedList)

        # Insert image
        actionImageInsert = QtWidgets.QAction(QtGui.QIcon("icons/image.png"),
                                              "Вставити зображення", self)
        actionImageInsert.setStatusTip("Insert image")
        actionImageInsert.setShortcut("Ctrl+Shift+I")
        actionImageInsert.triggered.connect(self.insertImage)

        self.toolbar = self.addToolBar("Options")

        self.toolbar.addAction(self.actionNew)
        self.toolbar.addAction(self.actionOpen)
        self.toolbar.addAction(self.actionSave)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.actionPrint)
        self.toolbar.addAction(self.actionViewHtml)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.actionCut)
        self.toolbar.addAction(self.actionCut)
        self.toolbar.addAction(self.actionPaste)
        self.toolbar.addAction(self.actionUndo)
        self.toolbar.addAction(self.actionRedo)

        self.toolbar.addSeparator()

        self.toolbar.addAction(actionBulletList)
        self.toolbar.addAction(actionNumberedList)

        self.toolbar.addAction(actionImageInsert)

        self.addToolBarBreak()

    def initFormatbar(self):

        self.formatbar = self.addToolBar("Format")

    def initMenubar(self):

        menuBar = self.menuBar()

        file = menuBar.addMenu("Файл")
        edit = menuBar.addMenu("Редагувати")
        find = menuBar.addMenu("Пошук")
        task = menuBar.addMenu("Задання")
        about = menuBar.addMenu("Про програму")

        file.addAction(self.actionNew)
        file.addAction(self.actionOpen)
        file.addAction(self.actionSave)
        file.addAction(self.actionPrint)
        file.addAction(self.actionViewHtml)

        edit.addAction(self.actionFormat)
        edit.addAction(self.actionUndo)
        edit.addAction(self.actionRedo)
        edit.addAction(self.actionCut)
        edit.addAction(self.actionCopy)
        edit.addAction(self.actionPaste)

        find.addAction(self.actionFind)
        task.addAction(self.actionCNP)
        about.addAction(self.actionAbout)

    def initUI(self):

        self.text_field = QtWidgets.QTextEdit(self)

        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        self.text_field.setTabStopWidth(33)

        self.setCentralWidget(self.text_field)

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        # If the cursor position changes, displays the line and column number
        self.text_field.cursorPositionChanged.connect(self.cursorPosition)

        # x, y, width, height
        self.setGeometry(500, 100, 1030, 800)
        self.setWindowTitle("Текстовий редактор")
        self.setWindowIcon(QtGui.QIcon("icons/icon.png"))

        self.text_field.textChanged.connect(self.changed_check)

    def new_file(self):

        spawn = Editor(self)
        spawn.raise_()
        spawn.activateWindow()
        spawn.show()
        return spawn

    def open_file(self):

        self.filename = QtWidgets.QFileDialog.getOpenFileName(self,
                                        'Open File', ".", "(*.html);;(*.txt)")[0]
        try:
            if self.filename:
                with open(self.filename, "rt") as file:
                    self.text_field.setPlainText(file.read())
        except:
            print("Error: File does not exist or contain non-text elements.")

    def open_html_file(self):

        with open(self.filename, "rt") as file:
            self.text_field.setText(file.read())

    def save_file(self):

        if not self.filename:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(self,
                                        'Save File', ".", "(*.html);;(*.txt)")[0]

        if self.filename:
            # Append extension if not there yet
            if not self.filename.endswith(".txt"):
                self.filename += ".txt"

            with open(self.filename, "wt") as file:
                file.write(self.text_field.toHtml())

            self.changes_saved = True

    def preview_file(self):
        # Open preview dialog
        preview = QtPrintSupport.QPrintPreviewDialog()

        # If a print is requested, open print dialog
        preview.paintRequested.connect(lambda p: self.text_field.print_(p))

        preview.exec_()

    def printHandler(self):
        # Open printing dialog
        dialog = QtPrintSupport.QPrintDialog()

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.text_field.document().print_(dialog.printer())

    def cursorPosition(self):

        cursor = self.text_field.textCursor()

        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()
        self.statusbar.showMessage("Рядок: {} | Стовпчик: {}".format(line, col))

    def insertBulletList(self):

        cursor = self.text_field.textCursor()
        cursor.insertList(QtGui.QTextListFormat.ListDisc)

    def insertNumberedList(self):

        cursor = self.text_field.textCursor()
        cursor.insertList(QtGui.QTextListFormat.ListDecimal)

    def insertImage(self):

        filename = \
            QtWidgets.QFileDialog.getOpenFileName(self, 'Вставити зображення', ".",
                                            "Images (*.png *.xpm *.jpg *.bmp *.gif)")[0]

        if filename:
            # Create image object
            image = QtGui.QImage(filename)

            # Error if unloadable
            if image.isNull():
                popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical,
                                            "Помилка при завантаженні зображення",
                                            "Не сожливо завантажити файл з зображенням.",
                                            QtWidgets.QMessageBox.Ok,
                                            self)
                popup.show()
            else:
                cursor = self.text_field.textCursor()
                cursor.insertImage(image, filename)

    def about_program(self):

        popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.about(self,
                        "Відомості про програму",
                        "Програма:     Текстовий редактор\nАвтор:            Чіома Еста\nОпис:\n"
                        "Текстовий редактор - це комп'ютерна програма-застосунок, призначений для "
                        "створення й зміни текстових файлів формату html (вставки, видалення та "
                        "копіювання тексту, заміни змісту, сортування та редагування), а також їх"
                        " їх перегляду, виводу на друк."))
        popup.show()

    def copy_new_paste(self):

        self.text_field.copy()
        n = self.new_file()
        n.text_field.paste()

    def getText(self):

        text_from_user, okPressed = QInputDialog.getText(self, "Пошук", "Введіть кілька слів: ")
        if okPressed and text_from_user != '':
            return text_from_user

    def search(self):
        # search and find file by few words from user
        self.library = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose a directory')
        directory = os.path.dirname((os.path.abspath(__file__)))
        my_folder = os.path.join(directory, self.library)
        flag = 0

        try:
            search_string = re.split(' ', self.getText())
        except:
            return
        
        for fname in glob.glob(os.path.join(my_folder, '*.html')):
            if flag == 0:
                with open(fname, 'rt') as file:
                    self.text_field.setText(file.read())
                    #  print(file.read())
                    for i in search_string:
                        if self.text_field.find(i):
                            flag = 1
                            # self.text.setText(f'Ваш запит знайдено у файлі - {os.path.basename(fname)}.')
                            self.text_field.toPlainText()
                            print(f'Found {search_string} in file {os.path.basename(fname)}')

                        else:
                            self.text_field.setText("Нажаль слова задані вами не "
                                                    "знайдено в жодному з файлів вказаної папки.")
                            #  self.text.setText(file.read())

    # Editing spaces and tabs with regular expressions
    def format_text(self):

        plaintext = QtWidgets.QTextEdit.toPlainText(self.text_field)
        QtWidgets.QTextEdit.setPlainText(self.text_field, re.sub('\t+', '', re.sub(' +', ' ', plaintext)))

    def changed_check(self):

        self.changes_saved = False

    def closeEvent(self, event):

        if self.changes_saved:
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
    main = Editor()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
