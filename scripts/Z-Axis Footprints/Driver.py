from ElastomerPadsRouted import ElastomerPadsRouted

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
    z.makeFootprint(
        numPads=507, numCols=5,
        pitchX=0.008, pitchY=0.275,
        padWidth=0.004, padHeight=0.15,
        cutPadWidth=0.08, cutPadHeight=0.004 
    )

if __name__ == "__main__":
    zfill622ForPCBWay()