import sqlite3
import arcade
from arcade.gui import UILabel, UIBoxLayout, UIFlatButton, UIAnchorLayout, UIManager

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Rating(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Рейтинг")
        arcade.set_background_color(arcade.color.SMOKE)

        self.manager = UIManager()
        self.manager.enable()

        self.conn = sqlite3.connect("assets/game.db")
        self.cursor = self.conn.cursor()

        self.anchor = UIAnchorLayout()
        self.main_layout = UIBoxLayout(vertical=True, space_between=10)
        self.anchor.add(self.main_layout)
        self.manager.add(self.anchor)

        self.load_rating_data()

    def load_rating_data(self):
        for child in list(self.main_layout.children):
            self.main_layout.remove(child)

        title = UILabel(
            text="Рейтинг",
            font_size=30,
            text_color=arcade.color.GOLD,
            width=700,
            align="center"
        )
        self.main_layout.add(title)
        self.cursor.execute("SELECT ID, user, coins_count, time_of_game FROM leaders")
        rows = self.cursor.fetchall()
        columns = ['ID,', 'Пользователь,', 'Монеты,', 'Время игры']

        headers_layout = UIBoxLayout(vertical=False, space_between=5)

        for col_name in columns:
            headers_layout.add(UILabel(
                text=col_name, width=150, align="center",
                font_size=16, text_color=arcade.color.CYAN
            ))

        self.main_layout.add(headers_layout)

        for row in rows:
            row_layout = UIBoxLayout(vertical=False, space_between=5)

            for value in row:
                row_layout.add(UILabel(
                    text=str(value),
                    width=150,
                    align="center",
                    font_size=14,
                    text_color=arcade.color.WHITE
                ))

            self.main_layout.add(row_layout)

        close_btn = UIFlatButton(
            text="Закрыть",
            width=200,
            height=40,
            color=arcade.color.RED
        )
        close_btn.on_click = self.close_window
        self.main_layout.add(close_btn)

    def close_window(self, event=None):
        if self.conn:
            self.conn.close()

        self.close()

        from main_menu import MyGUIWindow
        main_window = MyGUIWindow()
        arcade.run()

    def on_draw(self):
        self.clear()
        self.manager.draw()


def main():
    window = Rating()
    arcade.run()


if __name__ == "__main__":
    main()