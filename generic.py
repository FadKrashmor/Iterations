"""
Generic GUI to set up creation of image from Julia style iterations. Taken 
from earlier program mbrot_np, rev. 2.5. Some iterations are defined in child 
classes below.
Rev 1.0 - 21 Nov 22
    Features:
    * Facility to match x and y scales.
    * Allows specific number of contours to be shown (via "More" button).
    * It includes the facility to alter "set colour", "infinity colour" and 
      the first three contour colours (a colour palette from module myColour 
      is pre-selected).
    * Allows for an (contextual) "seed value"" to be set.
    * Reports runtime, and other info to console.
    * Can display result of iteration to screen and write to file (.png) 
Rev 1.1 - 22 Nov 22
    * Initialisation effected by keyword arguments
Rev 1.2 - 24 Nov 22
    * Streamlining, function z2_minus_c() now generic.
Rev 1.3 - 29 Nov 22
    * Separation of array traverse and iteration on pixel. Three sub-classes:
    (Julia, Mandelbrot and M<andel>brotRealPower)
Rev 2.0 - 30 Nov 22
    * Minor adjustments. A significant milestone has been reached.
Rev 2.1 - 07 Dec 22
    * LIMIT now a parameter. (e.g. escape radius for Mandelbrot iteration).
    * Adds an iteration for cube roots of one (Newton's method).
Rev 2,2 - 12 Dec 22
    * Parameterised filename
Rev 2.3 - 14 Dec 22
    * Adds speculative class MagModel1
Rev 2.4 - 21 Dec 22
    * Reversed sign in Julia/Mandelbrot function
    * That function now also returns |z|*2, this is an optimisation
    * Mandelbrot class iteration contains nascent alternative contour-colouring 
      mechanism; Generic class has a button to toggle this on and off.
Rev 2.5 - 24 Dec 22
    * The developing contour-colouring mechanism is now in get_contour_colour
    * More checks on xStart/xEnd sizes
@author: Owner
(Many thanks to Karl-Heinz Becker and Michael Doerffler)
"""
from sys import path
if not "../modules" in path:
    path.append('../modules')
