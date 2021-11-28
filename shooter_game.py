from pygame import*
from random import*


import time as timer

font.init()
font_titles = font.SysFont('Corbel', 80)
font_subtitles = font.SysFont('Corbel', 35, True)
win = font_titles.render('Ты выиграл!', True, (255, 255, 255))
lose = font_titles.render('Ты проиграл!', True, (180, 0, 0))
pause_text = font_titles.render('Пауза!', True, (255, 255, 255))
lose_boss = font_titles.render('Ты пропустил босса!', True, (180, 0, 0))
restart = font_subtitles.render('R - перезапуск!', True, (255, 255, 255))
start = font.SysFont('Corbel', 50).render("Нажми цифру что бы начать", True, (0, 255, 255))
start_diff = font_subtitles.render('1 - легко, 2 - нормально, 3 - сложно', True, (0,255,255))
font2 = font.SysFont('Tahoma', 30)

mixer.init()
mixer.music.load('sounds/space.ogg')

fire_sound = mixer.Sound('sounds/fire.ogg')
reload_sound = mixer.Sound('sounds/reload.ogg')
reload_sound.set_volume(0.5)
select_sound = mixer.Sound('sounds/select_diff.ogg')
boss_sound = mixer.Sound('sounds/boss.ogg')
game_over_sound = mixer.Sound('sounds/game_over.ogg')
destroy_sound = mixer.Sound('sounds/destroy.ogg')
heal = mixer.Sound('sounds/heal.ogg')
collide = mixer.Sound('sounds/collide.ogg')
collide.set_volume(0.5)
delayer = time.Clock()

IMG_BACK = "images/galaxy.jpg"
IMG_BULLET = "images/bullet.png"
IMG_HER0 = "images/rocket.png"
IMG_ENEMY = "images/ufo.png"
IMG_AST = "images/asteroid.png"
IMG_BOSS = "images/boss.png"
IMG_HEALTHPACK = "images/healthpack.png"


score = 0
lost = 0
life = 0
boss_counter = 0
boss_comming = 0
num_fire = 0

class Difficult:





    def __init__(self, goal = 50, max_lost = 10, max_life = 5, max_enemies = 5, reload_time = 1, boss_comming_at = 20):
        self.goal = goal
        self.max_lost = max_lost
        self.max_life = max_life
        self.max_enemies = max_enemies
        self.reload_time = reload_time
        self.boss_comming_at = boss_comming_at


class GameSprite(sprite.Sprite):
    
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):

        sprite.Sprite.__init__(self)

        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(IMG_BULLET, self.rect.centerx, self.rect.top, 10, 30, -15)
        bullets.add(bullet)


class Enemy(GameSprite):

    def update(self):
        self.rect.y += self.speed
        global lost

        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

class Boss(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, lifes_count):
        super().__init__(player_image, player_x, player_y, size_x, size_y, 1)
        self.lifes = lifes_count
    def update(self):
        global finish
        self.rect.y += self.speed
        if self.rect.y > win_height:
            mixer.music.stop()
            collide.play()
            finish = True
            window.blit(background, (0, 0))
            make_frame()
            window.blit(lose_boss, (win_width / 2 - lose_boss.get_width() / 2, 200))
            window.blit(restart, (win_width / 2 - restart.get_width() / 2, 300))

class Healthpack(GameSprite):

    def start(self):
        global past_time
        self.rect.y = -60
        self.canMove = False
        self.startTime = past_time

    def create(self):
        self.rect.x = randint(80, win_width-80)
        self.rect.y = -50
        self.canMove = True

    def hasTaked(self):
        self.rect.y = -60
        self.canMove = False

    def update(self):






        global life, past_time
        if past_time - self.startTime >= 30:
            self.create()
            self.startTime = past_time
        if self.canMove:
            if sprite.collide_rect(ship, health):
                life += 1
                heal.play()
                self.hasTaked()
            if self.rect.y < 0:
                self.hasTaked()
            self.rect.y += self.speed


class Bullet(GameSprite):

    def update(self):
        self.rect.y += self.speed

        if self.rect.y < 0:
            self.kill()



window = display.set_mode((800,500))
display.set_caption("Shoter 1.4")
win_width = display.Info().current_w
win_height = display.Info().current_h
background = transform.scale(image.load(IMG_BACK), (win_width, win_height))


