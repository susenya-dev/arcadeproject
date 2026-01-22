import arcade
from arcade.types import Color
import math
from functools import lru_cache

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Альфа версия"


@lru_cache(maxsize=8)
def load_tilemap_cached(filename: str, scaling: float = 1.0) -> arcade.TileMap:
    return arcade.load_tilemap(filename, scaling=scaling)


def load_textures(path, count):
    right = [arcade.load_texture(f"{path}{i}.png") for i in range(count)]
    left = [t.flip_left_right() for t in right]
    return right, left


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
    # Текстуры загружаются при первом использовании
    _textures_loaded = False
    _textures_right = None
    _textures_left = None

    def __init__(self, point_a, point_b, speed, facing_right):
        super().__init__(speed)

        # Загружаем текстуры если нужно
        if not NPC._textures_loaded:
            NPC._textures_right, NPC._textures_left = load_textures(
                "assets/car/Green_COUPE_CLEAN_EAST_00", 10
            )
            NPC._textures_loaded = True

        self.scale = 1
        self.textures_right = NPC._textures_right
        self.textures_left = NPC._textures_left
        self.texture = self.textures_right[0]

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
        self.camera_speed = 0

        self.fade_alpha = 0
        self.fade_state = 0
        self.fade_speed = 800

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

    def load_level(self, first=False):
        if not first:
            tile_map = self.level_manager.next_level()
        else:
            tile_map = self.level_manager.load_current()

        self.map_height = tile_map.height * tile_map.tile_height
        self.grass_list = tile_map.sprite_lists["grass"]
        # self.road_list = tile_map.sprite_lists["road"]
        self.rivers_list = tile_map.sprite_lists["river"]
        self.collisions_list = tile_map.sprite_lists["collisions"]
        # self.decorations_list = tile_map.sprite_lists["decorations"]
        # self.trees_list = tile_map.sprite_lists["trees"]

        self.npc_list.clear()
        self.npc_list.extend([
            NPC((2000, 360), (-100, 360), 1000, False),
            NPC((10, 705), (3000, 705), 800, True),
            NPC((2800, 800), (10, 800), 900, False),
        ])
        self.log_list.clear()
        self.log_list.extend([
            FloatingLog(400, 1216, 50),
            FloatingLog(0, 1248, 50),
            FloatingLog(400, 1270, 60),
            FloatingLog(800, 1286, 50),
            FloatingLog(400, 1316, 90)
        ])
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

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.grass_list.draw()
        self.coin_list.draw()
        # self.road_list.draw()
        self.rivers_list.draw()
        self.log_list.draw()
        self.collisions_list.draw()
        # self.decorations_list.draw()
        # self.trees_list.draw()

        self.player_list.draw()
        self.npc_list.draw()

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

        # Камера едет вверх
        cam_x, cam_y = self.camera.position
        cam_y += self.camera_speed * delta_time
        if self.player.center_y > cam_y:
            cam_y = self.player.center_y

        if self.player.center_y + 550 < cam_y:
            self.setup()

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, (cam_x, cam_y), 0.12
        )

        # === ПЕРЕХОД НА СЛЕДУЮЩУЮ КАРТУ ===
        if self.player.center_y > self.map_height - 200 and self.fade_state == 0:
            self.fade_state = 1

        if arcade.check_for_collision_with_list(self.player, self.npc_list):
            self.setup()

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
            print("True")

        # if self.player.is_jumping and not logs_hit:
        #     if self.player.center_y < 1200:
        #         self.player.is_jumping = False

        if arcade.check_for_collision_with_list(self.player, self.rivers_list) and self.player.on_ground == False:
            # self.player.on_ground = False
            self.setup()
            print("FALL")

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
