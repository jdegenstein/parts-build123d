# %%
import sys
sys.path.append('..')
from __ocp_action_api_OVERRIDE import show_object
from build123d import *
densa = 7800/1e6 #carbon steel density g/mm^3
densb = 2700/1e6 #aluminum alloy
densc = 1020/1e6 #ABS
ms = Mode.SUBTRACT
LMH, LMV = LengthMode.HORIZONTAL, LengthMode.VERTICAL
# %%

with BuildLine() as l:
    m0 = Line((0,0),(30,0))
    m1 = JernArc(m0@1,m0%1,75+30,45)
    m2 = Line(m1@1,m1@1+(m1%1)*40) #40 results in co-linearity of n4

with BuildLine() as l2:
    n1 = Line(m2@1,m2@1+(-70*(m2%1).Y,70*(m2%1).X))
    n2 = Line(n1@0,n1@0+(n1%0)*-40)
    n3 = JernArc(n2@1,n2%1,75+30,45)
    n4 = Line(n3@1,n3@1+(n3%1)*30)

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as s:
        Circle(60/2)
    sweep(s.sketch,l.line)

    with BuildSketch(Plane.YZ.offset((n4@1).X)) as s3:
        Circle(60/2)
    sweep(s3.sketch,l2.line)

    with BuildSketch(Plane.YZ.offset((n4@1).X)) as s5:
        Circle(85/2)
    extrude(s5.sketch,amount=-20)

    with BuildSketch(p.part.faces().sort_by(Axis.Y)[-1]) as s7:
        Circle(85/2)
    extrude(s7.sketch,amount=-15)
    
    with BuildSketch(Plane.YZ) as s9:
        Circle(85/2)
    extrude(s9.sketch,amount=20)

    with BuildSketch(Plane.YZ) as s10:
        Circle(65/2)
    extrude(s10.sketch,amount=10,mode=ms)

    with BuildSketch(p.part.faces().sort_by(Axis.Y)[-1]) as s8:
        Circle(65/2)
    extrude(s8.sketch,amount=-8,mode=ms)

    with BuildSketch(Plane.YZ.offset((n4@1).X)) as s6:
        Circle(65/2)
    extrude(s6.sketch,amount=-10,mode=ms)

    with BuildSketch(Plane.YZ.offset((n4@1).X)) as s4:
        Circle(40/2)
    sweep(s4.sketch,l2.line,mode=ms)

    with BuildSketch(Plane.YZ) as s2:
        Circle(40/2)
    sweep(s2.sketch,l.line,mode=ms)


print(f"\npart mass = {p.part.volume*densa}") #correct is 4969 grams
show_object(p.part)
