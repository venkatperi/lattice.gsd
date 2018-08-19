def int2color(x):
    """
    converts lattice integer to RGB tuple
    :param x: int
    :return: RGB
    """
    r = int(1000 * x % 255)
    g = int(10000 * x % 255)
    b = int(100000 * x % 255)
    return [r, g, b]


def int2color_tuple(x):
    """
    converts lattice integer to RGB tuple
    :param x: int
    :return: RGB
    """
    red_val = int(1000 * x % 255)
    green_val = int(10000 * x % 255)
    blue_val = int(100000 * x % 255)
    return red_val, green_val, blue_val


def count_colors(total, current):
    for i in range(0, 3):
        if current[i] > 100:
            total[i] += 1
    return total