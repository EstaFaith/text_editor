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
        self.file_name = ""
        self.changes_saved = True
        self.initUI()

    def initToolbar(self):  # створення панелі інструментів

        # Create
        self.actionNew = QtWidgets.QAction(QtGui.QIcon("images/new_image.png"),
                                           "Створити", self)
        self.actionNew.setStatusTip("Створити новий документ.")
        self.actionNew.setShortcut("Ctrl+N")
        self.actionNew.triggered.connect(self.new_file)


        # Open
        self.actionOpen = QtWidgets.QAction(QtGui.QIcon("images/open_image.png"),
                                            "Відкрити", self)
        self.actionOpen.setStatusTip("Відкрити існуючий документ.")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionOpen.triggered.connect(self.open_file)

        # Save
        self.actionSave = QtWidgets.QAction(QtGui.QIcon("images/save_image.png"),
                                            "Зберегти", self)
        self.actionSave.setStatusTip("Зберегти документ.")
        self.actionSave.setShortcut("Ctrl+S")
        self.actionSave.triggered.connect(self.save_file)

        # Print
        self.actionPrint = QtWidgets.QAction(QtGui.QIcon("images/print_image.png"),
                                             "Друкувати", self)
        self.actionPrint.setStatusTip("Друкувати документ.")
        self.actionPrint.setShortcut("Ctrl+P")
        self.actionPrint.triggered.connect(self.preview_file)

        # Edit (delete all tabs and extra spaces)
        self.actionFormat = QtWidgets.QAction(QtGui.QIcon("images/preview_image.png"),
                                              "Форматувати таби і пробіли", self)
        self.actionFormat.setStatusTip("Видалити пробіли і табуляції.")
        self.actionFormat.triggered.connect(self.format_text)

        # View HTML
        self.actionViewHtml = QtWidgets.QAction(QtGui.QIcon("images/preview_image.png"),
                                                "Переглянути HTML сторінку", self)
        self.actionViewHtml.setStatusTip("Переглянути HTML сторінку .")
        self.actionViewHtml.triggered.connect(self.open_html_file)

        # Cut
        self.actionCut = QtWidgets.QAction(QtGui.QIcon("images/cut_image.png"),
                                           "Вирізати", self)
        self.actionCut.setStatusTip("Видалити і скопіювати в буфер.")
        self.actionCut.setShortcut("Ctrl+X")
        self.actionCut.triggered.connect(self.text_field.cut)

        # Copy
        self.actionCopy = QtWidgets.QAction(QtGui.QIcon("images/copy_image.png"),
                                            "Копіювати", self)
        self.actionCopy.setStatusTip("Копіювати в буфер обміну.")
        self.actionCopy.setShortcut("Ctrl+C")
        self.actionCopy.triggered.connect(self.text_field.copy)

        # Paste
        self.actionPaste = QtWidgets.QAction(QtGui.QIcon("images/paste_image.png"),
                                             "Вставити", self)
        self.actionPaste.setStatusTip("Вставити з буферу обміну.")
        self.actionPaste.setShortcut("Ctrl+V")
        self.actionPaste.triggered.connect(self.text_field.paste)

        # Undo
        self.actionUndo = QtWidgets.QAction(QtGui.QIcon("images/undo_image.png"),
                                            "Крок назад", self)
        self.actionUndo.setStatusTip("Крок назад.")
        self.actionUndo.setShortcut("Ctrl+Z")
        self.actionUndo.triggered.connect(self.text_field.undo)

        # Redo
        self.actionRedo = QtWidgets.QAction(QtGui.QIcon("images/redo_image.png"),
                                            "Крок вперед", self)
        self.actionRedo.setStatusTip("Повернути крок назад.")
        self.actionRedo.setShortcut("Ctrl+Y")
        self.actionRedo.triggered.connect(self.text_field.redo)

        # Find
        self.actionFind = QtWidgets.QAction(QtGui.QIcon("images/find_image.png"),
                                            "Знайти", self)
        self.actionFind.setStatusTip("Пошук по файлам.")
        self.actionFind.triggered.connect(self.search)

        # About program
        self.actionAbout = QtWidgets.QAction(QtGui.QIcon("images/about_image.png"),
                                             "Про програму", self)
        self.actionAbout.setShortcut("Ctrl+I")
        self.actionAbout.setStatusTip("Деталі програми.")
        self.actionAbout.triggered.connect(self.about_program)

        # Task: copy + new + paste
        self.actionCNP = QtWidgets.QAction(QtGui.QIcon("images/cnp_image.png"),
                                           "Скопіювати + Створити + Додати", self)
        self.actionCNP.setShortcut("Ctrl+Alt+N")
        self.actionCNP.setStatusTip("За завданням: скопіювати+створити+додати")
        self.actionCNP.triggered.connect(self.copy_new_paste)

        # Insert bullet list
        actionBulletList = QtWidgets.QAction(QtGui.QIcon("images/bullet_image.png"),
                                             "Вставити список", self)
        actionBulletList.setStatusTip("Вставити список крапкою.")
        actionBulletList.setShortcut("Ctrl+Shift+B")
        actionBulletList.triggered.connect(self.insertBulletList)

        # Insert number list
        actionNumberedList = QtWidgets.QAction(QtGui.QIcon("images/number_image.png"),
                                               "Вставити нумерований список", self)
        actionNumberedList.setStatusTip("Вставити нумерований список.")
        actionNumberedList.setShortcut("Ctrl+Shift+L")
        actionNumberedList.triggered.connect(self.insertNumberedList)

        # Insert image
        actionImageInsert = QtWidgets.QAction(QtGui.QIcon("images/image_image.png"),
                                              "Вставити зображення", self)
        actionImageInsert.setStatusTip("Вставити зображення.")
        actionImageInsert.setShortcut("Ctrl+Shift+I")
        actionImageInsert.triggered.connect(self.insertImage)

        self.toolbar = self.addToolBar("Options")

        self.toolbar.addAction(self.actionNew)
        self.toolbar.addAction(self.actionOpen)
        self.toolbar.addAction(self.actionSave)

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

        self.text_field.setTabStopWidth(35)

        self.setCentralWidget(self.text_field)

        # Initialize a statusbar
        self.statusbar = self.statusBar()

        # If the cursor position changes, displays the line and column number
        self.text_field.cursorPositionChanged.connect(self.cursorPosition)

        # x, y, width, height
        self.setGeometry(500, 100, 1030, 800)
        self.setWindowTitle("Текстовий редактор")
        self.setWindowIcon(QtGui.QIcon("images/icon_image.png"))

        self.text_field.textChanged.connect(self.changed_check)

    def new_file(self):

        spawn = Editor(self)
        spawn.raise_()
        spawn.activateWindow()
        spawn.show()
        return spawn

    def open_file(self):

        self.file_name = QtWidgets.QFileDialog.getOpenFileName(self,
                                        'Open File', ".", "(*.html);;(*.txt)")[0]
        try:
            if self.file_name:
                with open(self.file_name, "rt") as file:
                    self.text_field.setPlainText(file.read())
        except:
            print("Error: File does not exist or contain non-text elements.")

    def open_html_file(self):

        with open(self.file_name, "rt") as file:
            self.text_field.setText(file.read())

    def save_file(self):

        if not self.file_name:
            self.file_name = QtWidgets.QFileDialog.getSaveFileName(self,
                                        'Save File', ".", "(*.html);;(*.txt)")[0]

        if self.file_name:
            # Append extension if not there yet
            if not self.file_name.endswith(".txt"):
                self.file_name += ".txt"

            with open(self.file_name, "wt") as file:
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

        file_name = \
            QtWidgets.QFileDialog.getOpenFileName(self, 'Вставити зображення', ".",
                                            "Images (*.png *.jpg *.gif)")[0]

        if file_name:
            # Create image object
            image = QtGui.QImage(file_name)

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
                cursor.insertImage(image, file_name)

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = Editor()
    main.show()
    sys.exit(app.exec_())

