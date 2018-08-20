def int2color(x):
    """
    converts lattice integer to RGB tuple
    :param x: int
    :return: RGB
    """
    # r = int(1000 * x % 255)
    # g = int(10000 * x % 255)
    # b = int(100000 * x % 255)
    x = 0 if x == 0 else int(1/x)
    b = x & 0xff
    g = (x >> 8) & 0xff
    r = (x >> 16) & 0xff
    return [r, g, b]


def has_colors(pix):
    return (1 if pix[0] > 100 else 0,
            1 if pix[1] > 100 else 0,
            1 if pix[2] > 100 else 0)


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
