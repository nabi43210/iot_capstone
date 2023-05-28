import pygame
import yt_dlp
import requests
import os
import time
import threading
import re
from pyvidplayer import Video

def clean_title(title):
    # 특수문자를 제거하는 정규표현식
    pattern = r'[^\w\s]'
    # 제목에서 특수문자를 제거하고 반환
    return re.sub(pattern, '', title)

def download_videos(yt_link, vid_list, index):
    ydl_opts = {'format' : 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]',
            'outtmpl' : index+".mp4",
            'extract_info' : True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(yt_link, download=False)
        title = info_dict.get('title', None)
        ydl.download(yt_link)
        vid_list.append(index + ".mp4")
        return index + ".mp4"

def show_popup(text, yes_callback=None, no_callback=None):
    font = pygame.font.Font("NanumSquare.ttf", 30)
    text_surface = font.render(text, True, (255, 255, 255))
    popup_width = text_surface.get_width() + 20
    popup_height = text_surface.get_height() + 80
    popup = pygame.Surface((popup_width, popup_height))
    popup.fill((0, 0, 0))
    popup.blit(text_surface, (10, 20))

    yes_btn = pygame.Rect(20, popup_height-60, 120, 40)
    no_btn = pygame.Rect(popup_width - yes_btn.width - 140 - 20, popup_height - 60, 120, 40)

    pygame.draw.rect(popup, (50, 50, 255), yes_btn)
    pygame.draw.rect(popup, (255, 50, 50), no_btn)

    yes_font = pygame.font.SysFont("Arial", 24)
    yes_text = yes_font.render("Yes", True, (255, 255, 255))
    yes_btn_center = yes_btn.center
    yes_text_center = yes_text.get_rect(center=yes_btn_center)
    popup.blit(yes_text, yes_text_center)

    no_font = pygame.font.SysFont("Arial", 24)
    no_text = no_font.render("No", True, (255, 255, 255))
    no_btn_center = no_btn.center
    no_text_center = no_text.get_rect(center=no_btn_center)
    popup.blit(no_text, no_text_center)

    popup_x = (800 - popup_width) // 2
    popup_y = (480 - popup_height) // 2
    win.blit(popup, (popup_x, popup_y))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                if yes_btn.collidepoint(x - popup_x, y - popup_y):
                    print("YES")
                    return 1
                elif no_btn.collidepoint(x - popup_x, y - popup_y):
                    return 0

def video_play(vid_link=None):
    #provide video class with the path to your video
    black_screen = pygame.Surface((800, 480))
    black_screen.fill((0, 0, 0))
    vid = Video(vid_link)
    vid.set_size((800, 480))
    x = 0
    y = 0
    while True:
        key = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                vid.close()
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                # 마우스 클릭 이벤트 처리
                x, y = event.pos
            elif event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
        popup_clicked = False
        #your program frame rate does not affect video playback
        clock.tick(60)
        if x < 266 and y > 160 and y < 320:
            vid.seek(-15)
        elif x > 532 and y > 160 and y < 320:
            vid.seek(15)
        elif x > 266 and x < 532:
            popup_clicked = not popup_clicked
        if(popup_clicked == True):
            vid.pause()
            res = show_popup("[강북구청]서울특별시 시민참여예산 제안사업 공모")
            print(res)
            if(res == 1):
                win.blit(black_screen, (0, 0))
                pygame.display.update()
                black_screen_bool = True
                while black_screen_bool:
                    for event in pygame.event.get():
                        if(event.type == pygame.MOUSEBUTTONUP):
                            vid.resume()
                            popup_clicked = not popup_clicked
                            black_screen_bool = not black_screen_bool
                            break
                    clock.tick(60)
            else:
                print("resume")
                popup_clicked = not popup_clicked
                vid.resume()
        else:
            vid.resume()
        x = 0
        y = 0

        if(int(vid.duration) == int(vid.get_pos())):
            return
    
        #draws the video to the given surface, at the given position
        vid.draw(win, (0, 0), force_draw=False)
        pygame.display.update()

def download_process(movie_links, vid_list):
    for movie_link in movie_links:
        vid_file = download_videos(movie_link)
        vid_list.append(vid_file)

pygame.init()
win = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
#win = pygame.display.set_mode((800, 480))
clock = pygame.time.Clock()

response = requests.get('http://hiroshilin.iptime.org:20000/get_rec_heal/요리')
movies = response.json()

vid_list = []
for index, movie in enumerate(movies):
    print(index)
    if(index == 0):
        vid = download_videos(movie, vid_list, str(index))
    elif(index == len(movies)):
        video_play(vid_list[index])
        os.remove(vid_list[index])
        break
    t = threading.Thread(target=download_videos, args=(movies[index + 1], vid_list, str(index+1)))
    t.start()
    video_play(vid_list[index])
    t.join()
    os.remove(vid_list[index])