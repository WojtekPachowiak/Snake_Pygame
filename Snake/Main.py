import pygame as pg
from pygame import *
from settings import *
import random
from os import path
import spritesheet
#def Draw_floor(floor_tile):
#    rect = floor_tile.get_rect()
#    surf = pg.Surface(WIDTH,HEIGHT)
#    for i in range(0,WIDTH,rect[2]):
#        for j in range(0,HEIGHT,rect[3]):
#            surf.blit(floor_tile,(i,j))

#def game_over():
#    pass

#def get_snake_start_coord():
#    head_coord = random.randint(0,TILES[1]-1) * TILE_SIZE
#    tail_coord = random.choice([(-TILE_SIZE,0),(TILE_SIZE,0),(0,TILE_SIZE),(0,-TILE_SIZE)])
#    return head_coord, tail_coord

pg.init()
pg.mixer.init()
SCREEN = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Futur Snek")
clock = pg.time.Clock()
running = True
#font_name = pg.font.match_font(FONT)

MOVESNAKE = pg.USEREVENT + 1
pg.time.set_timer(MOVESNAKE, 200)

img_dir = path.join(path.dirname(__file__), 'Assets\\img')
snd_dir = path.join(path.dirname(__file__), 'Assets\\snd')

my_font = pg.font.Font(path.join(img_dir, 'ARCADECLASSIC.TTF'), 60)

eat_apple_sound = pg.mixer.Sound(path.join(snd_dir, 'eatApple.wav'))
eat_apple_sound.set_volume(0.2)
death_sound = pg.mixer.Sound(path.join(snd_dir, 'snakeDeath.wav'))
death_sound.set_volume(0.5)
music = path.join(snd_dir, 'snakeMusic.mp3')


def get_image_from_spritesheet(x,y,width,height):
    img = spridesheet.image_at((x,y,width,height),WHITE)
    img = pg.transform.scale(img,(TILE_SIZE,TILE_SIZE))
    return img

spridesheet = spritesheet.spritesheet(path.join(img_dir, "Snake.png"))
apple_img = get_image_from_spritesheet(16,48,16,16)
floor_img = get_image_from_spritesheet(16,32,16,16)
snake_head_img = get_image_from_spritesheet(0,0,16,16)
snake_tail_img = get_image_from_spritesheet(0,48,16,16)
snake_straight_torso_img = get_image_from_spritesheet(0,16,16,16)
snake_curved_torso_img = get_image_from_spritesheet(0,32,16,16)


