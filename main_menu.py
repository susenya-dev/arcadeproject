import sqlite3
import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel, UIBoxLayout, UIAnchorLayout, UIMessageBox, UIInputText
import string as st
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

alp = st.ascii_letters + st.digits
alp = alp.replace('0', '').replace('o', '').replace('O', '').replace('l',
                                                                     '').replace('1',
                                                                                 '').replace('I', '')


def generate_password(m):
    return ''.join(random.choices(alp, k=m))


def main(n, m):
    ans = []
    while len(ans) < n:
        a = generate_password(m)
        if a not in ans:
            ans.append(a)
    return ans


class MyGUIWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Меню")
        arcade.set_background_color(arcade.color.SMOKE)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.user_layout = UIBoxLayout(vertical=True, space_between=10)
        self.main_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек для главного меню
        self.level_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек для выбора уровня

        # Изначально показываем главное меню
        f = open("assets/player.txt").readlines()
        if len(f) == 0:
            self.current_layout = self.user_layout
            self.user_menu()
        else:
            self.current_layout = self.main_layout
            self.setup_main_menu()

        self.anchor_layout.add(self.current_layout)  # Добавляем текущий layout в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

    def user_menu(self):
        self.user_layout.clear()

        input_text1 = UIInputText(x=0, y=0, width=200, height=30, text="Введи имя")
        input_text1.on_change = lambda text: text
        self.user_layout.add(input_text1)

        input_text2 = UIInputText(x=0, y=0, width=200, height=30, text="Введи пароль")
        input_text2.on_change = lambda text: text
        self.user_layout.add(input_text2)

        button = UIFlatButton(
            text="войти",
            width=200,
            height=50,
            color=arcade.color.BLUE
        )

        button.on_click = lambda event: self.menlog(input_text1, input_text2)
        self.user_layout.add(button)

    def menlog(self, input_text1, input_text2):
        self.login_user(input_text1, input_text2)
        self.show_main_menu(None)

    # пароль ник
    def login_user(self, input_text1, input_text2):
        us = ps = ""
        f = open("assets/player.txt", "w", encoding="utf-8")
        if (input_text1.text != "" and input_text2.text != "" and (input_text1.text != "Введи имя"
                                                                   and input_text2.text != "Введи пароль")):
            username = input_text1.text
            password = input_text2.text
            us = username
            ps = password

        elif (input_text1.text == "" and input_text2.text == "" or (input_text1.text == "Введи имя"
                                                                    and input_text2.text == "Введи пароль")):
            us = f"user_{''.join(main(3, 1))}"
            ps = "".join(main(10, 1))

        elif (input_text1.text == "Введи имя" or input_text1.text == "") and (
                input_text2.text != "" or input_text2.text != "Введи пароль"):
            us = f"user_{''.join(main(3, 1))}"
            ps = input_text2.text

        elif (input_text1.text != "Введи имя" or input_text1.text != "") and (
                input_text2.text == "" or input_text2.text == "Введи пароль"):
            us = input_text1.text
            ps = "".join(main(10, 1))

        print(str(us), file=f)
        print(str(ps), file=f)
        f.close()

        self.conn = sqlite3.connect("assets/game.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute(f'''INSERT INTO leaders (
                        user,
                        password
                    )
                    VALUES (
                    '{us}',
                        '{ps}'
                    );''')
        self.conn.commit()

    def dann(self, event):
        f = open("assets/player.txt").readlines()
        message_box = UIMessageBox(
            width=300, height=200,
            message_text=f"Данные аккаунта\nимя: {f[0]}пароль: {f[1]}",
            buttons=("OK",)
        )
        message_box.on_action = self.on_message_button
        self.manager.add(message_box)

    def setup_main_menu(self):
        self.main_layout.clear()

        label = UILabel(
            text="CrossWay2D",
            font_size=20,
            text_color=arcade.color.WHITE,
            width=300,
            align="center"
        )
        self.main_layout.add(label)

        level_button = UIFlatButton(
            text="Выбрать уровень",
            width=200,
            height=50,
            color=arcade.color.BLUE
        )
        level_button.on_click = self.show_levels
        self.main_layout.add(level_button)

        shop_button = UIFlatButton(
            text="Магазин",
            width=200,
            height=50,
            color=arcade.color.BLUE
        )
        shop_button.on_click = self.on_button_click
        self.main_layout.add(shop_button)

        # Кнопка "Настройки"
        settings_button = UIFlatButton(
            text="Рейтинг",
            width=200,
            height=50,
            color=arcade.color.BLUE
        )
        settings_button.on_click = self.show_rating
        self.main_layout.add(settings_button)
        settings_button3 = UIFlatButton(
            text="Данные аккаунта",
            width=200,
            height=50,
            color=arcade.color.BLUE
        )
        settings_button3.on_click = self.dann
        self.main_layout.add(settings_button3)
        settings_button2 = UIFlatButton(
            text="Выйти из аккаунта",
            width=200,
            height=50,
            color=arcade.color.BLUE
        )
        settings_button2.on_click = self.delet_user
        self.main_layout.add(settings_button2)

    def show_rating(self, event):

        from ledboard import show_rating_in_window
        show_rating_in_window(self)

    def delet_user(self, event=None):
        open("assets/player.txt", 'w').close()
        self.level_layout.clear()

        self.user_menu()

        self.sw_layout(self.user_layout)

    def setup_level_menu(self):
        self.level_layout.clear()

        back_button = UIFlatButton(
            text="Назад в меню",
            width=200,
            height=50,
            color=arcade.color.RED
        )
        back_button.on_click = self.show_main_menu
        self.level_layout.add(back_button)

        level_label = UILabel(
            text="Выберите уровень",
            font_size=18,
            text_color=arcade.color.WHITE,
            width=300,
            align="center"
        )
        self.level_layout.add(level_label)

        level1_button = UIFlatButton(
            text="Уровень 1",
            width=200,
            height=50,
            color=arcade.color.GREEN
        )
        level1_button.on_click = lambda event: self.start_level()
        self.level_layout.add(level1_button)

        level2_button = UIFlatButton(
            text="Уровень 2",
            width=200,
            height=50,
            color=arcade.color.ORANGE
        )
        level2_button.on_click = lambda event: self.start_level()
        self.level_layout.add(level2_button)

        level3_button = UIFlatButton(
            text="Уровень 3",
            width=200,
            height=50,
            color=arcade.color.RED
        )
        level3_button.on_click = lambda event: self.start_level()
        self.level_layout.add(level3_button)

    def show_levels(self, event):
        self.setup_level_menu()
        self.sw_layout(self.level_layout)

    def show_main_menu(self, event):
        self.setup_main_menu()
        self.sw_layout(self.main_layout)

    def sw_layout(self, new_layout):
        self.anchor_layout.remove(self.current_layout)

        self.current_layout = new_layout
        self.anchor_layout.add(self.current_layout)

    def start_level(self):
        message_box = UIMessageBox(
            width=300, height=200,
            message_text=f"!",
            buttons=("OK",)
        )
        message_box.on_action = self.on_message_button
        self.manager.add(message_box)

    def on_button_click(self, event):
        message_box = UIMessageBox(
            width=300, height=200,
            message_text="сообщения меню",
            buttons=("OK",)
        )
        message_box.on_action = self.on_message_button
        self.manager.add(message_box)

    def on_message_button(self, event):
        pass

    def on_draw(self):
        self.clear()
        self.manager.draw()  # Рисуй GUI поверх всего

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Для кликов, но manager сам обрабатывает


# Запуск
if __name__ == "__main__":
    window = MyGUIWindow()
    arcade.run()
