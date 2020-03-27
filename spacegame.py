import pygame, math, sys, random, pickle, os.path

SCREEN_X, SCREEN_Y = 1000, 1000
score = 0
highscore = 0

game_running = False

class Ship(pygame.sprite.Sprite):

    def __init__(self, shipImages):
        pygame.sprite.Sprite.__init__(self)
        self.images = shipImages

        self.max_lives = 10
        self.max_base_lives = 5

        self.lives = self.max_lives
        self.base_lives = self.max_base_lives

        self.damage_value = 1
        self.speed = 7

        self.laser_pic = "./resources/laserGreen.png"
        # all ship lasers
        self.lasers = []

        self.cooldown = 0

        self.shoot = False
        
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.images[self.index].get_rect()

        self.hearts = []
        for i in range(0, self.lives):
            self.hearts.append(Heart(10+(32*i), 10, "./resources/heartFullRed.png"))
            
        self.base_hearts = []
        for i in range(0, self.base_lives):
            self.base_hearts.append(Heart(10+(32*i), 10+32, "./resources/heartFullYellow.png"))
        

        self.rect.centerx = math.floor(SCREEN_X/2)
        self.rect.y = SCREEN_Y - self.rect.height - 40

        self.fly_left, self.fly_right = 0,0
        self.fly_up, self.fly_down = 0,0

    def reset(self):
        self.lives = self.max_lives
        self.base_lives = self.max_base_lives

        self.lasers = []

        self.cooldown = 0

        self.shoot = False
        
        self.hearts = []

        for i in range(0, self.lives):
            self.hearts.append(Heart(10+(32*i), 10, "./resources/heartFullRed.png"))
            
        self.base_hearts = []
        for i in range(0, self.base_lives):
            self.base_hearts.append(Heart(10+(32*i), 10+32, "./resources/heartFullYellow.png"))

        self.rect.centerx = math.floor(SCREEN_X/2)
        self.rect.y = SCREEN_Y - self.rect.height - 40

        self.fly_left, self.fly_right = 0,0
        self.fly_up, self.fly_down = 0,0

    def damage(self, damage=1):
        for i in range(self.lives-1, max(self.lives-damage-1, 0), -1):
            self.hearts[i].empty()
        
        self.lives -= damage

        if self.lives <= 0:
            pygame.event.post(gameover_event)

    def heal(self, heal=1):
        for i in range(self.lives, min(self.lives+heal, self.max_lives)):
            self.hearts[i].full()
        
        self.lives += heal
        
        if self.lives > self.max_lives:
            self.lives = self.max_lives

    def damage_base(self, damage=1):
        for i in range(self.base_lives-1, max(self.base_lives - damage - 1, 0), -1):
            self.base_hearts[i].empty()
        
        self.base_lives -= damage

        if self.base_lives <= 0:
            pygame.event.post(gameover_event)

    def heal_base(self, heal=1):
        for i in range(self.base_lives, min(self.base_lives+heal, self.max_base_lives)):
            self.base_hearts[i].full()
        
        self.base_lives += heal
        if self.base_lives > self.max_base_lives:
            self.base_lives = self.max_base_lives

    def update(self):
        self.image = self.images[math.floor(self.index)]
        self.index += 0.05
        if self.index > len(self.images):
            self.index = 0

        self.cooldown -= 1
        if self.cooldown < 0:
            self.cooldown = 0

        self.rect.x -= self.fly_left
        self.rect.x += self.fly_right

        self.rect.y -= self.fly_up
        self.rect.y += self.fly_down

        if self.rect.x + self.rect.width > SCREEN_X:
            self.rect.x = SCREEN_X - self.rect.width
        elif self.rect.x < 0:
            self.rect.x = 0

        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y + self.rect.height > SCREEN_Y:
            self.rect.y = SCREEN_Y - self.rect.height

        if self.shoot and self.cooldown == 0:
            self.lasers.append(Laser(self.rect.x+5, self.rect.y, self))
            self.lasers.append(Laser(self.rect.x+self.rect.width-5, self.rect.y, self))
            self.cooldown = 15

