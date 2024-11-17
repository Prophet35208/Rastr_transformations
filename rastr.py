import random
import pygame
import OpenGL
import numpy
import math
import pyglet

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

widthG = 0
heightG = 0
BRIGHTNESS_DELTA = 20
CONTRAST_DELTA = 100

def getBrightness(r,g,b):
    return 0.299 * r + 0.5876 *g + 0.114 * b

def BrightnessAdjustment (startX, startY, width, height, delta, pixels):
    global widthG
    endX = startX + width
    endY = startY + height
    for i in range(startY, endY):
        for j in range(startX, endX):

            r = pixels[(3 * widthG * i) + j * 3] + delta
            if (r>255): r = 255
            if (r < 0): r = 0

            g = pixels[(3 * widthG * i) + j * 3 + 1] + delta
            if (g>255): g = 255
            if (g < 0): g = 0

            b = pixels[(3 * widthG * i) + j * 3 + 2] + delta
            if (b>255): b = 255
            if (b < 0): b = 0

            pixels[(3 * widthG * i) + j * 3] = r
            pixels[(3 * widthG * i) + j * 3 + 1] = g
            pixels[(3 * widthG * i) + j * 3 + 2] = b

def ContrastAdjustment (startX, startY, width, height, delta, pixels):
    endX = startX + width
    endY = startY + height
    avrR = 0
    avrG = 0
    avrB = 0

    for i in range(startY, endY):
        for j in range(startX, endX):
            r = pixels[(3 * widthG * i) + j * 3]
            g = pixels[(3 * widthG * i) + j * 3 + 1]
            b = pixels[(3 * widthG * i) + j * 3 + 2] 
            avrR = avrR +  r
            avrG = avrG +  g
            avrB = avrB +  b

    avrR = avrR / (width * height)
    avrG = avrG / (width * height)
    avrB = avrB / (width * height)

    for i in range(startY, endY):
        for j in range(startX, endX):

            r = pixels[(3 * widthG * i) + j * 3] 
            g = pixels[(3 * widthG * i) + j * 3 + 1] 
            b = pixels[(3 * widthG * i) + j * 3 + 2] 

            r = int(delta * (r - avrR) + avrR)
            g = int(delta * (g - avrG) + avrG)
            b = int(delta * (b - avrB) + avrB)

            if (r>255): r = 255
            if (r < 0): r = 0
            if (g>255): g = 255
            if (g < 0): g = 0
            if (b>255): b = 255
            if (b < 0): b = 0

            pixels[(3 * widthG * i) + j * 3] = r
            pixels[(3 * widthG * i) + j * 3 + 1] = g
            pixels[(3 * widthG * i) + j * 3 + 2] = b

# Основной цвет - чёрный, фон - белый
def Binorization (startX, startY, width, height, pixels):
    endX = startX + width
    endY = startY + height
    for i in range(startY, endY):
        for j in range(startX, endX):

            r = pixels[(3 * widthG * i) + j * 3]
            g = pixels[(3 * widthG * i) + j * 3 + 1] 
            b = pixels[(3 * widthG * i) + j * 3 + 2] 
            sredn = (r + g + b)/3
            if (sredn > 125):
                r = 0
                g = 0
                b = 0
            else:
                r = 255
                g = 255
                b = 255

            pixels[(3 * widthG * i) + j * 3] = r
            pixels[(3 * widthG * i) + j * 3 + 1] = g
            pixels[(3 * widthG * i) + j * 3 + 2] = b

def OttSer (startX, startY, width, height, pixels):
    endX = startX + width
    endY = startY + height
    for i in range(startY, endY):
        for j in range(startX, endX):

            r = pixels[(3 * widthG * i) + j * 3]
            g = pixels[(3 * widthG * i) + j * 3 + 1] 
            b = pixels[(3 * widthG * i) + j * 3 + 2] 

            brigtness = int(getBrightness(r,g,b))

            pixels[(3 * widthG * i) + j * 3] = brigtness
            pixels[(3 * widthG * i) + j * 3 + 1] = brigtness
            pixels[(3 * widthG * i) + j * 3 + 2] = brigtness

