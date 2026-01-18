import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel, UIBoxLayout, UIAnchorLayout, UIMessageBox, UIInputText

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyGUIWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Супер GUI Пример!")
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
        # self.current_layout = self.main_layout
        #
        # # Добавляем главное меню
        # self.setup_main_menu()

        self.current_layout = self.user_layout
        self.user_menu()

        self.anchor_layout.add(self.current_layout)  # Добавляем текущий layout в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

    def user_menu(self):
        self.user_layout.clear()

        input_text = UIInputText(x=0, y=0, width=200, height=30, text="Введи имя")
        input_text.on_change = lambda text: print(f"Текст изменился: {text}")
        self.user_layout.add(input_text)

        input_text = UIInputText(x=0, y=0, width=200, height=30, text="Введи пароль")
        input_text.on_change = lambda text: print(f"Текст изменился: {text}")
        self.user_layout.add(input_text)

        button = UIFlatButton(
            text="войти",
            width=200,
            height=50,
            color=arcade.color.BLUE
        )
        button.on_click = lambda event: self.show_main_menu(event)
        self.user_layout.add(button)

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
        settings_button.on_click = self.on_button_click
        self.main_layout.add(settings_button)

        settings_button = UIFlatButton(
            text="Выйти из аккаунта",
            width=200,
            height=50,
            color=arcade.color.BLUE
        )
        settings_button.on_click = self.on_button_click
        self.main_layout.add(settings_button)

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
        # СНАЧАЛА создаем главное меню
        self.setup_main_menu()
        # ПОТОМ переключаем layout
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