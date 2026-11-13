
import pygame
from random import randint, choice
import os
import sys

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

# Collision Settings
COLLISION_VISIBLE = False

# (width, height)
SHIP_COLLISION_SIZE = (24, 30)
SHRINK_COLLISION_SIZE = (16, 20)


# Ship Class
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Sprites
        ship_1 = pygame.image.load('Sprites/Ship/ship1.png').convert_alpha()
        ship_2 = pygame.image.load('Sprites/Ship/ship2.png').convert_alpha()

        ship_shrink_1 = pygame.image.load('Sprites/Ship/tinyship.png').convert_alpha()
        ship_shrink_1 = pygame.transform.scale(
            ship_shrink_1,
            (int(ship_shrink_1.get_width() * 1.5),
             int(ship_shrink_1.get_height() * 1.5))
        )

        ship_shrink_2 = pygame.image.load('Sprites/Ship/tinyship2.png').convert_alpha()
        ship_shrink_2 = pygame.transform.scale(
            ship_shrink_2,
            (int(ship_shrink_2.get_width() * 1.5),
             int(ship_shrink_2.get_height() * 1.5))
        )

        self.ship_left = pygame.image.load('Sprites/Ship/shipleft.png').convert_alpha()
        self.ship_right = pygame.image.load('Sprites/Ship/shipright.png').convert_alpha()

        # Animation
        self.ship_shrink_sprites = [ship_shrink_1, ship_shrink_2]
        self.ship_sprites = [ship_1, ship_2]
        self.ship_index = 0

        # Ship Variables
        self.movespeed = 3
        self.image = self.ship_sprites[self.ship_index]
        self.rect = self.image.get_rect(center=(150, 550))
        self.mask = pygame.mask.from_surface(self.image)

        self.is_shrink = False
        self.collision_rect = pygame.Rect(0, 0, 0, 0)

        self.update_collision_mask()

    def update_collision_mask(self):
        """Cria uma máscara de colisão retangular centralizada."""

        if self.is_shrink:
            collision_width, collision_height = SHRINK_COLLISION_SIZE
        else:
            collision_width, collision_height = SHIP_COLLISION_SIZE

        # Impede que a colisão seja maior que o sprite
        collision_width = min(collision_width, self.image.get_width())
        collision_height = min(collision_height, self.image.get_height())

        # Retângulo centralizado no sprite
        self.collision_rect = pygame.Rect(
            0, 0, collision_width, collision_height
        )
        self.collision_rect.center = self.image.get_rect().center

        # Cria uma superfície transparente com apenas o retângulo preenchido
        collision_surface = pygame.Surface(
            self.image.get_size(),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            collision_surface,
            (255, 255, 255, 255),
            self.collision_rect
        )

        self.mask = pygame.mask.from_surface(collision_surface)

    def ship_input(self):
        keys = pygame.key.get_pressed()

        # Controls
        if keys[pygame.K_w]:
            self.rect.y -= self.movespeed
        if keys[pygame.K_s]:
            self.rect.y += self.movespeed
        if keys[pygame.K_a]:
            self.rect.x -= self.movespeed
        if keys[pygame.K_d]:
            self.rect.x += self.movespeed

        # Screen Hitbox
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 300:
            self.rect.right = 300
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 600:
            self.rect.bottom = 600

    def ship_animation(self):
        keys = pygame.key.get_pressed()
        self.movespeed = 3

        # Shrink Ship
        if keys[pygame.K_LSHIFT]:
            self.movespeed = 5
            self.is_shrink = True
            self.ship_index += 0.2

            if self.ship_index >= len(self.ship_sprites):
                self.ship_index = 0

            self.image = self.ship_shrink_sprites[int(self.ship_index)]
            self.rect = self.image.get_rect(center=self.rect.center)

        # Left Animation
        elif keys[pygame.K_a]:
            self.is_shrink = False
            self.image = self.ship_left
            self.rect = self.image.get_rect(center=self.rect.center)

        # Right Animation
        elif keys[pygame.K_d]:
            self.is_shrink = False
            self.image = self.ship_right
            self.rect = self.image.get_rect(center=self.rect.center)

        # Ship Default Animation
        else:
            self.is_shrink = False
            self.ship_index += 0.2

            if self.ship_index >= len(self.ship_sprites):
                self.ship_index = 0

            self.image = self.ship_sprites[int(self.ship_index)]
            self.rect = self.image.get_rect(center=self.rect.center)

        # Atualiza a máscara após qualquer mudança de sprite
        self.update_collision_mask()

    def update(self):
        global playing

        self.ship_input()
        self.ship_animation()

        # Position Reset
        if not playing:
            self.is_shrink = False
            self.image = self.ship_sprites[int(self.ship_index)]
            self.rect = self.image.get_rect(center=(150, 550))
            self.update_collision_mask()


# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # Bullet Variables
        self.image = pygame.image.load('Sprites/Ship/shot.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        destroybrick = pygame.mixer.Sound('Sound Effects and Music/destroy.mp3')

        self.rect.y -= 20
        hit_brick = pygame.sprite.spritecollide(
            self, bricks, True, pygame.sprite.collide_mask
        )

        if self.rect.y < -50:
            self.kill()

        # Bullet and Bricks Interaction
        if hit_brick:
            self.kill()
            destroybrick.play()

            for brick in hit_brick:
                animation.add(Animation('explosion', brick.rect.center))


# Bricks Class
class Brick(pygame.sprite.Sprite):
    def __init__(self, sprite):
        super().__init__()

        # Bricks Sprites Select
        if sprite == 1:
            self.original_image = pygame.image.load('Sprites/Bricks/brick1.png').convert_alpha()
        elif sprite == 2:
            self.original_image = pygame.image.load('Sprites/Bricks/brick2.png').convert_alpha()
        elif sprite == 3:
            self.original_image = pygame.image.load('Sprites/Bricks/brick3.png').convert_alpha()
        elif sprite == 4:
            self.original_image = pygame.image.load('Sprites/Bricks/brick4.png').convert_alpha()
        elif sprite == 5:
            self.original_image = pygame.image.load('Sprites/Bricks/brick5.png').convert_alpha()

        # Bricks Resize
        scale_factor = 1.8
        self.original_image = pygame.transform.scale(
            self.original_image,
            (
                int(self.original_image.get_width() * scale_factor),
                int(self.original_image.get_height() * scale_factor)
            )
        )

        # Bricks Variables
        self.image = self.original_image
        self.rect = self.image.get_rect(
            center=(randint(50, 250), randint(-200, -50))
        )
        self.angle = 0
        self.speed = randint(4, 9)

    def rotate(self):
        self.angle += 1.5

        if self.angle >= 360:
            self.angle = 0

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += self.speed
        self.rotate()

        if self.rect.y > 700:
            self.kill()


# Animations Class
class Animation(pygame.sprite.Sprite):
    def __init__(self, type, pos):
        super().__init__()

        self.frames = []

        # Animation Selection
        if type == 'explosion':
            for i in range(1, 7):
                self.frames.append(
                    pygame.image.load(
                        f'Sprites/Animations/Explosion/explosion{i}.png'
                    ).convert_alpha()
                )

        # Animation Variables
        self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.animation_index += 0.25

        if int(self.animation_index) >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.animation_index)]


# Ship and Bricks Collision
def collision_sprite():
    death = pygame.mixer.Sound('Sound Effects and Music/death.mp3')

    if pygame.sprite.spritecollide(
        ship.sprite, bricks, False, pygame.sprite.collide_mask
    ):
        death.play()
        bricks.empty()
        animation.empty()
        return False

    return True


# Score
def display_score():
    time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render(f'{time}', False, 'WHITE')
    score_rect = score_surf.get_rect(topleft=(120, 10))
    game_surface.blit(score_surf, score_rect)


# Fullscreen Functions
def toggle_fullscreen():
    global screen, fullscreen

    fullscreen = not fullscreen

    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))


def get_game_area():
    """Calcula o tamanho e a posição da área do jogo na tela."""

    screen_width, screen_height = screen.get_size()

    scale = min(
        screen_width / GAME_WIDTH,
        screen_height / GAME_HEIGHT
    )

    new_width = int(GAME_WIDTH * scale)
    new_height = int(GAME_HEIGHT * scale)

    offset_x = (screen_width - new_width) // 2
    offset_y = (screen_height - new_height) // 2

    return scale, new_width, new_height, offset_x, offset_y


