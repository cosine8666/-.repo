import pygame 
import random #引入隨機模組
import os #一個格式化檔案路徑的模組，適用於不同作業系統的檔案管理系統

#固定變數(遊戲過程中不會改變)通常會用全大寫
FPS = 60
WIDTH = 500
HEIGHT = 600

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,225,0)
RED = (255,0,0)
YELLOW = (255,255,0)

pygame.init() #遊戲初始化
pygame.mixer.init() #傳入音效前，需要先將mixer初始化
screen = pygame.display.set_mode((WIDTH,HEIGHT)) #製作一個與原組內同數值的螢幕
pygame.display.set_caption("太空生存戰(hibyby)") #改視窗上面的標題
clock = pygame.time.Clock() #創建一個時鐘物件

#載入圖片/字體，要放在初始化函式之後
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
#把圖片引入pygame，os.path代表pygame檔案的位置，join為引入其位置內資料夾下的檔案
#convert()為轉換方法，目的為轉換為pygame容易讀取的格式，讀得比較快
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
# rock_img = pygame.image.load(os.path.join("img", "rock.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 20))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert()) 
    #f""可以格式化字串，""裡面可以放變數、set{}
expl_anim = {} #用字典存放大爆炸與小爆炸和其圖片的定義
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img",f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75,75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30,30)))
    player_expl_img = pygame.image.load(os.path.join("img",f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()

#加入音效
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl2.mp3"))
              ]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
#pygame.mixer.music代表不是事件觸發，會在背景撥放
pygame.mixer.music.set_volume(0.4)
# pygame.mixer.music(pygame.mixer.Sound(os.path.join("sound", "expl1.mp3"))).set_volume(0) 

font_name = os.path.join("font.ttf")
#pygame.font.match_font() pygame會從電腦中找符合的字體載入
#盡量選通用字體，因為可能運行在各個玩家的電腦上
def draw_text(surf, text, size, x, y): #定義一個有5個變數的函示
    font = pygame.font.Font(font_name, size) #pygame.front.Front傳入字體與字體大小
    text_surface = font.render(text, True, WHITE) #將字體做渲染(內容，是否鋸齒(antialias為反鋸齒)，字體顏色)
    text_rect = text_surface.get_rect() #為文字方塊定位
    text_rect.centerx = x
    text_rect.top= y
    surf.blit(text_surface, text_rect) #將文字方塊畫在surf平面上(傳入該文字方塊, 位置)

def new_rock():
    #此函式除了要放在一開始讓石頭出現之外，還要在石頭消失處放置，讓石頭重新出現
    r = Rock() #每執行一次hit(碰撞)，會增加一顆石頭
    all_sprites.add(r) #讓新出現的石頭出現在畫面上
    rocks.add(r) #讓新出現的石頭繼續進行碰撞判斷

def draw_health(surf, hp, x, y):
    if hp <= 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HIGHT) #形成矩形(座標,長,寬)
    fill_rect = pygame.Rect(x, y, fill, BAR_HIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect) 
    #繪製矩形(平面,顏色,實心矩形)
    pygame.draw.rect(surf, WHITE, outline_rect, 2) 
    #繪製矩形外框(平面,顏色,空心矩形,外框厚度(像素))

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 35*i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(background_img, (0,0)) #將圖片畫(blit)出來，左上角座標為(0,0)
    draw_text(screen, "太空生存站!", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "← →移動飛船 空白鍵發射子彈", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "按任意鍵開始遊戲!", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS) #時鐘物件裡的tick函式，每秒只能被執行<=FPS次，讓每台電腦運行次數一樣
        #取得輸入
        for event in pygame.event.get(): #pygame.event.get()會回傳所有事件列表
            if event.type == pygame.QUIT: #事件列表裡的QUIT被觸發時
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False #停止running
                return False

