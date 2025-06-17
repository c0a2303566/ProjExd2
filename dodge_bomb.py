import os
import sys
import pygame as pg
import random
import time

WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0)
}

GAMEOVER_KK_IMG = None
GAMEOVER_TEXT = None
GAMEOVER_TEXT_RECT = None
BLACKOUT_SURFACE = None

# 基準となる元の左向き画像のみをロード
original_kk_img = pg.image.load("fig/3.png")
flip_kk_img = pg.transform.flip(original_kk_img,True,False)

# 全ての向きの画像を「元の左向き画像」から生成する
kk_imgs: dict[tuple[int, int], pg.Surface] = {
    # 停止時と左向き (0度)
    (0, 0): pg.transform.rotozoom(original_kk_img, 0, 0.9),
    (-5, 0): pg.transform.rotozoom(original_kk_img, 0, 0.9),
    # 右向き (180度)
    (+5, 0): pg.transform.rotozoom(flip_kk_img, 0, 0.9),
    # 上向き (時計回りに90度)
    (0, -5): pg.transform.rotozoom(flip_kk_img, 90, 0.9),
    # 下向き (反時計回りに90度)
    (0, +5): pg.transform.rotozoom(flip_kk_img, -90, 0.9),
    # 左上 (時計回りに45度)
    (-5, -5): pg.transform.rotozoom(original_kk_img, -45, 0.9),
    # 左下 (反時計回りに45度)
    (-5, +5): pg.transform.rotozoom(original_kk_img, 45, 0.9),
    # 右上 (時計回りに135度)
    (+5, -5): pg.transform.rotozoom(flip_kk_img, 45, 0.9),
    # 右下 (反時計回りに135度)
    (+5, +5): pg.transform.rotozoom(flip_kk_img, -45, 0.9),
}


def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    return kk_imgs.get(sum_mv)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def create_initial_bomb(bb_imgs: list[pg.Surface]) -> tuple[pg.Surface, pg.Rect, int, int]:
    bb_img = bb_imgs[0]
    bb_rect = bb_img.get_rect()
    bb_rect.x = random.randint(0, WIDTH - bb_rect.width)
    bb_rect.y = random.randint(0, HEIGHT - bb_rect.height)
    vx, vy = +5, +5
    return bb_img, bb_rect, vx, vy


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if not (0 <= obj_rct.left and obj_rct.right <= WIDTH):
        yoko = False
    if not (0 <= obj_rct.top and obj_rct.bottom <= HEIGHT):
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface):
    global GAMEOVER_KK_IMG, GAMEOVER_TEXT, GAMEOVER_TEXT_RECT, BLACKOUT_SURFACE

    if GAMEOVER_KK_IMG is None:
        GAMEOVER_KK_IMG = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.8)
        font = pg.font.Font(None, 80)
        GAMEOVER_TEXT = font.render("Game Over", True, (255, 255, 255))
        GAMEOVER_TEXT_RECT = GAMEOVER_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        BLACKOUT_SURFACE = pg.Surface((WIDTH, HEIGHT))
        BLACKOUT_SURFACE.set_alpha(128)

    screen.blit(BLACKOUT_SURFACE, (0, 0))
    
    text_center_y = GAMEOVER_TEXT_RECT.centery
    offset_x = GAMEOVER_TEXT_RECT.width / 2 + GAMEOVER_KK_IMG.get_width() / 2 + 20
    
    left_kk_rect = GAMEOVER_KK_IMG.get_rect(center=(GAMEOVER_TEXT_RECT.centerx - offset_x, text_center_y))
    right_kk_rect = GAMEOVER_KK_IMG.get_rect(center=(GAMEOVER_TEXT_RECT.centerx + offset_x, text_center_y))

    screen.blit(GAMEOVER_KK_IMG, left_kk_rect)
    screen.blit(GAMEOVER_KK_IMG, right_kk_rect)
    screen.blit(GAMEOVER_TEXT, GAMEOVER_TEXT_RECT)
    
    pg.display.update()
    time.sleep(5)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    kk_rct = original_kk_img.get_rect(center=(300, 200))
    kk_img = kk_imgs[(-5, 0)]

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img, bb_rect, vx, vy = create_initial_bomb(bb_imgs)

    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, [0, 0])
        
        idx = min(tmr // 500, 9)
        
        # 爆弾の更新
        new_speed_multiplier = bb_accs[idx]
        base_bomb_speed = 5
        vx_abs = base_bomb_speed * new_speed_multiplier
        vy_abs = base_bomb_speed * new_speed_multiplier
        vx = vx_abs if vx >= 0 else -vx_abs
        vy = vy_abs if vy >= 0 else -vy_abs

        old_bomb_center = bb_rect.center
        bb_img = bb_imgs[idx]
        bb_rect = bb_img.get_rect(center=old_bomb_center)
        
        bb_rect.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rect)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        # プレイヤーの更新
        key_lst = pg.key.get_pressed()
        mv_x, mv_y = 0, 0
        for key, (dx, dy) in DELTA.items():
            if key_lst[key]:
                mv_x += dx
                mv_y += dy
        
        sum_mv = (mv_x, mv_y)
        if sum_mv != (0, 0): # 移動がない場合は向きを維持
            kk_img = get_kk_img(sum_mv)

        kk_rct.move_ip(mv_x, mv_y)
        yoko, tate = check_bound(kk_rct)
        if not yoko:
            kk_rct.move_ip(-mv_x, 0)
        if not tate:
            kk_rct.move_ip(0, -mv_y)

        # 描画と衝突判定
        screen.blit(bb_img, bb_rect)
        screen.blit(kk_img, kk_rct)

        if kk_rct.colliderect(bb_rect):
            gameover(screen)
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()