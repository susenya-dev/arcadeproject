import arcade
import math
from functools import lru_cache
import datetime
from pyglet.graphics import Batch
import sqlite3
from random import randint, shuffle, choice

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Альфа версия"

CARS = ["assets/car/green_car/Green_COUPE_CLEAN_EAST_00",
        "assets/car/bus/BUS_CLEAN_EAST_00",
        "assets/car/ambulance/AMBULANCE_CLEAN_EAST_00",
        "assets/car/red_car/Red_JEEP_CLEAN_EAST_00",
        "assets/car/police_car/POLICE_CLEAN_EAST_00",
        "assets/car/yellow_car/Yellow_LUXURY_CLEAN_EAST_00",
        "assets/car/black_car/Black_SUPERCAR_CLEAN_EAST_00"
        ]
NPC_TEXTURE_CACHE = {}


def connect_to_db():
    """Подключается к БД"""
    conn = sqlite3.connect("assets/game.db")
    return conn


def update_balance():
    """Обновляет баланс текущего игрока"""
    with open("assets/player.txt", "r", encoding="utf-8") as f:
        user_name = f.readline().strip()

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE leaders SET coins_count = coins_count + 1 WHERE id = (SELECT id FROM leaders WHERE user = '{user_name}')")
    conn.commit()
    conn.close()


def update_time(current_time):
    """Обновляет баланс текущего игрока"""
    with open("assets/player.txt", "r", encoding="utf-8") as f:
        user_name = f.readline().strip()

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE leaders SET time_of_game = {current_time} WHERE id = (SELECT id FROM leaders WHERE user = '{user_name}') AND {current_time} > time_of_game")
    conn.commit()
    conn.close()
    print(user_name)


@lru_cache(maxsize=8)
def load_tilemap_cached(filename: str, scaling: float = 1.0) -> arcade.TileMap:
    return arcade.load_tilemap(filename, scaling=scaling)


def load_textures(path, count):
    right = [arcade.load_texture(f"{path}{i}.png") for i in range(count)]
    left = [t.flip_left_right() for t in right]
    return right, left


def generate_logs(start_x, end_x, start_y, end_y):
    logs = []
    y = start_y

    while y <= end_y:
        x = randint(start_x, end_x)
        speed = randint(48, 52)
        logs.append(FloatingLog(x, y, speed))
        y += 48
    return logs


def generate_cars(start_y, end_y):
    cars = []
    y = start_y

    while y <= end_y:
        car = choice(CARS)
        point1 = ((-10, y), True)
        point2 = ((1980, y), False)
        points = [point1, point2]
        shuffle(points)
        flag = points[0][1]
        speed = randint(600, 1000)
        cars.append(NPC(point1[0], point2[0], speed, flag, car))
        y += 64

    return cars


class AnimatedSprite(arcade.Sprite):
    def __init__(self, speed=0):
        super().__init__()
        self.speed = speed
        self.frame = 0
        self.time = 0
        self.delay = 0.1
        self.facing_right = True
        self.walking = False

    def animate(self, delta_time):
        if not self.walking:
            return

        self.time += delta_time
        if self.time >= self.delay:
            self.time = 0
            self.frame = (self.frame + 1) % len(self.textures_right)
            self.texture = (
                self.textures_right[self.frame]
                if self.facing_right
                else self.textures_left[self.frame]
            )


class NPC(AnimatedSprite):
    def __init__(self, point_a, point_b, speed, facing_right, texture_path):
        super().__init__(speed)

        if texture_path not in NPC_TEXTURE_CACHE:
            right, left = load_textures(texture_path, 10)
            NPC_TEXTURE_CACHE[texture_path] = (right, left)

        self.textures_right, self.textures_left = NPC_TEXTURE_CACHE[texture_path]

        self.texture = self.textures_right[0]
        self.scale = 1

        self.point_a = point_a
        self.point_b = point_b
        self.target = point_b
        self.facing_right = facing_right
        self.center_x, self.center_y = point_a
        self.walking = True

    def update(self, delta_time):
        dx = self.target[0] - self.center_x
        dy = self.target[1] - self.center_y
        dist = math.hypot(dx, dy)

        if dist < 5:
            self.target = self.point_a if self.target == self.point_b else self.point_b
            return

        self.facing_right = dx > 0
        self.center_x += dx / dist * self.speed * delta_time
        self.center_y += dy / dist * self.speed * delta_time