class SnakePart(pg.sprite.Sprite):
    def __init__(self, next, prev, xy):
        pg.sprite.Sprite.__init__(self)
        self.image = snake_tail_img

        self.rect = self.image.get_rect()
        #self.rect = self.image
        self.rect.x = xy[0]
        self.rect.y = xy[1]

        self.next = next
        self.prev = prev

        #second argument indicates horizontal flip
        self.img_rot = pg.math.Vector2(0,False)


    def move_body(self):
        self.rect.topleft = self.next.rect.topleft
        #check if the next part is a head
        if (self.next.next == None):
            self.next.move_head()
        else:
            self.next.move_body()


    def rotate_body_img(self, propagate = True):
        
        self.img_rot.update(0,False)

        diff_next = pg.math.Vector2(
            self.next.rect.topleft[0] - self.rect.topleft[0], 
            self.next.rect.topleft[1] - self.rect.topleft[1]) //TILE_SIZE

        #check if tail
        if (self.prev == None):
            if diff_next == (1,0):
                self.img_rot.update(-90, False) 
            elif diff_next == (-1,0):
                self.img_rot.update(90, False) 
            elif diff_next == (0,1):
                self.img_rot.update(180, False) 
            elif diff_next == (0,-1):
                self.img_rot.update(0, False) 
            self.image = snake_tail_img
            self.image = pg.transform.rotate(self.image, self.img_rot.x)
            return


        diff_prev = pg.math.Vector2(
            self.prev.rect.topleft[0] - self.rect.topleft[0],
            self.prev.rect.topleft[1] - self.rect.topleft[1]) //TILE_SIZE

        if diff_next == -diff_prev:
            ##jeżeli proste ciało
            if diff_next.x == 0:
                #jeżeli pionowe
                if diff_next.y == 1:
                    self.img_rot.update(180, False) 
                elif diff_next.y == -1:
                    self.img_rot.update(0, False) 
            elif diff_next.y == 0:
                #jeżeli poziome
                if diff_next.x == 1:
                    self.img_rot.update(-90,False) 
                elif diff_next.x == -1:
                    self.img_rot.update(90,False) 
            self.image = snake_straight_torso_img

        else:
            #jeżeli krzywe ciało
            if diff_next == (0,1):
                if diff_prev == (1,0):
                    self.img_rot.update(180,True) 
                elif diff_prev == (-1,0):
                    self.img_rot.update(180,False) 

            elif diff_next == (1,0):
                if diff_prev == (0,1):
                    self.img_rot.update(-90,False) 
                elif diff_prev == (0,-1):
                    self.img_rot.update(-90,True) 

            elif diff_next == (0,-1):
                if diff_prev == (1,0):
                    self.img_rot.update(0,False) 
                elif diff_prev == (-1,0):
                    self.img_rot.update(0,True) 

            elif diff_next == (-1,0):
                if diff_prev == (0,1):
                    self.img_rot.update(90,True) 
                elif diff_prev == (0,-1):
                    self.img_rot.update(90,False) 
            self.image = snake_curved_torso_img

        
        self.image = pg.transform.flip(self.image, bool(self.img_rot.y), False)
        self.image = pg.transform.rotate(self.image, self.img_rot.x)

        if propagate:
            self.prev.rotate_body_img()






    

class SnakeHead(pg.sprite.Sprite):
    def __init__(self, prev, x, y):
        pg.sprite.Sprite.__init__(self)
        self.move_dir = pg.math.Vector2(random.choice([(-1,0),(1,0),(0,1),(0,-1)]))
        self.move_dir * TILE_SIZE
        self.image = snake_head_img
        self.orig_img = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.next = None
        self.prev = prev
        self.eaten_apple = False
        self.img_rot = 0


    def update(self):
        self.check_input()


    def check_input(self):
        keystate = pg.key.get_pressed()
        if keystate[pg.K_LEFT] and self.move_dir.x != 1:
            self.move_dir.update(-1,0)
        elif keystate[pg.K_RIGHT] and self.move_dir.x != -1:
            self.move_dir.update(1,0)
        elif keystate[pg.K_UP] and self.move_dir.y != 1:
            self.move_dir.update(0,-1)
        elif keystate[pg.K_DOWN] and self.move_dir.y != -1:
            self.move_dir.update(0,1)

    def move_head(self):
        self.rect.move_ip(self.move_dir.x * TILE_SIZE, self.move_dir.y * TILE_SIZE)
        
        self.rotate_head_img()
        self.prev.rotate_body_img()

       

    def elongate(self):
        self.eaten_apple = True
        new_body_part = SnakePart(self, self.prev, self.rect.topleft)
        new_body_part.image = self.image
        self.prev.next = new_body_part
        self.prev = new_body_part
        #new_body_prect.topleft = self.rect.topleft
        #new_body_part.rotate_body_img(False)

        return new_body_part


    def rotate_head_img(self):
        #TO_DO: rotate only when direction has changed
        self.img_rot = 0
        self.image = self.orig_img
        if self.move_dir.x == 1:
            self.img_rot = -90
        elif self.move_dir.x == -1:
            self.img_rot = 90
        elif self.move_dir.y == 1:
            self.img_rot = 180
        elif self.move_dir.y == -1:
            return
        self.image = pg.transform.rotate(self.image, self.img_rot)


       





