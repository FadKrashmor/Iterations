# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 13:46:06 2022

@author: Owner
"""

from sys import path
if not "../modules" in path:
    path.append('../modules')
import myColour
from feigenbaum import Feigenbaum

class FeigColour(Feigenbaum):
    """ 11 Dec 22
    Colourful, standard function. Perhaps gives insight into period doubling.
    """
    def __init__(self, **kwargs):  
        self.palette = kwargs.setdefault("palette", "8RAINBOW")
        self.contourColours = myColour.get_palette(self.palette)
        super().__init__(**kwargs)

    def choose_colour(self, i):
        return self.contourColours[i%len(self.contourColours)]
        
#MAIN
if __name__ == "__main__":
    obj = FeigColour(ignore=96, maxIter=192)
    obj.image()