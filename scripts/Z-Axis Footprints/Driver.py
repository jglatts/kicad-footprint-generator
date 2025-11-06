from ElastomerPadsRouted import ElastomerPadsRouted
from ElastomerPadBuilder import ElastomerPadBuilder

def zfill621():
    z = ElastomerPadsRouted("zfill-621-rev-b-elastomer-pads")
    z.makeFootprint(
        numPads=459,    # total number of pads in array
        numCols=5,      # number of columns (Y-axis)
        pitchX=0.0045,  # pad-to-pad pitch in X-axis
        pitchY=0.36,    # pad-to-pad pitch in Y-axis
        padWidth=0.002, # pad width
        padHeight=0.136 # pad height
    )

def zwrap387():
    z = ElastomerPadsRouted("zwrap-387-elastomer-panel")
    z.makeFootprint(
        numPads=216,    # total number of pads
        numCols=29,     # number of columns
        pitchX=0.0045,  # horizontal pitch between pads
        pitchY=0.33,    # vertical pitch between pads
        padWidth=0.002, # pad width
        padHeight=0.234 # pad height
    )

def zfill622ForPCBWay():
    z = ElastomerPadsRouted("zfill-622-pcbway-pads")
    z.makeFootprint(
        numPads=507,        # total number of pads
        numCols=5,          # number of columns
        pitchX=0.008,       # pad pitch in X-axis
        pitchY=0.275,       # pad pitch in Y-axis
        padWidth=0.004,     # pad width
        padHeight=0.15,     # pad height
        cutPadWidth=0.08,   # width of cut pads for clearance
        cutPadHeight=0.004  # height of cut pads for clearance
    )

def tester():
    ## impl builder pattern (when I have time)
    z = ElastomerPadsRouted("test-for-groups")
    z.makeFootprint(
        numPads=10,             # total number of pads (x-axis)
        numCols=5,              # number of columns (y-axis)
        pitchX=0.008,           # center distance between pads in x-axis
        pitchY=0.275,           # center distance between pads in y-axis
        padWidth=0.004,         # width of each pad
        padHeight=0.15,         # height of each pad
        cutPadWidth=0.08,       # width of cut pads     (strip cutting)
        cutPadHeight=0.004,     # height of cut pads    (strip cutting)
        cutGapPart=0.025591,     # gap between group     (final length)
        numGroups=5,            # number of condunctor-groups in final parts
    )

# use build pattern like below for more complex parts
def builderTester():
    builder = (
        ElastomerPadBuilder("test-for-groups-builder")
        .withNumPads(217)
        .withNumCols(15)
        .withPitchX(0.007874)
        .withPitchY(0.275)
        .withPadWidth(0.004)
        .withPadHeight(0.15)
        .withCutPadWidth(0.08)
        .withCutPadHeight(.004)
        .withCutGapPart(0.018)
        .withNumGroups(5)
        .build()
        )
    builder.makeFootprint()


if __name__ == "__main__":
    builderTester()
