import random
import pygame
import OpenGL
import numpy as np
import math
import pyglet

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


heightG = 0
widthG = 0


def PointNoise(width, height, pixels):
    numPoints = random.randint(50, 100)
    for _ in range(numPoints):
        i = random.randint(0, height - 1)
        j = random.randint(0, width - 1)

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        pixels[(3 * width * i) + j * 3] = r
        pixels[(3 * width * i) + j * 3 + 1] = g
        pixels[(3 * width * i) + j * 3 + 2] = b
def LineNoise(width, height, pixels):
    numLines = random.randint(2, 5)
    
    lines = []

    for _ in range(numLines):
        x1 = random.randint(-width, width - 1) / width
        y1 = random.randint(-width, height - 1) / height
        x2 = random.randint(-width, width - 1) / width 
        y2 = random.randint(-width, height - 1) / height

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        lines.append([x1,y1, x2, y2, r,g,b])

    glLineWidth(1.0)
    for line in lines:
        glBegin(GL_LINES)
        glColor3f(line[4] / 255.0, line[5] / 255.0, line[6] / 255.0)
        glVertex2f(line[0], line[1])
        glVertex2f(line[2], line[3])
        glEnd()

    glReadPixels(0,0,width,height,GL_RGB, GL_UNSIGNED_BYTE, pixels)
def CircleNoise(width, height, pixels):
    numCircles = random.randint(2, 5)
    circles = []
    for _ in range(numCircles):
        centerX = random.randint(-width, width - 1) / width
        centerY = random.randint(-width, width - 1) / width
        radius = random.randint(0, 100)/ 1000
        
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        circles.append([centerX,centerY, radius,r,g,b])
    glLineWidth(1.0)
    for circle in circles:
        numSegments = 30
        glBegin(GL_LINE_LOOP) 
        glColor3f(circle[3] / 255.0, circle[4] / 255.0, circle[5] / 255.0)
        for i in range(numSegments):
            theta = 2.0 * 3.1415926 * i / numSegments
            x = circle[0] + circle[2] * math.cos(theta)
            y = circle[1] + circle[2] * math.sin(theta)
            glVertex2f(x, y)
        glEnd()
        glReadPixels(0,0,width,height,GL_RGB, GL_UNSIGNED_BYTE, pixels)