class Heart(pygame.sprite.Sprite):

    def __init__(self, x, y, heartImage):
        pygame.sprite.Sprite.__init__(self)
        
        self.full_heart = pygame.image.load(heartImage)
        self.empty_heart = pygame.image.load("./resources/heartEmpty.png")

        self.image = self.full_heart
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        
    def full(self):
        self.image = self.full_heart
    
    def empty(self):
        self.image = self.empty_heart

class Laser(pygame.sprite.Sprite):

    def __init__(self, xcenter, ycenter, origin):
        super(Laser, self)
        self.origin = origin
        self.image = pygame.image.load(origin.laser_pic)
        self.rect = self.image.get_rect()

        self.rect.centerx = xcenter
        self.rect.centery = ycenter - self.rect.height

    def update(self, enemies):
        # laser was sent by the ship
        if isinstance(self.origin, Ship):
            self.rect.centery -= 6
            if self.rect.y < - self.rect.height:
                return True
            else:
                for enemy in enemies:    
                    if self.rect.colliderect(enemy.rect):
                        enemy.damage(damage=ship.damage_value)
                        return True
                return False
        else:
            # laser was sent by an alien
            self.rect.centery += 6
            if self.rect.y > SCREEN_Y: # laser hit the base
                return True
            else: # laser did not yet hit the base
                for enemy in enemies:    
                    if self.rect.colliderect(enemy.rect):
                        enemy.damage(self.origin.damage_value)
                        return True
                return False

class Star(pygame.sprite.Sprite):

    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.image.load("./resources/star.png")
        self.rect = self.image.get_rect()

        self.rect.x = random.randrange(0, SCREEN_X-self.rect.width)
        self.rect.centery = random.randrange(0, SCREEN_Y-self.rect.height)
        self.buffer_y = self.rect.centery

        self.speed = 0.8

    def update(self):
        global game_running
    
        self.buffer_y += self.speed
        self.rect.centery = int(self.buffer_y)
        
        if self.rect.y > SCREEN_Y:
            self.rect.y = -self.rect.height
            self.buffer_y = self.rect.y
            self.rect.x = random.randrange(0, SCREEN_X-self.rect.width)

class Alien(pygame.sprite.Sprite):
    def __init__(self, config: dict):
        required_attrs = set(["type","group", "images", "laser_pic", "lives", "lasers", "score_increase", "speed", "score_decrease", "max_cooldown", "damage_value"])

        if required_attrs <= set(config.keys()):
            for key, value in config.items():
                setattr(self, key, value)

        pygame.sprite.Sprite.__init__(self, self.group)
        
        self.cooldown = 0
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.images[self.index].get_rect()
        
        self.rect.x = random.randrange(0,SCREEN_X-self.rect.width)
        self.rect.y = -self.rect.height
        self.buffer_y = self.rect.y

    def update(self):
        global score, ship

        self.animate()
        
        alive = self.move()
        if not alive:
            return

        self.act()

    def act(self):
        raise NotImplementedError()

    def animate(self):
        self.image = self.images[math.floor(self.index)]
        self.index += 0.05
        if self.index > len(self.images):
            self.index = 0
    
    def move(self):
        global ship, score
        self.buffer_y += self.speed
        self.rect.y = int(self.buffer_y)

        if self.rect.y > SCREEN_Y:
            self.kill()
            ship.damage_base(damage=self.damage_value)
            score -= self.score_decrease
            return False
        
        self.cooldown -= 1
        if self.cooldown < 0:
            self.cooldown = 0
        return True

    def damage(self, damage=1):
        global score
        self.lives -= damage
        if self.lives == 0:
            self.kill()
            score += self.score_increase

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, config: dict):
        required_attrs = set(["type","group", "images", "lives", "score_increase", "speed", "score_decrease", "damage_cooldown", "damage_value"])

        if required_attrs <= set(config.keys()):
            for key, value in config.items():
                setattr(self, key, value)

        pygame.sprite.Sprite.__init__(self, self.group)

        self.cooldown = 0
        
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.images[self.index].get_rect()
        
        self.rect.x = random.randrange(0,SCREEN_X-self.rect.width)
        self.rect.y = -self.rect.height
        self.buffer_y = self.rect.y

    def update(self):
        global score, ship

        self.animate()
        
        self.move()

    def animate(self):
        self.image = self.images[math.floor(self.index)]
        self.index += 0.05
        if self.index > len(self.images):
            self.index = 0
    
    def move(self):
        global ship, score
        
        self.buffer_y += self.speed
        self.rect.y = int(self.buffer_y)

        self.cooldown -= 1
        if self.cooldown < 0:
            self.cooldown = 0
            
        if self.rect.y > SCREEN_Y:
            self.kill()
            ship.damage_base(damage=self.damage_value)
            score -= self.score_decrease
            return False

        if self.rect.colliderect(ship.rect) and self.cooldown == 0:
            self.damage(damage=ship.damage_value)
            ship.damage(damage=self.damage_value)
            self.cooldown = self.damage_cooldown
            return False
        
        return True

    def damage(self, damage=1):
        global score
        self.lives -= damage
        if self.lives == 0:
            self.kill()
            score += self.score_increase

