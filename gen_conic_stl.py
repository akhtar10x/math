import os
import numpy as np
import trimesh

OUT = "/workspace/stl_v2"
os.makedirs(OUT, exist_ok=True)

H, R = 60.0, 24.0
SIDE_ANGLE = np.degrees(np.arctan2(H, R))  # ~68.2 deg: plane parallel to cone side
ANGLES = [0, 30, round(SIDE_ANGLE), 80]   # circle, ellipse, parabola, hyperbola
AXLE_Z = 6.0
PROT_X = 52.0
DETENT_R = 42.0


def cyl_x(radius, length, x=0.0, y=0.0, z=0.0, sections=48):
    c = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    c.apply_translation([x, y, z])
    return c


# --- Base disc + protractor arc plate (thin in x, standing at x = PROT_X) ---
base = trimesh.creation.cylinder(radius=62, height=4, sections=64)
base.apply_translation([0, 0, 2])
prot = trimesh.creation.cylinder(radius=52, height=4, sections=96)
prot.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
prot.apply_translation([PROT_X, 0, 0])
quad = trimesh.creation.box(extents=[8, 110, 110])
quad.apply_translation([PROT_X, 55, 55 + 4])
prot = prot.intersection(quad)
prot.apply_translation([0, 0, 4])
inner = cyl_x(9, 10, x=PROT_X, z=AXLE_Z + 4)
prot = prot.difference(inner)
for a in ANGLES:
    ar = np.radians(a)
    prot = prot.difference(cyl_x(1.8, 10, x=PROT_X, y=DETENT_R * np.cos(ar), z=4 + AXLE_Z + DETENT_R * np.sin(ar)))
prot = prot.difference(cyl_x(2.6, 10, x=PROT_X, z=4 + AXLE_Z))
base = base.union(prot)
base.export(f"{OUT}/conic_base.stl")

# --- Cone in two halves with a 4.2 mm gap; plane passes through the gap ---
cone = trimesh.creation.cone(radius=R, height=H, sections=64)
cone.apply_translation([0, 0, 4])
slot = trimesh.creation.box(extents=[90, 4.2, H + 20])
slot.apply_translation([0, 0, 4 + H / 2])
halves = cone.difference(slot)
halves.export(f"{OUT}/conic_cone_halves.stl")

# --- Slicing plane: 50 x 90 plate with axle along x and one detent hole ---
# world axle height = base (4 mm) + AXLE_Z
WZ = 4 + AXLE_Z
plate = trimesh.creation.box(extents=[50, 2, 90])
plate.apply_translation([0, 0, WZ + 45])
axle = cyl_x(2.4, 120, z=WZ)
plane = plate.union(axle)
plane = plane.difference(cyl_x(1.6, 8, x=PROT_X, y=0, z=WZ + DETENT_R))
plane.export(f"{OUT}/conic_slice_plane.stl")

# --- Locking pin ---
pin = cyl_x(1.5, 12, sections=24).union(cyl_x(4, 3, x=-5, sections=24))
pin.export(f"{OUT}/conic_pin.stl")

# --- Dandelin spheres with flat bases so they sit stably inside the cone ---
spheres = []
for k, r in enumerate([8.0, 10.0, 12.0]):
    s = trimesh.creation.icosphere(subdivisions=3, radius=r)
    s.apply_translation([(k - 1) * 32, 0, r + 4])
    flat = trimesh.creation.box(extents=[3 * r, 3 * r, 2 * r])
    flat.apply_translation([(k - 1) * 32, 0, 3])
    s = s.intersection(flat)
    spheres.append(s)
trimesh.util.concatenate(spheres).export(f"{OUT}/conic_spheres.stl")

for f in sorted(os.listdir(OUT)):
    m = trimesh.load(f"{OUT}/{f}")
    print(f, f"{os.path.getsize(OUT + '/' + f) // 1024} KB", "watertight:", m.is_watertight,
          "bounds:", np.round(m.bounds, 1).tolist())
print("side angle (parabola):", round(SIDE_ANGLE, 1), "deg")
