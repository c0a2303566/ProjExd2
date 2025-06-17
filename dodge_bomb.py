import os
import sys
import pygame as pg
import random


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))
DELTA = {pg.K_UP: (0,-5),pg.K_DOWN: (0,+5),pg.K_LEFT:(-5,0),pg.K_RIGHT:(+5,0)}


def create_bomb():
    r = 10
    bb_img = pg.Surface((2*r, 2*r))
    bb_img.fill((0, 0, 0))  # 黒で塗りつぶし
    bb_img.set_colorkey((0, 0, 0))  # 黒を透明に
    pg.draw.circle(bb_img, (255, 0, 0), (r, r), r)
    bb_rect = bb_img.get_rect()
    bb_rect.x = random.randint(0, WIDTH - 2*r)
    bb_rect.y = random.randint(0, HEIGHT - 2*r)
    vx = vy = 5
    return bb_img, bb_rect, vx, vy




def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    clock = pg.time.Clock()
    tmr = 0
    bb_img, bb_rect, vx, vy = create_bomb()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 
        
        bb_rect.move_ip(vx, vy)
        if bb_rect.left < 0 or bb_rect.right > WIDTH:
            vx = -vx
        if bb_rect.top < 0 or bb_rect.bottom > HEIGHT:
            vy = -vy

        key_lst = pg.key.get_pressed()
        mv_x = mv_y = 0
        for key, (dx,dy)in DELTA.items():
            if key_lst[key]:
                mv_x += dx
                mv_y += dy
                
        screen.blit(bb_img, bb_rect)
                
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        kk_rct.move_ip(mv_x,mv_y)
        screen.blit(kk_img, kk_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
