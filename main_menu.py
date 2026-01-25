import sqlite3
import time
import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel, UIBoxLayout, UIAnchorLayout, UIMessageBox, UIInputText, \
    UITextureButton
import string as st
import random
from main import Game
from arcade.gui import UITextWidget

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
        self.anchor_layout = UIAnchorLayout()
        # Центрирует виджеты

        self.user_layout = UIBoxLayout(vertical=True, space_between=10)
        self.main_layout = UIBoxLayout(vertical=True, space_between=10)
        self.level_layout = UIBoxLayout(vertical=True, space_between=10)
        self.shop_layout = UIBoxLayout(vertical=True, space_between=10)

        f = open("assets/player.txt").readlines()
        if len(f) == 0:
            self.current_layout = self.user_layout
            self.user_menu()
        else:
            self.current_layout = self.main_layout
            self.setup_main_menu()

        self.anchor_layout.add(self.current_layout)  # Добавляем текущий layout в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager
        self.current_mode = "menu"
        self.game_instance = None

    def shop_menu(self):
        self.shop_layout.clear()
        with open("assets/player.txt", "r", encoding="utf-8") as f:
            user_name = f.readline().strip()
        conn = sqlite3.connect("assets/game.db")
        cur = conn.cursor()
        sp = cur.execute(
            f"SELECT coins_count, skin FROM leaders WHERE user = '{user_name}'").fetchall()
        print(sp)
        conn.close()

        shop_label = UILabel(
            text=f"Coins: {sp[0][0]}",
            font_size=20,
            text_color=arcade.color.GOLD,
            width=300,
            align="center"
        )
        self.shop_layout.add(shop_label)

        if "s2" in sp[0][-1]:
            self.text = "Персонаж 2"
        else:
            self.text = "🔒Купить за 20💲🔒"

        if "s3" in sp[0][-1]:
            self.text2 = "Персонаж 3"
        else:
            self.text2 = "🔒Купить за 30💲🔒"

        initial_texture = arcade.load_texture("assets/shop_foto/1.png")

        back_button = UIFlatButton(
            text="Назад в меню",
            width=200,
            height=50,
            color=arcade.color.RED
        )
        back_button.on_click = self.show_main_menu
        self.shop_layout.add(back_button)

        shop_label = UILabel(
            text="Магазин",
            font_size=20,
            text_color=arcade.color.WHITE,
            width=300,
            align="center"
        )
        self.shop_layout.add(shop_label)

        self.character1_button = UIFlatButton(
            text="Персонаж 1",
            width=200,
            height=50,
            color=arcade.color.GRAY
        )
        self.character1_button.on_click = lambda event: self.shop_button_clicked(1)
        self.shop_layout.add(self.character1_button)

        self.character2_button = UIFlatButton(
            text=self.text,
            width=200,
            height=50,
            color=arcade.color.GRAY
        )
        self.character2_button.on_click = lambda event: self.skin_shop(2)
        self.shop_layout.add(self.character2_button)

        self.character3_button = UIFlatButton(
            text=self.text2,
            width=200,
            height=50,
            color=arcade.color.GRAY
        )
        self.character3_button.on_click = lambda event: self.skin_shop(3)
        self.shop_layout.add(self.character3_button)

        self.texture_widget = UITextureButton(
            texture=initial_texture,
            texture_hovered=initial_texture,
            texture_pressed=initial_texture,
            text="",
            width=100,
            height=100
        )
        self.shop_layout.add(self.texture_widget)

        self.sw_layout(self.shop_layout)

    def mag_send(self, event, param):
        message_box = UIMessageBox(
            width=300, height=200,
            message_text="Вы уверены что хотите купить персонажа?",
            buttons=("ДА", "НЕТ")
        )
        message_box.on_action = self.message_from_shop(event, param)
        self.manager.add(message_box)

    def message_from_shop(self, event, param):
        bt = event
        if bt == "ДА":
            self.skin_shop(param)
        else:
            pass

    def skin_shop(self, param):
        with open("assets/player.txt", "r", encoding="utf-8") as f:
            user_name = f.readline().strip()
        conn = sqlite3.connect("assets/game.db")
        cur = conn.cursor()
        sp = cur.execute(
            f"SELECT coins_count, skin FROM leaders WHERE user = '{user_name}'").fetchall()
        # print(sp[0][0])

        if f"s{param}" in sp[0][-1]:
            self.shop_button_clicked(param)
        else:
            if param == 2:
                sp = cur.execute(
                    f"SELECT coins_count, skin FROM leaders WHERE user = '{user_name}'").fetchall()
                # print(sp[0][0])
                if sp[0][0] > 20:
                    skin_db = f"{sp[0][-1]}s2"
                    ost_coin = sp[0][0] - 20
                    # print(skin_db)
                    # print(ost_coin)
                    cur.execute(
                        f""" UPDATE leaders SET coins_count = {ost_coin}, skin = '{skin_db}' 
                        WHERE user = '{user_name}'""")
                    self.character2_button.text = "Персонаж 2"
                    self.texture_widget.trigger_render()
                    self.shop_button_clicked(param)
                    print("купленно2")
                    message_box = UIMessageBox(
                        width=300, height=200,
                        message_text="Купленно",
                        buttons=("OK",)
                    )
                    message_box.on_action = self.on_message_button
                    self.manager.add(message_box)
                else:
                    message_box = UIMessageBox(
                        width=300, height=200,
                        message_text="Нехватает монет",
                        buttons=("OK",)
                    )
                    message_box.on_action = self.on_message_button
                    self.manager.add(message_box)

            elif param == 3:
                sp = cur.execute(
                    f"SELECT coins_count, skin FROM leaders WHERE user = '{user_name}'").fetchall()
                if sp[0][0] > 30:
                    skin_db = f"{sp[0][-1]}s3"
                    ost_coin = sp[0][0] - 30
                    cur.execute(
                        f""" UPDATE leaders SET coins_count = {ost_coin}, skin = '{skin_db}' 
                        WHERE user = '{user_name}'""")
                    self.character3_button.text = "Персонаж 2"
                    self.texture_widget.trigger_render()
                    self.shop_button_clicked(param)
                    print("купленно3")
                    message_box = UIMessageBox(
                        width=300, height=200,
                        message_text="Купленно",
                        buttons=("OK",)
                    )
                    message_box.on_action = self.on_message_button
                    self.manager.add(message_box)
                else:
                    message_box = UIMessageBox(
                        width=300, height=200,
                        message_text="Нехватает монет",
                        buttons=("OK",)
                    )
                    message_box.on_action = self.on_message_button
                    self.manager.add(message_box)

        conn.commit()
        conn.close()

    def shop_button_clicked(self, param):
        new_texture = arcade.load_texture(f"assets/shop_foto/{param}.png")
        with open("assets/player.txt", "r", encoding="utf-8") as f:
            user_name = f.readline().strip()
        conn = sqlite3.connect("assets/game.db")
        cur = conn.cursor()
        cur.execute(
            f"""UPDATE leaders SET current_skin = 's{param}' WHERE user = '{user_name}';""")
        conn.commit()
        conn.close()

        self.texture_widget.texture = new_texture
        self.texture_widget.texture_hovered = new_texture
        self.texture_widget.texture_pressed = new_texture
        self.texture_widget.trigger_render()

        # self.character3_button.text = "Персонаж 3"
        # self.texture_widget.trigger_render()
        # self.character2_button.text = "Персонаж 2"
        # self.texture_widget.trigger_render()

    def start_game(self, event):
        self.current_mode = "game"

        self.game_instance = Game()
        self.game_instance.setup()
        self.manager.disable()
        self.manager.clear()

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
        # self.show_main_menu(None)

    # пароль ник
    def login_user(self, input_text1, input_text2):
        self.conn = sqlite3.connect("assets/game.db")
        self.cursor = self.conn.cursor()

        # генерация паролей
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

        sp = self.cursor.execute(f'''SELECT user,
                password
                FROM leaders WHERE user like "{us}"''').fetchall()

        # проверка на наличие аккаунта
        if len(sp) == 0:
            self.show_main_menu(None)
            self.cursor.execute(f'''INSERT INTO leaders (
                                    user,
                                    password
                                )
                                VALUES (
                                '{us}',
                                    '{ps}'
                                );''')
            print(str(us), file=f)
            print(str(ps), file=f)

        elif len(sp) != 0 and sp[0][-1] != ps:
            message_box = UIMessageBox(
                width=300, height=200,
                message_text=f"Неверный пароль",
                buttons=("OK",)
            )
            message_box.on_action = self.on_message_button
            self.manager.add(message_box)
        elif len(sp) != 0 and sp[0][-1] == ps:
            self.show_main_menu(None)
            print(str(us), file=f)
            print(str(ps), file=f)
        # f.close()

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
            text="CrossyWay2D",
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
        shop_button.on_click = self.show_shop
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

    def show_shop(self, event):
        self.shop_menu()

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
        level3_button.on_click = lambda event: self.zapusk_igri(event)
        self.level_layout.add(level3_button)

    def zapusk_igri(self, event):
        self.close()
        time.sleep(0.3)
        from main import main as m
        m()

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

    def sw_layout2(self, new_layout):
        self.anchor_layout2.remove(self.current_layout)

        self.current_layout = new_layout
        self.anchor_layout2.add(self.current_layout)

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
        self.manager.draw()
        arcade.draw_text(
            "CrossyWayAlpha: 0.2",
            10,
            10,
            arcade.color.WHITE,
            10,  # Размер шрифта
            font_name="Arial",
            anchor_x="left",
            anchor_y="bottom"
        )
        # Рисуй GUI поверх всего

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Для кликов, но manager сам обрабатывает


# Запуск
if __name__ == "__main__":
    window = MyGUIWindow()
    arcade.run()