class Player(pygame.sprite.Sprite): #繼承pygame.sprite.Sprite類別
    def __init__(self): #初始函式
        pygame.sprite.Sprite.__init__(self) #繼承物件的初始函式
        self.image = pygame.transform.scale(player_img, (50,38)) #改變傳入的圖片大小
        self.image.set_colorkey(BLACK) #讓圖片內的該顏色變透明，可做為去背功能
        # self.image = pygame.Surface((50,40)) #創造第一個物件self.image，是一個平面(長,寬)
        # self.image.fill(GREEN) #平面顏色填滿
        self.rect = self.image.get_rect() #將一張圖片的四邊框起來，以利設定屬性
        #圖片左上角為(0,0)，右下角為(WIDTH,HEIGHT)
        # self.rect.x = 200 #平面左上角的X位點
        # self.rect.y = 200 #平面左上角的Y位點
        self.radius = 20 #為了碰撞判斷而另外增加的屬性，是circle的半徑
        # pygame.draw.circle(self.image,RED,self.rect.center,self.radius) #畫一個紅色的圓形判斷物(圖片，顏色，圓心，半徑)
        # self.rect.center = (WIDTH/2,HEIGHT/2) #直接設定位點在螢幕正中
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time >1000: #1000毫秒 = 1秒
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed() 
        #pygame.key.get_pressed()函式會回傳鍵盤上所有按鍵是否被觸動的bool[]
        if key_pressed[pygame.K_RIGHT]: 
            #key_pressed list 中 pygame.K_RIGHT = True (鍵盤右鍵被點擊)
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
            #key_pressed list 中 pygame.K_LEFT = True (鍵盤左鍵被點擊)
            # K_a為鍵盤上的A鍵被點擊 K_SPACE為鍵盤上空白鍵被點擊
        # self.rect.x += 2 #每執行一次while都會跑2
        # if self.rect.left > WIDTH: #當平面往左跑出去
        #     self.rect.right = 0 #會讓平面從右邊進來

    def shoot(self):
        if not(self.hidden) and self.gun == 1:
            bullet = Bullet(self.rect.centerx, self.rect.top) #子彈class中的(x,y) = 飛船的(centerx,top)
            all_sprites.add(bullet)
            bullets.add(bullet) #加群組的方法放在子彈出現的函式下
            shoot_sound.play()
        if self.gun >= 2:
            bullet1 = Bullet(self.rect.left, self.rect.y) 
            bullet2 = Bullet(self.rect.right, self.rect.y) 
            all_sprites.add(bullet1)
            all_sprites.add(bullet2)
            bullets.add(bullet1) 
            bullets.add(bullet2) 
            shoot_sound.play()

    def hide(self):
        #直接將飛船定位在視窗外
        self.hidden = True
        self.hide_time = pygame.time.get_ticks() #為了飛船再顯示時使用
        self.rect.center = (WIDTH/2, HEIGHT+500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()


class Rock(pygame.sprite.Sprite): #繼承pygame.sprite.Sprite類別
    def __init__(self): #初始函式
        pygame.sprite.Sprite.__init__(self) #繼承物件的初始函式
        self.image_ori = random.choice(rock_imgs) #從list rock_imgs中，隨機挑一張圖片
        self.image_ori.set_colorkey(BLACK) 
        self.image = self.image_ori.copy() #將每一次轉動後的圖片都儲存成self.image_ori.copy()
        # self.image = pygame.Surface((30,40)) #創造第一個物件self.image，是一個平面(長,寬)
        # self.image.fill(RED) #平面顏色填滿
        self.rect = self.image_ori.get_rect() #將一張圖片的四邊框起來，以利設定屬性
        self.radius = int(self.rect.width *0.85 / 2)
        # pygame.draw.circle(self.image,RED,self.rect.center,self.radius) #畫一個紅色的圓形判斷物(圖片，顏色，圓心，半徑)
        self.rect.x = random.randrange(0,WIDTH - self.rect.width) #self.rect.width石頭的寬度
        self.rect.y = random.randrange(-180,-100) #-100是原點以上100 -40是原點以左40
        self.speedy = random.randrange(2,5)
        self.speedx = random.randrange(-3,3) #石頭可以往左和往右邊跑
        self.total_degree = 0
        self.rot_degree = random.randrange(-3,3)

    def rotate(self):
        #pygame.transform.rotate()每轉一次會造成失真，如果疊加失真會讓遊戲無法正常運行，
        #所以每一次執行函式，都需要初始化，重新執行self.image_ori = rock_img
        self.total_degree += self.rot_degree #讓圖片在每一次的轉動會繼承上一次的角度
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori,self.total_degree)
        #因為轉動後定位會微跑掉，所以每一次轉動都需要重新定位轉動圓心
        center = self.rect.center #定義轉動前的center
        self.rect = self.image.get_rect() #用轉動後的圖片蓋掉原先的self.rect定義
        self.rect.center = center

    def update(self):
        self.rotate() #呼叫rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0: 
            #當石頭跑出去外面時，石頭的位置與速度都會重製
            self.rect.x = random.randrange(0,WIDTH - self.rect.width) 
            self.rect.y = random.randrange(-100,-40) 
            self.speedy = random.randrange(2,10)
            self.speedx = random.randrange(-3,3) 