class D_Alien(Alien):
    def __init__(self, group, laserlist):
        super().__init__({
            "type": "Default",
            "group": group,
            "images": [pygame.image.load("./resources/alienFrame1.png"), pygame.image.load("./resources/alienFrame2.png")],
            "laser_pic": "./resources/laserPurple.png",
            "lives": 5,
            "lasers": laserlist,
            "score_increase": 25,
            "speed": 1.2,
            "score_decrease": 50,
            "max_cooldown": 15,
            "damage_value": 1
        })
    
    def act(self):
        if random.random() < 0.01 and self.cooldown == 0:
            self.lasers.append(Laser(self.rect.centerx, self.rect.centery + self.rect.height, self))
            self.cooldown = self.max_cooldown

class W_Alien(Alien):
    def __init__(self, group, laserlist):
        super().__init__({
            "type": "W_Alien",
            "group": group,
            "images": [pygame.image.load("./resources/weirdAl1.png"), pygame.image.load("./resources/weirdAl2.png")],
            "laser_pic": "./resources/circleLaser.png",
            "lives": 13,
            "lasers": laserlist,
            "score_increase": 50,
            "speed": 1.8,
            "score_decrease": 100,
            "max_cooldown": 15,
            "damage_value": 2
        })
    
    def act(self):
        if random.random() < 0.01 and self.cooldown == 0:
            self.lasers.append(Laser(self.rect.centerx, self.rect.centery + self.rect.height, self))
            self.cooldown = self.max_cooldown

class RedHeartAlien(Alien):
    def __init__(self, group, laserlist):
        super().__init__({
            "type": "RedHeartAlien",
            "group": group,
            "images": [pygame.image.load("./resources/redHeartShip1.png"), pygame.image.load("./resources/redHeartShip2.png")],
            "laser_pic": "./resources/redLaser.png",
            "lives": 7,
            "lasers": laserlist,
            "score_increase": 100,
            "speed": 1.8,
            "score_decrease": 200,
            "max_cooldown": 15,
            "damage_value": 2
        })
    
    def act(self):
        if random.random() < 0.01 and self.cooldown == 0:
            self.lasers.append(Laser(self.rect.centerx, self.rect.centery + self.rect.height, self))
            self.cooldown = self.max_cooldown
    
    def damage(self, damage=1):
        global score
        self.lives -= damage
        if self.lives == 0:
            self.kill()
            ship.heal()
            score += self.score_increase

