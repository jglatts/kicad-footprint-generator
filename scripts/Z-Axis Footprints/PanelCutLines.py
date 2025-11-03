import sys
import os

sys.path.append(os.path.join(sys.path[0],".."))
sys.path.append('../..') # enable package import from parent directory

from KicadModTree import *

class PanelCutLines():
    
    def __init__(self, name):
        self.footprint_name = name
        self.kicad_mod = Footprint(self.footprint_name)

    def inToMM(self, val):
        return val * 25.4

    def save(self):
        file_handler = KicadFileHandler(self.kicad_mod)
        file_handler.writeFile(self.footprint_name + ".kicad_mod")
    
    def makePad(self, padNumber, padWidth, padHeight, x_val, y_val):
        return Pad(
                number=padNumber,
                type=Pad.TYPE_SMT,
                shape=Pad.SHAPE_RECT,
                at=[x_val, y_val],
                size=[padWidth, padHeight],
                layers=['F.Cu', 'F.Mask'],
                mask=[padWidth - 0.1, padHeight - 0.1]
            )


    def makeCutLines(self, padWidth=0, padHeight=0, 
                     pitchX=0, pitchY=0, numRows=0):
        padNumber = 1
        x_val = 0
        y_val = 0
        padWidth = self.inToMM(padWidth)
        padHeight = self.inToMM(padHeight)
        pitchX = self.inToMM(pitchX)
        pitchY = self.inToMM(pitchY)

        for i in range(numRows):
            pad_left = self.makePad(padNumber, padWidth,
                                    padHeight, x_val, y_val)
            pad_right = self.makePad(padNumber+1, padWidth,
                                     padHeight, x_val + pitchX, y_val)
            padNumber += 2
            x_val = 0
            y_val += pitchY

            self.kicad_mod.append(pad_left)
            self.kicad_mod.append(pad_right)
        
        print(self.kicad_mod.getRenderTree())
        self.save()


if __name__ == "__main__":
    PanelCutLines("PanelCutLines-Test").makeCutLines(
                    padWidth=0.5, padHeight=0.002,
                    pitchX=1.0, pitchY=0.36, numRows=10)
