import math  # эта библиотека для более сложных математических операций
import pyglet  # модуль для визуализации окна и звука, помогает центрировать игровое окно
import arcade  # основная библиотека для создания игры

# Константные значения
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Константы размеров наших спрайтов в отношении к их первоначальному размеру
TILE_SCALING = 0.5
CHARACTER_SCALING = TILE_SCALING * 2

# Константы стрельбы
SPRITE_SCALING_LASER = 0.8
SHOOT_SPEED = 15
BULLET_SPEED = 12
BULLET_DAMAGE = 25

# Константы огня
SPRITE_SCALING_FIRE = 3.2
FIRE_SPEED = 20
FIREBALL_SPEED = 12
FIRE_DAMAGE = 50

# Скорость перемещения игрока, в пикселях на кадр
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 2.3
PLAYER_JUMP_SPEED = 30

# Стартовые координаты игрока на разных уровнях
PLAYER_START_X1 = 2
PLAYER_START_Y1 = 1

PLAYER_START_X2 = 2
PLAYER_START_Y2 = 12

PLAYER_START_X3 = 3
PLAYER_START_Y3 = 14

PLAYER_START_X4 = 10
PLAYER_START_Y4 = 3

# Константы, используемые для отслеживания того, смотрит ли персонаж влево или вправо
RIGHT_FACING = 0
LEFT_FACING = 1

# Слои объектов на карте
LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemies"
LAYER_NAME_BULLETS = "Bullets"
LAYER_NAME_FIRE = "Fire"
LAYER_NAME_DEADFLOOR = "Deadfloor"


def load_texture_pair(filename):  # Функция, которая помогает отзеркаливать изображения персонажей при ходьбе и т.п.
    # Загружаем пару текстур, причем вторая будет зеркальным отображением.
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


# Создаем родительский класс "Сущность", который будет отвечать за классы спрайтов врагов и игрока
class Entity(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        # Устанавливаем обычное расположение лица "вправо"
        self.facing_direction = RIGHT_FACING

        # Используется для создания последовательностей изображений
        self.cur_texture = 0  # Нынешнее положение текстуры
        self.scale = CHARACTER_SCALING

        # Главный путь для загрузки текстур персонажей
        main_path = f"C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/images/animated_characters/{name_folder}/{name_file}"

        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Загружаем текстуры для ходьбы
        self.walk_textures = []
        for i in range(32):  # Проигрываются 32 текстуры (кадра)
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Загружаем текстуры для поднятия по лестнице
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # Устанавливаем исходную текстуру
        self.texture = self.idle_texture_pair[0]

        # Хитбокс будет установлен в зависимости от исходного изображения персонажа
        self.set_hit_box(self.texture.hit_box_points)


# Класс врагов
class Enemy(Entity):
    def __init__(self, name_folder, name_file):

        # Настройка родительского класса
        super().__init__(name_folder, name_file)

        self.should_update_walk = 0
        self.health = 0

    def update_animation(self, delta_time: float = 1 / 60):  # Обновление анимации спрайтов врагов

        # Определяем необходимо ли развернуть персонажа
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # "анимация" стоя на месте
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Анимация передвижения врагов
        if self.should_update_walk == 3:
            self.cur_texture += 1
            if self.cur_texture > 31:  # вплоть до 31 текстуры включительно
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
            self.should_update_walk = 0
            return

        self.should_update_walk += 1


# Класс робота
class RobotEnemy(Enemy):
    def __init__(self):

        # Set up parent class
        super().__init__("robot", "robot")
        self.type = 1
        self.health = 100
        self.enemy_score = 100


# Класс зомби
class ZombieEnemy(Enemy):
    def __init__(self):

        # Set up parent class
        super().__init__("zombie", "zombie")
        self.type = 2
        self.health = 50
        self.enemy_score = 50


# Класс голема
class GolemEnemy(Enemy):
    def __init__(self):

        # Set up parent class
        super().__init__("golem", "golem")
        self.type = 3
        self.health = 200
        self.enemy_score = 200


# Класс вражеского космического корабля
class EnemySpaceShip(Enemy):
    def __init__(self):

        # Настраиваем родительский класс
        super().__init__("enemy_space_ship", "enemy_space_ship")
        self.type = 4
        self.health = 600
        self.enemy_score = 1000


# Класс космического корабля игрока
class PlayerSpaceShip(Entity):

    def __init__(self):

        # Настраиваем родительский класс
        super().__init__("player_space_ship", "player_space_ship")

    def update_animation(self, delta_time: float = 1 / 60):  # Обновление анимации спрайта космического корабля игрока

        # Определяем необходимо ли развернуть персонажа
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # "анимация" стоя на месте
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Анимация передвижения
        self.cur_texture += 1
        if self.cur_texture > 7:  # вплоть до 7 текстуры включительно
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.facing_direction]