class Apple(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = apple_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (64*8,64*8)

    def spawn_new(self,snake_body_group):
        while(pg.sprite.spritecollide(self, snake_body_group,False)):
            self.rect.topleft = self.new_pos()
            ###TO_DO: check if apple spawn right next to player - there might be a bug
        #SCREEN.blit(self.image,self.rect.topleft)

    def new_pos(self):
        x = random.randint(0,TILES[0]-1) * TILE_SIZE
        y = random.randint(0,TILES[1]-1) * TILE_SIZE
        return (x,y)






class Floor(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        surf = pg.Surface((WIDTH,HEIGHT))
        for i in range(0,WIDTH,TILE_SIZE):
            for j in range(0,HEIGHT,TILE_SIZE):
                surf.blit(floor_img,(i,j))
        self.image = surf
        self.rect = self.image.get_rect()




#-----====-----------------------------------------------------------------====-----------------#



class Game():
    def __init__(self):
        self.running = True

    def new_game(self):
        #head_coord = (random.randint(0,TILES[1]-1) * TILE_SIZE
        #head_coord = ()
        #tail_coord = random.choice([(-TILE_SIZE,0),(TILE_SIZE,0),(0,TILE_SIZE),(0,-TILE_SIZE)])

        self.snakeHead = SnakeHead(None,5*TILE_SIZE,5*TILE_SIZE)
        self.snakeTail = SnakePart(self.snakeHead, None, (5*TILE_SIZE , 6*TILE_SIZE))
        self.snakeHead.prev = self.snakeTail
        self.apple = Apple()
        self.floor = Floor()
        self.SNAKE_BODY = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.SNAKE_BODY.add([self.snakeHead,self.snakeTail])
        self.all_sprites.add([self.floor,self.snakeHead,self.snakeTail,self.apple])
        self.score = 0
        pg.mixer.music.load(music)
        pg.mixer.music.set_volume(0.3)

        self.run()


    def events(self):
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            elif event.type == MOVESNAKE:
                if self.snakeHead.eaten_apple == True:
                    self.snakeHead.move_head()
                    self.snakeHead.eaten_apple = False
                else:
                    self.snakeTail.move_body()


    def update(self):
        self.all_sprites.update()


    def collisions(self):
        hit_apple_snake = pg.sprite.spritecollide(self.apple, self.SNAKE_BODY,False)
        if hit_apple_snake:
            eat_apple_sound.play()
            self.score += 1
            self.apple.spawn_new(self.SNAKE_BODY)
            new_body_part = self.snakeHead.elongate()
            self.all_sprites.add(new_body_part)
            self.SNAKE_BODY.add(new_body_part)

        hit_snake_snake = pg.sprite.spritecollide(self.snakeHead, self.SNAKE_BODY,False)
        for hit in hit_snake_snake:
            if hit != self.snakeHead and hit != self.snakeHead.prev and self.snakeHead.rect.center == hit.rect.center:
                death_sound.play()
                self.playing = False
                break

        if self.snakeHead.rect.x >= WIDTH or self.snakeHead.rect.y >= HEIGHT or self.snakeHead.rect.x < 0 or self.snakeHead.rect.y < 0:
            death_sound.play()
            self.playing = False 



    def draw(self):
        SCREEN.fill(BLACK)
        self.all_sprites.draw(SCREEN)
        self.draw_text(str(self.score), 22, ORANGE, WIDTH / 2, 15)
        pg.display.flip()


    def wait_for_key(self):
        waiting = True
        while waiting:
            clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False


    def draw_text(self, text, size, color, x, y):
        text_surface = my_font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        SCREEN.blit(text_surface, text_rect)

        
    def show_start_screen(self):
        pass


    def show_go_screen(self):
        pass


    def run(self):
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            clock.tick(FPS)
            self.events()
            self.update()
            self.collisions()
            self.draw()
        pg.mixer.music.fadeout(500)





g = Game()
g.show_start_screen()
while g.running:
    g.new_game()
    g.show_go_screen()

pg.quit()