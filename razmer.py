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
# Во сколько уменьшать\увеличивать изображение
SCALE = 2

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
                val = max(0, min(val, 255))
                newPixels[(3 * newWidth * y) + x * 3 + c] = val

    # Подготваливаемся к дальнейшей отрисовке
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
    changingH = heightG
    changingW = widthG

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
                    nearestNeighborScale(changingW,changingH,pixels,1/SCALE)
                if event.key == pygame.K_3:
                   nearestNeighborScale(changingW,changingH,pixels,SCALE)
                if event.key == pygame.K_4:
                    bicubicScale(changingW,changingH,pixels,1/SCALE)
                if event.key == pygame.K_5:
                   bicubicScale(changingW,changingH,pixels,SCALE)
        glDrawPixels(widthG, heightG, GL_RGB, GL_UNSIGNED_BYTE, pixels)                 
        pygame.display.flip()
        pygame.time.wait(12)
main() 


