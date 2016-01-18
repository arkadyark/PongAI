from collections import namedtuple
import pygame

__author__ = 'Christopher'


# #################################
# A class that lets you mark certain places on the board
# Call draw_things in the file/ class that has control of the board.
# Call mark in the file that you want to debug.

class VisualDebugger(object):
    BOX = "shape:box"
    POINT = "shape:point"
    Shape = namedtuple("Shape", ['shape', 'place', 'colour', 'priority'])

    def __init__(self, table_size):
        """
        Constructor
        :param table_size:  2-tuple of the x and y size of the table
        """

        self.table_size = table_size
        self.things_to_draw_once = []  # things that should be drawn once and then cleared from the screen
        # list of (named) tuples (shape, place, colour, priority),
        # type is a string; where is a tuple
        self.things_to_draw_continuously = []  # things to be drawn until cleared. Format same as things_to_draw_once

    def mark(self, shape, place, colour, priority=1, persistent=False):
        """
        Draw a cross at (x, y). Priority is the level it should be drawn at. Higher means it will get drawn on top.
        :param shape:   a string representing where to mark. These are represented by static variables in VisualDebugger
        :param place:   a tuple containing the coordinates. BOX requires 4: (x1,y1,x2,y2), POINT requires 2:(x,y)
        :param colour:  int colour (e.g. 0xFF0000 == red)
        :param priority:   representing what level it gets drawn. Higher means on top of things. Defaults to 1.
        :param persistent:  boolean representing whether the shape is drawn only for one tick (False) or remains on the
                            screen until cleared.
        """
        if persistent:
            self.things_to_draw_continuously.append(VisualDebugger.Shape(shape, place, colour, priority))
        else:
            self.things_to_draw_once.append(VisualDebugger.Shape(shape, place, colour, priority))

    def clear(self, hard=False, min_priority=float('inf')):
        """
        Clear everything that should be drawn once if the priority is less than priority
        :param hard:        if hard clear, it also clears the things that are always redrawn.
        :param min_priority:    the minimum priority to avoid being cleared. Defaults to infinity.
        """
        if hard:
            self.things_to_draw_continuously = [i for i in self.things_to_draw_continuously if
                                                i.priority > min_priority]
        self.things_to_draw_once = [i for i in self.things_to_draw_once if i.priority > min_priority]

    def draw_things(self, surface):
        """
        Draw the list of things to draw to surface. Clears the list of things to draw once.
        :param surface:     A pygame.Surface object
        """

        draw_me = self.things_to_draw_continuously + self.things_to_draw_once
        draw_me.sort(key=lambda x: x.priority)

        # The list of shapes to draw

        for shape in draw_me:
            if shape.shape == VisualDebugger.BOX:
                pygame.draw.rect(surface, shape.colour, shape.place)
            elif shape.shape == VisualDebugger.POINT:
                pygame.draw.line(surface, shape.colour, (shape.place[0] - 5, shape.place[1] - 5),
                                 (shape.place[0] + 5, shape.place[1] + 5), 3)
                pygame.draw.line(surface, shape.colour, (shape.place[0] + 5, shape.place[1] - 5),
                                 (shape.place[0] - 5, shape.place[1] + 5), 3)
        self.clear()
