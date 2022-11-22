""" Date 22 Nov 22
Generic GUI to set up creation of image from Julia style iterations. Taken 
from earlier program mbrot_np, rev. 2.5.
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
@author: Owner
"""
from sys import path
if not "../modules" in path:
    path.append('../modules')
import myColour
import numpy as np
from datetime import datetime
from tkinter import Tk, Frame, Label, StringVar, Entry, Button, E, W
from PIL import Image
#
# Iterate ??
#
class GenIteration():
    title = "Generic"
    
    def __init__(self, master, **kwargs):
        self.seed = kwargs.setdefault("seed", [0, 0])
        self.setColour = kwargs.setdefault("setColour", [0xD0,0xFF,0xFF])
        self.infColour = kwargs.setdefault("infColour", [0x03,0x03,0x03])
        self.palette = kwargs.setdefault("palette", "3TEST")
        self.maxIter = kwargs.setdefault("maxIter", 100)
        self.xStart = kwargs.setdefault("xStart", -2)
        self.xEnd = kwargs.setdefault("xEnd", 2)
        self.yStart = kwargs.setdefault("yStart", -1.5)
        self.imageRatio = kwargs.setdefault("imageRatio", 0.75)
        self.xSize = kwargs.setdefault("xSize", 720)
        self.saveImage = kwargs.setdefault("saveImage", False)
        self.showImage = kwargs.setdefault("showImage", True)
        
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

        self.ABSURD_ITER = 10000
        self.LIMIT = 49


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
        self.moreButton = Button(self.frame, text="More", \
                                 width=6, command=self.more_input)
        self.moreButton.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.currentColumn += 1
        self.runButton = Button(self.frame, text="Go", \
                                 width=6, command=self.iteration)
        self.runButton.grid(row=self.currentRow, column=self.currentColumn)

    def auto_y(self):
        #Set the end value for y, according to defined ratio
        try:
            self.xStart = float(self.xStartText.get())
            self.xEnd = float(self.xEndText.get())
            self.yStart = float(self.yStartText.get())
            self.yEnd = self.yStart + \
                         (self.xEnd - self.xStart) * self.imageRatio
            self.yEntry2.delete(0,"end")
            self.yEntry2.insert(0, str(self.yEnd))
        except ValueError:
            self.messageText.set(self.MESSAGES[2])

        
    def more_input(self):
        #The assumption is that the user now wants contours to be shown.
        #Adjustments to how they are displayed are made possible below.
        #Further, there is a facility to set the seed value for z.
        self.moreButton["state"] = "disable"
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

    def save_image(self, image):
        try:
            image.save("tempgimage.png", format="PNG")
        except:
            print("Couldn't save file")
    

    def iteration(self):        

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

        #Make start less than end
        if self.xEnd < self.xStart:
            self.xStart, self.xEnd = self.xEnd, self.xStart
        if self.yEnd < self.yStart:
            self.yStart, self.yEnd = self.yEnd, self.yStart
        #Determine increase per pixel
        self.xIncr = (self.xEnd - self.xStart)/self.xSize
        self.yIncr = (self.yEnd - self.yStart)/self.ySize

        self.iArray = np.ones((self.ySize, self.xSize, 3), dtype=np.uint8)

        self.calculate()

        im = Image.fromarray(self.iArray)
        if self.showImage:
            im.show()
        if self.saveImage:
            self.save_image(im)

        print("Runtime =", datetime.now() - startTime)
        self.runButton["state"] = "active"
        self.messageText.set(self.MESSAGES[0])

    def calculate(self):
        #Dummy calculation
        for xPixel in range(self.xSize):
            for yPixel in range(self.ySize):
                #Initialise pixel
                colour = self.defaultColour
                # - do something - 
                for i in range(self.maxIter):
                    #Compute:
                    #  determine what colour the pixel should have
                    break
                #end_for_i
                self.iArray[(self.ySize -1 -yPixel), xPixel] = colour
            #end_for_y    
        #end_for_x
        return
    
    def contour(self, i):
        index = i % len(self.contourColours)
        return self.contourColours[index]


class Julia(GenIteration):
    """ 
    Date 21 Nov 22
    Julia iteration
    @author: Owner
    
    Interesting c values:
        0.7454054, 0.1130063
        0.745428, 0.113009
    """
    title = "Julia:  z0 = x, iy;  z := z**2 - c;  c fixed"
    #It is possible to change the initial "seed" value of c
    #via the generic GUI
    
    def calculate(self):
        xCurrent = self.xStart
        for xPixel in range(self.xSize):
            yCurrent = self.yStart
            for yPixel in range(self.ySize):
                x = xCurrent
                y = yCurrent
                xSq = x*x
                ySq = y*y
                dSq = xSq + ySq
                for i in range(self.maxIter):
                    #Compute
                    y = x*y
                    y = y + y - self.ySeed
                    x = xSq - ySq - self.xSeed
                    xSq = x*x
                    ySq = y*y
                    dSq = xSq + ySq
                    #Tst
                    tooLarge = dSq > self.LIMIT
                    if tooLarge:
                        if self.contourInputActive == True:
                            if i > self.contourStart:
                                colour = self.contour(i)
                            else:
                                colour = self.infColour
                        else:
                            colour = self.infColour
                        break
                    else:
                        continue
                #end_for_i
                if not tooLarge:
                    colour = self.setColour
                self.iArray[(self.ySize -1 -yPixel), xPixel] = colour
                yCurrent += self.yIncr
            #end_for_y    
            xCurrent += self.xIncr
        #end_for_x
    
class Mandelbrot(GenIteration):
    """ 
    Date 21 Nov 22
    Mandelbrot iteration
    @author: Owner
    """    
    title = "Mandelbrot Delay:  z0 = 0;  z := z**2 - c;  c = (x, iy)"
    #It is possible to change the initial "seed" value of z0 
    #via the generic GUI
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("seed", [0, 0])
        kwargs.setdefault("xStart", -1)
        kwargs.setdefault("xEnd", 2)
        kwargs.setdefault("yStart", -1.125)
        kwargs.setdefault("imageRatio", 0.75)
        
        GenIteration.__init__(self, master, **kwargs)
        
    def calculate(self):
        cReal = self.xStart
        for xPixel in range(self.xSize):
            cImag = self.yStart
            for yPixel in range(self.ySize):
                x = self.xSeed
                y = self.ySeed
                xSq, ySq, = x*x, y*y
                dSq = xSq + ySq
                colour = self.setColour
                for i in range(self.maxIter):
                    #Compute
                    y = x*y
                    y = y + y - cImag
                    x = xSq - ySq - cReal
                    xSq = x*x
                    ySq = y*y
                    dSq = xSq + ySq
                    #Test
                    tooLarge = dSq > self.LIMIT
                    if tooLarge:
                        if self.contourInputActive == True:
                            if i > self.contourStart:
                                colour = self.contour(i)
                            else:
                                colour = self.infColour
                        else:
                            colour = self.infColour
                        break
                    else:
                            continue
                #end_for_i
                self.iArray[(self.ySize -1 -yPixel), xPixel] = colour
                cImag += self.yIncr
            #end_for_y    
            cReal += self.xIncr
        #end_for_x
        

#MAIN
current = "M"
root = Tk()
if current == "J":
    myGUI = Julia(root, seed=[0.745405, 0.113006], palette="3CAL2_0")
if current == "M":
    myGUI = Mandelbrot(root, xStart=-1, xEnd=2, yStart=-1.125)
root.mainloop()
