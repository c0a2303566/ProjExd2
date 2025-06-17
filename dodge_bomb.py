import os
import sys
import pygame as pg
import random


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))
DELTA = {pg.K_UP: (0,-5),pg.K_DOWN: (0,+5),pg.K_LEFT:(-5,0),pg.K_RIGHT:(+5,0)}


def create_bomb(r: int = 10, initial_vx: int = 5, initial_vy: int = 5) -> tuple[pg.Surface, pg.Rect, int, int]:
    """
    爆弾を生成する関数。
    引数:
        r (int): 爆弾の半径。デフォルトは10。
        initial_vx (int): 爆弾の初期横方向速度。デフォルトは5。
        initial_vy (int): 爆弾の初期縦方向速度。デフォルトは5。
    戻り値:
        tuple[pg.Surface, pg.Rect, int, int]: 爆弾の画像、Rectオブジェクト、横方向速度、縦方向速度。
    """
    bb_img = pg.Surface((2*r, 2*r))
    bb_img.fill((0, 0, 0))  # 黒で塗りつぶし
    bb_img.set_colorkey((0, 0, 0))  # 黒を透明に
    pg.draw.circle(bb_img, (255, 0, 0), (r, r), r)
    bb_rect = bb_img.get_rect()
    bb_rect.x = random.randint(0, WIDTH - 2*r)
    bb_rect.y = random.randint(0, HEIGHT - 2*r)
    vx = initial_vx
    vy = initial_vy
    return bb_img, bb_rect, vx, vy

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し、真理値タプルを返す関数
    引数：
        obj_rct (pg.Rect): こうかとんRect or 爆弾Rect
    戻り値：
        tuple[bool, bool]: 横方向,縦方向の真理値タプル (True: 画面内/False: 画面外)
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # ゲームオーバー用画像の読み込み
    gameover_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0) # 例として8番の画像を使用
    # ゲームオーバーテキスト用のフォント設定
    font = pg.font.Font(None, 80) # Noneでデフォルトフォント、80はフォントサイズ
    gameover_text = font.render("Game Over", True, (255, 255, 255)) # テキスト、アンチエイリアス、色(白)
    gameover_text_rect = gameover_text.get_rect(center=(WIDTH/2, HEIGHT/2))


    clock = pg.time.Clock()
    tmr = 0
    bb_img, bb_rect, vx, vy = create_bomb()
    
    game_active = True # ゲームがアクティブかどうかのフラグ

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:  
                return
        
        if game_active: # ゲームがアクティブな場合のみ処理を続行
            screen.blit(bg_img, [0, 0])  
            
            # 爆弾の移動と画面外判定
            bb_rect.move_ip(vx, vy)
            yoko, tate = check_bound(bb_rect)
            if not yoko:
                vx = -vx
            if not tate:
                vy = -vy

            key_lst = pg.key.get_pressed()
            mv_x = mv_y = 0
            for key, (dx,dy)in DELTA.items():
                if key_lst[key]:
                    mv_x += dx
                    mv_y += dy
                    
            # こうかとんの移動と画面外判定
            kk_rct.move_ip(mv_x,mv_y)
            yoko, tate = check_bound(kk_rct)
            if not yoko: # 画面外に出たら元に戻す
                kk_rct.move_ip(-mv_x, 0)
            if not tate: # 画面外に出たら元に戻す
                kk_rct.move_ip(0, -mv_y)
            
            screen.blit(bb_img, bb_rect)
            screen.blit(kk_img, kk_rct)

            # 衝突判定
            if kk_rct.colliderect(bb_rect):
                game_active = False # ゲームオーバーにする
        else:
            # ゲームオーバー画面の表示
            screen.blit(bg_img, [0, 0]) # 背景を再描画
            screen.blit(gameover_kk_img, kk_rct) # こうかとんの画像をゲームオーバー用に切り替え
            screen.blit(gameover_text, gameover_text_rect) # "Game Over"テキスト表示

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()