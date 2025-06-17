import os
import sys
import pygame as pg
import random
import time
import math

# 画面サイズの設定
WIDTH, HEIGHT = 1100, 650

# カレントディレクトリをスクリプトの場所に変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# プレイヤーの移動方向と速度（キー入力に対応）
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0)
}

# ゲームオーバー時の表示関連のグローバル変数
GAMEOVER_KK_IMG = None
GAMEOVER_TEXT = None
GAMEOVER_TEXT_RECT = None
BLACKOUT_SURFACE = None

# こうかとん画像の読み込みと反転処理
original_kk_img = pg.image.load("fig/3.png")
flip_kk_img = pg.transform.flip(original_kk_img, True, False)

# 移動方向に応じたこうかとん画像の設定
kk_imgs: dict[tuple[int, int], pg.Surface] = {
    (0, 0): pg.transform.rotozoom(original_kk_img, 0, 0.9),
    (-5, 0): pg.transform.rotozoom(original_kk_img, 0, 0.9),
    (+5, 0): pg.transform.rotozoom(flip_kk_img, 0, 0.9),
    (0, -5): pg.transform.rotozoom(flip_kk_img, 90, 0.9),
    (0, +5): pg.transform.rotozoom(flip_kk_img, -90, 0.9),
    (-5, -5): pg.transform.rotozoom(original_kk_img, -45, 0.9),
    (-5, +5): pg.transform.rotozoom(original_kk_img, 45, 0.9),
    (+5, -5): pg.transform.rotozoom(flip_kk_img, 45, 0.9),
    (+5, +5): pg.transform.rotozoom(flip_kk_img, -45, 0.9),
}

# 爆弾がこうかとんに向かって追尾するベクトルを計算する関数
def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾(org)からこうかとん(dst)への正規化された方向ベクトルを返す。
    近距離（300px未満）では慣性（現在の速度）を維持する。
    """
    diff_x = dst.centerx - org.centerx
    diff_y = dst.centery - org.centery
    distance = math.sqrt(diff_x**2 + diff_y**2)

    if distance < 300:
        return current_xy
    if distance == 0:
        return (0, 0)
        
    speed = math.sqrt(50)
    vx = (diff_x / distance) * speed
    vy = (diff_y / distance) * speed
    
    return vx, vy

# 移動方向に応じたこうかとん画像を返す
def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    return kk_imgs.get(sum_mv)

# 爆弾の画像リストと加速度リストを初期化
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        bb_img.set_colorkey((0, 0, 0))  # 黒色を透明に
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs

# 最初の爆弾を生成（位置・速度つき）
def create_initial_bomb(bb_imgs: list[pg.Surface]) -> tuple[pg.Surface, pg.Rect, int, int]:
    bb_img = bb_imgs[0]
    bb_rect = bb_img.get_rect()
    bb_rect.x = random.randint(0, WIDTH - bb_rect.width)
    bb_rect.y = random.randint(0, HEIGHT - bb_rect.height)
    vx, vy = +5, +5
    return bb_img, bb_rect, vx, vy

# オブジェクトが画面内に収まっているかを判定
def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if not (0 <= obj_rct.left and obj_rct.right <= WIDTH):
        yoko = False
    if not (0 <= obj_rct.top and obj_rct.bottom <= HEIGHT):
        tate = False
    return yoko, tate

# ゲームオーバー時の演出を表示
def gameover(screen: pg.Surface):
    global GAMEOVER_KK_IMG, GAMEOVER_TEXT, GAMEOVER_TEXT_RECT, BLACKOUT_SURFACE

    if GAMEOVER_KK_IMG is None:
        GAMEOVER_KK_IMG = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.8)
        font = pg.font.Font(None, 80)
        GAMEOVER_TEXT = font.render("Game Over", True, (255, 255, 255))
        GAMEOVER_TEXT_RECT = GAMEOVER_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        BLACKOUT_SURFACE = pg.Surface((WIDTH, HEIGHT))
        BLACKOUT_SURFACE.set_alpha(128)  # 半透明の黒い幕

    screen.blit(BLACKOUT_SURFACE, (0, 0))
    
    # こうかとん2体とGame Overテキストを表示
    text_center_y = GAMEOVER_TEXT_RECT.centery
    offset_x = GAMEOVER_TEXT_RECT.width / 2 + GAMEOVER_KK_IMG.get_width() / 2 + 20
    left_kk_rect = GAMEOVER_KK_IMG.get_rect(center=(GAMEOVER_TEXT_RECT.centerx - offset_x, text_center_y))
    right_kk_rect = GAMEOVER_KK_IMG.get_rect(center=(GAMEOVER_TEXT_RECT.centerx + offset_x, text_center_y))

    screen.blit(GAMEOVER_KK_IMG, left_kk_rect)
    screen.blit(GAMEOVER_KK_IMG, right_kk_rect)
    screen.blit(GAMEOVER_TEXT, GAMEOVER_TEXT_RECT)

    pg.display.update()
    time.sleep(5)  # 5秒停止してゲーム終了

# メイン関数
def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    # こうかとん初期設定
    kk_rct = original_kk_img.get_rect(center=(300, 200))
    kk_img = kk_imgs[(-5, 0)]  # 初期向き

    # 爆弾の初期化
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img, bb_rect, vx, vy = create_initial_bomb(bb_imgs)

    clock = pg.time.Clock()
    tmr = 0  # タイマー

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, [0, 0])

        # 爆弾のサイズを時間経過で変更
        idx = min(tmr // 500, 9)
        old_bomb_center = bb_rect.center
        bb_img = bb_imgs[idx]
        bb_rect = bb_img.get_rect(center=old_bomb_center)

        # 爆弾の追跡処理
        vx, vy = calc_orientation(bb_rect, kk_rct, (vx, vy))
        bb_rect.move_ip(vx, vy)

        # 爆弾が画面外に出た場合の補正
        yoko, tate = check_bound(bb_rect)
        if not yoko:
            if bb_rect.left < 0: bb_rect.left = 0
            if bb_rect.right > WIDTH: bb_rect.right = WIDTH
        if not tate:
            if bb_rect.top < 0: bb_rect.top = 0
            if bb_rect.bottom > HEIGHT: bb_rect.bottom = HEIGHT

        # プレイヤー移動の処理
        key_lst = pg.key.get_pressed()
        mv_x, mv_y = 0, 0
        for key, (dx, dy) in DELTA.items():
            if key_lst[key]:
                mv_x += dx
                mv_y += dy

        sum_mv = (mv_x, mv_y)
        if sum_mv != (0, 0):
            kk_img = get_kk_img(sum_mv)  # 移動中なら向きを更新

        kk_rct.move_ip(mv_x, mv_y)

        # 画面外に出ないよう制限
        yoko, tate = check_bound(kk_rct)
        if not yoko:
            kk_rct.move_ip(-mv_x, 0)
        if not tate:
            kk_rct.move_ip(0, -mv_y)

        # 描画と衝突判定
        screen.blit(bb_img, bb_rect)
        screen.blit(kk_img, kk_rct)

        if kk_rct.colliderect(bb_rect):  # 衝突したら終了
            gameover(screen)
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)  # 1秒間に50フレーム

# 実行開始
if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
