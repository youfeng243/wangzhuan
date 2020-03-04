#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-27 15:47
# @Author  : youfeng
# @Site    : 
# @File    : play_audio.py
# @Software: PyCharm
import time

import pygame


def play_hint_audio():
    # return
    pygame.mixer.init()
    pygame.mixer.music.load("./audio/7500.mp3")
    pygame.mixer.music.play(loops=50)
    while True:
        if pygame.mixer.music.get_busy():
            time.sleep(1)
            continue
        break


if __name__ == '__main__':
    play_hint_audio()
