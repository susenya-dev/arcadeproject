import sqlite3
import arcade
from arcade.gui import UILabel, UIBoxLayout, UIFlatButton, UIAnchorLayout, UIManager

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def show_rating_in_window(main_window):
    rating_layout = UIBoxLayout(vertical=True, space_between=10)
    load_rating_data(rating_layout, main_window)
    main_window.sw_layout(rating_layout)


def load_rating_data(layout, main_window):
    back_button = UIFlatButton(
        text="Назад в меню",
        width=200,
        height=50,
        color=arcade.color.RED
    )
    back_button.on_click = main_window.show_main_menu
    layout.add(back_button)

    title = UILabel(
        text="Рейтинг",
        font_size=30,
        text_color=arcade.color.GOLD,
        width=700,
        align="center"
    )
    layout.add(title)

    conn = sqlite3.connect("assets/game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ID, user, coins_count, time_of_game FROM leaders")
    rows = cursor.fetchall()
    conn.close()

    columns = ['ID', 'Пользователь', 'Монеты', 'Время игры']

    headers_layout = UIBoxLayout(vertical=False, space_between=5)
    for col_name in columns:
        headers_layout.add(UILabel(
            text=col_name, width=150, align="center",
            font_size=16, text_color=arcade.color.CYAN
        ))
    layout.add(headers_layout)

    if rows:
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
            layout.add(row_layout)
    else:
        no_data = UILabel(
            text="Нет данных",
            font_size=18,
            text_color=arcade.color.WHITE,
            width=400,
            align="center"
        )
        layout.add(no_data)