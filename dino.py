import sys
import pygame
import os
import random
import math

WIDTH = 623
HEIGHT = 150

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino")

class Dino:

    def __init__(self):
        self.width = 44
        self.height = 44
        self.x = 10
        self.y = 80
        self.texture_num = 0
        self.jump_height = 3
        self.gravity = 1.2
        self.onground = True
        self.jumping = False
        self.jump_stop = 10
        self.falling = False
        self.fall_stop = self.y
        self.set_texture()
        self.set_sound()
        self.show()

    def update(self, loops):
        # jumping
        if self.jumping:
            self.y -= self.jump_height
            if self.y <= self.jump_stop:
                self.set_falling()

        # falling
        elif self.falling:
            self.y += self.gravity * self.jump_height
            if self.y >= self.fall_stop:
                self.set_onground()

        # walking
        # speed of dino move (image)
        elif self.onground and loops % 4 == 0:
            # can switch between 3 different dino png file
            self.texture_num = (self.texture_num + 1) % 3
            self.set_texture()

    def show(self):
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join(f"assets/images/dino{self.texture_num}.png")
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

    def set_sound(self):
        path = os.path.join(f"assets/sounds/jump.wav")
        self.sound = pygame.mixer.Sound(path)

    def set_jumping(self):
        self.sound.play()
        self.jumping = True
        self.onground = False

    def set_falling(self):
        self.jumping = False
        self.falling = True

    def set_onground(self):
        self.falling = False
        self.onground = True

class Cactus:

    def __init__(self, x):
        self.width = 34
        self.height = 44
        self.x = x
        self.y = 80
        self.set_texture()
        self.show()

    def update(self, dis):
        self.x += dis

    def show(self):
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join("assets/images/cactus.png")
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

class Background:

    def __init__(self, x):
        self.width = WIDTH
        self.height = HEIGHT
        self.x = x
        self.y = 0
        self.set_texture()
        self.show()

    def update(self, speed):
        self.x += speed
        # is the background outside the screen
        if self.x <= -WIDTH:
            self.x = WIDTH

    def show(self):
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join("assets/images/bg.png")
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

class Collision:

    def between(self, obj1, obj2):
        distance = math.sqrt((obj1.x-obj2.x)**2 + (obj1.y-obj2.y)**2)
        return distance < 35

class Score:

    def __init__(self, high_score):
        self.high_score = high_score
        self.actual = 0
        self.font = pygame.font.SysFont('monospace', 18)
        self.color = (0,0,0)
        self.set_sound()
        self.show()

    def update(self, loops):
        self.actual = loops // 10
        self.check_highscore()
        self.check_sound()

    def show(self):
        self.label = self.font.render(f"HI {self.high_score} {self.actual}", 1, self.color)
        label_width = self.label.get_rect().width
        screen.blit(self.label, (WIDTH - label_width - 10, 10))

    def check_highscore(self):
        if self.actual >= self.high_score:
            self.high_score = self.actual

    def set_sound(self):
        path = os.path.join(f'assets/sounds/point.wav')
        self.sound = pygame.mixer.Sound(path)

    def check_sound(self):
        if self.actual % 100 == 0 and self.actual != 0:
            self.sound.play()

class Game:

    def __init__(self, high_score=0):
        # need at least two backgrounds
        self.background = [Background(0), Background(WIDTH)]
        self.dino = Dino()
        self.obstacles = []
        self.collision = Collision()
        self.score = Score(high_score)
        self.speed = 3
        self.playing = False
        self.set_sound()
        self.set_labels()
        self.spawn_cactus()

    def set_labels(self):
        big_font = pygame.font.SysFont("monospace", 24, bold=True)
        small_font = pygame.font.SysFont("monospace", 18)
        self.big_label = big_font.render(f'G A M E  O V E R', 1, (0,0,0))
        self.small_label = small_font.render(f'press r to restart', 1, (0,0,0))

    def set_sound(self):
        path = os.path.join(f'assets/sounds/die.wav')
        self.sound = pygame.mixer.Sound(path)

    def start(self):
        self.playing = True

    def over(self):
        self.sound.play()
        screen.blit(self.big_label, (WIDTH // 2 - self.big_label.get_width() // 2, HEIGHT // 4))
        screen.blit(self.small_label, (WIDTH // 2 - self.small_label.get_width() // 2, HEIGHT // 2))
        self.playing = False

    def tospawn(self, loops):
        return loops % 80 == 0

    def spawn_cactus(self):
        if len(self.obstacles) > 0:
            prev_cactus = self.obstacles[-1]
            x = random.randint(prev_cactus.x + self.dino.width + 84, WIDTH + prev_cactus.x + self.dino.width + 84)
        # empty list, initial condition
        else:
            x = random.randint(WIDTH + 100, 900)

        # create new cactus
        cactus = Cactus(x)
        self.obstacles.append(cactus)

    def restart(self):
        self.__init__(self.score.high_score)


def main():
    game = Game()
    dino = game.dino
    over = False
    clock = pygame.time.Clock()
    loops = 0

    while True:

        if game.playing:
            loops += 1

            # background
            for background in game.background:
                background.update(-game.speed)
                background.show()

            # dino
            dino.update(loops)
            dino.show()

            # cactus
            if game.tospawn(loops):
                game.spawn_cactus()

            for cactus in game.obstacles:
                cactus.update(-game.speed)
                cactus.show()

                # collision
                if game.collision.between(dino, cactus):
                    over = True
                
            if over:
                game.over()

            # score
            game.score.update(loops)
            game.score.show()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not over:
                        if dino.onground:
                            dino.set_jumping()

                        if not game.playing:
                            game.start()

                # restart
                if event.key == pygame.K_r:
                    game.restart()
                    dino = game.dino
                    loops = 0
                    over = False

        clock.tick(80)
        pygame.display.update()

main()
