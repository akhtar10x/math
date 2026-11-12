import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

A = np.array([[1.6, 0.6],
              [0.4, 1.1]])

w, V = np.linalg.eig(A)
w = w.real; V = V.real
order = np.argsort(w)[::-1]
w, V = w[order], V[:, order]

fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(-4, 4)
ax.set_ylim(-4, 4)
ax.set_aspect("equal")
ax.grid(True, alpha=0.2)
ax.axhline(0, color="k", lw=0.5)
ax.axvline(0, color="k", lw=0.5)

n = 9
lines = []
for i in range(-n, n + 1):
    lines.append(ax.plot([], [], color="steelblue", lw=1.2, alpha=0.8)[0])
    lines.append(ax.plot([], [], color="steelblue", lw=1.2, alpha=0.8)[0])

eig_lines = [ax.plot([], [], lw=2.5)[0] for _ in range(2)]
eig_arrows = [ax.annotate("", xy=(0, 0), xytext=(0, 0),
                          arrowprops=dict(arrowstyle="-|>", lw=3)) for _ in range(2)]
title = ax.set_title("")

colors = ["crimson", "darkorange"]

def frame(t):
    M = np.eye(2) + t * (A - np.eye(2))
    k = 0
    for i in range(-n, n + 1):
        xs, ys = np.array([i] * (2 * n + 1)), np.linspace(-n, n, 2 * n + 1)
        pts = M @ np.vstack([xs, ys])
        lines[k].set_data(pts[0], pts[1]); k += 1
        xs, ys = np.linspace(-n, n, 2 * n + 1), np.array([i] * (2 * n + 1))
        pts = M @ np.vstack([xs, ys])
        lines[k].set_data(pts[0], pts[1]); k += 1
    for j in range(2):
        v = V[:, j] / np.linalg.norm(V[:, j])
        eig_lines[j].set_data([-4 * v[0], 4 * v[0]], [-4 * v[1], 4 * v[1]])
        eig_lines[j].set_color(colors[j])
        s = w[j] ** t
        eig_arrows[j].set_color(colors[j])
        eig_arrows[j].xy = (s * v[0], s * v[1])
        eig_arrows[j].xytext = (0, 0)
    title.set_text(
        f"M(t) = (1-t)I + tA,  t = {t:.2f}\n"
        f"eigenvalues: lambda1 = {w[0]:.3f} (red),  lambda2 = {w[1]:.3f} (orange)"
    )
    return lines + eig_lines + eig_arrows + [title]

anim = FuncAnimation(fig, frame, frames=np.linspace(0, 1, 61), interval=60, blit=False)
anim.save("/workspace/eigen_grid.gif", writer=PillowWriter(fps=15))

frame(1.0)
fig.savefig("/workspace/eigen_grid_final.png", dpi=110, bbox_inches="tight")
print("eigenvalues:", w)
print("saved /workspace/eigen_grid.gif and eigen_grid_final.png")
