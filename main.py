# importing libraries
import pygame
import random
from pygame import mixer

pygame.font.init()

# Set the width & height of the pygame window
WIDTH, HEIGHT = 500, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

# Game caption
pygame.display.set_caption("Space Invaders Game")

# Initializing the sound and playing the background music
pygame.mixer.init()
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)


# Load images from the pygame module use the "image.load" method to load each of the images
RED_SPACE_SHIP = pygame.image.load("pixel_ship_red_small.png")
GREEN_SPACE_SHIP = pygame.image.load("pixel_ship_green_small.png")
BLUE_SPACE_SHIP = pygame.image.load("pixel_ship_blue_small.png")
# The player's ship
YELLOW_SPACE_SHIP = pygame.image.load("pixel_ship_yellow.png")
# The bullets
RED_LASER = pygame.image.load("pixel_laser_red.png")
GREEN_LASER = pygame.image.load("pixel_laser_green.png")
BLUE_LASER = pygame.image.load("pixel_laser_blue.png")
YELLOW_LASER = pygame.image.load("pixel_laser_yellow.png")

# Loads background image and set size to the height and width previously defined
BG = pygame.transform.scale(pygame.image.load("background-black.png"), (WIDTH, HEIGHT))

class Laser:
 def __init__(self, x, y, img):
  self.x = x
  self.y = y
  self.img = img
  self.mask = pygame.mask.from_surface(self.img)

 def draw(self, window):
  window.blit(self.img, (self.x, self.y))

# Changes the y value of the laser after its shot so that it moves along the screen looking like a bullet
 def move(self, vel):
  self.y += vel

 def off_screen(self, height):
  return not (self.y <= height and self.y >= 0)

 def collision(self, obj):
  return collide(self, obj)


class Ship:
 COOLDOWN = 30

# all the variables that are related to the enemy ship are inside this function
 def __init__(self, x, y, health=100):
  self.x = x
  self.y = y
  self.health = health
  self.ship_img = None
  self.laser_img = None
  self.lasers = []
  self.cool_down_counter = 0

 def draw(self, window):
  window.blit(self.ship_img, (self.x, self.y))
  for laser in self.lasers:
   laser.draw(window)

# when the laser is shot, and it hits the player minus 10 health from 100
 def move_lasers(self, vel, obj):
  self.cooldown()
  for laser in self.lasers:
   laser.move(vel)
   if laser.off_screen(HEIGHT):
    self.lasers.remove(laser)
   elif laser.collision(obj):
    obj.health -= 10
    self.lasers.remove(laser)

# cooldown is the pause that happens after the player shoots a bullet (presses space bar)
 def cooldown(self):
  if self.cool_down_counter >= self.COOLDOWN:
   self.cool_down_counter = 0
  elif self.cool_down_counter > 0:
   self.cool_down_counter += 1

 def shoot(self):
  if self.cool_down_counter == 0:
   laser = Laser(self.x, self.y, self.laser_img)
   self.lasers.append(laser)
   self.cool_down_counter = 1

 def get_width(self):
  return self.ship_img.get_width()

 def get_height(self):
  return self.ship_img.get_height()

# player ship health
class Player(Ship):
 def __init__(self, x, y, health=100):
  super().__init__(x, y, health)
  self.ship_img = YELLOW_SPACE_SHIP
  self.laser_img = YELLOW_LASER
  self.mask = pygame.mask.from_surface(self.ship_img)
  self.max_health = health

# moving the lasers when they're shot
 def move_lasers(self, vel, objs):
  self.cooldown()
  for laser in self.lasers:
   laser.move(vel)
   if laser.off_screen(HEIGHT):
    self.lasers.remove(laser)
   else:
    for obj in objs:
     if laser.collision(obj):
      objs.remove(obj)
      if laser in self.lasers:
       self.lasers.remove(laser)

 def draw(self, window):
  super().draw(window)
  self.healthbar(window)