class Bullet(pygame.sprite.Sprite): #繼承pygame.sprite.Sprite類別
    def __init__(self,x,y): #初始函式
        pygame.sprite.Sprite.__init__(self) #繼承物件的初始函式
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        # self.image = pygame.Surface((10,20)) #創造第一個物件self.image，是一個平面(長,寬)
        # self.image.fill(YELLOW) #平面顏色填滿
        self.rect = self.image.get_rect() #將一張圖片的四邊框起來，以利設定屬性
        #圖片左上角為(0,0)，右下角為(WIDTH,HEIGHT)
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10 #速度為負，子彈才會往上飛
        
    def update(self):
        self.rect.bottom += self.speedy
        if self.rect.bottom < 0: #當子彈跑出螢幕外
            self.kill() #直接刪除子彈

class Explosion(pygame.sprite.Sprite): #繼承pygame.sprite.Sprite類別
    def __init__(self, center, size): #初始函式
        pygame.sprite.Sprite.__init__(self) #繼承物件的初始函式
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect() #將一張圖片的四邊框起來，以利設定屬性
        #圖片左上角為(0,0)，右下角為(WIDTH,HEIGHT)
        self.rect.center = center
        #如果單純用update的更新速度會太快(FPS = 60)
        self.frame = 0 #更新到第幾張圖片
        self.last_update = pygame.time.get_ticks() 
        #pygame.time.get_ticks()從初始化的時間，也是上一次圖片更新的時間
        self.frame_rate = 50 #經過多少毫秒更新下一張圖片
        
    def update(self):
        new = pygame.time.get_ticks()
        if new - self.last_update >= self.frame_rate:
            #限縮動畫更新速度
            self.last_update = new
            self.frame += 1
            if self.frame == len(expl_anim[self.size]): 
                self.kill() #跑完圖以後刪掉爆炸動畫
            else :
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect() 
                self.rect.center = center
                #重新定義中心點，以免在動畫跑的時候中心跑掉

