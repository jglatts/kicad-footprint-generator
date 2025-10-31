"""
Zwrap-387 Footprint Generator for KiCad

This script uses the KicadModTree Python API to programmatically create a custom 
KiCad footprint for the Zwrap-387 pad configuration. 

Features:
- Generates 216 SMT pads arranged in two rows per column.
- Pads are rectangular with a specific pitch and dimensions in inches (converted from mm).
- Sets footprint metadata such as description and tags.
- Outputs a `.kicad_mod` file ready for use in KiCad PCB layouts.
- Prints debug information about the footprint structure for verification.

Usage:
    python zwrap387_footprint.py

Author: John Glatts
Date: 2025-10-31
"""
import sys
import os

sys.path.append(os.path.join(sys.path[0],".."))
sys.path.append('../..') # enable package import from parent directory

from KicadModTree import *
from KicadModTree.nodes.specialized.PadArray import PadArray

class Zwrap387Footprint():
    def __init__(self):
        self.footprint_name = "zwrap-387-test-pads"
        self.kicad_mod = Footprint(self.footprint_name)

    def setFootprint(self):
        if (self.kicad_mod != None):
            self.kicad_mod.setDescription("footprint for wrap-387 pads")
            self.kicad_mod.setTags("zacc footprint")            

    def inToMM(self, val)
        return val * 25.4

    def createPads(self):
        padNumber = 1
        padX = 0
        padY = 0
        pitchX = self.inToMM(0.0045)
        pitchY = self.inToMM(0.33)
        numPads = 216
        numCols = 29

        # makes 1 complete Y column of pads
        # can be used to make full FPC Panel footprint 
        # by duplicating in X direction with ROUTED traces
        for i in range(numPads):
            # make the copper pads
            for j in range(numCols):
                pad_width  = self.inToMM(0.002)
                pad_height = self.inToMM(0.234)
                pad = Pad(
                    number=padNumber,
                    type=Pad.TYPE_SMT,
                    shape=Pad.SHAPE_RECT,
                    at=[padX, padY],
                    size=[pad_width, pad_height],
                    layers=['F.Cu','F.Mask'], 
                    mask=[pad_width-0.1, pad_height-0.1]  
                )
                self.kicad_mod.append(pad)
                padNumber += 1
                padY += pitchY
            padX += pitchX
            padY = 0

    def printFootprintInfo(self): 
        print(self.kicad_mod)
        print(self.kicad_mod.getRenderTree())
        print(self.kicad_mod.getCompleteRenderTree())

    def save(self, name):
        file_handler = KicadFileHandler(self.kicad_mod)
        file_handler.writeFile(name)
    
    def makeFootprint(self):
        self.setFootprint()
        self.createPads()
        self.printFootprintInfo()
        self.save(self.footprint_name + ".kicad_mod")        


if __name__ == '__main__':
    Zwrap387Footprint().makeFootprint()
