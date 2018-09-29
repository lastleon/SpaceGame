import pygame, math, sys, random

SCREEN_X, SCREEN_Y = 1000, 700
score = 0

class Ship(pygame.sprite.Sprite):

    def __init__(self, shipImages):
        pygame.sprite.Sprite.__init__(self)
        self.images = shipImages

        self.lives = 10
        self.base_lives = 5

        self.laser_pic = "./resources/laserGreen.png"

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
        self.rect.y = SCREEN_Y - self.rect.height

        self.fly_left, self.fly_right = 0,0
        self.fly_up, self.fly_down = 0,0

    def damage(self):
        self.lives -= 1;
        self.hearts[self.lives].update()
        if self.lives == 0:
            gameover()
            
    def damage_base(self):
        self.base_lives -= 1
        self.base_hearts[self.base_lives].update()
        if self.base_lives == 0:
            gameover()

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

        self.image = pygame.image.load(heartImage)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        
    def update(self):
        self.image = pygame.image.load("./resources/heartEmpty.png")

class Laser(pygame.sprite.Sprite):

    def __init__(self, xcenter, ycenter, ship):
        super(Laser, self)
        self.ship = ship
        self.image = pygame.image.load(ship.laser_pic)
        self.rect = self.image.get_rect()

        self.rect.centerx = xcenter
        self.rect.centery = ycenter - self.rect.height

    def update(self, enemies):
        if isinstance(self.ship, Ship):
            self.rect.centery -= 6
            if self.rect.y < - self.rect.height:
                return True
            else:
                for enemy in enemies:    
                    if self.rect.colliderect(enemy.rect):
                        enemy.damage()
                        return True
                return False
        else:
            self.rect.centery += 6
            if self.rect.y > SCREEN_Y:
                return True
            else:
                for enemy in enemies:    
                    if self.rect.colliderect(enemy.rect):
                        enemy.damage()
                        return True
                return False

class Star(pygame.sprite.Sprite):

    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.image.load("./resources/star.png")
        self.rect = self.image.get_rect()

        self.rect.x = random.randrange(0, SCREEN_X-self.rect.width)
        self.rect.centery = random.randrange(0, SCREEN_Y-self.rect.height)
        self.increment = 0

    def update(self):
        self.increment += 0.5
        self.rect.centery += int(self.increment)
        if self.increment == 1:
            self.increment = 0
        if self.rect.y > SCREEN_Y:
            self.rect.y = -self.rect.height
            self.rect.x = random.randrange(0, SCREEN_X-self.rect.width)

class Alien(pygame.sprite.Sprite):
    def __init__(self, alienImages, group, laserlist):
        pygame.sprite.Sprite.__init__(self, group)
        self.images = alienImages
        self.laser_pic = "./resources/laserPurple.png"
        self.lives = 5
        self.lasers = laserlist

        self.cooldown = 0
        
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.images[self.index].get_rect()
        
        self.rect.x = random.randrange(0,SCREEN_X-self.rect.width)
        self.rect.y = -self.rect.height

    def update(self):
        global score, ship
        self.image = self.images[math.floor(self.index)]
        self.index += 0.05
        if self.index > len(self.images):
            self.index = 0
        
        self.rect.y += 1

        if self.rect.y > SCREEN_Y:
            self.kill()
            ship.damage_base()
            score -= 50
            return
        
        self.cooldown -= 1
        if self.cooldown < 0:
            self.cooldown = 0
        
        if random.random() < 0.01 and self.cooldown == 0:
            self.lasers.append(Laser(self.rect.centerx, self.rect.centery + self.rect.height, self))
            self.cooldown = 15
            
    def damage(self):
        global score
        self.lives -= 1
        if self.lives == 0:
            self.kill()
            score += 25

def gameover():
    print("Game Over!\nScore:", score)
    pygame.time.wait(1000)
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    
def main():
    global ship
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_X,SCREEN_Y))

    pygame.display.set_caption("Spacegame")

    clock = pygame.time.Clock()

    ship = Ship([pygame.image.load("./resources/shipFrame1.png"), pygame.image.load("./resources/shipFrame2.png")])

    lasers = []
    stars = pygame.sprite.Group()
    aliens = pygame.sprite.Group()

    font = pygame.font.Font("./resources/monobit.ttf", 80)
    max_aliens = 0
    
    for _ in range(0,20):
        Star(stars)
    
    while True:
        clock.tick(60)
        screen.fill((0, 3, 47))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    ship.fly_left = 5
                if event.key == pygame.K_RIGHT:
                    ship.fly_right = 5
                if event.key == pygame.K_UP:
                    ship.fly_up = 5
                if event.key == pygame.K_DOWN:
                    ship.fly_down = 5
                if event.key == pygame.K_SPACE:
                    ship.shoot = True;

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

        max_aliens = int(int(pygame.time.get_ticks()/1000)/20)+1

        if max_aliens > 20:
            max_aliens = 20
        
        if len(aliens)<max_aliens and random.random()< 0.01:
            Alien([pygame.image.load("./resources/alienFrame1.png"), pygame.image.load("./resources/alienFrame2.png")], aliens, lasers)

        stars.update()
        stars.draw(screen)
        
        aliens.update()
        aliens.draw(screen)
        
        
        ship.update()


        for heart in ship.hearts:
            screen.blit(heart.image, heart.rect)
        for heart in ship.base_hearts:
            screen.blit(heart.image, heart.rect)
        
        for laser in ship.lasers:
            if not laser.update(aliens.sprites()):
                screen.blit(laser.image, laser.rect)
            else:
                ship.lasers.remove(laser)
    
        for laser in lasers:
            if not laser.update([ship]):
                screen.blit(laser.image, laser.rect)
            else:
                lasers.remove(laser)
        screen.blit(ship.image, ship.rect)

        
        text = font.render(str(score), True, (200,200,200))
        screen.blit(text, (SCREEN_X-(font.size(str(score))[0]+10), 0))

        pygame.display.flip()
    

if __name__ == "__main__":
    main()