# Класс игрока
class PlayerCharacter(Entity):

    def __init__(self):

        # Настраиваем родительский класс
        super().__init__("male_person", "malePerson")

        # Отслеживаем положение нашего спрайта в пространстве
        self.climbing = False
        self.is_on_ladder = False

    def update_animation(self, delta_time: float = 1 / 60):  # Обновление анимации спрайта игрока

        # Определяем необходимо ли развернуть персонажа
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Анимация лазания
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Анимация прыжка
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.facing_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.facing_direction]
            return

        # "анимация" стоя на месте
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Анимация передвижения
        self.cur_texture += 1
        if self.cur_texture > 7:  # Вплоть до 7 текстуры включительно
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.facing_direction]


class MainMenu(arcade.View):

    # Класс, который управляет представлением главного меню.
    def __init__(self):

        super().__init__()

        # Фоновое изображение будет сохранено в этой переменной
        self.background = None

    def on_show_view(self):
        # Функция вызывается при переключении на этот режим просмотра (вид)

        self.background = arcade.load_texture(f"C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/background/background1.jpg")

    def on_draw(self):
        # Прорисовываем главное меню

        # Очищаем окно просмотра
        self.clear()

        # Рисуем текстуру заднего плана
        arcade.draw_lrwh_rectangle_textured(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.background)

        arcade.draw_text("My Platformer Game",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2 + 180,
                         arcade.color.BLACK,
                         font_size=30,
                         anchor_x="center")
        arcade.draw_text("Click on your mouse to Start",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2 + 100,
                         arcade.color.BLACK,
                         font_size=25,
                         anchor_x="center")
        arcade.draw_text("Press Q to Quit",
                         SCREEN_WIDTH - 100,
                         20,
                         arcade.color.WHITE,
                         font_size=14,
                         anchor_x="right")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # Используйте нажатие мыши, чтобы перейти в основное игровое окно
        game_view = GameView()
        self.window.show_view(game_view)

    def on_key_press(self, _key, _modifiers):
        if _key == arcade.key.Q:
            self.window.close()