def Negative (startX, startY, width, height, pixels):
    endX = startX + width
    endY = startY + height
    for i in range(startY, endY):
        for j in range(startX, endX):

            r = 255 - pixels[(3 * widthG * i) + j * 3]
            g = 255 - pixels[(3 * widthG * i) + j * 3 + 1] 
            b = 255 - pixels[(3 * widthG * i) + j * 3 + 2] 

            pixels[(3 * widthG * i) + j * 3] = r
            pixels[(3 * widthG * i) + j * 3 + 1] = g
            pixels[(3 * widthG * i) + j * 3 + 2] = b

def SendDiagramInfo(startX, startY, width, height, pixels):
    f = open('Out.txt', 'w')
    endX = startX + width
    endY = startY + height
    for i in range(startY, endY):
        for j in range(startX, endX):

            r = pixels[(3 * widthG * i) + j * 3]
            g = pixels[(3 * widthG * i) + j * 3 + 1] 
            b = pixels[(3 * widthG * i) + j * 3 + 2] 

            f.write(str(int(getBrightness(r,g,b))))
            f.write(" ")  
    f.write("\n")

    endX = startX + width
    endY = startY + height
    for i in range(startY, endY):
        for j in range(startX, endX):

            r = pixels[(3 * widthG * i) + j * 3]
            g = pixels[(3 * widthG * i) + j * 3 + 1] 
            b = pixels[(3 * widthG * i) + j * 3 + 2] 

            f.write(str(int(r)))
            f.write(" ")  
    f.write("\n")

    endX = startX + width
    endY = startY + height
    for i in range(startY, endY):
        for j in range(startX, endX):

            r = pixels[(3 * widthG * i) + j * 3]
            g = pixels[(3 * widthG * i) + j * 3 + 1] 
            b = pixels[(3 * widthG * i) + j * 3 + 2] 

            f.write(str(int(g)))
            f.write(" ")  
    f.write("\n")

    endX = startX + width
    endY = startY + height
    for i in range(startY, endY):
        for j in range(startX, endX):

            r = pixels[(3 * widthG * i) + j * 3]
            g = pixels[(3 * widthG * i) + j * 3 + 1] 
            b = pixels[(3 * widthG * i) + j * 3 + 2] 

            f.write(str(int(b)))
            f.write(" ")    

    f.close()


def main():
    area_x = 0
    area_y = 0
    global widthG
    global heightG
    image_stream = open('C.jpg', 'rb')
    image = pyglet.image.load('C.jpg', file=image_stream).get_image_data()
    heightG = image.height
    widthG = image.width

    area_width = widthG
    area_height = heightG
    data = image.get_data('RGB', image.width * 3)
    pixels = (GLubyte * len(data)) (*data)
    display = (widthG,heightG)

    pygame.display.set_mode(display, pygame.DOUBLEBUF|pygame.OPENGL)
    glTranslatef(0,0, -1) # Камера

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pixels = (GLubyte * len(data)) (*data)
                if event.key == pygame.K_2:
                    BrightnessAdjustment(area_x,area_y,area_width,area_height,BRIGHTNESS_DELTA,pixels)
                if event.key == pygame.K_3:
                   BrightnessAdjustment(area_x,area_y,area_width,area_height,-BRIGHTNESS_DELTA,pixels)
                if event.key == pygame.K_4:
                    ContrastAdjustment(area_x,area_y,area_width,area_height,CONTRAST_DELTA,pixels)
                if event.key == pygame.K_5:
                   ContrastAdjustment(area_x,area_y,area_width,area_height,1/CONTRAST_DELTA,pixels)
                if event.key == pygame.K_KP1:
                    Binorization(area_x,area_y,area_width,area_height,pixels)
                if event.key == pygame.K_KP2:
                    OttSer(area_x,area_y,area_width,area_height,pixels)
                if event.key == pygame.K_KP3:
                    Negative(area_x,area_y,area_width,area_height,pixels)
                if event.key == pygame.K_KP4:
                    SendDiagramInfo(area_x,area_y,area_width,area_height,pixels)
                if event.key == pygame.K_KP5:
                    f = open('In.txt', 'r')
                    area_x = int(f.readline())
                    area_y = int(f.readline())
                    area_width = int(f.readline())
                    area_height = int(f.readline())
                                     
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glDrawPixels(widthG, heightG, GL_RGB, GL_UNSIGNED_BYTE, pixels)

        pygame.display.flip()
        pygame.time.wait(12)
main() 


