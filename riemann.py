# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 23:29:58 2022
This program is intended for the examination of iterations on (x, y) that 
either do or do not tend to infinity for each point in a plane.
Conceptually, the plane is projected onto a sphere of unit radius resting 
on the origin. The program works to view a hemisphere in the following way: 
    * for each point in the plane's unit circle, map it by projecting 
    vertically to find the z coord.;
    * rotate the sphere the desired amount around the x and z axes;
    * project from z=2 (the top of the sphere as it now appears) through the
    new position, back to the plane, to find the associated x and y coordinates;
    * perform the desired iteration on that point: it is envisaged that the 
    return code is a colour which depends on the number of iterations completed;
    * the result is stored in a numpy array of the desired resolution;
    * using PIL the array can be displayed to screen and/or saved to file.
Parameters can be set when calling the program.
    
@author: Owner
(Many thanks to Karl-Heinz Becker and Michael Doerffler)
"""
from datetime import datetime
from numpy import ones, uint8
from PIL import Image
from sys import path
if not "../modules" in path:
    path.append('../modules')
from myMatrices import matrix_3x3
import myColour
from myMathOO import ComplexVar

class RiemannIteration():
    title = "Riemann"
    def __init__(self, **kwargs):
        self.seed = kwargs.setdefault("seed", [0, 0])
        self.setColour = kwargs.setdefault("setColour", [0xD0,0xFF,0xFF])
        self.infColour = kwargs.setdefault("infColour", [0x03,0x03,0x03])
        self.palette = kwargs.setdefault("palette", "3TEST")
        self.maxIter = kwargs.setdefault("maxIter", 100)
        self.xAngle = kwargs.setdefault("xAngle", 0)
        self.zAngle = kwargs.setdefault("zAngle", 0)
        self.imageRatio = kwargs.setdefault("imageRatio", 1)
        self.xSize = kwargs.setdefault("xSize", 400)
        self.showGtCircles = kwargs.setdefault("lines", True)
        self.saveImage = kwargs.setdefault("saveImage", True)
        self.showImage = kwargs.setdefault("showImage", True)

        self.set_matrices(self.xAngle+90, self.zAngle)
            #The values for the matrices mean that the angles can be  
            #understood as latitude and longitude (increasing Eastwards)
            
        self.ySize = int(self.xSize * self.imageRatio)
        self.xSeed = self.seed[0]
        self.ySeed = self.seed[1]

        self.contourColours = myColour.get_palette(self.palette)

        self.defaultColour = [0x80,0x80,0x80]
        self.lineColour = [0x60,0x60,0x60]
        self.ABSURD_ITER = 10000
        self.LIMIT = 49 #test whether heading for infinity

        self.MESSAGES = ["Look out kid, it's something you did"]

    def getContourColour(self, i):
        return self.contourColours[i%len(self.contourColours)]

    def set_matrices(self, xAngle, zAngle):
        self.x_rot = matrix_3x3()
        self.z_rot = matrix_3x3()
        self.x_rot.construct_x_rotation(xAngle)
        self.z_rot.construct_z_rotation(zAngle)

    def run(self):
        startTime = datetime.now()
        print("Time:", startTime.time(), "- Iterating...", self.maxIter)
        print("x angle", self.xAngle, "z angle", self.zAngle)
        print("Size =", self.xSize, "x", self.ySize)        

        #Initialise array
        self.iArray = ones((self.ySize, self.xSize, 3), dtype=uint8)
        
        #Perform iteration
        self.traverse_array(self.xSize, self.ySize)
        
        im = Image.fromarray(self.iArray)
        if self.showImage:
            im.show()
        if self.saveImage:
            self.save_image(im)

        print("Runtime =", datetime.now() - startTime)

    def traverse_array(self, xSize, ySize):
        #Determine increase per pixel
        xIncr = (2/xSize)
        yIncr = (2/ySize)
        
        x = -1
        for xPixel in range(xSize):
            y = -1
            for yPixel in range(ySize):
                #Initialise pixel
                hypSq = x*x + y*y
                colour = self.defaultColour
                #Is it outside unit circle?
                if hypSq > 1:
                    self.iArray[yPixel, xPixel] = colour
                    y += yIncr
                    continue
                #Otherwise...
                xMap, yMap, gtCircle = self.mapping(x, y)
                #Will we draw great circle here?
                if gtCircle and self.showGtCircles:
                    colour = self.lineColour
                else:
                    #for MBrot, iterate(z, c)
                    colour = self.iterate(self.xSeed, self.ySeed,
                                          xMap, yMap,
                                          self.setColour,
                                          self.maxIter, self.LIMIT)
                #end_if
                self.iArray[(ySize -1 -yPixel), xPixel] = colour
                y += yIncr
            #end_for_y    
            x += xIncr
        #end_for_x
        return

    def mapping(self, x, y):
        LINE_GRADE = 0.003 #used for great circles
        greatCircle = False
        z = - (1 - (x*x + y*y))**(0.5)
        v = [x, y, z] # coords on sphere
        v = self.x_rot.matrix_v_multiply(v)
        v = self.z_rot.matrix_v_multiply(v)
        if v[2] == 1:
            x, y = 0, 0
        else:
            x = v[0]/(1-v[2])
            y = v[1]/(1-v[2])
            if abs(v[0]) < LINE_GRADE \
               or abs(v[1]) < LINE_GRADE \
                  or abs(v[2]) < LINE_GRADE:
                      greatCircle = True
        return x, y, greatCircle

    def iterate(self, x1, y1, x2, y2, colour, maxIter, limit, colours):
        return self.defaultColour

    def save_image(self, image):
        try:
            image.save("../images/temprimage.png", format="PNG")
        except:
            print("Couldn't save file")


class MbrotRIter(RiemannIteration):
        
    """
    Here follows an alternative version using (my own) ComplexVar, however ...
    it is much slower.
    ----------------------------------------------------------
    
    def iterate(self, x1, y1, x2, y2, colour, maxIter, limit, colours):
        var1 = ComplexVar(x1, y1)
        var2 = ComplexVar(x2, y2)
        for i in range(maxIter):
            #Compute:
            #  determine what colour the pixel should have
            var1 = var1.mult_complex(var1).minus(var2)
            #if too large:
            if var1.abs_val() > limit:
                colour = colours[i%len(colours)]
                break
        #end_for_i
        return colour

    ------------------------------------------------------------
    """
    #Old version
    def iterate(self, x1, y1, x2, y2, colour, maxIter, limit, colours):
        x_sq = x1*x1
        y_sq = y1*y1
        d_sq = x_sq + y_sq
        for i in range(maxIter):
            #compute
            y1 = x1 * y1
            y1 = y1 + y1 - y2
            x1 = x_sq - y_sq - x2
            x_sq = x1*x1
            y_sq = y1*y1
            d_sq = x_sq + y_sq
            #test
            too_large = d_sq > limit
            if too_large:
                colour = super().getContourColour(i)
                break
        #end_for_i
        return colour
        
class MbrotRRealPower(RiemannIteration):
    #Allows choice of value for power in 'z := z**power - c'

    def __init__(self, **kwargs):
        self.zPower = kwargs.setdefault("zPower", 2)
        super().__init__(**kwargs)
      
    def iterate(self, x1, y1, x2, y2, colour, maxIter, limit):
        var1 = ComplexVar(x1, y1)
        var2 = ComplexVar(x2, y2)
        for i in range(maxIter):
            #Compute:
            #  determine what colour the pixel should have
            var1 = var1.power_dm(self.zPower).minus(var2)
            #if too large:
            if var1.abs_val() > limit:
                colour = super().getContourColour(i)
                break
        #end_for_i
        return colour

if __name__ == "__main__":
    tc=2
    if tc==0:
        myIter = RiemannIteration()
    if tc==1:
        myIter = MbrotRIter(xAngle=-90, zAngle=0, palette = "3CAL_0")
    if tc==2:
        myIter = MbrotRRealPower(xAngle=40, zAngle=-70, zPower=2.2,\
                                    maxIter=60, palette = "9BL_GR")
    myIter.run()