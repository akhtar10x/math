import numpy as np
import trimesh

OUT = "/workspace/stl"
import os
os.makedirs(OUT, exist_ok=True)

SPACING = 14.0
N = 9
SPAN = (N - 1) * SPACING

# --- Base plate with 9x9 hole grid ---
plate = trimesh.creation.box(extents=[SPAN + 30, SPAN + 30, 5])
plate.apply_translation([0, 0, 2.5])
holes = None
for i in range(N):
    for j in range(N):
        x, y = (i - (N - 1) / 2) * SPACING, (j - (N - 1) / 2) * SPACING
        h = trimesh.creation.cylinder(radius=2.2, height=8, sections=24)
        h.apply_translation([x, y, 2.5])
        holes = h if holes is None else holes.union(h)
plate = plate.difference(holes)
plate.export(f"{OUT}/base_plate.stl")

# --- Deformable lattice: 9x9 nodes joined by thin bars (living-hinge style) ---
parts = []
for i in range(N):
    for j in range(N):
        x, y = (i - (N - 1) / 2) * SPACING, (j - (N - 1) / 2) * SPACING
        node = trimesh.creation.cylinder(radius=3.0, height=3, sections=20)
        node.apply_translation([x, y, 1.5])
        parts.append(node)
for i in range(N):
    for j in range(N):
        x, y = (i - (N - 1) / 2) * SPACING, (j - (N - 1) / 2) * SPACING
        if i < N - 1:
            bar = trimesh.creation.box(extents=[SPACING - 4, 3.0, 2.0])
            bar.apply_translation([x + SPACING / 2, y, 1.0])
            parts.append(bar)
        if j < N - 1:
            bar = trimesh.creation.box(extents=[3.0, SPACING - 4, 2.0])
            bar.apply_translation([x, y + SPACING / 2, 1.0])
            parts.append(bar)
grid = trimesh.util.concatenate(parts)
grid.export(f"{OUT}/flex_grid.stl")

# --- Two eigen-direction dowels (dia 4mm, ~170mm, cone tips) ---
dowels = []
for k in range(2):
    rod = trimesh.creation.cylinder(radius=2.0, height=160, sections=20)
    rod.apply_translation([0, (k - 0.5) * 12, 80])
    tip = trimesh.creation.cone(radius=2.0, height=10, sections=20)
    tip.apply_translation([0, (k - 0.5) * 12, 165])
    dowels.append(rod.union(tip))
dowels = trimesh.util.concatenate(dowels)
dowels.export(f"{OUT}/eigen_dowels.stl")

for f in sorted(os.listdir(OUT)):
    m = trimesh.load(f"{OUT}/{f}")
    print(f, f"{os.path.getsize(OUT + '/' + f) // 1024} KB", "watertight:", m.is_watertight, "bounds:", np.round(m.bounds, 1).tolist())