class Power(pygame.sprite.Sprite): #繼承pygame.sprite.Sprite類別
    def __init__(self, center): #初始函式
        pygame.sprite.Sprite.__init__(self) #繼承物件的初始函式
        self.type = random.choice(['shield','gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #將一張圖片的四邊框起來，以利設定屬性
        #圖片左上角為(0,0)，右下角為(WIDTH,HEIGHT)
        self.rect.center = center
        self.speedy = 3
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT: 
            self.kill() 

#因為lives == 0 後，重新開始，所有數據需要重新設定
# all_sprites = pygame.sprite.Group() #創建一個可以加入很多東西的群組
# rocks = pygame.sprite.Group() #建立一個群組，放入全部的子彈
# bullets = pygame.sprite.Group() #建立一個群組，放入全部的石頭
# player = Player() #以方便呼叫裡面的函式
# all_sprites.add(player) 
# player_group = pygame.sprite.Group(player) #碰撞判斷必須要是Group形式
# all_sprites.add(player_group) 
# for i in range(8): #會跑8次迴圈，產生8顆石頭，加入all_sprites群組 #初始的石頭
#     new_rock()
# score = 0
# pygame.mixer.music.play(-1) #-1代表無限循環
# powers = pygame.sprite.Group()
 
# Game loop 遊戲迴圈
# process input(取得輸入) > update game(更新遊戲) > render(畫面渲染) 
# 每隔一段時間重複一次迴圈

running = True
show_init = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group() #創建一個可以加入很多東西的群組
        rocks = pygame.sprite.Group() #建立一個群組，放入全部的子彈
        bullets = pygame.sprite.Group() #建立一個群組，放入全部的石頭
        player = Player() #以方便呼叫裡面的函式
        all_sprites.add(player) 
        player_group = pygame.sprite.Group(player) #碰撞判斷必須要是Group形式
        all_sprites.add(player_group) 
        for i in range(8): #會跑8次迴圈，產生8顆石頭，加入all_sprites群組 #初始的石頭
            new_rock()
        score = 0
        powers = pygame.sprite.Group()
        pygame.mixer.music.play(-1) #-1代表無限循環

    clock.tick(FPS) #時鐘物件裡的tick函式，每秒只能被執行<=FPS次，讓每台電腦運行次數一樣
    #取得輸入
    for event in pygame.event.get(): #pygame.event.get()會回傳所有事件列表
        if event.type == pygame.QUIT: #事件列表裡的QUIT被觸發時
            running = False #停止running
        elif event.type == pygame.KEYDOWN: #當鍵盤上有任何按鍵被觸動
            if event.key == pygame.K_SPACE: #被觸動的鍵是空白鍵
                player.shoot() #呼叫射擊函式 Group不能直接.其函式

    #更新遊戲
    all_sprites.update() #會執行all_sprites群組裡的所有update函式

    #判斷石頭、子彈相撞
    hits:dict = pygame.sprite.groupcollide(rocks, bullets ,True, True)
    # groupcollide()判斷兩個群組中的物件碰撞後，是否要將其刪除，
    # 然後會回傳一個字典(碰撞到的石頭(key):碰撞到的子彈(value))
    for hit in hits: #每碰撞一次，就會增加一個hit在hits裡
        score += hit.radius #hits的key(碰撞到的石頭)，其radius
        new_rock()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl) #加進去後才能畫出來
        random.choice(expl_sounds).play()
        if random.random() > 0.95: #random.random()會回傳0~1隨機值
            #random.random() > 0.1:為九成的機率
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)

    #判斷石頭、飛船相撞
    died = pygame.sprite.groupcollide(rocks, player_group, True, False,pygame.sprite.collide_circle)
    # 碰撞後，石頭會被消除，pygame.sprite.collide_circle將矩形碰撞判斷改為圓形碰撞判斷
    for die in died : #如果death值>1
        new_rock()
        player.health -= die.radius
        expl = Explosion(die.rect.center, 'sm')
        all_sprites.add(expl) #加進去後才能畫出來
        random.choice(expl_sounds).play()
        if player.health <= 0 :
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            if player.lives > 0:
                player.health = 100
                player.hide()
            elif player.lives==0 : 
                #alive()方法代表判斷函式是否仍在進行
                show_init = True
                # running = False
                # and not(death_expl.alive())
                # #跑完動畫再關視窗

    #判斷寶物、飛船相撞
    gets = pygame.sprite.groupcollide(powers, player_group, True, False)
    for get in gets:
        if get.type == 'shield':
            player.health += 20
            if player.health > 100:
                player.health = 100
            shield_sound.play()
        if get.type == 'gun':
            player.gunup()
            gun_sound.play()

    #畫面顯示
    screen.fill((BLACK))
    screen.blit(background_img, (0,0)) #將圖片畫(blit)出來，左上角座標為(0,0)
    all_sprites.draw(screen) #將all_sprites整個群組畫在螢幕上
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH-100, 15)
    pygame.display.update() #更新螢幕已輸入函式

pygame.quit() #注意函式為小寫，事件為大寫

