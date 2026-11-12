# Math — Interactive Physical Model Animations

Renderings and animations for interactive 3D-printable math teaching models.

## Eigenvector grid deformation

A square grid deforming under a linear map `A`. The two colored lines are the
eigenvectors — the only directions that do not rotate. The arrows show the
eigenvalue stretch factors (red: λ = 1.9, orange: λ = 0.8).

![Eigenvector grid animation](eigen_grid.gif)

Final frame:

![Final frame](eigen_grid_final.png)

### Reproduce

```bash
pip install numpy matplotlib pillow
python eigen_grid.py   # writes eigen_grid.gif and eigen_grid_final.png
```

### Physical model mapping

- Blue grid → deformable lattice on a sliding-pin frame (3D printed)
- Red/orange lines → removable eigen-direction dowels that stay fixed while the grid shears
- Arrows → stretch factors read off as eigenvalues
