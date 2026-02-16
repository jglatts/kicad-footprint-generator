from re import S
import re
import sys
import os
from tkinter import SEL

from sympy import true

sys.path.append(os.path.join(sys.path[0],".."))
sys.path.append('../..') # enable package import from parent directory

from KicadModTree import *
from KicadModTree.nodes.specialized.PadArray import PadArray
from collections import defaultdict


# works well, but names could be better 
class ElastomerPadBuilder():
    def __init__(self, name):
        self.footprint_name = name
        self.kicad_mod = Footprint(self.footprint_name)
        self.pad_positions = []
        self.cut_pad_positions = []
        self.numPattern = 0 
        self.cutMove = 0
        self.pitchX = 0
        self.pitchY = 0
        self.numPadsInX = 0
        self.numPads = 0
        self.numCols = 0
        self.padWidth = 0
        self.padHeight = 0
        self.offsetForCutLineY = 0
        self.cutPadWidth = 0
        self.cutPadHeight = 0
        self.numGroups = 0
        self.blankSize = 0


    def withNumGroups(self, val):
        self.numGroups = val
        return self

    def withNumPadsInX(self, val):
        self.numPadsInX = val
        return self

    def withCutPadWidth(self, val):
        self.cutPadWidth = self.inToMM(val)
        return self

    def withCutPadHeight(self, val):
        self.cutPadHeight = self.inToMM(val)
        return self

    def withPadHeight(self, val):
        self.padHeight = self.inToMM(val)
        return self

    def withBlankSize(self, val):
        self.blankSize = self.inToMM(val)
        return self

    def withPadWidth(self, val):
        self.padWidth = self.inToMM(val)
        return self


    def withNumCols(self, val):
        self.numCols = val
        return self


    def withNumPads(self, val):
        self.numPads = val
        return self

    def withCutGapPart(self, val):
        self.cutMove = self.inToMM(val)
        return self

    def withCutMove(self, val):
        self.cutMove = self.inToMM(val)
        return self


    def withPitchX(self, val):
        self.pitchX = self.inToMM(val)
        return self


    def build(self):
        return self


    def withPitchY(self, val):
        self.pitchY = self.inToMM(val)
        return self

    def withOffsetForCutLineY(self, val):
        self.offsetForCutLineY = self.inToMM(val)
        return self

    def setFootprint(self):
        if self.kicad_mod:
            self.kicad_mod.setDescription("footprint for " + self.footprint_name)
            self.kicad_mod.setTags("zacc footprint " + self.footprint_name)


    def inToMM(self, val):
        return val * 25.4


    def printFootprintInfo(self):
        print(self.kicad_mod.getRenderTree())


    def save(self, name):
        file_handler = KicadFileHandler(self.kicad_mod)
        file_handler.writeFile(name)
        print("\n\nfootprint-name: \t" + self.footprint_name + "\n\t\t\tSAVED\n\n")


    def adjustForGap(self, number, padX):
        if number == 0:
            padX += self.cutMove
        else:
            padX += self.cutMove - self.pitchX
        return padX


    def createPad(self, number, x, y, w, h):
        return Pad(
            number=number,
            type=Pad.TYPE_SMT,
            shape=Pad.SHAPE_RECT,
            at=[x, y],
            size=[w, h],
            layers=['F.Cu', 'F.Mask'],
            solder_mask_margin=0.25
        )


    def createPads(self):
        padNumber = 1
        padX = 0
        padY = 0
        
        # add a checks for the fielfds being set
        numLoops = 1 if self.numGroups == 0 else self.numGroups
        cutMove = 0 if self.cutMove == 0 else self.cutMove

        # adjust for blank size where gold is not fully wrapping around
        gapBtwnGroupsY = 0
        if self.blankSize != 0:
            gapBtwnGroupsY = self.blankSize - self.pitchY

        doMove = False
        for k in range(numLoops):
            padX = self.adjustForGap(k, padX)
            for i in range(self.numPads):
                for j in range(self.numCols):
                    pad = self.createPad(padNumber, padX, padY, 
                                         self.padWidth, self.padHeight)
                    self.kicad_mod.append(pad)
                    self.pad_positions.append((padNumber, padX, padY))
                    padNumber += 1
                    if doMove:
                        padY += gapBtwnGroupsY
                        doMove = False
                    else:
                        padY += self.pitchY
                        doMove = True
                padX += self.pitchX
                padY = 0


    def connectPads(self, trace_width=0.1):
        """ Draw copper lines between pads vertically within each column """
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

    def makeCutLines(self):
        """
            Place horizontal cut-line pads perpendicular to vertical main pads,
            centered on the first and last columns.
        """
        if not self.pad_positions:
            return

        if not self.cutPadWidth or not self.cutPadHeight:
            return

        # Determine pad bounds
        xs = [x for _, x, _ in self.pad_positions]
        ys = [y for _, _, y in self.pad_positions]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        min_x = min_x - self.cutPadWidth
        max_x = max_x + self.cutPadWidth
        padNumber = max([n for n, _, _ in self.pad_positions]) + 1
        y = 0
        
        for i in range(self.numCols):
            cut_pad_left = Pad(
                number=padNumber,
                type=Pad.TYPE_SMT,
                shape=Pad.SHAPE_RECT,
                at=[min_x, y],
                size=[self.cutPadWidth, self.cutPadHeight],
                layers=['F.Cu', 'F.Mask'],
                orientation=0  # horizontal
            )
            cut_pad_right = Pad(
                number=padNumber+1,
                type=Pad.TYPE_SMT,
                shape=Pad.SHAPE_RECT,
                at=[max_x, y],
                size=[self.cutPadWidth, self.cutPadHeight],
                layers=['F.Cu', 'F.Mask'],
                orientation=0  # horizontal
            )
            y += self.pitchY
            padNumber += 2
            self.kicad_mod.append(cut_pad_left)
            self.kicad_mod.append(cut_pad_right)


    def makeCutLinesWrap(self):
        # Determine pad bounds
        xs = [x for _, x, _ in self.pad_positions]
        ys = [y for _, _, y in self.pad_positions]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        if not self.offsetForCutLineY:
            return

        if not self.cutPadHeight or not self.cutPadWidth:
            return

        min_x = min_x - self.cutPadWidth
        max_x = max_x + self.cutPadWidth
        padNumber = max([n for n, _, _ in self.pad_positions]) + 1
        
        # adjust to edge of top of pad
        y = (-1) * (self.padHeight/2)
        y -= (self.cutPadHeight/2)

        # adjust to our offset
        y -= self.offsetForCutLineY - (self.cutPadHeight/2)
        numLines = int((self.numCols/2)+1)        

        for i in range(numLines):
            cut_pad_left = Pad(
                number=padNumber,
                type=Pad.TYPE_SMT,
                shape=Pad.SHAPE_RECT,
                at=[min_x, y],
                size=[self.cutPadWidth, self.cutPadHeight],
                layers=['F.Cu', 'F.Mask'],
                orientation=0  # horizontal
            )
            cut_pad_right = Pad(
                number=padNumber+1,
                type=Pad.TYPE_SMT,
                shape=Pad.SHAPE_RECT,
                at=[max_x, y],
                size=[self.cutPadWidth, self.cutPadHeight],
                layers=['F.Cu', 'F.Mask'],
                orientation=0  # horizontal
            )
            y += self.blankSize
            padNumber += 2
            self.kicad_mod.append(cut_pad_left)
            self.kicad_mod.append(cut_pad_right)


    def makeFootprint(self):
        self.setFootprint()
        self.createPads()
        self.connectPads(trace_width=0.0137795) 
        #self.makeCutLines()
        self.makeCutLinesWrap()
        self.addEdgeCuts(clearanceX=7.5, clearanceY=3.5)
        self.printFootprintInfo()
        self.save(self.footprint_name + ".kicad_mod")


if __name__ == "__main__":
    pass

    