class GameView(arcade.View):

    # Основной класс приложения (основное игровое окно).

    def __init__(self):
        # Инициализатор для игры

        # Функция super() в Python позволяет наследовать базовые классы (суперклассы или родительские классы)
        # без необходимости явно ссылаться на базовый класс.
        super().__init__()

        # Отслеживание текущего состояния нажатия/отжатия клавиши
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shoot_pressed = False
        self.jump_needs_reset = False

        # Наш объект TileMap
        self.tile_map = None

        # Объект нашей сцены
        self.scene = None

        # Отдельная переменная, содержащая спрайт игрока
        self.player_sprite = None

        # Наш физический движок
        self.physics_engine = None

        # Камера, которую можно использовать для прокрутки экрана - используется для центрирования камеры на игроке
        self.camera = None

        # Камера, которую можно использовать для рисования элементов графического интерфейса пользователя
        self.gui_camera = None

        # Отслеживаем уровень текущей локации
        self.level = 1

        # Должны ли мы сбрасывать счет игрока
        self.reset_score = True

        # Отслеживаем счет игрока
        self.score = 0

        # Должны ли мы сбрасывать счет здоровья игрока
        self.reset_health_score = True

        # Отслеживаем здоровье игрока
        self.health_score = 100

        # Механика выстрелов игрока
        self.can_shoot = False
        self.shoot_timer = 0

        # Механика выстрелов врагов
        self.enemy_can_shoot = False
        self.enemy_shoot_timer = 0

        # Загружаем звуки
        self.collect_coin_sound = arcade.load_sound("C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/sounds/jump1.wav")
        self.game_over = arcade.load_sound("C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/sounds/gameover1.wav")
        self.shoot_sound = arcade.load_sound("C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound("C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/sounds/hit5.wav")

        # Фоновое изображение будет сохранено в этой переменной
        self.background = None

    def setup(self):
        # Настраиваем игру здесь. Также можем вызвать эту функцию, чтобы перезапустить игру с нового уровня.

        # Загружаем фоновое изображение
        self.background = arcade.load_texture(f"C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/background/background{self.level}.jpg")

        # Настраиваем камеры
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        # Имя Tile карты
        map_name = f"C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/tiled_maps/map_{self.level}.json"

        # Параметры, относящиеся к конкретному слою для Titlemap
        # use_spatial_hash – Если установлено значение True, это сделает перемещение спрайта в SpriteList медленнее,
        # но это ускорит обнаружение коллизий с элементами в SpriteList.
        # Отлично подходит для обнаружения столкновений со статичными стенами/платформами.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DEADFLOOR: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
        }

        # Загружаем TileMap
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Создаем новую сцену с помощью нашей Tilemap, которая автоматически добавит все слои
        # Из карты в виде списка спрайтов в сцене в нужном порядке.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Отслеживаем здоровье игрока(и сбрасываем, если это необходимо)
        if self.reset_health_score:
            self.health_score = 100
        self.reset_health_score = True

        # Отслеживаем счет игрока(и сбрасываем, если это необходимо)
        if self.reset_score:
            self.score = 0
        self.reset_score = True

        # Установка механики выстрелов игрока
        self.can_shoot = True
        self.shoot_timer = 0

        # Установка механики выстрелов врагов
        self.enemy_can_shoot = True
        self.enemy_shoot_timer = 0

        # Настроим положение игрока, специально разместив его по этим координатам, в зависимости от уровня локации
        if self.level < 4:
            self.player_sprite = PlayerCharacter()

        if self.level == 4:
            self.player_sprite = PlayerSpaceShip()

        if self.level == 1:
            self.player_sprite.center_x = (
                self.tile_map.tile_width * TILE_SCALING * PLAYER_START_X1
            )
            self.player_sprite.center_y = (
                self.tile_map.tile_height * TILE_SCALING * PLAYER_START_Y1
            )

        if self.level == 2:
            self.player_sprite.center_x = (
                self.tile_map.tile_width * TILE_SCALING * PLAYER_START_X2
            )
            self.player_sprite.center_y = (
                self.tile_map.tile_height * TILE_SCALING * PLAYER_START_Y2
            )

        if self.level == 3:
            self.player_sprite.center_x = (
                self.tile_map.tile_width * TILE_SCALING * PLAYER_START_X3
            )
            self.player_sprite.center_y = (
                self.tile_map.tile_height * TILE_SCALING * PLAYER_START_Y3
            )

        if self.level == 4:
            self.player_sprite.center_x = (
                self.tile_map.tile_width * TILE_SCALING * PLAYER_START_X4
            )
            self.player_sprite.center_y = (
                self.tile_map.tile_height * TILE_SCALING * PLAYER_START_Y4
            )

        # Добавляем спрайт игрока в список спрайтов слоя игрока
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Подготавливаем слой врагов из нашей tile map
        enemies_layer = self.tile_map.object_lists[LAYER_NAME_ENEMIES]

        for my_object in enemies_layer:  # Для объекта тайла в слое врагов tile карты
            # При заданном наборе координат в пиксельных единицах это возвращает декартовы координаты.
            # Предполагается, что указанные координаты являются пиксельными.
            # И декартова сетка строится на основе размера фрагмента карты
            cartesian = self.tile_map.get_cartesian(
                my_object.shape[0], my_object.shape[1]
            )
            enemy_type = my_object.properties["type"]
            if enemy_type == "robot":
                enemy = RobotEnemy()
            if enemy_type == "golem":
                enemy = GolemEnemy()
            if enemy_type == "zombie":
                enemy = ZombieEnemy()
            if enemy_type == "enemy_space_ship":
                enemy = EnemySpaceShip()
            # Выставляем координаты спрайтов наших врагов
            enemy.center_x = math.floor(
                cartesian[0] * TILE_SCALING * self.tile_map.tile_width
            )
            enemy.center_y = math.floor(
                (cartesian[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)
            )
            # Границы движения врагов
            if "boundary_left" in my_object.properties:
                enemy.boundary_left = my_object.properties["boundary_left"]
            if "boundary_right" in my_object.properties:
                enemy.boundary_right = my_object.properties["boundary_right"]
            if "change_x" in my_object.properties:
                enemy.change_x = my_object.properties["change_x"]
            # Добавляем спрайты наших врагов в список спрайтов слоя врагов
            self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)

        # Добавляем в список спрайт листов список с пулями
        self.scene.add_sprite_list(LAYER_NAME_BULLETS)

        # Добавляем в список спрайт листов список с огнем(шарами)
        self.scene.add_sprite_list(LAYER_NAME_FIRE)

        if self.level < 4:
            # Создаем "физический движок" для уровней 1-3
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite,
                platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
                gravity_constant=GRAVITY,
                ladders=self.scene[LAYER_NAME_LADDERS],
                walls=self.scene[LAYER_NAME_PLATFORMS]
            )

        if self.level == 4:
            # Создаем "физический движок" 4 уровня, в нем нет гравитации - это отрытый космос
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite,
                platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
                gravity_constant=0,
                ladders=self.scene[LAYER_NAME_LADDERS],
                walls=self.scene[LAYER_NAME_PLATFORMS]
            )

    def on_show_view(self):
        # Функция для показа вида GameViev, когда его вызывают из MainMenu или GameOver
        # Чтобы сразу подготовить уровень(его логику), с помощью self.setup()
        self.setup()

    def on_draw(self):  # Функция для визуализации игрового окна
        # Визуализация экрана (текущего окна)

        # Очищаем окно просмотра
        self.clear()

        # Рисуем текстуру заднего плана
        arcade.draw_lrwh_rectangle_textured(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.background)

        # Активируем игровую камеру для персонажа
        self.camera.use()

        # Рисуем нашу игровую сцену
        self.scene.draw()

        # Активируйте камеру графического интерфейса пользователя
        # Перед рисованием элементов графического интерфейса пользователя
        self.gui_camera.use()

        score_text = f"Score: {self.score}"

        health_score_text = f"Health: {self.health_score}"

        # Нарисуем наш счет на экране, прокручивая его в окне просмотра
        arcade.draw_text(
            score_text,
            25,
            20,
            arcade.csscolor.WHITE,
            18,
            anchor_x="left"
        )

        # Нарисуем здоровье игрока, прокручивая его в окне просмотра
        arcade.draw_text(
            health_score_text,
            180,
            20,
            arcade.csscolor.RED,
            18,
            anchor_x="left"
        )

        # Нарисуем подсказку для игрока, ведущую его в главное меню
        arcade.draw_text("Press Esc to Quit",
                         SCREEN_WIDTH - 25,
                         20,
                         arcade.csscolor.WHITE,
                         font_size=18,
                         anchor_x="right")

        # Подскажем игроку, как стрелять во врагов
        arcade.draw_text("Press E to Shoot",
                         SCREEN_WIDTH/2,
                         20,
                         arcade.csscolor.WHITE,
                         font_size=18,
                         anchor_x="center")

    def process_keychange(self):
        # Вызывается, когда мы меняем клавишу вверх/вниз, поднимаемся/сходим с лестницы, ходим вправо или влево.

        if self.level < 4:
            # Движение вверх/вниз
            if self.up_pressed and not self.down_pressed:
                if self.physics_engine.is_on_ladder():
                    self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED  # Движение вверх по лестнице
                elif (
                    self.physics_engine.can_jump(y_distance=10)
                    and not self.jump_needs_reset
                ):
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED  # Прыжок
                    self.jump_needs_reset = True
                    arcade.play_sound(self.jump_sound)
            elif self.down_pressed and not self.up_pressed:
                if self.physics_engine.is_on_ladder():
                    self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED  # Движение вниз по лестнице

            # Отсутствие движения персонажа при зажатии обеих клавиш вврех/вниз или бездействия
            if self.physics_engine.is_on_ladder():
                if not self.up_pressed and not self.down_pressed:
                    self.player_sprite.change_y = 0
                elif self.up_pressed and self.down_pressed:
                    self.player_sprite.change_y = 0

        if self.level == 4:

            if self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED  # Движение корабля вверх

            if self.down_pressed and not self.up_pressed:
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED  # Движение корабля вниз

            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Передвижение влево/вправо и остановка (когда нажаты обе клавиши, либо ни одной)
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED  # Движение вправо
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED  # Движение влево
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        # Вызывается, когда игрок нажимает клавишу

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        if key == arcade.key.ESCAPE:
            menu_view = MainMenu()
            self.window.show_view(menu_view)

        if key == arcade.key.E:
            self.shoot_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        # Вызывается, когда игрок отжимает клавишу

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        if key == arcade.key.E:
            self.shoot_pressed = False

        self.process_keychange()

    def center_camera_to_player(self, speed=0.2):  # Фиксация камеры на игроке(его спрайте)
        screen_center_x = self.camera.scale * (self.player_sprite.center_x - (self.camera.viewport_width / 2))
        screen_center_y = self.camera.scale * (self.player_sprite.center_y - (self.camera.viewport_height / 2))
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = (screen_center_x, screen_center_y)

        self.camera.move_to(player_centered, speed)

    def on_update(self, delta_time):
        # Функция, обновляющая спрайты на карте (основном игровом окне), метод вызывается примерно 60 раз в секунду.
        # Она вызывается каждый кадр и позволяет обновлять различные параметры, которые меняются со временем в игре.

        # Передвижение и игровая логика

        # Передвижение игрока в соответствии с физикой игры
        self.physics_engine.update()

        if self.level < 4:
            # Обновление анимаций в зависимости от физики игры
            if self.physics_engine.can_jump():
                self.player_sprite.can_jump = False
            else:
                self.player_sprite.can_jump = True

            if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
                self.player_sprite.is_on_ladder = True
                self.process_keychange()
            else:
                self.player_sprite.is_on_ladder = False
                self.process_keychange()

        # Механика стрельбы игрока
        if self.can_shoot:
            if self.shoot_pressed:
                arcade.play_sound(self.shoot_sound)  # Проигрываем звук выстрела

                if self.level < 4:
                    bullet = arcade.Sprite(
                        "C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/images/space_shooter/laserBlue01.png",
                        SPRITE_SCALING_LASER,
                    )

                if self.level == 4:
                    bullet = arcade.Sprite(
                        "C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/images/space_shooter/laserRed01.png",
                        SPRITE_SCALING_LASER,
                    )

                if self.level < 4:
                    if self.player_sprite.facing_direction == RIGHT_FACING:
                        bullet.change_x = BULLET_SPEED
                        bullet.center_x = self.player_sprite.center_x + 50
                    else:
                        bullet.change_x = -BULLET_SPEED
                        bullet.center_x = self.player_sprite.center_x - 50

                    bullet.center_y = self.player_sprite.center_y

                if self.level == 4:
                    bullet.change_y = BULLET_SPEED
                    bullet.center_y = self.player_sprite.center_y + 50
                    bullet.center_x = self.player_sprite.center_x

                self.scene.add_sprite(LAYER_NAME_BULLETS, bullet)

                self.can_shoot = False
        else:
            self.shoot_timer += 1
            # Условие на скорость стрельбы(чтобы игрок не стрелял слишком быстро)
            if self.shoot_timer == SHOOT_SPEED:
                self.can_shoot = True
                self.shoot_timer = 0

        # Механика стрельбы врагов
        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            if (enemy.type == 1) or (enemy.type == 4):
                if self.enemy_can_shoot:
                    if enemy.type == 4:
                        arcade.play_sound(self.shoot_sound)  # Проигрываем звук выстрела для космического корабля

                    bullet = arcade.Sprite(
                        "C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/images/space_shooter/laserBlue01.png",
                        SPRITE_SCALING_LASER,
                    )
                    if enemy.type == 1:  # Стрельба роботов
                        if enemy.facing_direction == RIGHT_FACING:
                            bullet.change_x = BULLET_SPEED
                            bullet.center_x = enemy.center_x + 50
                        else:
                            bullet.change_x = -BULLET_SPEED
                            bullet.center_x = enemy.center_x - 50

                        bullet.center_y = enemy.center_y

                    if enemy.type == 4:  # Стрельба вражеского космического корабля

                        if enemy.facing_direction == RIGHT_FACING:
                            start_x = enemy.center_x + 65

                        if enemy.facing_direction == LEFT_FACING:
                            start_x = enemy.center_x - 65

                        start_y = enemy.center_y - 100

                        # Укажем конечное местоположение пули
                        dest_x = self.player_sprite.center_x
                        dest_y = self.player_sprite.center_y

                        # Выполним математические вычисления, чтобы рассчитать, как доставить пулю в пункт назначения
                        # Вычислим угол в радианах между начальной точкой и конечной точкой
                        # Это угол, под которым пролетит пуля
                        x_diff = dest_x - start_x
                        y_diff = dest_y - start_y
                        angle = math.atan2(y_diff, x_diff)

                        # Ставим врага лицом к игроку
                        enemy.angle = math.degrees(angle) - 90

                        bullet.center_x = start_x
                        bullet.center_y = start_y

                        # Направляем спрайт пули под углом
                        bullet.angle = math.degrees(angle)

                        # Принимая во внимание угол, вычисляем наши значения change_x и change_y для пули
                        bullet.change_x = math.cos(angle) * BULLET_SPEED
                        bullet.change_y = math.sin(angle) * BULLET_SPEED

                    self.scene.add_sprite(LAYER_NAME_BULLETS, bullet)

                    self.enemy_can_shoot = False
                else:
                    self.enemy_shoot_timer += 1
                    # Условие на скорость стрельбы(чтобы враг не стрелял слишком быстро)
                    if enemy.type == 4:  # Для вражеского космического корабля
                        if self.enemy_shoot_timer == SHOOT_SPEED * 4:
                            self.enemy_can_shoot = True
                            self.enemy_shoot_timer = 0
                    if enemy.type == 1:  # Для роботов
                        if self.enemy_shoot_timer == SHOOT_SPEED * 8:
                            self.enemy_can_shoot = True
                            self.enemy_shoot_timer = 0

        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            if enemy.type == 3:  # Стрельба големов
                if self.enemy_can_shoot:
                    fire = arcade.Sprite(
                        "C:/Users/banic/PycharmProjects/PLATFORMER/assets/resources/images/fire/fire.png",
                        SPRITE_SCALING_FIRE,
                    )

                    if enemy.facing_direction == RIGHT_FACING:
                        fire.change_x = FIREBALL_SPEED
                        fire.center_x = enemy.center_x + 50
                    else:
                        fire.change_x = -FIREBALL_SPEED
                        fire.center_x = enemy.center_x - 50

                    fire.center_y = enemy.center_y - 10

                    self.scene.add_sprite(LAYER_NAME_FIRE, fire)

                    self.enemy_can_shoot = False
                else:
                    self.enemy_shoot_timer += 1
                    # Условие на скорость стрельбы(чтобы враг не стрелял слишком быстро)
                    if self.enemy_shoot_timer == FIRE_SPEED * 8:
                        self.enemy_can_shoot = True
                        self.enemy_shoot_timer = 0

        # Обновляем анимации на карте
        self.scene.update_animation(
            delta_time,
            [
                LAYER_NAME_COINS,
                LAYER_NAME_BACKGROUND,
                LAYER_NAME_PLAYER,
                LAYER_NAME_ENEMIES,
            ],
        )

        # Обновляем двигающиеся платформы, монстров, снаряды на карте
        self.scene.update(
            [LAYER_NAME_MOVING_PLATFORMS, LAYER_NAME_ENEMIES, LAYER_NAME_BULLETS, LAYER_NAME_FIRE]
        )

        # Условие для врагов, когда они дошли до границы своего пути и им необходимо развернуться
        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            if (
                enemy.boundary_right
                and enemy.right > enemy.boundary_right
                and enemy.change_x > 0
            ):
                enemy.change_x *= -1

            if (
                enemy.boundary_left
                and enemy.left < enemy.boundary_left
                and enemy.change_x < 0
            ):
                enemy.change_x *= -1

        # Условия для попадания снарядов пуль по определенной цели (слою объектов)
        for bullet in self.scene[LAYER_NAME_BULLETS]:
            hit_list = arcade.check_for_collision_with_lists(
                bullet,
                [
                    self.scene[LAYER_NAME_PLAYER],
                    self.scene[LAYER_NAME_ENEMIES],
                    self.scene[LAYER_NAME_PLATFORMS],
                    self.scene[LAYER_NAME_DEADFLOOR],
                    self.scene[LAYER_NAME_MOVING_PLATFORMS],
                ],
            )

            if hit_list:
                bullet.remove_from_sprite_lists()

                for collision in hit_list:
                    if (
                        self.scene[LAYER_NAME_ENEMIES]
                        in collision.sprite_lists
                    ):
                        # Столкновение пули с врагом
                        collision.health -= BULLET_DAMAGE

                        if collision.health <= 0:
                            collision.remove_from_sprite_lists()
                            self.score += collision.enemy_score

                            if self.level == 4:
                                game_complete = GameCompleteView()
                                self.window.show_view(game_complete)
                        # Проигрываем звук попадания
                        arcade.play_sound(self.hit_sound)

                    if (
                        self.scene[LAYER_NAME_PLAYER]
                        in collision.sprite_lists
                    ):
                        # Столкновение пули с игроком
                        self.health_score -= BULLET_DAMAGE

                        if self.health_score <= 0:
                            collision.remove_from_sprite_lists()
                            arcade.play_sound(self.game_over)
                            game_over = GameOverView()
                            self.window.show_view(game_over)

                        # Проигрываем звук попадания
                        arcade.play_sound(self.hit_sound)

                return

            if (bullet.right < 0) or (
                bullet.left
                > (self.tile_map.width * self.tile_map.tile_width) * TILE_SCALING
            ):
                bullet.remove_from_sprite_lists()

        # Условия для попадания снарядов огня по определенной цели
        for fire in self.scene[LAYER_NAME_FIRE]:
            hit_list = arcade.check_for_collision_with_lists(
                fire,
                [
                    self.scene[LAYER_NAME_PLAYER],
                    self.scene[LAYER_NAME_PLATFORMS],
                    self.scene[LAYER_NAME_MOVING_PLATFORMS],
                    self.scene[LAYER_NAME_DEADFLOOR],
                ],
            )

            if hit_list:
                fire.remove_from_sprite_lists()

                for collision in hit_list:
                    if (
                        self.scene[LAYER_NAME_PLAYER]
                        in collision.sprite_lists
                    ):
                        # Столкновение огня с игроком
                        self.health_score -= FIRE_DAMAGE

                        if self.health_score <= 0:
                            collision.remove_from_sprite_lists()
                            arcade.play_sound(self.game_over)
                            game_over = GameOverView()
                            self.window.show_view(game_over)

                        # Проигрываем звук попадания
                        arcade.play_sound(self.hit_sound)

                return

            if (fire.right < 0) or (
                fire.left
                > (self.tile_map.width * self.tile_map.tile_width) * TILE_SCALING
            ):
                fire.remove_from_sprite_lists()

        player_collision_list = arcade.check_for_collision_with_lists(
            self.player_sprite,
            [
                self.scene[LAYER_NAME_COINS],
                self.scene[LAYER_NAME_ENEMIES],
                self.scene[LAYER_NAME_DEADFLOOR],
            ],
        )

        # Перебираем каждый подбираемый нами предмет и удаляем его с экрана
        # Также учитываем столкновения персонажа игрока с врагами и смертоносной поверхностью
        for collision in player_collision_list:

            if self.scene[LAYER_NAME_ENEMIES] in collision.sprite_lists:
                arcade.play_sound(self.game_over)
                game_over = GameOverView()
                self.window.show_view(game_over)
                return
            if self.scene[LAYER_NAME_DEADFLOOR] in collision.sprite_lists:
                arcade.play_sound(self.game_over)
                game_over = GameOverView()
                self.window.show_view(game_over)
                return
            else:
                if "next_level1" in collision.properties:
                    nextlevel1 = int(collision.properties["next_level1"])

                    # Переход на следующий уровень(повышение уровня локации)
                    self.level = self.level + nextlevel1

                    # Выключаем сброс очков
                    self.reset_score = False

                    # Выключаем сброс здоровья
                    self.reset_health_score = False

                    # Перезагружаем сцену игрового окна с нового уровня(локации)
                    self.setup()

                if "Healing" in collision.properties:

                    heal = int(collision.properties["Healing"])

                    if self.health_score + heal < 100:
                        self.health_score += heal
                    else:
                        self.health_score = 100

                elif "Points" in collision.properties:
                    points = int(collision.properties["Points"])
                    self.score += points

                # Убираем спрайт подобранного объекта
                collision.remove_from_sprite_lists()
                arcade.play_sound(self.collect_coin_sound)

        # Удерживаем камеру на игроке
        self.center_camera_to_player()


