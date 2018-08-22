#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 10:51:05 2016

@author: dyanni3
"""
# %% imports and prep
from threading import Lock

import numpy as np
from numpy.random import rand as r
from collections import defaultdict as d, defaultdict
from PIL import Image
from functools import reduce

from util import int2color, int2color_tuple, count_colors, has_colors

# RED = 0.2295
# RED = 0.1841900
# BLUE = 0.00254
# BLUE = 0.01234

RED = 1.0 / float(0xe41a1c)
BLUE = 1.0 / float(0x377eb8)


# BLUE = 1.0  / 0x4daf4a


class Lattice(object):
    def __init__(self, size=100, slider=0, onlyRedBlue=False,
                 redAdvantage=1, blueAdvantage=1, defKillers=False, density=1,
                 numRatio=1, redGrowth=1, blueGrowth=1, deathRate=100000000,
                 antibioticDeath=1):
        """

        :type slider: float, optional
        if slider is 0 then only killing happens, if slider is 1 then only "random death"
        and for a range between it's a mixture. Default 0.

        :type onlyRedBlue: bool, optional
        True means the lattice contains only red and blue bacteria. Defaults to False

        :type size: int or tuple of ints, optional
        Size of the lattice. If the given size is an int, the lattice is assumed to be
        square, i.e. size=[value, value]. For a non-square lattice, use size=[x,y]. Defaults
        to 100 for [100,100] lattice.

        :type redAdvantage: float, optional
        killing disparity, 1 means equal killers. Defaults to 1

        :type blueAdvantage: float, optional
        killing disparity, 1 means equal killers. Defaults to 1

        :type redGrowth: float, optional
        1 for equal growth. Defaults to 1

        :type blueGrowth: float, optional
        1 for equal growth. Defaults to 1

        :type defKillers: bool, optional
        if true (defective killers), killers then red and blue can't kill each other. Defaults
        to False

        :type density: float, optional
        overall cell density at initialization of the lattice. Defaults to 1

        :type numRatio: float, optional
        overall number ratio (number of blue/ total number of cells). Default 1

        """
        self.onlyRedBlue = onlyRedBlue
        self.slider = slider
        self.redGrowth = redGrowth
        self.blueGrowth = blueGrowth
        self.redAdvantage = redAdvantage
        self.blueAdvantage = blueAdvantage
        self.defKillers = defKillers
        self.density = density
        self.numRatio = numRatio
        self.size = size
        self.generation = 0
        self.lock = Lock()
        self.surface = None
        self.counts = (0, 0, 0)  # number of red, blue, green pixels

        try:
            self.x, self.y = size[1], size[0]
        except TypeError:
            self.x, self.y = size, size

        self.rgb_image = np.empty((self.x, self.y, 3), dtype=np.uint8)

        # if defective killers set to true then there's no random death either
        # (no killing, no random death)
        if defKillers:
            self.slider = 0

        self.lattice, self.killdict = self.create_red_blue_lattice(density, numRatio) \
            if onlyRedBlue else \
            self.create_other_lattice(density)

        self.to_rgb_image()

    def create_other_lattice(self, density):
        """
        initialize the lattice with a bunch of different types of cells
        (represented as different colors)
        :param density:
        """
        lattice = r(self.x, self.y)
        if density != 1:
            for bug in np.ravel(lattice):
                if r() > density:
                    lattice[lattice == bug] = 0
        # killdict is a hashtable containing the killing effectiveness for each color
        killdict = d(list)  # type: defaultdict[Any, float]
        killdict[0] = 0
        for color in np.ravel(lattice):
            killdict[color] = r()
        killdict[0] = 0
        return lattice, killdict

    def create_red_blue_lattice(self, density, numRatio):
        """
        initialize the lattice to contain only red and blue cells and empty sites,
        chosen randomly according to numRatio and density
        :param density:
        :param numRatio:
        :return:
        """
        try:
            if density != 1:
                return np.random.choice(
                    [0, RED, BLUE],
                    p=[1.0 - density, density * (1.0 - numRatio), density * numRatio],
                    size=(self.x, self.y)), None
            else:
                return np.random.choice([RED, BLUE], size=(self.x, self.y)), None
        except ValueError:
            print("ERROR: Density should be an integer or float")
            exit(-1)

    def set(self, i, j, value):
        """
        Sets lattice value at pixel (i,j). Also updates rgb_image(i,j)
        as well as red/blue counts.
        :param i:
        :param j:
        :param value:
        """
        self.lattice[i, j] = value
        prev = has_colors(self.rgb_image[i, j])
        color = self.rgb_image[i, j] = int2color(value)
        self.surface.set_at((i, j), color)
        x = has_colors(self.rgb_image[i, j])
        c = self.counts
        self.counts = (c[0] + x[0] - prev[0],
                       c[1] + x[1] - prev[1],
                       c[2] + x[2] - prev[2])

    def evolve(self, n_steps=1):
        """
        main function, moves the lattice forward n steps in time

        :param n_steps:
        """
        for t in range(n_steps):
            self.generation += 1

            # pick lattice site
            i, j = self.random_site

            # random death happens if slider>random float in [0,1]
            if self.slider > r():
                self.random_death(i, j)

            # else killing/filling a la IBM happens
            else:
                n_blue, n_enemy, n_red, neighborhood = \
                    self.get_neighborhood(i, j)

                # site is filled with red bact
                if self.onlyRedBlue and self.is_red(i, j):
                    self.kill_red(i, j, n_blue, self.thresh)

                # site is filled with a blue bacteria
                elif self.onlyRedBlue and self.is_blue(i, j):
                    self.kill_blue(i, j, n_red, self.thresh)

                elif n_enemy > 0 and not self.is_empty(i, j):
                    if self.has_enough_enemies(i, j, neighborhood):
                        self.kill(i, j)

                    # FILLING ....... #########
                    elif self.is_empty(i, j):
                        if self.onlyRedBlue and n_red + n_blue > 0:
                            self.fill_red_or_blue(i, j, n_blue, n_red)

                        elif n_enemy > 0:
                            if not self.fill_with_neighbor_color(i, j, neighborhood):
                                continue

    @property
    def thresh(self):
        return 0.5 if self.x == 1 else 2

    def get_neighborhood(self, i, j):
        # get the neighborhood of the ith,jth 'pixel'
        neighborhood = self.lattice[i - 1:i + 2, j - 1:j + 2]
        # find number of species one (red, RED),
        # species two (blue, BLUE)
        n_blue = np.size(neighborhood[neighborhood == BLUE])
        n_red = np.size(neighborhood[neighborhood == RED])
        # total number of differently colored cells in neighborhood
        n_enemy = np.size(neighborhood[neighborhood != self.lattice[i, j]])
        return n_blue, n_enemy, n_red, neighborhood

    def is_empty(self, i, j):
        return self.lattice[i, j] == 0

    def is_red(self, i, j):
        return self.lattice[i, j] == RED

    def is_blue(self, i, j):
        return self.lattice[i, j] == BLUE

    def fill_red_or_blue(self, i, j, n_blue, n_red):
        if ((n_red * self.redGrowth + n_blue * self.blueGrowth) * r()) > 2:
            if n_red * self.redGrowth * r() > n_blue * self.blueGrowth * r():
                self.set(i, j, RED)
            else:
                self.set(i, j, BLUE)
        else:
            self.kill(i, j)

    def fill_with_neighbor_color(self, i, j, neighborhood):
        # find all the other colors in neighborhood
        choices = np.ravel(neighborhood[neighborhood != 0])
        # if no other cells in neighborhood then stay empty
        if choices.size == 0:
            self.kill(i, j)
            return False

        # fill with one of the other colors in neighborhood
        # (according to number of cells)
        choices = list(choices)
        choices2 = [choice * (1 - self.killdict[choice]) for choice in choices]
        choices2 = [choice / len(choices2) for choice in choices2]
        zeroprob = 1 - sum(choices2)
        choices2.append(zeroprob)
        choices2 = np.array(choices2)
        choices.append(0)
        choices = np.array(choices)
        self.set(i, j, np.random.choice(choices, p=choices2))
        # self.lattice[i,j]=np.random.choice(np.ravel(neighborhood[neighborhood!=0]))
        return True

    def kill_blue(self, i, j, n_red, thresh):
        if n_red * r() * self.redAdvantage > thresh and not self.defKillers:
            self.set(i, j, 0)

    def kill_red(self, i, j, n_blue, thresh):
        """
        if number of blue cells * their killing advantage * random number > 2,
        kill this red bacteria (replace with empty site)
        :param i:
        :param j:
        :param n_blue:
        :param thresh:
        """
        if n_blue * r() * self.blueAdvantage > thresh and not self.defKillers:
            self.kill(i, j)

    def has_enough_enemies(self, i, j, neighborhood):
        return self.enemy_weight(i, j, neighborhood) * r() > 2

    def enemy_weight(self, i, j, neighborhood):
        enemy_weight = 0
        for enemy in np.ravel(neighborhood):
            if enemy != 0 and enemy != self.lattice[i, j]:
                try:
                    enemy_weight += self.killdict[enemy]
                except TypeError:
                    print("ERROR")
                    pass
                    # enemy_weight=enemy_weight+self.killdict[enemy][0];
        return enemy_weight

    def kill(self, i, j):
        self.set(i, j, 0)

    def random_death(self, i, j):
        self.set(i, j, np.random.choice(np.ravel(
            self.lattice[i - 1:i + 2, j - 1:j + 2])))

    @property
    def random_site(self):
        try:
            j = np.random.randint(1, self.y - 2)
            i = np.random.randint(1, self.x - 2)
        except ValueError:
            # this will happen if you've chosen your lattice to be one dimensional
            i = 0
            j = np.random.randint(0, self.y - 1)
        return i, j

    def to_rgb_image(self):
        """
        Convert lattice to a list of RGB tuples

        """
        r, g, b = (0, 0, 0)
        # img = np.empty((self.x, self.y, 3), dtype=np.uint8)
        for i in range(self.x):
            for j in range(self.y):
                x = self.lattice[i, j]
                self.rgb_image[i, j] = int2color(x)
                r += 1 if x == RED else 0
                b += 1 if x == BLUE else 0
        self.counts = (r, g, b)
        return self.rgb_image

    def view(self):
        """
        Convert lattice to an image

        :return:
        RGB image of the lattice
        """
        lu = list(map(int2color_tuple, np.ravel(self.lattice[:, :])))
        imu = Image.new('RGB', [self.lattice.shape[1], self.lattice.shape[0]])
        imu.putdata(lu)

        print(reduce(count_colors, lu, [0, 0, 0]))

        if not self.onlyRedBlue:
            return imu

        return imu
