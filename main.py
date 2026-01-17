import arcade
import math

SCREEN_WIDTH = 1980
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Альфа версия"


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
    textures_right, textures_left = load_textures(
        "assets/car/Green_COUPE_CLEAN_EAST_00", 10
    )

    def __init__(self, point_a, point_b, speed, facing_right):
        super().__init__(speed)

        self.scale = 1
        self.textures_right = NPC.textures_right
        self.textures_left = NPC.textures_left
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
    textures_right, textures_left = load_textures("assets/duck/duck", 7)
    idle_right = arcade.load_texture("assets/duck/duck0.png")
    idle_left = idle_right.flip_left_right()

    def __init__(self, x, y):

        super().__init__(speed=1)
        self.scale = 1
        self.textures_right = Player.textures_right
        self.textures_left = Player.textures_left
        self.texture = Player.idle_right

        self.center_x = x
        self.center_y = y

    def animate(self, delta_time):
        if self.walking:
            super().animate(delta_time)
        else:
            self.texture = Player.idle_right if self.facing_right else Player.idle_left


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.GREEN)

        self.camera = arcade.Camera2D()
        self.camera_speed = 400

        self.camera_shake = arcade.camera.grips.ScreenShake2D(
            self.camera.view_data,
            max_amplitude=15,
            acceleration_duration=0.12,
            falloff_time=0.1,
            shake_frequency=30,
        )

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.npc_list = arcade.SpriteList()

        tile_map = arcade.load_tilemap("assets/maps/city0.tmx", scaling=1.5)

        self.grass_list = tile_map.sprite_lists["grass"]
        self.road_list = tile_map.sprite_lists["road"]
        self.rivers_list = tile_map.sprite_lists["river"]
        self.collisions_list = tile_map.sprite_lists["collisions"]
        self.decorations_list = tile_map.sprite_lists["decorations"]
        self.trees_list = tile_map.sprite_lists["trees"]
        self.player = Player(self.width // 2, self.height // 5)
        self.player_list.append(self.player)

        self.npc_list.extend([
            NPC((3300, 360), (200, 360), 1000, False),
            NPC((250, 325), (3000, 325), 800, True),
            NPC((2800, 420), (250, 420), 600, False),
            NPC((250, 465), (3000, 465), 1200, True),

            NPC((3300, 740), (200, 740), 700, False),
            NPC((250, 705), (3000, 705), 800, True),
            NPC((2800, 800), (250, 800), 900, False),
            NPC((250, 845), (3000, 845), 1000, True)
        ])

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.collisions_list
        )

        self.camera.position = (self.width // 2, self.height // 2)

    def game_over(self):
        print("GAME OVER")
        self.camera_shake.start()
        self.setup()

    def on_draw(self):
        self.clear()
        self.camera_shake.update_camera()
        self.camera.use()

        self.collisions_list.draw()
        self.grass_list.draw()
        self.road_list.draw()
        self.rivers_list.draw()
        self.decorations_list.draw()
        self.trees_list.draw()

        self.player_list.draw()
        self.npc_list.draw()

        self.camera_shake.readjust_camera()

    def on_update(self, delta_time):
        self.player_list.update()
        self.npc_list.update()

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

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, (cam_x, cam_y), 0.12
        )

        # Столкновение с NPC
        if arcade.check_for_collision_with_list(self.player, self.npc_list):
            self.game_over()

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

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0
        elif key in (arcade.key.A, arcade.key.D):
            self.player.change_x = 0
        self.player.walking = False


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
