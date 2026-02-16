import sys
import os

sys.path.append(os.path.join(sys.path[0],".."))
sys.path.append('../..') # enable package import from parent directory

from KicadModTree import *
from KicadModTree.nodes.specialized.PadArray import PadArray


class EdgeCuts():
    def __init__(self, name):
        self.footprint_name = name
        self.kicad_mod = Footprint(self.footprint_name)

    def save(self):
        file_handler = KicadFileHandler(self.kicad_mod)
        file_handler.writeFile(self.footprint_name + ".kicad_mod")

    def inToMM(self, val):
        return val * 25.4

    def printInfo(self):
        print(self.kicad_mod.getRenderTree())

    def makeEdgeCut(self, width=1.0, height=1.0, use_mm=False):
        if use_mm:
            w = width / 2
            h = height / 2
            line_width = 0.15
        else:
            w = self.inToMM(width) / 2
            h = self.inToMM(height) / 2
            line_width = self.inToMM(0.006)  

        corners = [(-w, -h), (w, -h), (w, h), (-w, h)]
        for i in range(len(corners)):
            start = corners[i]
            end = corners[(i + 1) % len(corners)]
            line = Line(start=start, end=end, layer='Edge.Cuts', width=line_width)
            self.kicad_mod.append(line)

        self.save()
        self.printInfo()


if __name__ == "__main__":
    e = EdgeCuts("panel-edge-cuts-test")
    e.makeEdgeCut(width=2.0, height=3.0, use_mm=True)

    