def ravnomFilter(width, height, pixels, mod = 1):
    # Выполним реализацию 3 апертур. Они будут равномерными; размерами 3, 5 и 7
    kernelSize = 3
    if (mod == 1):
        kernelSize = 3  
    if (mod == 2):
        kernelSize = 5  
    if (mod == 3):
        kernelSize = 7 

    for y in range(height):
        for x in range(width):
            # Вычисляем границы места работы
            ymin = max(0, y - kernelSize // 2)
            ymax = min(height, y + kernelSize // 2 + 1)
            xmin = max(0, x - kernelSize // 2)
            xmax = min(width, x + kernelSize // 2 + 1)
            # Вычисляем среднее значение каналов
            meanR=0
            meanG=0
            meanB=0
            count = 0
            for i in range(ymin, ymax):
                for j in range(xmin, xmax):
                    index = (3 * width * i) + j * 3
                    meanR += pixels[index] 
                    meanG += pixels[index + 1] 
                    meanB += pixels[index + 2] 
                    count +=1
            
            meanR //= count
            meanG //= count
            meanB //= count
            # Применяем вычисленные цвета на пиксель
            index = (3 * width * y) + x * 3
            pixels[index] = meanR
            pixels[index + 1] = meanG
            pixels[index + 2] = meanB

# Медианный фильтр
def medianFilter(width, height, pixels, mod = 1):
    kernelSize = 3
    if (mod == 1):
        kernelSize = 3  
    if (mod == 2):
        kernelSize = 5  
    if (mod == 3):
        kernelSize = 7 

    for y in range(height):
        for x in range(width):
            # Вычисляем границы места работы
            ymin = max(0, y - kernelSize // 2)
            ymax = min(height, y + kernelSize // 2 + 1)
            xmin = max(0, x - kernelSize // 2)
            xmax = min(width, x + kernelSize // 2 + 1)
            # Составим список каналов пикселей и найдём медиану
            medR=0
            medG=0
            medB=0

            spR = []
            spG = []
            spB = []
            for i in range(ymin, ymax):
                for j in range(xmin, xmax):
                    index = (3 * width * i) + j * 3
                    spR.append(pixels[index]) 
                    spG.append(pixels[index + 1]) 
                    spB.append(pixels[index + 2])
            
            medR = int(np.median(spR))
            medG = int(np.median(spG))
            medB = int(np.median(spB)) 
            # Применяем вычисленные цвета на пиксель
            index = (3 * width * y) + x * 3
            pixels[index] = medR
            pixels[index + 1] = medG
            pixels[index + 2] = medB

# Фильтр резкости
def rezFilter(width, height, pixels, k = 2):
     # Реализуем функцию относительно параметра k, после чего протестируем при разных значениях k
    kernel = [-k/8, -k/8, -k/8], [-k/8, k+1, -k/8], [-k/8, -k/8, -k/8]

    for y in range(height):
        for x in range(width):
            ymin = max(0, y - 1)
            ymax = min(height, y + 2)
            xmin = max(0, x - 1)
            xmax = min(width, x + 2)

            sharpenR = 0
            sharpenG = 0
            sharpenB = 0
            # Применяем матрицу к каналам пикселей
            for i in range(ymin, ymax):
                for j in range(xmin, xmax):
                    index = (3 * width * i) + j * 3
                    sharpenR += pixels[index] * kernel[i - ymin][j - xmin]
                    sharpenG += pixels[index + 1] * kernel[i - ymin][j - xmin]
                    sharpenB += pixels[index + 2] * kernel[i - ymin][j - xmin]

            # Полученное значение с учётом возможности выхода за пределы 0 - 255 заносим в параметры текущего пикселя
            index = (3 * width * y) + x * 3
            pixels[index] = int(np.clip(pixels[index] +  sharpenR, 0, 255))
            pixels[index + 1] = int(np.clip(pixels[index + 1] +  sharpenG, 0, 255))
            pixels[index + 2] = int(np.clip(pixels[index + 2] + sharpenB, 0, 255))

# Эффект акварели - в начале применяем сглаживание, после чего используем фильтр резкости
def Aquarel(width, height, pixels):
    medianFilter(width, height, pixels,3)
    rezFilter(width, height, pixels,2)


def main():
    area_x = 0
    area_y = 0
    global widthG
    global heightG
    image_stream = open('Cl.jpg', 'rb')
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

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glDrawPixels(widthG, heightG, GL_RGB, GL_UNSIGNED_BYTE, pixels)

        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pixels = (GLubyte * len(data)) (*data)
                if event.key == pygame.K_2:
                    ravnomFilter(widthG,heightG,pixels,1)         
                if event.key == pygame.K_3:
                   ravnomFilter(widthG,heightG,pixels,2)
                if event.key == pygame.K_4:
                    ravnomFilter(widthG,heightG,pixels,3)
                if event.key == pygame.K_5:
                   medianFilter(widthG,heightG,pixels,1)
                if event.key == pygame.K_6:
                   medianFilter(widthG,heightG,pixels,2)
                if event.key == pygame.K_7:
                   medianFilter(widthG,heightG,pixels,3)
                if event.key == pygame.K_KP1:
                    rezFilter(widthG,heightG,pixels,1)
                if event.key == pygame.K_KP2:
                    rezFilter(widthG,heightG,pixels,2)
                if event.key == pygame.K_KP3:
                    rezFilter(widthG,heightG,pixels,4)
                if event.key == pygame.K_KP4:
                    PointNoise(widthG,heightG,pixels)
                if event.key == pygame.K_KP5:
                    LineNoise(widthG,heightG,pixels)
                if event.key == pygame.K_KP6:
                    CircleNoise(widthG,heightG,pixels)
                if event.key == pygame.K_KP7:
                    Aquarel(widthG,heightG,pixels)


        glDrawPixels(widthG, heightG, GL_RGB, GL_UNSIGNED_BYTE, pixels)

                                     
        pygame.display.flip()
        pygame.time.wait(12)
main() 