# displaying and updating the health bar
 def healthbar(self, window):
  pygame.draw.rect(window, (255, 0, 0),
                   (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
  pygame.draw.rect(window, (0, 255, 0), (
  self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
 COLOR_MAP = {
  "red": (RED_SPACE_SHIP, RED_LASER),
  "green": (GREEN_SPACE_SHIP, GREEN_LASER),
  "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
 }

 def __init__(self, x, y, color, health=100):
  super().__init__(x, y, health)
  self.ship_img, self.laser_img = self.COLOR_MAP[color]
  self.mask = pygame.mask.from_surface(self.ship_img)

 def move(self, vel):
  self.y += vel

# automatic shooting from the enemy ships
 def shoot(self):
  if self.cool_down_counter == 0:
   laser = Laser(self.x - 20, self.y, self.laser_img)
   self.lasers.append(laser)
   self.cool_down_counter = 1

# what happens when object on the screen collide
def collide(obj1, obj2):
 offset_x = obj2.x - obj1.x
 offset_y = obj2.y - obj1.y
 return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
 run = True
 FPS = 60
# setting that levels start from 0 and lives start from 5
 level = 0
 lives = 5
# setting the fonts
 main_font = pygame.font.SysFont("comicsans", 30)
 lost_font = pygame.font.SysFont("comicsans", 60)

 enemies = []
 wave_length = 5
 enemy_vel = 1

 player_vel = 5
 laser_vel = 5

# where the player starts off from (spawn place)
 player = Player(300, 630)

 clock = pygame.time.Clock()

 lost = False
 lost_count = 0

# displaying and updating the lives and the level when it changes
 def redraw_window():
  global enemy
  WINDOW.blit(BG, (0, 0))
# draw text - f strings allow for stings to contain variables
  lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
  level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

# location on the screen of the lives label and the level label
  WINDOW.blit(lives_label, (10, 10))
  WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

  for enemy in enemies:
   enemy.draw(WINDOW)
  player.draw(WINDOW)

# The "you lost!" screen
  if lost:
   lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
   WINDOW.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

  pygame.display.update()

# The FPS of the game - also how fast every thing updates according to the keyboard input
 while run:
  clock.tick(FPS)
  redraw_window()

# what happens if the person dies (health wise) or looses all 5 lives --> the game ends
  if lives <= 0 or player.health <= 0:
   lost = True
   lost_count += 1

# if the person loose a life then slow down the game and make it easier for them
  if lost:
   if lost_count > FPS * 3:
    run = False
   else:
    continue

# generate enemy ships at random and of random colour choice (from the choices below)
  if len(enemies) == 0:
   level += 1
   wave_length += 5
   for i in range(wave_length):
    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                  random.choice(["red", "blue", "green"]))
    enemies.append(enemy)

  for event in pygame.event.get():
   if event.type == pygame.QUIT:
    quit()

  keys = pygame.key.get_pressed()

# keys that are used to play the game (Arrow Keys)
  if keys[pygame.K_LEFT] and player.x - player_vel > 0:  # left
   player.x -= player_vel

  if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:  # right
   player.x += player_vel

  if keys[pygame.K_UP] and player.y - player_vel > 0:  # up
   player.y -= player_vel

  if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
   player.y += player_vel

  if keys[pygame.K_SPACE]:
   player.shoot()  # shoot bullet
   bulletSound = mixer.Sound("shoot.mp3")
   bulletSound.play()

  for enemy in enemies[:]:
   enemy.move(enemy_vel)
   enemy.move_lasers(laser_vel, player)

   if random.randrange(0, 2 * 60) == 1:
    enemy.shoot()

# remove health from player if it collides with other ships and minus health from the enemy ship that was collided into
   if collide(enemy, player):
    player.health -= 10
    enemies.remove(enemy)
   elif enemy.y + enemy.get_height() > HEIGHT:
    lives -= 1
    enemies.remove(enemy)
  player.move_lasers(-laser_vel, enemies)

# starting page
def main_menu():
 title_font = pygame.font.SysFont("comicsans", 50)
 run = True
 while run:
  WINDOW.blit(BG, (0, 0))
  title_label = title_font.render("Click to begin...", 1, (255, 255, 255))
  WINDOW.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
  pygame.display.update()
  for event in pygame.event.get():
   if event.type == pygame.QUIT:
    run = False

# how the game begins (mouse/trackpad is clicked)
   if event.type == pygame.MOUSEBUTTONDOWN:
    main()
    pygame.quit()


main_menu()