class Player(AnimatedSprite):
    _textures_loaded = False
    _textures_right = None
    _textures_left = None
    _idle_right = None
    _idle_left = None

    def __init__(self, x, y):
        super().__init__(speed=1)

        if not Player._textures_loaded:
            Player._textures_right, Player._textures_left = load_textures(
                "assets/duck/duck", 7
            )
            Player._idle_right = arcade.load_texture("assets/duck/duck0.png")
            Player._idle_left = Player._idle_right.flip_left_right()
            Player._textures_loaded = True

            # Player._textures_right, Player._textures_left = load_textures(
            #     "assets/pupa/", 4
            # )
            # Player._idle_right = arcade.load_texture("assets/pupa/0.png")
            # self.scale = 2
        self.scale = 1
        self.textures_right = Player._textures_right
        self.textures_left = Player._textures_left
        self.texture = Player._idle_right

        self.jump_speed = 5
        self.on_ground = False
        self.is_jumping = False
        self.center_x = x
        self.center_y = y

    def animate(self, delta_time):
        if self.walking:
            super().animate(delta_time)
        else:
            self.texture = Player._idle_right if self.facing_right else Player._idle_left


class FloatingLog(arcade.Sprite):
    def __init__(self, x, y, speed):
        super().__init__("assets/log.png", scale=0.5)

        self.center_x = x
        self.center_y = y
        self.speed = speed

    def update(self, delta_time):
        self.center_x += self.speed * delta_time

        # если уплыло далеко — возвращаем
        if self.center_x > 3500:
            self.center_x = -200


