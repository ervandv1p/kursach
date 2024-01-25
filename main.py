import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from login_window import Ui_LoginForm
from main_window import Ui_MainWindow
import sqlite3
import bcrypt
import random


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.image_path = ''
        self.word = ''
        self.displayed_word_list = []
        self.displayed_word = ''
        self.current_state = 0
        self.letter_buttons = [self.pushButton_A, self.pushButton_B, self.pushButton_V, self.pushButton_G,
                               self.pushButton_D, self.pushButton_E, self.pushButton_JO, self.pushButton_J,
                               self.pushButton_Z, self.pushButton_I, self.pushButton_Y, self.pushButton_K,
                               self.pushButton_L, self.pushButton_M, self.pushButton_N, self.pushButton_O,
                               self.pushButton_P, self.pushButton_R, self.pushButton_S, self.pushButton_T,
                               self.pushButton_U, self.pushButton_F, self.pushButton_X, self.pushButton_TS,
                               self.pushButton_CH, self.pushButton_W, self.pushButton_CHS, self.pushButton_b_,
                               self.pushButton_bI, self.pushButton_b, self.pushButton_EH, self.pushButton_YU,
                               self.pushButton_YA]

        self.disable_all_buttons()
        self.playButton.clicked.connect(self.play_game)
        for button in self.letter_buttons:
            button.clicked.connect(self.check_letter)

    def disable_all_buttons(self):
        for button in self.letter_buttons:
            button.setEnabled(False)

    def enable_all_buttons(self):
        for button in self.letter_buttons:
            button.setEnabled(True)

    def play_game(self):
        self.enable_all_buttons()
        self.win_loseLabel.setText('')
        self.current_state = 1
        random_index = random.randint(0, 51300)

        with open('russian_nouns.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if 0 <= random_index < len(lines):
                self.word = lines[random_index].strip()
                self.display_word(self.word)

        print(self.word)
        self.original_hangman_state()

    def display_word(self, word):
        self.displayed_word_list = []
        self.displayed_word = ''

        for letter in word:
            if letter.isalpha():
                self.displayed_word_list.append(" __ ")
            else:
                self.displayed_word_list.append(letter + " ")

        for letter in self.displayed_word_list:
            self.displayed_word += str(letter)

        self.wordLabel.setText(self.displayed_word)

    def original_hangman_state(self):
        self.image_path = 'images/hangman_0.png'
        pixmap = QPixmap(self.image_path)
        self.hangmanImage.setPixmap(pixmap)
        self.current_state = 1

    def check_letter(self):
        sender_button = self.sender()
        letter = sender_button.text().lower()

        if letter in self.word:
            for i in range(len(self.word)):
                if self.word[i] == letter and self.displayed_word_list[i] == " __ ":
                    self.displayed_word_list[i] = f'  {letter}  '

            self.displayed_word = ''.join(self.displayed_word_list)
            self.wordLabel.setText(self.displayed_word)
            sender_button.setEnabled(False)

            if " __ " not in self.displayed_word_list:
                self.game_over(True)
        else:
            self.current_state += 1

            if self.current_state == 7:
                self.game_over(False)
            else:
                self.update_hangman_image()

            sender_button.setEnabled(False)

    def update_hangman_image(self):
        self.image_path = f'images/hangman_{self.current_state}.png'
        pixmap = QPixmap(self.image_path)
        self.hangmanImage.setPixmap(pixmap)

    def game_over(self, win):
        self.disable_all_buttons()
        if win:
            self.win_loseLabel.setText("Поздравляю, вы выиграли!")
        else:
            self.image_path = 'images/hangman_end.png'
            pixmap = QPixmap(self.image_path)
            self.hangmanImage.setPixmap(pixmap)
            self.wordLabel.setText(self.word)
            self.win_loseLabel.setText("Вы проиграли, попробуйте еще раз!")


class LoginForm(QMainWindow, Ui_LoginForm):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.setupUi(self)

        self.login.clicked.connect(self.login_clicked)
        self.registration.clicked.connect(self.registration_clicked)

    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()

    def login_clicked(self):
        username = self.loginEdit.text()
        password = self.passwordEdit.text()

        if not username or not password:
            self.label.setText("Введите логин и пароль для входа")
        else:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            cursor.execute("SELECT password FROM users WHERE username=?", (username,))
            user_data = cursor.fetchone()
            conn.close()

            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[0]):
                self.close()
                self.open_main_window()
            else:
                self.label.setText("Не верно введен логин или пароль")
                self.passwordEdit.clear()

    def registration_clicked(self):
        username = self.loginEdit.text()
        password = self.passwordEdit.text()

        if not username or not password:
            self.label.setText("Введите логин и пароль для создания нового аккаунта")
        else:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                self.label.setText("Пользователь с таким логином уже существует")
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                conn.close()

                self.label.setText("Новый аккаунт успешно создан")

            self.loginEdit.clear()
            self.passwordEdit.clear()


if __name__ == '__main__':
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT NOT NULL,
                          password TEXT NOT NULL)''')

    conn.commit()
    conn.close()

    app = QApplication(sys.argv)
    window = LoginForm()
    window.show()
    sys.exit(app.exec_())