ship = Player(IMG_HER0, 5, win_height - 60, 80, 55, 10)
boss = Boss(IMG_BOSS, randint(80, win_width - 80), - 40, 80, 81, 10)
health = Healthpack(IMG_HEALTHPACK, randint(80, win_width - 80), - 50, 50, 50, 7)
difficult = None
monsters = sprite.Group()
asteroids = sprite.Group()
bullets = sprite.Group()

finish = False
run = True
rel_time = False
first_start = True
pause = False
boss_time = False
show_hud = True

def make_enemies():




    for i in range(difficult.max_enemies):
        monsters.add(Enemy(IMG_ENEMY, randint(80, win_width - 80),-40, 80, 50, randint(1, 3)))
    for i in range(3):
        asteroids.add(Enemy(IMG_AST, randint(30, win_width - 30), randint(-40, 30), 80, 50, randint(1, 2)))








def make_frame():
    if show_hud or finish:
        window.blit(font2.render("Счёт: " + str(score) + "/" + str(difficult.goal), 1, (255, 255, 255)), (10,20))
        window.blit(font2.render("Пропущено: " + str(lost) + "/" + str(difficult.max_lost), 1, (255, 255, 255)), (10,50))
        window.blit(font2.render("Боссов: " + str(boss_counter), 1, (255, 255, 255)), (10,80))

top_score = 0
try:
    with open("top.score", "r") as file:
        top_score = int(file.read())
except Exception as ex:
    top_score = 0
top_start = font_subtitles.render('Твой прошлый рекорд: ' + str(top_score), True, (0,150,150))





def record_top():
    global top_score,score
    if score > top_score:
        top_text = font_subtitles.render("Новый рекорд: " + str(score), 1, (0, 200, 10))
        window.blit(top_text, (win_width/2 - top_text.get_width() / 2, 350))
        top_score = score
        with open("top.score", "w") as file:
            file.write(str(top_score))
    else:
        top_text = font_subtitles.render("Твой рекорд: " + str(top_score), 1, (0, 150, 50))
        window.blit(top_text, (win_width/2 - top_text.get_width() / 2, 350))









past_time = timer.time()





window.blit(start, (win_width/2 - start.get_width() / 2, win_height/2 - start.get_height()/2))
window.blit(start_diff, (win_width/2 - start_diff.get_width() / 2, win_height/2 - start_diff.get_height()/2 + 50))
if top_score == 0:
    window.blit(top_start, (win_width/2 - top_start.get_width() / 2, win_height/2 - top_start.get_height() /2 + 100))
display.update()


