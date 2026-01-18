import arcade
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox  # Это разные виджеты
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout  # А это менеджеры компоновки, как в pyQT

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyGUIWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Супер GUI Пример!")
        arcade.set_background_color(arcade.color.GRAY)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

    def on_button_click(self, button_text):
        message_box = UIMessageBox(
            width=300, height=200,
            message_text="Это UIMessageBox!\nХочешь продолжить?",
            buttons=("Да", "Нет")
        )
        message_box.on_action = self.on_message_button
        self.manager.add(message_box)

    def setup_widgets(self):

        input_text = UIInputText(x=0, y=0, width=200, height=30, text="Введи имя")
        input_text.on_change = lambda text: print(f"Текст изменился: {text}")
        self.box_layout.add(input_text)

    def on_message_button(self, event):
        print(f"Диалог: {event}")

    def on_draw(self):
        self.clear()
        self.manager.draw()  # Рисуй GUI поверх всего

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Для кликов, но manager сам обрабатывает


# Запуск
window = MyGUIWindow()
arcade.run()