class GameOverView(arcade.View):
    # Меню возрождения

    def on_show_view(self):
        # Вызывается при переключении на этот режим просмотра
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        # Прорисовываем наше окно
        self.clear()
        arcade.draw_text(
            "Game Over - Click on your mouse to restart",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            30,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press Q to Quit",
            SCREEN_WIDTH - 100,
            20,
            arcade.color.WHITE,
            font_size=14,
            anchor_x="right")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # Используйте нажатие мыши, чтобы перейти в основное игровое окно
        game_view = GameView()
        self.window.show_view(game_view)

    def on_key_press(self, _key, _modifiers):
        # Используйте нажатие Q, чтобы выйти из игры
        if _key == arcade.key.Q:
            self.window.close()


class GameCompleteView(arcade.View):
    # Конечное окно (окно полного прохождения игры)

    def on_show_view(self):
        # Вызывается при переключении на этот режим просмотра
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        # Прорисовываем наше окно
        self.clear()
        arcade.draw_text(
            "The game is over, thank you for playing!",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.GREEN,
            30,
            anchor_x="center",
        )

        arcade.draw_text(
            "Click to go to the main menu",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 100,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        arcade.draw_text(
            "Press Q to Quit",
            SCREEN_WIDTH - 100,
            20,
            arcade.color.WHITE,
            font_size=14,
            anchor_x="right")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # Используйте нажатие мыши, чтобы перейти в главное меню
        game_view = MainMenu()
        self.window.show_view(game_view)

    def on_key_press(self, _key, _modifiers):
        # Используйте нажатие Q, чтобы выйти из игры
        if _key == arcade.key.Q:
            self.window.close()


def center_window(self):  # Функция для центрирования окна

    # Получаем параметры экрана отображения с помощью pyglet
    display = pyglet.canvas.Display()
    screen = display.get_default_screen()
    screen_width = screen.width
    screen_height = screen.height

    window_width, window_height = self.get_size()
    # Центрирование окна
    self.set_location((screen_width - window_width) // 2, (screen_height - window_height) // 2)


def main():  # Главная функция запуска игры

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainMenu()
    window.show_view(menu_view)
    window.center_window()
    arcade.run()


if __name__ == "__main__":
    main()
