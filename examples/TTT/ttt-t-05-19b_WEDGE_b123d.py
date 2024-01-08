# %%
import sys
sys.path.append('..')
from __ocp_action_api import show_object
from build123d import *
densa = 7800/1e6 #carbon steel density g/mm^3
densb = 2700/1e6 #aluminum alloy
densc = 1020/1e6 #ABS
ms = Mode.SUBTRACT
LMH, LMV = LengthMode.HORIZONTAL, LengthMode.VERTICAL
# %%
#designed in inches, scaled at the end
with BuildPart() as p:
    with BuildSketch(Plane.XZ.offset(2/2)) as s:
        with Locations((-2.5,1.5)):
            Circle(.75)
        Circle(.75)
        Rectangle(2.5+.75,.01,align=(Align.MAX,Align.CENTER))
        make_hull()
        split(bisect_by=Plane.XZ,keep=Keep.BOTTOM)
    extrude(amount=-.75/2)
    with BuildSketch() as s2:
        with Locations((-3+1.75,0)):
            
            RectangleRounded(6,2,.5)
    extrude(s2.sketch,amount=.25)    

    with BuildSketch(Plane.XZ) as s3:
        Circle(.75)
        split(bisect_by=Plane.XZ,keep=Keep.BOTTOM)
    extrude(s3.sketch,amount=3/2,both=True)

    with BuildSketch() as s5:
        Circle(.9/2)
    extrude(s5.sketch,amount=1)
    with BuildSketch() as s6:
        Circle(.5/2)
    extrude(s6.sketch,amount=1,mode=ms)

    with BuildSketch(Plane.XZ) as s4:
        Circle(.75/2)
        split(bisect_by=Plane.XZ,keep=Keep.BOTTOM)

    extrude(s4.sketch,amount=3/2,both=True,mode=ms)
    mirror(about=Plane.XZ)

    with Locations(Plane.XZ):
        with Locations((-2.5,1.5)):
            Hole(.9/2)

print(f"\npart mass = {p.part.scale(IN).volume*densc/LB}") #correct answer is 0.265 lbs +/- 0.002 lbs

if 'show_object' in globals():
    show_object(p.part.scale(IN), "WEDGE")
else:
    assert p.part.scale(IN).export_stl("WEDGE.stl"), "Failed to export STL"
