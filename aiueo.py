import os
import random
import sys
import time
import math
import pygame as pg

WIDTH = 1100
HEIGHT = 650
NUM_OF_BOMBS = 5  # 複数爆弾用

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

class Bird:
    delta = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)
    imgs = {
        (+5, 0): img,
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),
        (-5, 0): img0,
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),
    }

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+5, 0)]
        self.rct = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0)

    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if sum_mv != [0, 0]:
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = tuple(sum_mv)
        screen.blit(self.img, self.rct)

class Beam:
    def __init__(self, bird: Bird):
        self.img0 = pg.image.load("fig/beam.png")
        vx, vy = bird.dire
        self.vx, self.vy = vx, vy
        angle = math.degrees(math.atan2(-vy, vx))
        self.img = pg.transform.rotozoom(self.img0, angle, 1.0)
        self.rct = self.img.get_rect()
        self.rct.centerx = bird.rct.centerx + bird.rct.width * vx // 5
        self.rct.centery = bird.rct.centery + bird.rct.height * vy // 5

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        if check_bound(self.rct) != (True, True):
            return False
        screen.blit(self.img, self.rct)
        return True

class Bomb:
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Explosion:
    def __init__(self, bomb: Bomb):
        self.imgs = [
            pg.image.load("fig/explosion.png"),
            pg.transform.flip(pg.image.load("fig/explosion.png"), True, True)
        ]
        self.rct = self.imgs[0].get_rect(center=bomb.rct.center)
        self.life = 50

    def update(self, screen: pg.Surface):
        self.life -= 1
        screen.blit(self.imgs[self.life//25%2], self.rct)

class Score:
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.update_surface()

    def update_surface(self):
        self.img = self.fonto.render(f"スコア: {self.score}", True, self.color)
        self.rct = self.img.get_rect()
        self.rct.topleft = (10, HEIGHT-50)

    def update(self, screen: pg.Surface):
        self.update_surface()
        screen.blit(self.img, self.rct)

""" def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []
    explosions = []
    score = Score()
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))

        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        for beam in beams:
            if not beam.update(screen):
                beams.remove(beam)

        for bomb in bombs:
            bomb.update(screen)

        for exp in explosions:
            exp.update(screen)

        # ビームと爆弾の衝突判定
        for beam in beams:
            for bomb in bombs:
                if bomb is not None and beam is not None and beam.rct.colliderect(bomb.rct):
                    explosions.append(Explosion(bomb))
                    bombs[bombs.index(bomb)] = None
                    beams[beams.index(beam)] = None
                    bird.change_img(6, screen)
                    score.score += 1

        # リスト整理
        bombs = [b for b in bombs if b is not None]
        beams = [b for b in beams if b is not None]
        explosions = [e for e in explosions if e.life > 0]

        # こうかとんと爆弾の衝突判定（ゲームオーバー）
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(2)
                return

        score.update(screen)
        pg.display.update()
        clock.tick(50)
        tmr += 1

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
 """
 
 # 省略（前半部のクラス定義などは前のコードと同じです）

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []
    explosions = []
    score = Score()
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))

        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        # --- update beams ---
        for beam in beams[:]:
            if not beam.update(screen):
                beams.remove(beam)

        # --- update bombs ---
        for bomb in bombs:
            bomb.update(screen)

        # --- update explosions ---
        for exp in explosions:
            exp.update(screen)

        # --- ビームと爆弾の衝突処理 ---
        for beam in beams[:]:
            for bomb in bombs[:]:
                if bomb is not None and beam is not None and beam.rct.colliderect(bomb.rct):
                    explosions.append(Explosion(bomb))
                    bombs.remove(bomb)
                    beams.remove(beam)
                    bird.change_img(6, screen)  # 喜び顔（撃ち落とした）
                    score.score += 1
                    break  # beam1本で複数ヒットを防ぐ

        # --- こうかとん vs 爆弾の衝突処理（Game Over） ---
        for bomb in bombs:
            if bomb is not None and bird.rct.colliderect(bomb.rct):
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(2)
                return

        # --- remove expired explosions ---
        explosions = [e for e in explosions if e.life > 0]

        # --- update score ---
        score.update(screen)

        pg.display.update()
        clock.tick(50)
        tmr += 1

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