import numpy as np
from datetime import datetime
from scipy import nextafter
from tkinter import Tk, Frame, Label, StringVar, Entry, Button, E, W
from PIL import Image
import myColour
from myMathOO import ComplexVar
#from math import log
#
# Iterate ??
#
class GenIteration():
    title = "Generic"
    
    def __init__(self, master, **kwargs):
        self.seed = kwargs.setdefault("seed", [0, 0])
        self.setColour = kwargs.setdefault("setColour", [0xD0,0xFF,0xFF])
        self.infColour = kwargs.setdefault("infColour", [0x00,0x00,0x00])
        self.palette = kwargs.setdefault("palette", "3TEST")
        self.maxIter = kwargs.setdefault("maxIter", 100)
        self.limit = kwargs.setdefault("limit", 25)
        self.xStart = kwargs.setdefault("xStart", -2)
        self.xEnd = kwargs.setdefault("xEnd", 2)
        self.yStart = kwargs.setdefault("yStart", -1.5)
        self.imageRatio = kwargs.setdefault("imageRatio", 0.75)
        self.xSize = kwargs.setdefault("xSize", 720)
        self.saveImage = kwargs.setdefault("saveImage", False)
        self.fname = kwargs.setdefault("fname", "../images/tempgimage.png")
        self.showImage = kwargs.setdefault("showImage", True)
        
        if self.xEnd < self.xStart:
            self.xStart, self.xEnd = self.xEnd, self.xStart
        self.yEnd = self.yStart + \
                     (self.xEnd - self.xStart) * self.imageRatio
        self.ySize = int(self.xSize * self.imageRatio)
        print("Size =", self.xSize, "x", self.ySize)
        
        self.xSeed = self.seed[0]
        self.ySeed = self.seed[1]
        self.seedInputActive = False
        
        self.defaultColour = [0x80,0x80,0x80]
        #gold=FFD700, AntiqueWhite=FAEBD7
        self.contourColours = myColour.get_palette(self.palette)
        self.contourInputActive = False
        self.redField = False
        self.REDOFFSET = 64

        self.ABSURD_ITER = 10000


        self.master = master
        master.title(self.title)

        self.MESSAGES = ["Ready",
                         "Please enter iterations: ",
                         "Please enter ranges",
                         "Look out kid, it's something you did",
                         "Please enter nr. of contours",
                         "Please enter hex value for colour",
                         "Please enter seed value"]

        self.LABELS =  ["Iterations: ",
                        "Range x: ",
                        "Range y: ",
                        "I don't know when but you're doing it again",
                        "Contours",
                        "Seed x",
                        "Seed y"]

        self.frame = Frame(master)
        self.frame.grid()

        self.currentRow = 0
        self.currentColumn = 0
        self.messageText = StringVar()
        self.messageText.set(self.MESSAGES[0])
        self.mLabel = Label(self.frame, textvariable=self.messageText)
        self.mLabel.grid(row=self.currentRow, column=self.currentColumn, 
                          columnspan=5, sticky=W)

        self.currentRow += 1
        self.iLabelText = StringVar()
        self.iLabelText.set(self.LABELS[0])
        self.iLabel = Label(self.frame, textvariable=self.iLabelText)
        self.iLabel.grid(row=self.currentRow, column=self.currentColumn, 
                          sticky=E)

        self.currentColumn += 1
        self.maxIterText = StringVar()
        self.iEntry = Entry(self.frame, textvariable=self.maxIterText, width=4)
        self.iEntry.insert(0, str(self.maxIter))
        self.iEntry.grid(row=self.currentRow, column=self.currentColumn, 
                         sticky=W)

        self.currentColumn += 1
        self.xLabelText = StringVar()
        self.xLabelText.set(self.LABELS[1])
        self.xLabel = Label(self.frame, textvariable=self.xLabelText)
        self.xLabel.grid(row=self.currentRow, column=self.currentColumn, sticky=E)

        self.currentColumn += 1
        self.xStartText = StringVar()
        self.xEntry1 = Entry(self.frame, textvariable=self.xStartText, width=10)
        self.xEntry1.insert(0, str(self.xStart))
        self.xEntry1.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.xEndText = StringVar()
        self.xEntry2 = Entry(self.frame, textvariable=self.xEndText, width=10)
        self.xEntry2.insert(0, str(self.xEnd))
        self.xEntry2.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.yLabelText = StringVar()
        self.yLabelText.set(self.LABELS[2])
        self.yLabel = Label(self.frame, textvariable=self.yLabelText)
        self.yLabel.grid(row=self.currentRow, column=self.currentColumn, sticky=E)

        self.currentColumn += 1
        self.yStartText = StringVar()
        self.yEntry1 = Entry(self.frame, textvariable=self.yStartText, width=10)
        self.yEntry1.insert(0, str(self.yStart))
        self.yEntry1.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.yEndText = StringVar()
        self.yEntry2 = Entry(self.frame, textvariable=self.yEndText, width=10)
        self.yEntry2.insert(0, str(self.yEnd))
        self.yEntry2.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.yAutoButton = Button(self.frame, text="Auto y", \
                                 width=6, command=self.auto_y)
        self.yAutoButton.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.redButton = Button(self.frame, text="Red!", \
                                 width=6, command=self.toggle_redField)
        self.redButton.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.moreButton = Button(self.frame, text="More", \
                                 width=6, command=self.more_input)
        self.moreButton.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.runButton = Button(self.frame, text="Go", \
                                 width=6, command=self.create_image)
        self.runButton.grid(row=self.currentRow, column=self.currentColumn)

    def auto_y(self):
        #Set the end value for y, according to defined ratio
        try:
            self.xStart = float(self.xStartText.get())
            self.xEnd = float(self.xEndText.get())
            if self.xEnd < self.xStart:
                self.xStart, self.xEnd = self.xEnd, self.xStart
            self.yStart = float(self.yStartText.get())
            self.yEnd = self.yStart + \
                         (self.xEnd - self.xStart) * self.imageRatio
            self.yEntry2.delete(0,"end")
            self.yEntry2.insert(0, str(self.yEnd))
        except ValueError:
            self.messageText.set(self.MESSAGES[2])
        
    def toggle_redField(self):
        if self.redField == False:
            self.redField = True
            self.redButton.config(relief="sunken")
        else:
            self.redField = False
            self.redButton.config(relief="raised")
        print("red!", self.redField)

    def more_input(self):
        #The assumption is that the user now wants contours to be shown.
        #Adjustments to how they are displayed are made possible below.
        #Further, there is a facility to set the seed value for z.
        self.moreButton["state"] = "disable"
        if self.redField == True:
            self.redField = False
            self.redButton.config(relief="raised")
        print("red!", self.redField)
        self.contourInputActive = True
        self.currentRow += 1

        self.currentColumn = 0
        self.contLabelText = StringVar()
        self.contLabelText.set(self.LABELS[4])
        self.contLabel = Label(self.frame, textvariable=self.contLabelText)
        self.contLabel.grid(row=self.currentRow, column=self.currentColumn,
                             sticky=E)

        self.currentColumn += 1
        self.contourText = StringVar()
        self.contEntry = Entry(self.frame, textvariable=self.contourText, 
                                width=4)
        self.contEntry.insert(0, str(self.maxIter))
        self.contEntry.grid(row=self.currentRow, column=self.currentColumn,
                            sticky=W)

        self.currentColumn += 1
        self.setColText = StringVar()
        self.setColText.set(myColour.rgb_hexstring(self.setColour))
        self.setButton = Button(self.frame, text="SET",\
                                 bg="#"+self.setColText.get(), width=4,
                                 command=self.change_set_col)
        self.setButton.grid(row=self.currentRow, column=self.currentColumn,
                            sticky=E)

        self.currentColumn += 1
        self.setEntry = Entry(self.frame, textvariable=self.setColText, 
                               width=6)
        self.setEntry.grid(row=self.currentRow, column=self.currentColumn)
                
        self.currentColumn += 1
        self.infColText = StringVar()
        self.infColText.set(myColour.rgb_hexstring(self.infColour))
        self.infButton = Button(self.frame, text="INF",\
                                 bg="#"+self.infColText.get(), width=4,
                                 command=self.change_inf_col)
        self.infButton.grid(row=self.currentRow, column=self.currentColumn,
                            sticky=E)

        self.currentColumn += 1
        self.infEntry = Entry(self.frame, textvariable=self.infColText, 
                               width=6)
        self.infEntry.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.cont0Text = StringVar()
        self.cont0Text.set(myColour.rgb_hexstring(self.contourColours[0]))
        self.cont0Button = Button(self.frame, text="C0",\
                                 bg="#"+self.cont0Text.get(), width=4,
                                 command=self.change_c0_col)
        self.cont0Button.grid(row=self.currentRow, column=self.currentColumn,
                              sticky=E)

        self.currentColumn += 1
        self.cont0Entry = Entry(self.frame, textvariable=self.cont0Text, 
                                width=6)
        self.cont0Entry.grid(row=self.currentRow, column=self.currentColumn)
                
        self.currentColumn += 1
        self.cont1Text = StringVar()
        self.cont1Text.set(myColour.rgb_hexstring(self.contourColours[1]))
        self.cont1Button = Button(self.frame, text="C1",\
                                 bg="#"+self.cont1Text.get(), width=4,
                                 command=self.change_c1_col)
        self.cont1Button.grid(row=self.currentRow, column=self.currentColumn,
                              sticky=E)

        self.currentColumn += 1
        self.cont1Entry = Entry(self.frame, textvariable=self.cont1Text, 
                                width=6)
        self.cont1Entry.grid(row=self.currentRow, column=self.currentColumn)
                
        self.currentColumn += 1
        self.cont2Text = StringVar()
        self.cont2Text.set(myColour.rgb_hexstring(self.contourColours[2]))
        self.cont2Button = Button(self.frame, text="C2",\
                                 bg="#"+self.cont2Text.get(), width=4,
                                 command=self.change_c2_col)
        self.cont2Button.grid(row=self.currentRow, column=self.currentColumn,
                              sticky=E)

        self.currentColumn += 1
        self.cont2Entry = Entry(self.frame, textvariable=self.cont2Text, 
                                width=6)
        self.cont2Entry.grid(row=self.currentRow, column=self.currentColumn)
                
        #New row adds entries for seed value
        self.seedInputActive = True
        self.currentRow += 1
        self.currentColumn = 0
        self.xSeedLabelText = StringVar()
        self.xSeedLabelText.set(self.LABELS[5])
        self.xSeedLabel = Label(self.frame, textvariable=self.xSeedLabelText)
        self.xSeedLabel.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.xSeedText = StringVar()
        self.xSeedEntry = Entry(self.frame, textvariable=self.xSeedText, 
                                width=9)
        self.xSeedEntry.insert(0, str(self.xSeed))
        self.xSeedEntry.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.ySeedLabelText = StringVar()
        self.ySeedLabelText.set(self.LABELS[6])
        self.ySeedLabel = Label(self.frame, textvariable=self.ySeedLabelText)
        self.ySeedLabel.grid(row=self.currentRow, column=self.currentColumn,
                             sticky=E)

        self.currentColumn += 1
        self.ySeedText = StringVar()
        self.ySeedEntry = Entry(self.frame, textvariable=self.ySeedText, 
                                width=9)
        self.ySeedEntry.insert(0, str(self.ySeed))
        self.ySeedEntry.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1

    def change_set_col(self):
        newColour = self.setColText.get()
        print("New set colour:", newColour)
        if len(newColour) == 6:
            try:
                myColour.change_colour(newColour, self.setColour)
                self.setButton.config(bg="#"+newColour)
            except ValueError:
                self.messageText.set(self.MESSAGES[5])
        else:
            self.messageText.set(self.MESSAGES[5])

    def change_inf_col(self):
        newColour = self.infColText.get()
        print("New inf colour:", newColour)
        if len(newColour) == 6:
            try:
                myColour.change_colour(newColour, self.infColour)
                self.infButton.config(bg="#"+newColour)
            except ValueError:
                self.messageText.set(self.MESSAGES[5])
        else:
            self.messageText.set(self.MESSAGES[5])

    def change_c0_col(self):
        newColour = self.cont0Text.get()
        print("New contour colour:", newColour)
        if len(newColour) == 6:
            try:
                myColour.change_colour(newColour, self.contourColours[0])
                self.cont0Button.config(bg="#"+newColour)
            except ValueError:
                self.messageText.set(self.MESSAGES[5])
        else:
            self.messageText.set(self.MESSAGES[5])

    def change_c1_col(self):
        newColour = self.cont1Text.get()
        print("New contour colour:", newColour)
        if len(newColour) == 6:
            try:
                myColour.change_colour(newColour, self.contourColours[1])
                self.cont1Button.config(bg="#"+newColour)
            except ValueError:
                self.messageText.set(self.MESSAGES[5])
        else:
            self.messageText.set(self.MESSAGES[5])

    def change_c2_col(self):
        newColour = self.cont2Text.get()
        print("New contour colour:", newColour)
        if len(newColour) == 6:
            try:
                myColour.change_colour(newColour, self.contourColours[2])
                self.cont2Button.config(bg="#"+newColour)
            except ValueError:
                self.messageText.set(self.MESSAGES[5])
        else:
            self.messageText.set(self.MESSAGES[5])

    def get_contour_colour(self, i, maxIter):
        if self.redField == True:
            #I have not yet understood what this messing with logs is 
            #about:
            #[increase accuracy by iterating again, if required
            #zReal, zImag = self.function(zReal, zImag, cReal, cImag)]
            #then:
            #temp = log(zReal*zReal + zImag*zImag)
            #temp = i + 1 - log(temp/log(limit), 2)
            #
            #iterationFactor = temp/maxIter???
            #
            #But you could simply do the following:
            #iterationFactor = i/maxIter
            #index = int(iterationFactor*len(self.contourColours))
            #
            #Temporarily, so that the program runs here...
            colour = self.infColour.copy()
            remaining = maxIter - i
            if remaining < self.REDOFFSET:
                #so that we get some bright pixels next to the set
                colour[0] = 256 - remaining
            else:
                if maxIter < 256:
                    colour[0] = (colour[0] + i)
                else:
                    iterationFactor = int((i)*256/maxIter)
                    colour[0] = (colour[0] + iterationFactor)
        else: 
            #Alternative method of cycling colour palette:
            if self.contourInputActive == True:
                if i > self.contourStart:
                    colour = self.contourColours[i%len(self.contourColours)]
                else:
                    colour = self.infColour
            else:
                colour = self.infColour
        return colour

    def create_image(self):        
        while True:
            #Read input values
            try:
                self.maxIter = int(self.maxIterText.get())
                if self.maxIter <= 1 or self.maxIter > self.ABSURD_ITER:
                    self.messageText.set(self.MESSAGES[1])
                    return
            except ValueError:
                self.messageText.set(self.MESSAGES[1])
                return
            try:
                self.xStart = float(self.xStartText.get())
                self.xEnd = float(self.xEndText.get())
                self.yStart = float(self.yStartText.get())
                self.yEnd = float(self.yEndText.get())
            except ValueError:
                self.messageText.set(self.MESSAGES[2])
                return
            try:
                if self.contourInputActive == True:
                    self.contourStart = self.maxIter - \
                                     int(self.contourText.get()) - 1
                    print("Start after contour:", self.contourStart)
            except ValueError:
                self.messageText.set(self.MESSAGES[4])
                return
            try:
                if self.seedInputActive == True:
                    self.xSeed = float(self.xSeedText.get())
                    self.ySeed = float(self.ySeedText.get())
                print("Seed: ", self.xSeed, self.ySeed)
            except ValueError:
                self.messageText.set(self.MESSAGES[6])
                return
            break

        self.runButton["state"] = "disable"
        startTime = datetime.now()
        print(startTime.time(), "- Iterating...", self.maxIter)
        print("x start", self.xStart, ": x end", self.xEnd)
        print("y start", self.yStart, ": y end", self.yEnd)


        self.iArray = np.ones((self.ySize, self.xSize, 3), dtype=np.uint8)

        self.traverse_array(self.iArray, self.xStart, self.xEnd, 
                            self.yStart, self.yEnd, self.xSize, self.ySize)

        im = Image.fromarray(self.iArray)
        if self.showImage:
            im.show()
        if self.saveImage:
            self.save_image(im)

        print("Runtime =", datetime.now() - startTime)
        self.runButton["state"] = "active"
        self.messageText.set(self.MESSAGES[0])

    def traverse_array(self, array, xStart, xEnd, yStart, yEnd, xSize, ySize):
        #Make start less than end
        if xEnd < xStart:
            xStart, xEnd = xEnd, xStart
        if yEnd < yStart:
            yStart, yEnd = yEnd, yStart
        #Determine increase per pixel
        xIncr = (xEnd - xStart)/xSize
        yIncr = (yEnd - yStart)/ySize

        x = xStart
        for xPixel in range(xSize):
            y = yStart
            for yPixel in range(ySize):
                # - do something -
                colour = self.iterate(self.xSeed, self.ySeed, 
                                      x, y, self.setColour, 
                                      self.maxIter, self.limit)
                array[(ySize -1 -yPixel), xPixel] = colour
                y+= yIncr
            #end_for_y
            x += xIncr
        #end_for_x

    def iterate(self, x1, y1, x2, y2, colour, maxIter, limit):
        #Dummy iteration
        for i in range(self.maxIter):
            #Compute:
            #  determine what colour the pixel should have
            break
        #end_for_i
        return colour
    
    def save_image(self, image):
        try:
            image.save(self.fname, format="PNG")
        except:
            print("Couldn't save file")
                
                   
