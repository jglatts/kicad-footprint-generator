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

class GenericElatomerPads():
    def __init__(self, name):
        self.footprint_name = name
        self.kicad_mod = Footprint(self.footprint_name)

    def setFootprint(self):
        if (self.kicad_mod != None):
            self.kicad_mod.setDescription("footprint for " + self.footprint_name)
            self.kicad_mod.setTags("zacc footprint " + self.footprint_name)            

    def inToMM(self, val):
        return val * 25.4

    def createPads(self, numPads=0, numCols=0, pitchX=0, pitchY=0,
                   padWidth=0, padHeight=0):
        padNumber = 1
        padX = 0
        padY = 0
        pitchX = self.inToMM(pitchX)
        pitchY = self.inToMM(pitchY)
        padWidth = self.inToMM(padWidth)
        padHeight = self.inToMM(padHeight)

        # makes 1 complete Y column of pads
        # can be used to make full FPC Panel footprint 
        # by duplicating in X direction with ROUTED traces
        for i in range(numPads):
            for j in range(numCols):
                pad = Pad(
                    number=padNumber,
                    type=Pad.TYPE_SMT,
                    shape=Pad.SHAPE_RECT,
                    at=[padX, padY],
                    size=[padWidth, padHeight],
                    layers=['F.Cu','F.Mask'], 
                    mask=[padWidth-0.1, padHeight-0.1]  
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
        file_handler.writeFile(self.footprint_name)
    
    def makeFootprint(self):
        self.setFootprint()

        # have this data come from a param dict or similar
        self.createPads(numPads=216, numCols=29, 
                        pitchX=0.0045, pitchY=0.33,
                        padWidth=0.002, padHeight=0.234)
        
        self.printFootprintInfo()
        self.save(self.footprint_name + ".kicad_mod")        


if __name__ == '__main__':
    GenericElatomerPads("testing-generic-pads").makeFootprint()