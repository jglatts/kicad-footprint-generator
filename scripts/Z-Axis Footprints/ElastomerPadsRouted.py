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
        self.cut_pad_positions = []

    def setFootprint(self):
        if self.kicad_mod:
            self.kicad_mod.setDescription("footprint for " + self.footprint_name)
            self.kicad_mod.setTags("zacc footprint " + self.footprint_name)


    def inToMM(self, val):
        return val * 25.4


    def createPads(self, numPads=0, numCols=0, pitchX=0, pitchY=0,
                   padWidth=0, padHeight=0, cutPadWidth=0, cutPadHeight=0):
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
                    width=self.inToMM(trace_width)
                )
                self.kicad_mod.append(line)


    def makeCutLines(self, cutPadWidth=0, cutPadHeight=0, pitchY=0, numCols=0):
        """
            Place horizontal cut-line pads perpendicular to vertical main pads,
            centered on the first and last columns.
        """
        if not self.pad_positions:
            return

        # Convert dimensions to mm
        padWidth = self.inToMM(cutPadWidth)
        padHeight = self.inToMM(cutPadHeight)
        pitchY = self.inToMM(pitchY)

        # Determine pad bounds
        xs = [x for _, x, _ in self.pad_positions]
        ys = [y for _, _, y in self.pad_positions]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        min_x = min_x - padWidth
        max_x = max_x + padWidth
        padNumber = max([n for n, _, _ in self.pad_positions]) + 1
        y = 0
        
        for i in range(numCols):
            cut_pad_left = Pad(
                number=padNumber,
                type=Pad.TYPE_SMT,
                shape=Pad.SHAPE_RECT,
                at=[min_x, y],
                size=[padWidth, padHeight],
                layers=['F.Cu', 'F.Mask'],
                orientation=0  # horizontal
            )
            cut_pad_right = Pad(
                number=padNumber+1,
                type=Pad.TYPE_SMT,
                shape=Pad.SHAPE_RECT,
                at=[max_x, y],
                size=[padWidth, padHeight],
                layers=['F.Cu', 'F.Mask'],
                orientation=0  # horizontal
            )
            y += pitchY
            padNumber += 2
            self.kicad_mod.append(cut_pad_left)
            self.kicad_mod.append(cut_pad_right)


    def addEdgeCuts(self, clearanceX=1.0, clearanceY=0.5):
        # add edge cuts around the pads with specified clearance
        # units are in MM
        if not self.pad_positions:
            return

        # Find min/max pad coordinates
        xs = [x for _, x, _ in self.pad_positions]
        ys = [y for _, _, y in self.pad_positions]
        min_x, max_x = min(xs) - clearanceX, max(xs) + clearanceX
        min_y, max_y = min(ys) - clearanceY, max(ys) + clearanceY

        # Define corners (lists for KicadModTree)
        corners = [
            [min_x, min_y],
            [max_x, min_y],
            [max_x, max_y],
            [min_x, max_y]
        ]

        # Draw lines around rectangle
        for i in range(len(corners)):
            start = corners[i]
            end = corners[(i + 1) % len(corners)]
            line = Line(
                start=start,
                end=end,
                layer='Edge.Cuts',
                width=0.15
            )
            self.kicad_mod.append(line)


    def printFootprintInfo(self):
        print(self.kicad_mod.getRenderTree())


    def save(self, name):
        file_handler = KicadFileHandler(self.kicad_mod)
        file_handler.writeFile(name)
        print("\n\nfootprint-name: \t" + self.footprint_name + "\n\t\t\tSAVED\n\n")


    def makeFootprint(self, **kwargs):
        self.setFootprint()
        self.createPads(**kwargs)
        self.connectPads(trace_width=0.004) 
        self.addEdgeCuts(clearanceX=3.5, clearanceY=2.5)
        self.makeCutLines(kwargs.get('cutPadWidth', 0), kwargs.get('cutPadHeight', 0), 
                          kwargs.get('pitchY', 0), kwargs.get('numCols', 0))
        self.printFootprintInfo()
        self.save(self.footprint_name + ".kicad_mod")


def zfill621():
    z = ElastomerPadsRouted("zfill-621-rev-b-elastomer-pads")
    z.makeFootprint(
        numPads=459, numCols=5,
        pitchX=0.0045, pitchY=0.36,
        padWidth=0.002, padHeight=0.136
    )

def zwrap387():
    z = ElastomerPadsRouted("zwrap-387-elastomer-panel")
    z.makeFootprint(
        numPads=216, numCols=29,
        pitchX=0.0045, pitchY=0.33,
        padWidth=0.002, padHeight=0.234
    )

def zfill622ForPCBWay():
    z = ElastomerPadsRouted("zfill-622-pcbway-pads")
    # pitchX is wire pitch
    # pitchY is blank cut dimension (distance between pads vertically)
    z.makeFootprint(
        numPads=507, numCols=5,
        pitchX=0.008, pitchY=0.275,
        padWidth=0.004, padHeight=0.15,
        cutPadWidth=0.08, cutPadHeight=0.004 
    )


### detailed docs coming soon
if __name__ == '__main__':
    zfill622ForPCBWay()