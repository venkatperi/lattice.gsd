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

from util import int2color, int2color_tuple, count_colors

RED = 0.2295
BLUE = 0.00254


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

        # initialize the lattice to contain only red and blue cells and empty sites,
        # chosen randomly according to numRatio and density
        if onlyRedBlue:
            self.lattice = np.random.choice(
                [RED, BLUE],
                size=(self.x, self.y))

            try:
                if density != 1:
                    self.lattice = np.random.choice(
                        [0, RED, BLUE],
                        p=[1 - density, density * (1 - numRatio), density * numRatio],
                        size=(self.x, self.y))
            except ValueError:
                print("Density should be an integer or float")

        # initialize the lattice with a bunch of different types of cells
        # (represented as different colors)
        else:
            self.lattice = r(self.x, self.y)
            if density != 1:
                for bug in np.ravel(self.lattice):
                    if r() > density:
                        self.lattice[self.lattice == bug] = 0

            # killdict is a hashtable containing the killing effectiveness for each color
            killdict = d(list)  # type: defaultdict[Any, float]
            killdict[0] = 0

            for color in np.ravel(self.lattice):
                killdict[color] = r()

            killdict[0] = 0
            self.killdict = killdict

    def evolve(self, n_steps=1):
        """
        main function, moves the lattice forward n steps in time

        :param n_steps:
        """
        self.lock.acquire()
        self.generation += 1
        for t in range(n_steps):
            # pick lattice site
            try:
                j = np.random.randint(1, self.y - 2)
                i = np.random.randint(1, self.x - 2)
            except ValueError:
                # this will happen if you've chosen your lattice to be one dimensional
                i = 0
                j = np.random.randint(0, self.y - 1)

            # random death happens if slider>random float in [0,1]
            if self.slider > r():
                self.lattice[i, j] = np.random.choice(np.ravel(
                    self.lattice[i - 1:i + 2, j - 1:j + 2]))

            # else killing/filling a la IBM happens
            else:
                # get the neighborhood of the ith,jth 'pixel'
                neighborhood = self.lattice[i - 1:i + 2, j - 1:j + 2]

                # find number of species one (red, RED), 
                # species two (blue, BLUE)
                n_blue = np.size(neighborhood[neighborhood == BLUE])
                n_red = np.size(neighborhood[neighborhood == RED])

                # total number of differently colored cells in neighborhood
                n_enemy = np.size(
                    neighborhood[neighborhood != self.lattice[i, j]])

                # KILLING..........##########

                # if your lattice is one dimensional
                thresh = 0.5 if self.x == 1 else 2

                # site is filled with red bact
                if self.onlyRedBlue and self.lattice[i, j] == RED:
                    # if number of blue cells * their killing advantage * random number > 2,
                    # kill this red bacteria (replace with empty site)
                    if n_blue * r() * self.blueAdvantage > thresh and not self.defKillers:
                        self.lattice[i, j] = 0

                elif self.onlyRedBlue and self.lattice[
                    i, j] == BLUE:  # site is filled with a blue bacteria
                    if n_red * r() * self.redAdvantage > thresh and not self.defKillers:
                        self.lattice[i, j] = 0  # kill this bacteria

                # site is not empty and has neighbors (non-specific neighbors, different color)
                elif n_enemy > 0 and self.lattice[i, j] != 0:
                    enemy_weight = 0
                    for enemy in np.ravel(neighborhood):
                        if enemy != 0 and enemy != self.lattice[i, j]:
                            try:
                                enemy_weight += self.killdict[enemy]
                            except TypeError:
                                print("ERROR")
                                pass
                                # enemy_weight=enemy_weight+self.killdict[enemy][0];

                    # if enough enemies, kill this bacterium
                    if enemy_weight * r() > 2:
                        self.lattice[i, j] = 0

                    # FILLING ....... #########
                    elif self.lattice[i, j] == 0:  # site is empty
                        # fill with either red or blue
                        if self.onlyRedBlue and n_red + n_blue > 0:
                            if ((n_red * self.redGrowth + n_blue * self.blueGrowth) * r()) > 2:
                                if n_red * self.redGrowth * r() > n_blue * self.blueGrowth * r():
                                    self.lattice[i, j] = RED
                                else:
                                    self.lattice[i, j] = BLUE
                            else:
                                self.lattice[i, j] = 0

                        elif n_enemy > 0:
                            # find all the other colors in neighborhood
                            choices = np.ravel(neighborhood[neighborhood != 0])

                            # if no other cells in neighborhood then stay empty
                            if choices.size == 0:
                                self.lattice[i, j] = 0
                                continue

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
                            self.lattice[i, j] = np.random.choice(choices, p=choices2)
                            # self.lattice[i,j]=np.random.choice(np.ravel(neighborhood[neighborhood!=0]))

        self.lock.release()

    def to_rgb_image(self):
        """
        Convert lattice to a list of RGB tuples

        """
        r, g, b = (0, 0, 0)
        # img = np.empty((self.x, self.y, 3), dtype=np.uint8)
        # self.lock.acquire()
        for i in range(self.x):
            for j in range(self.y):
                x = self.lattice[i, j]
                pix = [(1000 * x % 255), int(10000 * x % 255), int(100000 * x % 255)]
                self.rgb_image[i, j] = pix
                r += 1 if pix[0] > 100 else 0
                g += 1 if pix[1] > 100 else 0
                b += 1 if pix[2] > 100 else 0
        self.counts = (r, g, b)
        # self.lock.release()
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