class YellowHeartAlien(Alien):
    def __init__(self, group, laserlist):
        super().__init__({
            "type": "YellowHeartAlien",
            "group": group,
            "images": [pygame.image.load("./resources/yellowHeartShip1.png"), pygame.image.load("./resources/yellowHeartShip2.png")],
            "laser_pic": "./resources/yellowLaser.png",
            "lives": 7,
            "lasers": laserlist,
            "score_increase": 100,
            "speed": 1.8,
            "score_decrease": 200,
            "max_cooldown": 15,
            "damage_value": 2
        })
    
    def act(self):
        if random.random() < 0.01 and self.cooldown == 0:
            self.lasers.append(Laser(self.rect.centerx, self.rect.centery + self.rect.height, self))
            self.cooldown = self.max_cooldown
    
    def damage(self, damage=1):
        global score
        self.lives -= damage
        if self.lives == 0:
            self.kill()
            ship.heal_base()
            score += self.score_increase
    
class Asteroid(Obstacle):
    def __init__(self, group):
        super().__init__({
            "type": "Asteroid",
            "group": group,
            "images": [pygame.image.load("./resources/asteroid_big.png")],
            "lives": 40,
            "score_increase": 40,
            "speed": 1,
            "score_decrease": 100,
            "damage_cooldown": 100,
            "damage_value": 2
        })

class MiniAsteroid(Obstacle):
    def __init__(self, group):
        super().__init__({
            "type": "MiniAsteroid",
            "group": group,
            "images": [pygame.image.load("./resources/asteroid_2.png")],
            "lives": 1,
            "score_increase": 10,
            "speed": 3,
            "score_decrease": 20,
            "damage_cooldown": 100,
            "damage_value": 1
        })

def main():
    global ship, clock, screen, stars, font, GAMEOVER, gameover_event, highscore, s_font
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_X,SCREEN_Y))

    pygame.display.set_caption("Spacegame")

    clock = pygame.time.Clock()

    ship = Ship([pygame.image.load("./resources/shipFrame1.png"), pygame.image.load("./resources/shipFrame2.png")])

    stars = pygame.sprite.Group()
    
    font = pygame.font.Font("./resources/monobit.ttf", 80)
    s_font = pygame.font.Font("./resources/monobit.ttf", 50)
    
    for _ in range(0,20):
        Star(stars)

    GAMEOVER = pygame.USEREVENT + 1
    gameover_event = pygame.event.Event(GAMEOVER)

    highscore = load_highscore()

    while True:
        homescreen()

        start_game()

def homescreen():
    running = True
    
    global game_running
    game_running = False

    logo_img = pygame.image.load("./resources/logo.png")
    logo_rect = logo_img.get_rect()
    logo_rect.centerx = int(SCREEN_X / 2)
    logo_rect.centery = int(SCREEN_Y / 3)

    while running:
        clock.tick(60)
        screen.fill((0, 3, 47))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False
                    break
            if event.type == pygame.QUIT:
                save_highscore()
                pygame.quit()
                sys.exit(0)
        
        stars.update()
        stars.draw(screen)

        screen.blit(logo_img, logo_rect)
        screen.blit(ship.image, ship.rect)

        start_text = "Press SPACE to start..."
        text = font.render(start_text, True, (200,200,200))
        screen.blit(text, (int(SCREEN_X / 2 - font.size(start_text)[0] / 2), logo_rect.centery + 90))

        highscore_text = "Highscore: " + str(highscore)
        text = s_font.render(highscore_text, True, (200,200,200))
        screen.blit(text, (5,0))

        score_text = "Score: " + str(score)
        text = s_font.render(score_text, True, (200,200,200))
        screen.blit(text, (5,s_font.size(highscore_text)[1]-4))

        pygame.display.flip()