def screen_to_game(pos):
    """Converte a posição do mouse para a resolução virtual do jogo."""

    if not fullscreen:
        return pos

    scale, new_width, new_height, offset_x, offset_y = get_game_area()

    mouse_x, mouse_y = pos

    # Ignora cliques nas bordas pretas
    if not (
        offset_x <= mouse_x < offset_x + new_width
        and offset_y <= mouse_y < offset_y + new_height
    ):
        return None

    game_x = int((mouse_x - offset_x) / scale)
    game_y = int((mouse_y - offset_y) / scale)

    return game_x, game_y


def draw_screen():
    """Desenha o jogo mantendo a proporção original."""

    if fullscreen:
        scale, new_width, new_height, offset_x, offset_y = get_game_area()

        scaled_surface = pygame.transform.scale(
            game_surface,
            (new_width, new_height)
        )

        screen.fill('black')
        screen.blit(scaled_surface, (offset_x, offset_y))

    else:
        screen.blit(game_surface, (0, 0))

    pygame.display.update()


# Main Variables and Configs
pygame.init()

# Resolution Settings
GAME_WIDTH = 300
GAME_HEIGHT = 600

fullscreen = False

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

pygame.display.set_caption('Spaceonave')

icon = pygame.image.load('Sprites/Menu and Icon/icon.png').convert_alpha()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
test_font = pygame.font.Font('Font/Pixeltype.ttf', 50)

playing = False
final_score = 0
high_score = 0
start_time = 0
ammo = 3


# Space Ship
ship = pygame.sprite.GroupSingle()
ship.add(Ship())

# Bullets
bullets = pygame.sprite.Group()

# Bricks
bricks = pygame.sprite.Group()

# Animations
animation = pygame.sprite.Group()


# Musics and Sound Effects
laser = pygame.mixer.Sound('Sound Effects and Music/laser.mp3')
play = pygame.mixer.Sound('Sound Effects and Music/play.mp3')
shrink = pygame.mixer.Sound('Sound Effects and Music/shrink.mp3')
background_music = pygame.mixer.Sound('Sound Effects and Music/background.mp3')

background_music.play(loops=-1)


# Background
background = pygame.image.load(
    'Sprites/Backgorunds/Background.png'
).convert_alpha()


# Main Menu
# Title
titlelog = pygame.image.load('Sprites/Menu and Icon/title.png').convert_alpha()

titlelogo = pygame.transform.scale(
    titlelog,
    (titlelog.get_width() * 2, titlelog.get_height() * 2)
)

titlerect = titlelogo.get_rect(center=(150, 150))


# Instructions
howplay1 = test_font.render('Move with WASD', False, 'WHITE')
howplay2 = test_font.render('Shrink with [Shift]', False, 'WHITE')
howplay3 = test_font.render('Shoot with [Space]', False, 'WHITE')

howplay1_rect = howplay1.get_rect(midbottom=(150, 360))
howplay2_rect = howplay2.get_rect(midbottom=(150, 410))
howplay3_rect = howplay3.get_rect(midbottom=(150, 460))


# Play Button
play_sprites = []
play_index = 0

play_sprites.append(
    pygame.image.load('Sprites/Menu and Icon/Play1.png').convert_alpha()
)

play_sprites.append(
    pygame.image.load('Sprites/Menu and Icon/Play2.png').convert_alpha()
)

play_scaled = pygame.transform.scale(
    play_sprites[play_index],
    (
        play_sprites[play_index].get_width() * 4,
        play_sprites[play_index].get_height() * 4
    )
)

playrect = play_scaled.get_rect(center=(150, 530))


# Game Display
# Display Interface
display = pygame.image.load('Sprites/Display/display.png').convert_alpha()
displayrect = display.get_rect(midtop=(150, 0))


# AMMO Meter
ammo_display_list = []

ammo_display_list.append(
    pygame.image.load('Sprites/Display/1bullet.png').convert_alpha()
)

ammo_display_list.append(
    pygame.image.load('Sprites/Display/2bullet.png').convert_alpha()
)

ammo_display_list.append(
    pygame.image.load('Sprites/Display/3bullet.png').convert_alpha()
)

ammodispimage = ammo_display_list[ammo - 1]
ammodisprect = ammodispimage.get_rect(midtop=(150, 0))


