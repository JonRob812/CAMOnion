import math


def rotate_point(point, angle, center=(0, 0)):
    x, y = point
    if angle == 0:
        return x, y
    angle = math.radians(angle)
    center_x, center_y = center
    sin = math.sin(angle)
    cos = math.cos(angle)
    temp_x = x + center_x
    temp_y = y + center_y
    rotated_temp_x = temp_x * cos + temp_y * sin
    rotated_temp_y = (temp_x * -1) * sin + temp_y * cos
    x = round(rotated_temp_x - center_x, 4)
    if x == 0:
        x = abs(x)
    y = round(rotated_temp_y - center_y, 4)
    if y == 0:
        y = abs(y)
    return x, y
