#!/usr/bin/env nix-shell
# !nix-shell -p pythonPackages.pillow -i python
# http://www.mattkandler.com/blog/duotone-image-filter-javascript-rails

from PIL import Image


def grayscale(img, pixels):
    r_max = 0
    r_min = 255

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = pixels[i, j]

            # Fetch maximum and minimum pixel values
            r_max = max(r_max, r)
            r_min = min(r_min, r)

            # Grayscale by averaging RGB values
            v = int((1. / 3) * r + (1. / 3) * g + (1. / 3) * b)
            pixels[i, j] = (v, v, v)

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = pixels[i, j]

            # Normalize each pixel to scale 0-255
            v = int((r - r_min) * (255. / (r_max - r_min)))
            pixels[i, j] = (v, v, v)

    return pixels


def hex_to_rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def gradient_map(tone1, tone2):
    r1, g1, b1 = hex_to_rgb(tone1)
    r2, g2, b2 = hex_to_rgb(tone2)

    gradient = []

    for i in range(256):
        r = int(((256 - i) * r1 + i * r2) / 256.)
        g = int(((256 - i) * g1 + i * g2) / 256.)
        b = int(((256 - i) * b1 + i * b2) / 256.)
        gradient.append((r, g, b))

    return gradient


def duotone(img, tone1='#002957', tone2='#f86c58'):
    pixels = grayscale(img, img.load())
    gradient = gradient_map(tone1, tone2)
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = pixels[i, j]
            r = gradient[r][0]
            g = gradient[g][1]
            b = gradient[b][2]
            pixels[i, j] = (r, g, b)
    return pixels

# img = Image.open('image.jpg')
# duotone(img, '#002957', '#f86c58')
# img.save('duotone.jpg')
