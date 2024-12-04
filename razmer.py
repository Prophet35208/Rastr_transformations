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

def nearestNeighborScale(width, height, pixels, k):
    global changingH
    global changingW
    if k <= 0:
        return None
    # Желаемое разрешение
    newWidth = int(round(width * k))
    newHeight = int(round(height * k))

    # Сохраняем границы, чтобы не выйти за пределы открытого окна
    if (newHeight > heightG):
        newHeight = heightG

    if (newWidth > widthG):
        newWidth = widthG
    
    # Создаём массив для пикселей
    newPixels = np.zeros(newWidth * newHeight * 3, dtype=np.uint8)

    # Заполняем новый массив пикселей
    for y in range(newHeight):
        for x in range(newWidth):
            # Определяем пиксель для получения изображения
            oldX = int((x / k))
            oldY = int((y / k))

            # Соблюдаем границы начального изображения
            oldX = max(0, min(oldX, width - 1))
            oldY = max(0, min(oldY, height - 1))

            oldIndex = (3 * widthG * oldY) + oldX * 3 # Индекс для старого массива, это расположение rgb пикселя. который будем присваивать
            newIndex = (3 * newWidth * y) + x * 3 # Индекс для нового массива

            newPixels[newIndex] = pixels[oldIndex]
            newPixels[newIndex + 1] = pixels[oldIndex + 1]
            newPixels[newIndex + 2] = pixels[oldIndex + 2]
    # Подготваливаемся к дальнейшей отрисовке
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glReadPixels(0,0,widthG,heightG,GL_RGB, GL_UNSIGNED_BYTE, pixels)
    for y in range(newHeight):
        for x in range(newWidth):
            oldIndex = (3 * widthG * y) + x * 3
            newIndex = (3 * newWidth * y) + x * 3
            pixels[oldIndex] = newPixels[newIndex]
            pixels[oldIndex+1] = newPixels[newIndex+1]
            pixels[oldIndex+2] = newPixels[newIndex+2]
    changingW = newWidth
    changingH = newHeight
    
# Ф-ия вычисления весов для кубической интерполяции
def bicubicWeight(x):
    absx = np.abs(x)
    if absx <= 1:
        return (1.5 * absx**3 - 2.5 * absx**2 + 1)
    elif absx < 2:
        return (-0.5 * absx**3 + 2.5 * absx**2 - 4 * absx + 2)
    else:
        return 0

# Бикубическая интерполяция. 
# По сравнению с методом ближайшего соседа имеет намного более сложный алгоритм
def bicubicScale(width, height, pixels, k):
    global changingW
    global changingH
    if k <= 0:
        return None
    
    # Желаемое разрешение
    newWidth = int(round(width * k))
    newHeight = int(round(height * k))

    # Создаём массив для пикселей
    newPixels = np.zeros(newWidth * newHeight * 3, dtype=np.float32) 

    # Заполняем новый массив пикселей
    for y in range(newHeight):
        for x in range(newWidth):

            xf = int(x / k)
            yf = int(y / k)

            # Следим за тем, чтоб не выйти из окна
            xf = max(0, min(xf, width - 1))
            yf = max(0, min(yf, height - 1))

            for c in range(3):# Итерация по каналам
                val = 0
                for i in range(-1, 3):
                    for j in range(-1, 3):
                        # Находим индексы
                        xInd = np.clip(xf + i, 0, width - 1)
                        yInd = np.clip(yf + j, 0, height - 1)
                        # Находим веса
                        weight_x = bicubicWeight(xf - xf - i)
                        weight_y = bicubicWeight(yf - yf - j)
                        # Аккумулируем значение по формуле
                        val += pixels[(3 * widthG * yInd) + xInd * 3 + c] * weight_x * weight_y
                # Следим за тем, чтобы не выйти за предел 0 - 255
                val = max(0, min(val, 255))
                newPixels[(3 * newWidth * y) + x * 3 + c] = val

    
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glReadPixels(0,0,widthG,heightG,GL_RGB, GL_UNSIGNED_BYTE, pixels)

    for y in range(newHeight):
        for x in range(newWidth):
            oldIndex = (3 * widthG * y) + x * 3
            newIndex = (3 * newWidth * y) + x * 3
            pixels[oldIndex] = int(newPixels[newIndex])
            pixels[oldIndex+1] = int(newPixels[newIndex+1])
            pixels[oldIndex+2] = int(newPixels[newIndex+2])

    changingW = newWidth
    changingH = newHeight

    







def main():
    global widthG
    global heightG
    global changingH
    global changingW
    image_stream = open('pic.png', 'rb')
    image = pyglet.image.load('C.jpg', file=image_stream).get_image_data()
    heightG = image.height
    widthG = image.width
    changingH = 3
    changingW = 3

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
                    changingH = heightG
                    changingW = widthG
                if event.key == pygame.K_2:
                    nearestNeighborScale(changingW,changingH,pixels,0.5)

                    
                if event.key == pygame.K_3:
                   nearestNeighborScale(changingW,changingH,pixels,100)
                if event.key == pygame.K_4:
                    bicubicScale(changingW,changingH,pixels,0.5)
                if event.key == pygame.K_5:
                   bicubicScale(changingW,changingH,pixels,25)
                if event.key == pygame.K_6:
                   medianFilter(widthG,heightG,pixels,2)
                if event.key == pygame.K_7:
                   medianFilter(widthG,heightG,pixels,3)
                if event.key == pygame.K_KP1:
                    rezFilter(widthG,heightG,pixels,2)
                if event.key == pygame.K_KP2:
                    rezFilter(widthG,heightG,pixels,4)
                if event.key == pygame.K_KP3:
                    rezFilter(widthG,heightG,pixels,6)
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