class Coin(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("assets/coin.png", scale=1)

        self.center_x = x
        self.center_y = y


class LevelManager:
    def __init__(self):
        self.maps = [f"assets/maps/city{i}.tmx" for i in range(2)]
        self.current_level = 0

    def load_current(self):
        return load_tilemap_cached(self.maps[self.current_level], scaling=1)

    def next_level(self):
        self.current_level = (self.current_level + 1) % len(self.maps)
        return self.load_current()


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.types.Color.from_hex_string("#70A853"))
        self.level_manager = LevelManager()
        self.camera = arcade.Camera2D()
        self.wd_cam = arcade.Camera2D()
        self.camera_speed = 500

        self.fade_alpha = 0
        self.fade_state = 0
        self.fade_speed = 800
        self.score = 0

        self.start_time = None
        self.game_time = 0

        self.camera_shake = arcade.camera.grips.ScreenShake2D(
            self.camera.view_data,
            max_amplitude=15,
            acceleration_duration=0.12,
            falloff_time=0.1,
            shake_frequency=30,
        )

    def setup(self):
        self.player_list = arcade.SpriteList(use_spatial_hash=True)
        self.npc_list = arcade.SpriteList(use_spatial_hash=True)
        self.log_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)

        self.load_level(first=True)

        self.player = Player(self.width // 2, self.height // 5)
        self.player_list.append(self.player)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collisions_list
        )

        self.camera.position = (self.width // 2, self.height // 6)

        self.batch = Batch()
        self.start_time = datetime.datetime.now()
        self.game_time = 0

    def load_level(self, first=False):
        if not first:
            tile_map = self.level_manager.next_level()
        else:
            tile_map = self.level_manager.load_current()

        self.map_height = tile_map.height * tile_map.tile_height
        self.grass_list = tile_map.sprite_lists["grass"]
        # self.road_list = tile_map.sprite_lists["road"]
        self.rivers_list = tile_map.sprite_lists["river"]
        self.coastline_list = tile_map.sprite_lists["coastline"]
        self.collisions_list = tile_map.sprite_lists["collisions"]
        # self.decorations_list = tile_map.sprite_lists["decorations"]
        # self.trees_list = tile_map.sprite_lists["trees"]

        self.npc_list.clear()
        self.npc_list.extend([
            NPC((2000, 264), (-100, 264), 1000, False, CARS[0]),
            NPC((2000, 480), (-100, 480), 1000, False, CARS[0]),
            NPC((-100, 544), (2000, 544), 1000, True, CARS[0])
            # NPC((10, 705), (3000, 705), 800, True),
            # NPC((2800, 800), (10, 800), 900, False),
        ])

        self.npc_list.extend(generate_cars(690, 912))
        self.npc_list.extend(generate_cars(1024, 1150))
        self.npc_list.extend(generate_cars(1490, 1730))
        self.log_list.clear()

        # for _ in range(4):
        #     speed = randint(48, 52)
        #     x, y = randint(300, 400), randint(1200, )
        #     FloatingLog()
        # self.log_list.extend([
        #     FloatingLog(400, 1200, 50),
        #     FloatingLog(400, 1248, 50),
        #     FloatingLog(400, 1296, 50),
        #     FloatingLog(420, 1344, 50),
        #
        #     FloatingLog(660, 1200, 55),
        #     FloatingLog(700, 1248, 50),
        #     FloatingLog(750, 1296, 50),
        #     FloatingLog(800, 1344, 50),
        #
        #     FloatingLog(350, 1848, 50),
        #     FloatingLog(350, 1896, 50),
        #     FloatingLog(350, 1944, 50),
        #     FloatingLog(350, 1992, 50),
        #     FloatingLog(350, 2040, 50),
        #     FloatingLog(350, 2088, 50),
        #     FloatingLog(350, 2136, 50),
        #
        # ])

        self.log_list.extend(generate_logs(390, 420, 1200, 1352))
        self.log_list.extend(generate_logs(200, 250, 1200, 1352))
        self.log_list.extend(generate_logs(550, 700, 1200, 1352))

        self.log_list.extend(generate_logs(390, 420, 1848, 2140))
        self.log_list.extend(generate_logs(0, 100, 1848, 2140))
        self.log_list.extend(generate_logs(-260, -250, 1848, 2140))
        self.log_list.extend(generate_logs(-460, -450, 1848, 2140))
        self.log_list.extend(generate_logs(800, 900, 1848, 2140))

        self.coin_list.clear()
        for _ in range(100):
            point1 = arcade.math.rand_in_circle((1920 // 2, 2560 // 2), 2560)
            coin = Coin(point1[0], point1[1])

            self.coin_list.append(coin)

        if hasattr(self, "player"):
            self.player.center_x = self.width // 2
            self.player.center_y = self.height // 5
            self.camera.position = (
                self.player.center_x,
                self.player.center_y
            )
            self.physics_engine = arcade.PhysicsEngineSimple(
                self.player, self.collisions_list
            )

    def game_over(self):
        update_time(round(self.game_time))
        self.game_time = 0
        self.load_level(first=False)
        self.player.center_x = self.width // 2
        self.player.center_y = self.height // 5

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.grass_list.draw()
        self.coin_list.draw()
        # self.road_list.draw()
        self.rivers_list.draw()
        self.coastline_list.draw()
        self.log_list.draw()
        self.collisions_list.draw()

        self.player_list.draw()
        self.npc_list.draw()

        self.wd_cam.use()
        self.batch.draw()

        if self.fade_alpha > 0:
            arcade.draw_lbwh_rectangle_filled(
                0,
                0,
                1000000,
                1000000,
                (0, 0, 0, int(self.fade_alpha))
            )

    def on_update(self, delta_time):
        self.player_list.update()

        self.npc_list.update()
        self.log_list.update(delta_time)
        self.player.animate(delta_time)
        for npc in self.npc_list:
            npc.animate(delta_time)

        self.physics_engine.update()
        self.camera_shake.update(delta_time)

        self.game_time += delta_time

        # Камера едет вверх
        cam_x, cam_y = self.camera.position
        cam_y += self.camera_speed * delta_time
        if self.player.center_y > cam_y:
            cam_y = self.player.center_y

        if self.player.center_y + 550 < cam_y:
            self.game_over()

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, (cam_x, cam_y), 0.12
        )

        chk = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for i in chk:
            i.remove_from_sprite_lists()
            self.score += 1
            update_balance()

        if self.player.center_y > self.map_height - 200 and self.fade_state == 0:
            self.fade_state = 1

        if arcade.check_for_collision_with_list(self.player, self.npc_list):
            self.game_over()

        # self.player.on_ground = False

        logs_hit = arcade.check_for_collision_with_list(
            self.player, self.log_list
        )
        self.player.on_ground = False
        for log in logs_hit:
            # если игрок сверху бревна
            # if self.player.bottom >= log.top - 10:
            # self.player.center_y = log.top + self.player.height / 2
            # self.player.change_y = 0
            # self.player.on_ground = True

            # игрок едет вместе с бревном

            self.player.center_x += log.speed * delta_time
            self.player.on_ground = True
            # print("True")

        # if self.player.is_jumping and not logs_hit:
        #     if self.player.center_y < 1200:
        #         self.player.is_jumping = False

        if arcade.check_for_collision_with_list(self.player, self.rivers_list) and not self.player.on_ground:
            self.load_level(first=False)
            self.player.center_x = self.width // 2
            self.player.center_y = self.height // 5
            # print("FALL")

        if self.fade_state == 1:  # затемнение
            self.fade_alpha += self.fade_speed * delta_time
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.load_level()
                self.fade_state = 2

        elif self.fade_state == 2:  # проявление
            self.fade_alpha -= self.fade_speed * delta_time
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_state = 0

        time_str = f'Time: {int(self.game_time // 60):02d}:{int(self.game_time % 60):02d}'

        self.text = arcade.Text(f'''Score: {self.score}   {time_str}''',
                                10, self.height - 30, arcade.color.WHITE,
                                24, batch=self.batch)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = self.player.speed
            self.player.walking = True
        elif key == arcade.key.S:
            self.player.change_y = -self.player.speed
            self.player.walking = True
        elif key == arcade.key.A:
            self.player.change_x = -self.player.speed
            self.player.facing_right = False
            self.player.walking = True
        elif key == arcade.key.D:
            self.player.change_x = self.player.speed
            self.player.facing_right = True
            self.player.walking = True
        elif key == arcade.key.SPACE:
            self.player.is_jumping = True
            self.player.center_y += 48

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0
        elif key in (arcade.key.A, arcade.key.D):
            self.player.change_x = 0
        self.player.walking = False


def main():
    game = Game()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
