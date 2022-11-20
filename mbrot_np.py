# Date 18 Nov 22
# Rev 2.0 : Automatic calculation of end_y
#           Reports runtime
#     2.1 : Facility to change first three contour colours
#     2.2 : Rationalisation of how contours are handled
#     2.3 : (26 Oct 22) Except ValueError protection for auto_y
#     2.4 : (18 Nov 22) Camel case for variables.
#                       Loads contour palette from dictionary in myColour
#
from sys import path
if not "../modules" in path:
    path.append('../modules')
import myColour
import numpy as np
from datetime import datetime
from tkinter import Tk, Frame, Label, StringVar, Entry, Button, E, W
from PIL import Image
#
# Iterate z_new := z**2 - c, for range of values of c, z0 = 0
#
# The initial figures give the same scale for x and y.
#
class MandelbrotGUI:
    
    def __init__(self, master):
        self.master = master
        master.title("Mandelbrot Delay:  z0 = 0;  z := z**2 - c;  c = (x, iy)")

        self.SAVE_IMAGE = True
        self.SHOW_IMAGE = True
        
        self.setColour = [0xFA,0xE8,0xD7]
        #gold=FFD700, AntiqueWhite=FAEBD7
        self.GONE = (0x03,0x03,0x03) #Headed off to infinity?              
        self.contourColours = myColour.get_palette("RAINBOW")
        self.showContours = False

        self.maxIter = 192 
        self.ABSURD_ITER = 10000
        self.xStart = 0.748207
        self.xEnd = 0.748555
        self.yStart = 0.068471
        self.xSize = 720
        self.IMAGE_RATIO = 3/4
        self.yEnd = self.yStart + \
                     (self.xEnd - self.xStart) * self.IMAGE_RATIO
        self.ySize = int(self.xSize * self.IMAGE_RATIO)
        print("Size =", self.xSize, "x", self.ySize)
        self.LIMIT = 49

        self.MESSAGES = ["Ready",
                         "Please enter iterations: ",
                        "Please enter ranges",
                        "Look out kid, it's something you did",
                        "Please enter nr. of contours",
                        "Please enter hex value for colour"]

        self.LABELS =  ["Iterations: ",
                        "Range x: ",
                        "Range y: ",
                        "I don't know when but you're doing it again",
                        "Contours"]

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
        self.iEntry.grid(row=self.currentRow, column=self.currentColumn)

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
        self.runButton = Button(self.frame, text="Go", \
                                 width=6, command=self.iter_complex)
        self.runButton.grid(row=self.currentRow, column=self.currentColumn)

    def auto_y(self):
        #Set the end value for y, according to defined ratio
        try:
            self.xStart = float(self.xStartText.get())
            self.xEnd = float(self.xEndText.get())
            self.yStart = float(self.yStartText.get())
            self.yEnd = self.yStart + \
                         (self.xEnd - self.xStart) * self.IMAGE_RATIO
            self.yEntry2.delete(0,"end")
            self.yEntry2.insert(0, str(self.yEnd))
        except ValueError:
            self.messageText.set(self.MESSAGES[2])

        
    def more_input(self):
        # The assumption is that the user now wants contours to be shown.
        # Adjustments to how they are displayed are made possible below.
        self.moreButton["state"] = "disable"
        self.showContours = True
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
                             sticky=E)

        self.currentColumn += 1
        self.setColText = StringVar()
        self.setColText.set(myColour.rgb_hexstring(self.setColour))
        self.setButton = Button(self.frame, text="SET",\
                                 bg="#"+self.setColText.get(), width=4,
                                 command=self.change_set_col)
        self.setButton.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.setEntry = Entry(self.frame, textvariable=self.setColText, 
                               width=7)
        self.setEntry.grid(row=self.currentRow, column=self.currentColumn,
                            sticky=W)
                
        self.currentColumn += 1
        self.cont0Text = StringVar()
        self.cont0Text.set(myColour.rgb_hexstring(self.contourColours[0]))
        self.cont0Button = Button(self.frame, text="C0",\
                                 bg="#"+self.cont0Text.get(), width=4,
                                 command=self.change_c0_col)
        self.cont0Button.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.cont0Entry = Entry(self.frame, textvariable=self.cont0Text, 
                                width=7)
        self.cont0Entry.grid(row=self.currentRow, column=self.currentColumn,
                              sticky=W)
                
        self.currentColumn += 1
        self.cont1Text = StringVar()
        self.cont1Text.set(myColour.rgb_hexstring(self.contourColours[1]))
        self.cont1Button = Button(self.frame, text="C1",\
                                 bg="#"+self.cont1Text.get(), width=4,
                                 command=self.change_c1_col)
        self.cont1Button.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.cont1Entry = Entry(self.frame, textvariable=self.cont1Text, 
                                width=7)
        self.cont1Entry.grid(row=self.currentRow, column=self.currentColumn,
                              sticky=W)
                
        self.currentColumn += 1
        self.cont2Text = StringVar()
        self.cont2Text.set(myColour.rgb_hexstring(self.contourColours[2]))
        self.cont2Button = Button(self.frame, text="C2",\
                                 bg="#"+self.cont2Text.get(), width=4,
                                 command=self.change_c2_col)
        self.cont2Button.grid(row=self.currentRow, column=self.currentColumn)

        self.currentColumn += 1
        self.cont2Entry = Entry(self.frame, textvariable=self.cont2Text, 
                                width=7)
        self.cont2Entry.grid(row=self.currentRow, column=self.currentColumn,
                              sticky=W)
                
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
            image.save("tempmimage.png", format="PNG")
        except:
            print("Couldn't save file")
    

    def iter_complex(self):        

        while True:
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
                if self.showContours == True:
                    contourStart = self.maxIter - \
                                     int(self.contourText.get()) - 1
                    print("Start after contour:", contourStart)
            except ValueError:
                self.messageText.set(self.MESSAGES[4])
                return
            break

        self.runButton["state"] = "disable"
        startTime = datetime.now()
        print("Iterating...", self.maxIter)
        print("x start", self.xStart, ": x end", self.xEnd)
        print("y start", self.yStart, ": y end", self.yEnd)
        if self.xEnd < self.xStart:
            self.xStart, self.xEnd = self.xEnd, self.xStart
        if self.yEnd < self.yStart:
            self.yStart, self.yEnd = self.yEnd, self.yStart
        self.xIncr = (self.xEnd - self.xStart)/self.xSize
        self.yIncr = (self.yEnd - self.yStart)/self.ySize

        iArray = np.ones((self.ySize, self.xSize, 3), dtype=np.uint8)
        cReal = self.xStart
        for xPixel in range(self.xSize):
            cImag = self.yStart
            for yPixel in range(self.ySize):
                x = 0
                y = 0
                xSq, ySq, dSq = 0, 0, 0
                colour = self.setColour
                for i in range(self.maxIter):
                    try:
                        #compute
                        y = x*y
                        y = y + y - cImag
                        x = xSq - ySq - cReal
                        xSq = x*x
                        ySq = y*y
                        dSq = xSq + ySq
                        #test
                        tooLarge = dSq > self.LIMIT
                        if tooLarge:
                            if self.showContours == True:
                                if i > contourStart:
                                    colour = self.contour(i)
                                else:
                                    colour = self.GONE
                            else:
                                colour = self.GONE
                            break
                        else:
                            continue
                    except OverflowError:
                         print("Overflow: i=", i, "x=", x, "y=", y)
                         self.overflow = True
                         break
                #end_for_i
                iArray[(self.ySize -1 -yPixel), xPixel] = colour
                cImag += self.yIncr
            #end_for_y    
            cReal += self.xIncr
        #end_for_x

        im = Image.fromarray(iArray)
        if self.SHOW_IMAGE:
            im.show()
        if self.SAVE_IMAGE:
            self.save_image(im)

        print("Runtime =", datetime.now() - startTime)
        self.runButton["state"] = "active"
        self.messageText.set(self.MESSAGES[0])

    def contour(self, i):
        index = i % len(self.contourColours)
        return self.contourColours[index]


root = Tk()
my_gui = MandelbrotGUI(root)
root.mainloop()
