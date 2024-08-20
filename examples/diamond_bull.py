# diamond_bull.py
# for entry into the NeedItMakeIt duct design competition

from build123d import *
# from ocp_vscode import *
from inspect import currentframe as cf

import sys
sys.path.append('..')
from TTT.__ocp_action_api_OVERRIDE import show_object
from build123d import *

# set_port(3939)
# show_clear()
# set_defaults(ortho=True, default_edgecolor="#121212")
densa = 7800 / 1e6  # carbon steel density g/mm^3
densb = 2700 / 1e6  # aluminum alloy
densc = 1020 / 1e6  # ABS
# %%

#from https://makerworld.com/en/models/559282#profileId-478439
step = import_step("DUCT_TEMPLATE_v4.step")

# select some objects from step file
nozzle_bottom_face = step.faces().sort_by(Axis.Y)[-1]
inlet_cavity_bot_face = (
    step.faces()
    .filter_by(GeomType.PLANE)
    .filter_by(Axis.Y)
    .group_by(Axis.Z)[-3]
    .sort_by(Axis.Y)[-1]
)
inlet_bot_face = (
    step.faces()
    .filter_by(GeomType.PLANE)
    .filter_by(Axis.Y)
    .group_by(Axis.Z)[-2]
    .sort_by(Axis.Y)[-1]
    .outer_wire()
)

nzbf_center = nozzle_bottom_face.center()
icbf_center = inlet_cavity_bot_face.center()

# create sweep center
vtx_side = Vertex(15, 15, 15)

# create sweep path for duct
pts = [icbf_center, vtx_side, nzbf_center + (12, -4, 10.5)]
rhs_spline = Spline(pts)

# airflow helper for visualization
airflow_pts = [icbf_center, vtx_side, nzbf_center + (12, -4, 10.5), nzbf_center]
airflow_spline = Spline(airflow_pts)

# get left hand mount bottom face for support
LHMNT_bot_face = step.faces().filter_by(Axis.Y).group_by(Axis.X)[-1].sort_by(Axis.Y)[-2]
LHMNT_bot_face_center = LHMNT_bot_face.center()

# create support pts and spline
support_pts = [
    LHMNT_bot_face_center,
    Vector(32.2, 8.6, -15.7),
    vtx_side + (0.6, 9, -9.9),
]
support_spline = Spline(support_pts)

with BuildPart() as p:
    loc_start = Location((icbf_center), (90, 0, 0))
    with BuildSketch(loc_start) as s0: # starting sketch circle for inlet
        Circle(8)
    # create a location for the end of duct and apply some rotation to angle towards nozzle
    loc_end = Location(rhs_spline @ 1, (46, 27, 0), Intrinsic.YXZ)
    with BuildSketch(loc_end) as s:
        with BuildLine() as l: # create diamond sketch by drawing one straight line and mirroring twice
            Line((23, 0), (0, 3))
            mirror(about=Plane.XZ)
            mirror(about=Plane.YZ)
            fillet(l.vertices(), 1) # add fillets to round corners
        make_face()
    sweep(multisection=True, path=rhs_spline) # perform multisection sweep from s0 to s
    split(bisect_by=Plane.YZ) # bisect and mirror avoids problems with OCCT
    mirror(about=Plane.YZ)

    with BuildPart() as p_support: # create mounts that go from support to ducts
        with BuildSketch(support_spline ^ 1) as s4:
            Circle(3)
        sweep(
            sections=[LHMNT_bot_face, s4.sketch], multisection=True, path=support_spline
        )
        with BuildSketch(LHMNT_bot_face) as szz:
            Circle(2.6)
        extrude(amount=30, mode=Mode.SUBTRACT)

        mirror(about=Plane.YZ)

    with BuildPart(mode=Mode.SUBTRACT) as p_hollow: # create internal duct for boolean subtraction
        with BuildSketch(loc_start) as s2:
            Circle(6.5)
        with BuildSketch(loc_end) as s3:
            add(l.line)
            make_face()
            offset(amount=-1)
        zz = sweep(multisection=True, path=rhs_spline)
        split(bisect_by=Plane.YZ)
        mirror(zz, about=Plane.YZ)

    add(step.children[0])  # LHMOUNT from step file
    add(step.children[1])  # RHMOUNT   ''
    add(step.children[2])  # REARMOUNT ''

    mounthole = (
        step.children[1]
        .faces()
        .sort_by(Axis.Y)[-1]
        .edges()
        .filter_by(GeomType.CIRCLE)
        .sort_by(SortBy.RADIUS)[0]
    )
    mounthole_face = Face(Wire(mounthole))
    with BuildSketch(mounthole_face) as s_rear_clr:
        Circle(2.6)
    extrude(amount=-10, mode=Mode.SUBTRACT) # provide clearance for bolt head on rearmount

# stats:
print(p.part.bounding_box()) # check that duct has enough clearance versus nozzle
print(step.bounding_box())
print(f"\npart mass = {p.part.volume*densc}")

print(f"{s2.sketch.area=}") # compare inlet area vs area of both outlets
print(f"{2*s3.sketch.area=}")

# OCP VSCODE SHOW COMMANDS, not needed for parts-build123d repo
# classes = (BuildPart, BuildSketch, BuildLine)  # for OCP-vscode
# set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="7"))
# variables, s_o, s_n, slocal = (list(cf().f_locals.items()), [], [], False)
# for name, obj in variables:
#     if (
#         isinstance(obj, classes)
#         and not name.startswith("_")
#         and not name.startswith("obj")
#     ):
#         if obj._obj_name != "sketch" or slocal:
#             s_o.append(obj), s_n.append(f"{name}.{obj._obj_name}")
#         elif obj._obj_name == "sketch":
#             s_o.append(obj.sketch), s_n.append(f"{name}.{obj._obj_name}")
# show(
#     *s_o,
#     step,
#     Face(inlet_bot_face),
#     airflow_spline,
#     rhs_spline,
#     vtx_side,
#     LHMNT_bot_face,
#     support_spline,
#     mounthole,
#     mounthole_face,
#     names=s_n,
#     reset_camera=Camera.KEEP,
# )

show_object(p.part)
# %%

# exports
fname = "diamond_bull"
export_stl(p.part, fname + ".stl")
export_step(p.part, fname + ".step")