while run:

    for e in event.get():
        if e.type == QUIT:
            run = False

        elif e.type == KEYDOWN:

            if e.key == K_ESCAPE:
                if pause and not first_start and not finish:
                    pause = False
                    mixer.music.unpause()
                elif not  pause and not first_start and not finish:
                    pause = True
                    mixer.music.pause()
                    window.blit(pause_text, (win_width/2-pause_text.get_width()/2,win_height/2-pause_text.get_height()))
                    display.update()
            elif e.key == K_q:
                run = False

            elif e.key == K_SPACE and not finish and not pause:

                if num_fire < 5 and rel_time == False:
                    num_fire = num_fire + 1
                    fire_sound.play()
                    ship.fire()
                if num_fire >=5 and rel_time == False:
                    reload_sound.play()
                    last_time = past_time
                    rel_time = True

            elif e.key == K_1 and first_start:
                    difficult = Difficult()
                    life = difficult.max_life
                    boss_comming = difficult.boss_comming_at
                    select_sound.play()
                    mixer.music.play()
                    first_start = False
                    make_enemies()
                    health.start()

            elif e.key == K_2 and first_start:
                    difficult = Difficult(125, 7, 4, 7, 2, 15)
                    life = difficult.max_life
                    boss_comming = difficult.boss_comming_at
                    select_sound.play()
                    mixer.music.play()
                    first_start = False
                    make_enemies()
                    health.start()

            elif e.key == K_3 and first_start:
                    difficult = Difficult(300, 5, 3, 10, 3, 10)
                    life = difficult.max_life
                    boss_comming = difficult.boss_comming_at
                    select_sound.play()
                    mixer.music.play()
                    first_start = False
                    make_enemies()
                    health.start()

            elif e.key == K_r and finish:

                    score = 0
                    lost = 0
                    life = difficult.max_life
                    boss_counter = 0
                    num_fire = 0
                    boss_comming = difficult.boss_comming_at
                    for monster in monsters:
                        monster.kill()
                    for asteroid in asteroids:
                        asteroid.kill()
                    make_enemies()
                    for bullet in bullets:


                        bullet.kill()
                    if boss_time:
                        boss.kill()
                        boss_time = False
                    finish = False
                    health.start()
                    mixer.music.play()
            elif e.key == K_h and not first_start and not finish and not pause:
                show_hud = not show_hud
    if not first_start:
        if not pause:

            if not finish:
                past_time = timer.time()

                window.blit(background,(0,0))


                ship.update()
                monsters.update()
                asteroids.update()
                bullets.update()
                health.update()

                ship.reset()
                monsters.draw(window)
                asteroids.draw(window)
                bullets.draw(window)
                health.reset()

                make_frame()


                if boss_time:
                    cols = sprite.spritecollide(boss, bullets, True)
                    for col in cols:
                        boss.lifes -= 1
                    if show_hud:
                        window.blit(font2.render('BOSS: ' + str(boss.lifes), 1, (255, 0, 0)), (10, 140))
                    boss.update()
                    boss.reset()
                    if boss.lifes <=0:
                        boss_time = False
                        score += 5
                        boss_comming = score + difficult.boss_comming_at
                        boss_counter += 1
                        boss.kill()

                if not boss_time and boss_comming - score <= 0:
                    boss_time = True
                    boss = Boss(IMG_BOSS, randint(80, win_width - 80), -40, 80, 81, 5)
                    boss_sound.play()


                collides = sprite.groupcollide(monsters, bullets, True, True)
                for c in collides:

                    score += 1
                    destroy_sound.play()
                    monsters.add(Enemy(IMG_ENEMY, randint(80, win_width - 80), -40, 80, 50, randint(1,3)))


                if sprite.spritecollide(ship, monsters, False):
                    sprite.spritecollide(ship, monsters, True)
                    monsters.add(Enemy(IMG_ENEMY, randint(80, win_width - 80), -40, 80, 50, randint(1,3)))
                    life -= 1
                    collide.play()
                if sprite.spritecollide(ship, asteroids, False):
                    sprite.spritecollide(ship, monsters, True)
                    monsters.add(Enemy(IMG_AST, randint(30, win_width - 30), -40, 80, 50, randint(1,3)))
                    life -= 1
                    collide.play()


                if life <= 0 or lost >= difficult.max_lost or ship.rect.colliderect(boss):

                    mixer.music.stop()
                    finish = True
                    window.blit(background, (0, 0))
                    make_frame()
                    window.blit(lose, (win_width/2 - lose.get_width()/2, 200))
                    window.blit(restart, (win_width/2 - restart.get_width()/2, 300))
                    game_over_sound.play()
                    record_top()



                if score >= difficult.goal:
                    mixer.music.stop()
                    finish = True
                    window.blit(background, (0,0))
                    make_frame()
                    window.blit(win, (win_width/2 - win.get_width()/2, 200))
                    window.blit(restart, (win_width/2 - restart.get_width()/2, 300))
                    record_top()



                if rel_time:
                    now_time = past_time
                    if now_time - last_time < difficult.reload_time:
                        if show_hud:
                            window.blit(font2.render("Патроны: заряжаются", 1, (255, 0, 0)), (10, 110))
                    else:
                        num_fire = 0
                        rel_time = False
                else:
                    if show_hud:
                        window.blit(font2.render("Патроны: " + str(5 - num_fire), 1, (255, 255, 255)), (10, 110))

                if show_hud:

                    if life >= difficult.max_life or life > 2:
                        life_color = (0,150,0)
                    elif life == 2:
                            life_color = (150,150, 0)
                    else:
                        life_color = (150,0,0)

                    text_life = font2.render(" " + str(life), 1, life_color)
                    window.blit(text_life, (730, 10))

                display.update()
            delayer.tick(30)