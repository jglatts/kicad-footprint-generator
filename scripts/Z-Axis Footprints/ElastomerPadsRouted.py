import sys
import os

sys.path.append(os.path.join(sys.path[0],".."))
sys.path.append('../..') # enable package import from parent directory

from KicadModTree import *
from KicadModTree.nodes.specialized.PadArray import PadArray
from collections import defaultdict

class ElastomerPadsRouted():
    def __init__(self, name):
        self.footprint_name = name
        self.kicad_mod = Footprint(self.footprint_name)
        self.pad_positions = []

    def setFootprint(self):
        if self.kicad_mod:
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

        for i in range(numPads):
            for j in range(numCols):
                pad = Pad(
                    number=padNumber,
                    type=Pad.TYPE_SMT,
                    shape=Pad.SHAPE_RECT,
                    at=[padX, padY],
                    size=[padWidth, padHeight],
                    layers=['F.Cu', 'F.Mask'],
                    mask=[padWidth - 0.1, padHeight - 0.1]
                )
                self.kicad_mod.append(pad)
                # Save pad position
                self.pad_positions.append((padNumber, padX, padY))
                padNumber += 1
                padY += pitchY
            padX += pitchX
            padY = 0

    def connectPads(self, trace_width=0.1):
        """Draw copper lines between pads vertically within each column."""
        columns = defaultdict(list)

        for pad_num, x, y in self.pad_positions:
            columns[round(x, 5)].append((pad_num, x, y))

        # Sort columns by X position (left-to-right)
        for col_x in sorted(columns.keys()):
            # Sort pads in this column by Y position (bottom-to-top)
            col_pads = sorted(columns[col_x], key=lambda p: p[2])
            
            # Draw vertical lines between consecutive pads
            for i in range(len(col_pads) - 1):
                (pad_a, x1, y1) = col_pads[i]
                (pad_b, x2, y2) = col_pads[i + 1]
                line = Line(
                    start=[x1, y1 + self.inToMM(0.001)],  # tiny offset
                    end=[x2, y2 - self.inToMM(0.001)],
                    layer='F.Cu',
                    width=trace_width
                )
                self.kicad_mod.append(line)

    def printFootprintInfo(self):
        print(self.kicad_mod.getRenderTree())

    def save(self, name):
        file_handler = KicadFileHandler(self.kicad_mod)
        file_handler.writeFile(name)

    def makeFootprint(self, **kwargs):
        self.setFootprint()
        self.createPads(**kwargs)
        self.connectPads(trace_width=0.05)  # add routing
        self.printFootprintInfo()
        self.save(self.footprint_name + ".kicad_mod")


if __name__ == '__main__':
    z = ElastomerPadsRouted("zwrap-387-elastomer-panel")
    z.makeFootprint(
        numPads=216, numCols=29,
        pitchX=0.0045, pitchY=0.33,
        padWidth=0.002, padHeight=0.234
    )