def start_game():
    global start_time, score, game_running

    start_time = pygame.time.get_ticks()
    game_running = True

    running = True

    score = 0
    # all enemy lasers
    lasers = []
    aliens = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    while running:
        clock.tick(60)
        screen.fill((0, 3, 47))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_highscore()
                pygame.quit()
                sys.exit(0)
            
            if event.type == GAMEOVER:
                reset()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    ship.fly_left = ship.speed
                if event.key == pygame.K_RIGHT:
                    ship.fly_right = ship.speed
                if event.key == pygame.K_UP:
                    ship.fly_up = ship.speed
                if event.key == pygame.K_DOWN:
                    ship.fly_down = ship.speed
                if event.key == pygame.K_SPACE:
                    ship.shoot = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    ship.fly_left = 0
                if event.key == pygame.K_RIGHT:
                    ship.fly_right = 0
                if event.key == pygame.K_UP:
                    ship.fly_up = 0
                if event.key == pygame.K_DOWN:
                    ship.fly_down = 0
                if event.key == pygame.K_SPACE:
                    ship.shoot = False

        #### SPAWNING

        max_aliens = int(int(get_time()/1000)/20)+1
        max_obstacles = int(int(get_time()/1000)/30)+1

        if max_aliens > 20:
            max_aliens = 20
        if max_obstacles > 8:
            max_obstacles = 8
        

        if len(aliens)<max_aliens and random.random() < 0.009:
            D_Alien(aliens, lasers)

        if len(aliens)<max_aliens and random.random() < 0.005:
            W_Alien(aliens, lasers)

        if len(aliens)<max_aliens and random.random() < 0.0005:
            RedHeartAlien(aliens, lasers)

        if len(aliens)<max_aliens and random.random() < 0.0005:
            YellowHeartAlien(aliens, lasers)

        if len(obstacles) < max_obstacles and random.random() < 0.0005:
            Asteroid(obstacles)

        if len(obstacles) < max_obstacles and random.random() < 0.004:
            MiniAsteroid(obstacles)
        
        ####

        stars.update()
        stars.draw(screen)
        
        aliens.update()
        aliens.draw(screen)

        obstacles.update()
        obstacles.draw(screen)
        
        ship.update()

        for heart in ship.hearts:
            screen.blit(heart.image, heart.rect)
        for heart in ship.base_hearts:
            screen.blit(heart.image, heart.rect)
        
        # lasers shot by ship
        for laser in ship.lasers:
            # if laser doesn't hit enemy, then it should be drawn
            # aliens.sprites() => aliens are the enemy of the ship
            if not laser.update(aliens.sprites() + obstacles.sprites()):
                screen.blit(laser.image, laser.rect)
            else:
            # else it hit the ship and doesn't exist any longer
                ship.lasers.remove(laser)

        # lasers shot by alien
        for laser in lasers:
            # [ship] => ship is enemy of the aliens
            if not laser.update([ship]):
                screen.blit(laser.image, laser.rect)
            else:
                lasers.remove(laser)

        screen.blit(ship.image, ship.rect)
        
        text = font.render(str(score), True, (200,200,200))
        screen.blit(text, (SCREEN_X-(font.size(str(score))[0]+10), 0))

        pygame.display.flip()
        print(ship.lives)

def reset():
    global score, highscore
    ship.reset()
    if score > highscore:
        highscore = score
        save_highscore()


def save_highscore():
    global highscore

    with open("save.p", "rb") as file:
        saved_highscore = pickle.load(file)
    
    if highscore > saved_highscore:
        with open("save.p", "wb") as file:
            pickle.dump(highscore, file)

def load_highscore():
    if not os.path.exists("save.p"):
        with open("save.p", "wb") as file:
            pickle.dump(0, file)
            return 0
    else:
        with open("save.p", "rb") as file:
            return pickle.load(file)

def get_time():
    global start_time
    return pygame.time.get_ticks() - start_time


if __name__ == "__main__":
    main()
