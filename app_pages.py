from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from ui.interfaces import Ui_DictionaryWindow, Ui_TranslationWindow, Ui_TestWindow, Ui_AddElementWindow
import sqlite3
import random


class DictionaryWindow(QMainWindow, Ui_DictionaryWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.modified = {}

        self.tableWidget.itemChanged.connect(self.row_changed)
        self.save_btn.pressed.connect(self.save_changes)
        self.del_button.pressed.connect(self.delete_element)
        self.new_button.pressed.connect(self.new_element)

        self.con = sqlite3.connect('data/idioms.db')
        self.fill_table()

    def fill_table(self):
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM idioms").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]

        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def row_changed(self, item: QTableWidgetItem):
        row = item.row()
        col = item.column()

        # Retrieve the ID of the modified row
        id_item = self.tableWidget.item(row, 0)
        if id_item is not None:
            id_value = id_item.text()

            # Store the modified value in the 'modified' dictionary
            if id_value not in self.modified:
                self.modified[id_value] = {}
            column_title = self.titles[col]
            self.modified[id_value][column_title] = item.text()

    def save_changes(self):
        cur = self.con.cursor()

        for id_value, changes in self.modified.items():
            update_query = "UPDATE idioms SET "
            update_values = []
            for col, val in changes.items():
                update_query += f"{col} = ?, "
                update_values.append(val)
            update_query = update_query[:-2] + " WHERE id = ?"
            update_values.append(id_value)

            cur.execute(update_query, update_values)

        self.con.commit()
        self.modified = {}  # Clear the modifications dictionary after saving changes

        QMessageBox.information(self, '', "Изменения сохранены")

    def new_element(self):
        global new_elem_window
        new_elem_window = NewElementWindow()
        new_elem_window.show()
        new_elem_window.closeEvent = self.update_table

    def delete_element(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]

        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids), QMessageBox.Yes, QMessageBox.No
        )

        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE FROM idioms WHERE id IN (" + ", ".join('?' * len(ids)) + ")", ids)
            self.con.commit()
            for row in rows:
                self.tableWidget.removeRow(row)

    def update_table(self, event):
        self.fill_table()


class NewElementWindow(QMainWindow, Ui_AddElementWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.con = sqlite3.connect('data/idioms.db')
        self.add_button.pressed.connect(self.add_element)
        self.cancel_button.pressed.connect(self.close)

    def add_element(self):
        cur = self.con.cursor()

        chinese = self.idiom_input.text()
        pronunciation = self.pronunciation_input.text()
        translation = self.translation_input.text()

        cur.execute("INSERT INTO idioms (chinese, pronunciation, translation) VALUES (?, ?, ?)", (chinese, pronunciation, translation))
        self.con.commit()
        self.close()

class TranslationWindow(QMainWindow, Ui_TranslationWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect('data/idioms.db')

        self.translate_button.pressed.connect(self.show_translation)

    def show_translation(self):
        cur = self.con.cursor()
        text = self.search_input.text()
        result = cur.execute("SELECT translation FROM idioms WHERE chinese = ?", (text,)).fetchone()

        if result:
            self.translation_output.setText(result[0])
        else:
            self.translation_output.setText("Not found")


class TestWindow(QMainWindow, Ui_TestWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.con = sqlite3.connect('data/idioms.db')
        self.current_pair = self.get_random_pair()
        self.idiom_output.setText(self.current_pair[0])

        self.new_button.pressed.connect(self.new_idiom)
        self.check_button.pressed.connect(self.check_translation)

    def get_random_pair(self) -> tuple[str, str]:
        cur = self.con.cursor()
        idiom, translation = random.choice(cur.execute("SELECT chinese, translation FROM idioms").fetchall())
        return idiom, translation

    def check_translation(self):
        user_input = self.translation_input.text()
        if user_input == self.current_pair[1]:
            self.translation_input.setStyleSheet("background-color: green")
        else:
            self.translation_input.setStyleSheet("background-color: red")

    def new_idiom(self):
        self.translation_input.setText("")
        self.translation_input.setStyleSheet("background-color: white")

        new = self.get_random_pair()
        while new == self.current_pair:
            new = self.get_random_pair()
        self.current_pair = new
        self.idiom_output.setText(self.current_pair[0])