class Julia(GenIteration):
    """ 
    Date: 21 Nov 22
    Julia iteration
    @author: Owner
    
    Interesting c values:
        -0.7454054, -0.1130063
        -0.745428, -0.113009
    """
    title = "Julia:  z0 = x, iy;  z := z**2 + c;  c fixed"
    #It is possible to change the initial "seed" value of c
    #via the generic GUI
    
    def iterate(self, cReal, cImag, zReal, zImag, colour, maxIter, limit):
        for i in range(maxIter):
            #Compute next z value
            zReal, zImag, rSq = self.function(zReal, zImag, cReal, cImag)
            #Test
            if rSq > limit:
                colour = self.get_contour_colour(i, maxIter)
                break
        #end_for_i
        return colour

    def function(self, x, y, cr, ci):
        #Compute z**2 + c
        xSq = x*x
        ySq = y*y
        y = x*y
        y = y + y + ci
        x = xSq - ySq + cr
        return x, y, (xSq + ySq)

class Mandelbrot(GenIteration):
    """ 
    Date: 21 Nov 22
    Mandelbrot iteration
    @author: Owner
    """    
    title = "Mandelbrot:  z0 = 0;  z := z**2 + c;  c = (x, iy)"
    #It is possible to change the initial "seed" value of z0 
    #via the generic GUI
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("seed", [0, 0])
        kwargs.setdefault("xStart", -2)
        kwargs.setdefault("xEnd", 1)
        kwargs.setdefault("yStart", -1.125)
        kwargs.setdefault("imageRatio", 0.75)
        
        super().__init__(master, **kwargs)
        
    def iterate(self, zReal, zImag, cReal, cImag, colour, maxIter, limit):
        for i in range(maxIter):
            #Compute next z value
            zReal, zImag, rSq = self.function(zReal, zImag, cReal, cImag)
            #Test
            if rSq > limit:
                colour = self.get_contour_colour(i, maxIter)
                break
        #end_for_i
        return colour

    def function(self, x, y, cr, ci):
        #Compute z**2 + c
        xSq = x*x
        ySq = y*y
        y = x*y
        y = y + y + ci
        x = xSq - ySq + cr
        return x, y, (xSq + ySq)


