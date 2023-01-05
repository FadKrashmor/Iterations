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
    * project from the top of the sphere as it now appears through the
      new position, back to the plane, to find the associated x and y coordinates;
    * perform the desired iteration on that point: it is envisaged that the 
      return code is a colour which depends on the number of iterations completed;
    * the result is stored in a numpy array of the desired resolution;
    * using PIL the array can be displayed to screen and/or saved to file.
Parameters can be set when calling the program.
Rev 1.1 - 22 Dec 22
    * Reversed sign in function
    * Parameterised default colour and limit (square of escape radius)
Rev 1.2 - 26 Dec 22
    * Parameterised file directory and file name for image
Rev 1.3 - 04 Jan 23
    * Increased default size (to 500); default saveImage := False
    * Name for function changed: get_contour_colour; it is now called by 
      referring to self rather than super().
    * Added class NRCubeRoot1 (copied from version in file "generic" - and 
      modified, isn't that just the problem!)
    * Added class NRComplexRoot, to show basins of attaction for the nth roots
      of one.
@author: Owner
(Many thanks to Karl-Heinz Becker and Michael Doerffler)
"""
from datetime import datetime
from numpy import ones, uint8
from PIL import Image
from sys import path
from math import pi
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
        self.defColour = kwargs.setdefault("defColour", [0x00,0x00,0x00])
        self.palette = kwargs.setdefault("palette", "3TEST")
        self.maxIter = kwargs.setdefault("maxIter", 100)
        self.limit = kwargs.setdefault("limit", 49)
        self.xAngle = kwargs.setdefault("xAngle", 0)
        self.zAngle = kwargs.setdefault("zAngle", 0)
        self.imageRatio = kwargs.setdefault("imageRatio", 1)
        self.xSize = kwargs.setdefault("xSize", 500)
        self.showGtCircles = kwargs.setdefault("lines", True)
        self.saveImage = kwargs.setdefault("saveImage", False)
        self.showImage = kwargs.setdefault("showImage", True)
        self.fileDir = kwargs.setdefault("fileDir", "../images")
        self.fileName = kwargs.setdefault("fileName", "temprimage")
        
        self.set_matrices(self.xAngle+90, self.zAngle)
            #The values for the matrices mean that the angles can be  
            #understood as latitude and longitude (increasing Westwards)
            
        self.ySize = int(self.xSize * self.imageRatio)
        self.xSeed = self.seed[0]
        self.ySeed = self.seed[1]

        self.contourColours = myColour.get_palette(self.palette)

        self.lineColour = [0x60,0x60,0x60]
        self.ABSURD_ITER = 10000
        self.MESSAGES = ["Look out kid, it's something you did"]

    def get_contour_colour(self, i):
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
        for self.xPixel in range(xSize):
            y = -1
            for self.yPixel in range(ySize):
                #Initialise pixel
                hypSq = x*x + y*y
                colour = self.defColour
                #Is it outside unit circle?
                if hypSq > 1:
                    self.iArray[self.yPixel, self.xPixel] = colour
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
                                          self.maxIter, self.limit)
                #end_if
                self.iArray[(self.ySize -1 -self.yPixel), self.xPixel] = colour
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

    def iterate(self, x1, y1, x2, y2, colour, maxIter, limit):
        return self.defColour

    def save_image(self, image):
        try:
            image.save(self.fileDir + "/" + self.fileName + ".png", format="PNG")
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
            var1 = var1.mult_complex(var1).plus(var2)
            #if too large:
            if var1.abs_val() > limit:
                colour = colours[i%len(colours)]
                break
        #end_for_i
        return colour

    ------------------------------------------------------------
    """
    #Old version
    def iterate(self, x1, y1, x2, y2, colour, maxIter, limit):
        x_sq = x1*x1
        y_sq = y1*y1
        d_sq = x_sq + y_sq
        for i in range(maxIter):
            #compute
            y1 = x1 * y1
            y1 = y1 + y1 + y2
            x1 = x_sq - y_sq + x2
            x_sq = x1*x1
            y_sq = y1*y1
            d_sq = x_sq + y_sq
            #test
            if d_sq > limit:
                colour = self.get_contour_colour(i)
                break
        #end_for_i
        return colour
        
class MbrotRRealPower(RiemannIteration):
    #Allows choice of value for power in 'z := z**power + c'

    def __init__(self, **kwargs):
        self.zPower = kwargs.setdefault("zPower", 2)
        super().__init__(**kwargs)
      
    def iterate(self, x1, y1, x2, y2, colour, maxIter, limit):
        var1 = ComplexVar(x1, y1)
        var2 = ComplexVar(x2, y2)
        for i in range(maxIter):
            #Compute:
            #  determine what colour the pixel should have
            var1 = var1.power_dm(self.zPower).plus(var2)
            #if too large:
            if var1.abs_val() > limit:
                colour = self.get_contour_colour(i)
                break
        #end_for_i
        return colour


class NRCubeRoot1(RiemannIteration):
    """
    Date: 04 Jan 23
    Shows contours in the basins of attraction for the cube roots of one,
    approached using Newton's method.
    """
    title = "Cube Root (Newton)"

    def __init__(self, **kwargs):
        kwargs.setdefault('setColour', [0xFF,0x40,0x40])
        kwargs.setdefault('palette', '4CAL_4')
        kwargs.setdefault('maxIter', 16)
        kwargs.setdefault('limit', 0.0025)
        kwargs.setdefault('lines', False)
        super().__init__(**kwargs)

    def belongs_to_root(self, x, y, limit):
        #given (x,y), is the point close to one of the cube roots of one?
        #returns 0 if not; 1, 2 or 3 depending on which root is close
        if ((x+0.5)**2 + (y+0.8660254)**2) < limit:
            return 1
        elif ((x+0.5)**2 + (y-0.8660254)**2) < limit:
            return 2
        elif ((x-1)**2 + y**2) < limit:
            return 3
        else:
            return 0
    
    def iterate(self, xSeed, ySeed, x, y, colour, maxIter, limit):
        # Find cube roots of 1 using Newton's method
        # Internally:
        #   0: root not yet determined
        #   1, 2 or 3 for each respective root
        rootFound = 0
        for i in range(maxIter):
            if (x==0) and (y==0):
                break
            try:
                xSq, ySq, dSq = x*x, y*y, (x*x + y*y)
                temp = 3*(dSq*dSq)
                xNew = 2*x/3 + (xSq - ySq)/temp
                yNew = 2*y/3 - 2*x*y/temp
            except ArithmeticError:
                print("Arithmetic Error: x={}, y={}, i={}".format(x, y, i))
                break
            rootFound = self.belongs_to_root(xNew, yNew, limit)
            if rootFound:
                return self.get_contour_colour(i)
            x = xNew
            y = yNew
        #end_for_i
        return colour


class NRComplexRoot(RiemannIteration):
    """
    Date: 04 Jan 23
    Shows contours in the basins of attraction for the nth roots of one,
    approached using Newton's method.
    """
    title = "Complex Root (Newton)"

    def __init__(self, n, **kwargs):
        self.TWOPI = 2*pi
        self.power = n
        self.testAngle = self.TWOPI/n
        kwargs.setdefault('setColour', [0xFF,0x40,0x40])
        kwargs.setdefault('palette', '4CAL_4')
        kwargs.setdefault('maxIter', 20)
        kwargs.setdefault('limit', 0.005)
        kwargs.setdefault('lines', False)
        super().__init__(**kwargs)
        
    def belongs_to_root(self, z, limit):
        #Is it close to one of the roots? return 0 for no.
        #(one value for limit is used for both tests (size and angle))
        zPolar = z.cart_to_polar()
        if abs(zPolar.val_r() - 1) < limit: #it's on the unit circle...
            if abs(zPolar.val_angle()) < limit: #...and it's really one
                return 1
            else:
                if zPolar.val_angle() < 0:
                    zPolar = zPolar.add_angle(self.TWOPI)
                for j in range(1, self.power):
                    if abs(zPolar.val_angle() - j*self.testAngle) < limit:
                        return j + 1
        return 0
    
    def iterate(self, xSeed, ySeed, x, y, colour, maxIter, limit):
        #Find roots of 1 using Newton's method
        #Internally:
        #   0: root not yet determined
        #   1, 2, 3... for each respective root
        rootFound = 0
        z = ComplexVar(x, y)
        for i in range(maxIter):
            if (x==0) and (y==0):
                break
            try:
                divisor = z.power_dm(self.power - 1).times(self.power)
                zNew = z.minus(z.power_dm(self.power).add_real(-1).divide(divisor))
            except ArithmeticError:
                print("Arithmetic Error: x={}, y={}, i={}".format(x, y, i))
                break
            rootFound = self.belongs_to_root(zNew, limit)
            if rootFound:
                return self.get_contour_colour(i)
            z = zNew
        #end_for_i
        return colour

#MAIN
if __name__ == "__main__":
    tc=4
    if tc==0:
        myIter = RiemannIteration()
        myIter.run()
    if tc==1:
        myIter = MbrotRIter(xAngle=-0, zAngle=0, palette = "3CAL_0")
        myIter.run()
    if tc==2:
        myIter = MbrotRRealPower(xAngle=40, zAngle=70, zPower=2.2,\
                                    maxIter=60, palette = "9BL_GR")
        myIter.run()
    if tc==3:
        myIter = NRCubeRoot1(xAngle=-30, zAngle=0, xSize=600, maxIter=12)
        myIter.run()
    if tc==4:
        myIter = NRComplexRoot(8, xAngle=-30, zAngle=0, maxIter=60,
                               limit=0.01)
        myIter.run()
