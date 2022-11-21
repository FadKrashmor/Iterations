# R1.1 18 Nov 22
# Contains useful stuff for working with colours
#
paletteDict = {"TEST" :     [[0x00, 0x80, 0xF0], 
                             [0x00, 0x40, 0xB0],
                             [0x00, 0x00, 0x70]],
               "DEFAULT" :  [[0xA0, 0x10, 0x10], 
                             [0x10, 0xA0, 0x10],
                             [0x10, 0x10, 0xA0]],
               "PALETTE5" : [[0xA0, 0xFF, 0xFF], #Blues
                             [0x00, 0x00, 0x40],
                             [0x10, 0x00, 0xE0],
                             [0x40, 0x80, 0xFF],
                             [0x03, 0x03, 0x03]],
               "PORTUGAL" : [[0x00, 0x10, 0x80], #Colours of Portuguese flag
                             [0x10, 0x80, 0x10],
                             [0xf0, 0xd0, 0x00],
                             [0xFF, 0x00, 0x00],
                             [0xFC, 0xFC, 0xFC]],
               "RAINBOW" :  [[0xB0,0x20,0x20],
                             [0xFF,0x80,0x20],
                             [0xFF,0xD7,0x00],
                             [0x40,0xB0,0x30],
                             [0x40,0x90,0xA0],
                             [0x60,0x60,0xC0],
                             [0x00,0x00,0xF0],
                             [0x60,0x10,0xA0]]
               }

def change_colour(new_colour, rgb_list=None):
    #Converts Hex string (without leading "#") to rgb integer list elements
    if rgb_list == None:
        rgb_list = []
        for i in range(3):
            rgb_list.append[0]
    rgb_list[0] = int(new_colour[0:2], 16)
    rgb_list[1] = int(new_colour[2:4], 16)
    rgb_list[2] = int(new_colour[4:6], 16)
    print(rgb_list)
    return rgb_list

    
def rgb_hexstring(rgb):
    #Converts an rgb sequence to hex string
    hexstring = ""
    for el in rgb:
        hexstring += '{0:00{1}x}'.format(el,2)
    return hexstring

def get_palette(name="", reqLength=3):
    # Returns a named palette from the dictionary.
    # If not in dictionary, a default palette grey-scale palette is retuned,
    # which has three tones, unless a required length is specified, in which 
    # case a palette of that length is returned.
    if name in paletteDict:
        return paletteDict.get(name)
    else:
        return generate_palette(reqLength)
        
def generate_palette(length):
    #return a grey-scale palette of the requested length
    generatedPalette = []
    for i in range(length):
        rgbElement = 8 + (48*i % 256)
        colour = []
        for el in range(3):
            colour.append(rgbElement)
        generatedPalette.append(colour)
    return generatedPalette
           