# Timers
brick_timer = pygame.USEREVENT + 1
pygame.time.set_timer(brick_timer, 500)

recharge = pygame.USEREVENT + 2
pygame.time.set_timer(recharge, 5000)


# Game Run
while True:

    # Events
    for event in pygame.event.get():

        # Quit Game
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Play Interaction
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = screen_to_game(event.pos)

            if mouse_pos is not None and playrect.collidepoint(mouse_pos):
                play_index = 1
            else:
                play_index = 0

        # Play by Clicking
        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = screen_to_game(event.pos)

            if mouse_pos is not None and playrect.collidepoint(mouse_pos):
                ammo = 3
                play.play()
                ship.update()
                bullets.empty()
                animation.empty()

                start_time = int(pygame.time.get_ticks() / 1000)
                playing = True

        # Keyboard Events
        elif event.type == pygame.KEYDOWN:

            # Toggle Fullscreen with F11
            if event.key == pygame.K_F11:
                toggle_fullscreen()

            # Play by Pressing R
            elif event.key == pygame.K_r and not playing:
                play.play()
                ship.update()
                bullets.empty()
                animation.empty()

                start_time = int(pygame.time.get_ticks() / 1000)
                ammo = 3
                playing = True

        # Gameplay Events
        if playing:

            # Brick Spawner
            if event.type == brick_timer:
                bricks.add(Brick(choice([1, 2, 3, 4, 5])))

            # Bullet Recharge
            if event.type == recharge and ammo < 3:
                ammo += 1

            # Bullet Shoot and Shrink Sound
            if event.type == pygame.KEYDOWN and ammo > 0:

                keys = pygame.key.get_pressed()

                # Bullet Shoot
                if event.key == pygame.K_SPACE and not keys[pygame.K_LSHIFT]:
                    bullets.add(Bullet(ship.sprite.rect.center))
                    laser.play()
                    ammo -= 1

                # Shrink Sound
                if event.key == pygame.K_LSHIFT:
                    shrink.play()

    # Gameplay
    if playing:

        # Background
        game_surface.blit(background, (0, 0))

        # Animations
        animation.draw(game_surface)
        animation.update()

        # Bricks
        bricks.draw(game_surface)
        bricks.update()

        # Bullets
        bullets.draw(game_surface)
        bullets.update()

        # Space Ship
        ship.draw(game_surface)
        ship.update()

        # Collision Visualization
        if COLLISION_VISIBLE:
            collision_rect = ship.sprite.collision_rect.move(
                ship.sprite.rect.topleft
            )

            pygame.draw.rect(
                game_surface,
                'RED',
                collision_rect,
                1
            )

        # Display
        game_surface.blit(display, displayrect)

        # AMMO Display
        if ammo > 0:
            ammodispimage = ammo_display_list[ammo - 1]
            game_surface.blit(ammodispimage, ammodisprect)

        # Score Display
        display_score()

        # Collision Check
        if not collision_sprite():
            final_score = int(pygame.time.get_ticks() / 1000) - start_time
            playing = False

    # Main Menu
    else:

        # Elements
        play_scaled = pygame.transform.scale(
            play_sprites[play_index],
            (
                play_sprites[play_index].get_width() * 4,
                play_sprites[play_index].get_height() * 4
            )
        )

        finalscore_surf = test_font.render(
            f'Final Score: {final_score}', False, 'WHITE'
        )

        finalscore_rect = finalscore_surf.get_rect(midbottom=(150, 360))

        # Background
        game_surface.blit(background, (0, 0))

        # Blits
        game_surface.blit(play_scaled, playrect)
        game_surface.blit(titlelogo, titlerect)

        # Score and Final Score
        if start_time > 0:

            game_surface.blit(finalscore_surf, finalscore_rect)

            if final_score > high_score:
                high_score = final_score

            highlscore_surf = test_font.render(
                f'High Score: {high_score}', False, 'WHITE'
            )

            highscore_rect = highlscore_surf.get_rect(midbottom=(150, 410))

            game_surface.blit(highlscore_surf, highscore_rect)

        # Play Instructions
        else:
            game_surface.blit(howplay1, howplay1_rect)
            game_surface.blit(howplay2, howplay2_rect)
            game_surface.blit(howplay3, howplay3_rect)

    # Draw Final Screen
    draw_screen()

    clock.tick(60)