class MbrotRealPower(GenIteration):
    """ 
    Date: 29 Nov 22
    Mandelbrot iteration, variable power
    @author: Owner
    """
    title = "Mandelbrot++:  z0 = 0;  z := z**power - c;  c = (x, iy)"

    def __init__(self, master, **kwargs):
        self.zPower = kwargs.setdefault("zPower", 3)
        kwargs.setdefault("seed", [0, 0])
        kwargs.setdefault("xStart", -1.6)
        kwargs.setdefault("xEnd", 1.6)
        kwargs.setdefault("yStart", -1.2)
        kwargs.setdefault("imageRatio", 0.75)
        
        super().__init__(master, **kwargs)
        
    def iterate(self, zReal, zImag, cReal, cImag, colour, maxIter, limit):
        var1 = ComplexVar(zReal, zImag)
        var2 = ComplexVar(cReal, cImag)
        for i in range(maxIter):
            #Compute next z value
            var1 = var1.power_dm(self.zPower).plus(var2)
            #Test
            if var1.abs_val() > limit:
                colour = self.get_contour_colour(i, maxIter)
                break
        #end_for_i
        return colour

class NCubeRoot1(GenIteration):
    """
    Date: 07 Dec 22
    Shows contours in the basins of attraction for the cube roots of one,
    approached using Newton's method.
    """
    title = "Cube Root (Newton)"

    def __init__(self, master, **kwargs):
        kwargs.setdefault('setColour', [0xFF,0x40,0x40])
        kwargs.setdefault('palette', '4CAL_4')
        kwargs.setdefault('maxIter', 16)
        kwargs.setdefault("limit", 0.0025)

        super().__init__(master, **kwargs)

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
                x = nextafter(0,1)
                continue
            x_sq, y_sq, d_sq = x*x, y*y, (x*x + y*y)
            temp = 3*(d_sq*d_sq)
            x_new = 2*x/3 + (x_sq - y_sq)/temp
            y_new = 2*y/3 - 2*x*y/temp
            rootFound = self.belongs_to_root(x_new, y_new, limit)
            if rootFound:
                return self.get_contour_colour(i, maxIter)
            x = x_new
            y = y_new
        #end_for_i
        return colour


