from PIL import Image
import math


def pixelation(image: str, width: int, height: int, palette: list):
    img = Image.open(image)
    if img is None:
        return None

    
    img = img.convert('RGBA')
    img = img.resize((width, height))
    pixels = list(img.getdata())
    print(pixels)
    cnt = 0
    res = []
    print(pixels)
    for i in range(height):
        res.append([])
        for j in range(width):
            if pixels[i * width + j][-1] == 0:
                res[i].append(-1)
            else:
                pixel = rgbToHex(pixels[i * width + j])
                idx = findIndex(pixel, palette)
                res[i].append(idx)

    return list(res)


def rgbToHex(rgb):
    return '#%02x%02x%02x' % rgb[:-1]


def findIndex(color: list, palette: list):
    distance = []
    color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    for j in range(len(palette)):
        currentColor = tuple(
            int(palette[j].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        get_distance = math.sqrt(
            sum([(a - b) ** 2 for a, b in zip(currentColor, color)]))
        distance.append(get_distance)

    index = distance.index(min(distance))
    return index
