import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

H, R = 10.0, 4.0
C = 3.5
SIDE_SLOPE = H / R

fig = plt.figure(figsize=(8, 7))
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(-7, 7); ax.set_ylim(-7, 7); ax.set_zlim(0, 11)
ax.set_box_aspect((7, 7, 5.5))
ax.view_init(elev=22, azim=-55)
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")

theta = np.linspace(0, 2 * np.pi, 40)
zs = np.linspace(0, H, 30)
T, Z = np.meshgrid(theta, zs)
Xc = R * (1 - Z / H) * np.cos(T)
Yc = R * (1 - Z / H) * np.sin(T)
ax.plot_surface(Xc, Yc, Z, color="sandybrown", alpha=0.35, linewidth=0)

plane_poly = Poly3DCollection([], alpha=0.35, facecolor="steelblue", edgecolor="navy")
ax.add_collection3d(plane_poly)
curve_col = Line3DCollection([np.array([[0, 0, -5], [0, 0, -5]])], colors="crimson", linewidths=2.5)
ax.add_collection3d(curve_col)
sphere_artists = []
title = ax.set_title("")


def conic_segments(m):
    ys = np.linspace(-R * 1.6, R * 1.6, 600)
    z_plane = C + m * ys
    r_cone = R * (1 - z_plane / H)
    val = r_cone**2 - ys**2
    ok = (val >= 0) & (z_plane >= -0.01) & (z_plane <= H + 0.01)
    segs = []
    if not ok.any():
        return segs
    idx = np.where(ok)[0]
    splits = np.where(np.diff(idx) > 1)[0]
    groups = np.split(idx, splits + 1)
    for g in groups:
        y = ys[g]
        x = np.sqrt(val[g])
        z = C + m * y
        segs.append(np.vstack([x, y, z]).T)
        segs.append(np.vstack([-x, y, z]).T)
    return segs


def dandelin_spheres(m):
    def h(zc):
        return abs(zc - C) / np.sqrt(1 + m**2) - R * (1 - zc / H)
    grid = np.linspace(0.02, H - 0.02, 600)
    vals = np.array([h(z) for z in grid])
    roots = []
    for i in range(len(grid) - 1):
        if vals[i] == 0 or vals[i] * vals[i + 1] < 0:
            a, b = grid[i], grid[i + 1]
            for _ in range(60):
                mid = (a + b) / 2
                if h(a) * h(mid) <= 0:
                    b = mid
                else:
                    a = mid
            roots.append((a + b) / 2)
    return [(zc, R * (1 - zc / H)) for zc in roots]


def frame(alpha_deg):
    m = np.tan(np.radians(alpha_deg))
    xs = np.linspace(-6.5, 6.5, 2)
    ys = np.linspace(-6.5, 6.5, 2)
    X, Y = np.meshgrid(xs, ys)
    Zp = C + m * Y
    plane_poly.set_verts([list(zip(X.flatten(), Y.flatten(), Zp.flatten()))])
    segs = conic_segments(m)
    curve_col.set_segments(segs if segs else [np.array([[0, 0, -5], [0, 0, -5]])])
    for s in sphere_artists:
        s.remove()
    sphere_artists.clear()
    for zc, rho in dandelin_spheres(m):
        u = np.linspace(0, 2 * np.pi, 24)
        v = np.linspace(0, np.pi, 16)
        U, V = np.meshgrid(u, v)
        s = ax.plot_surface(rho * np.sin(V) * np.cos(U),
                            rho * np.sin(V) * np.sin(U),
                            zc + rho * np.cos(V),
                            color="seagreen", alpha=0.3, linewidth=0)
        sphere_artists.append(s)
    if abs(m - SIDE_SLOPE) < 0.15:
        kind = "PARABOLA (plane parallel to cone side)"
    elif m < SIDE_SLOPE:
        kind = "circle" if m < 0.05 else "ELLIPSE"
    else:
        kind = "HYPERBOLA"
    title.set_text(f"plane tilt = {alpha_deg:.0f} deg   ->   {kind}"
                   f"\n(green spheres = Dandelin spheres, tangent to cone and plane)")
    return [plane_poly, curve_col, title] + sphere_artists


alphas = np.concatenate([np.linspace(2, 60, 30), np.linspace(61, 80, 31)])
anim = FuncAnimation(fig, frame, frames=alphas, interval=70, blit=False)
anim.save("/workspace/conic_slicer.gif", writer=PillowWriter(fps=12))

frame(30.0)
fig.savefig("/workspace/conic_slicer_ellipse.png", dpi=110, bbox_inches="tight")
print("saved conic_slicer.gif and conic_slicer_ellipse.png")
