import os
import numpy as np
import trimesh

OUT = "/workspace/stl"
os.makedirs(OUT, exist_ok=True)

H, R = 60.0, 24.0

# --- Cone split into two halves by a 3 mm vertical slot through the axis ---
cone = trimesh.creation.cone(radius=R, height=H, sections=64)
cone.apply_translation([0, 0, cone.bounds[0][2]])
slot = trimesh.creation.box(extents=[2 * R + 20, 3.0, H + 20])
slot.apply_translation([0, 0, H / 2])
halves = cone.difference(slot)
halves.export(f"{OUT}/conic_cone_halves.stl")

# --- Slicing plane: thin rectangle that slides through the slot ---
plane = trimesh.creation.box(extents=[80.0, 50.0, 2.0])
plane.export(f"{OUT}/conic_slice_plane.stl")

# --- Dandelin spheres (three sizes so students can find the tangent one) ---
spheres = []
for k, r in enumerate([7.0, 9.5, 12.0]):
    s = trimesh.creation.icosphere(subdivisions=3, radius=r)
    s.apply_translation([(k - 1) * 30, 0, r])
    spheres.append(s)
trimesh.util.concatenate(spheres).export(f"{OUT}/conic_spheres.stl")

for f in ["conic_cone_halves.stl", "conic_slice_plane.stl", "conic_spheres.stl"]:
    m = trimesh.load(f"{OUT}/{f}")
    print(f, f"{os.path.getsize(OUT + '/' + f) // 1024} KB",
          "watertight:", m.is_watertight, 
          "bounds:", np.round(m.bounds, 1).tolist())