class MagModel1(GenIteration):
    """ 
    Date: 14 Dec 22
    Magnetism Model 1
    @author: Owner
    """
    title = "Magnetism model 1"

    def __init__(self, master, **kwargs):
        kwargs.setdefault("seed", [0, 0])
        kwargs.setdefault("xStart", -0.9)
        kwargs.setdefault("xEnd", 3.5)
        kwargs.setdefault("yStart", -2.2)
        kwargs.setdefault("imageRatio", 1)
        kwargs.setdefault("maxIter", 64)
        kwargs.setdefault("xSize", 400)
        
        super().__init__(master, **kwargs)
        
    def iterate(self, zReal, zImag, cReal, cImag, colour, maxIter, limit):
        var1 = ComplexVar(zReal, zImag)
        var2 = ComplexVar(cReal, cImag)
        for i in range(maxIter):
            #Compute next z value
            var1 = self.function(var1, var2)
            #Test
            if var1.abs_val() > limit:
                colour = self.get_contour_colour(i, maxIter)
                break
        #end_for_i
        return colour

    def function(self, var1, var2):
        temp1 = var1.power(2).plus(var2).add_c1(-1)
        temp2 = var1.times(2).plus(var2).add_c1(-2)
        return temp1.divide(temp2).power(2)
    
"""
MAIN
"""
if __name__ == "__main__":
    current = "j"
    root = Tk()
    if current == "g":
        myGUI = GenIteration(root)
    if current == "j":
        myGUI = Julia(root, seed=[-0.745405, -0.113006], palette="3CAL_0")
    if current == "m":
        myGUI = Mandelbrot(root, palette="9BL_GR")
    if current == "m2":
        myGUI = Mandelbrot(root, xStart=0.6258, xEnd=0.6264, yStart=0.40332, 
                           xSize=600, palette="10CAL_10", maxIter=550)
    if current == "n":
        myGUI = NCubeRoot1(root, xSize=800, maxIter=12)
    if current == "p":
        myGUI = MbrotRealPower(root, zPower=5, maxIter=60, limit=49)
    if current == "mag1":
        myGUI = MagModel1(root, maxIter=80, xSize=400, palette="10CAL_10")

    root.mainloop()
