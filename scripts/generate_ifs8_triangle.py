
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from pathlib import Path
import os

Path('examples').mkdir(parents=True, exist_ok=True)

def get_user_input(prompt, default=None, choices=None, typ=str):
    while True:
        val = input(f"{prompt} [{default}]: ") or default
        try:
            if choices and val not in choices:
                print(f"Alege dintre: {choices}")
            else:
                return typ(val)
        except:
            print("Valoare invalidă, încearcă din nou.")

# -----------------------------
# 8-map IFS pe triunghi (r=1/3)
# Subdivide în 9 sub-triunghiuri și elimină doar pe cel central inversat
# -----------------------------

def equilateral_triangle():
    A = np.array([0.5, np.sqrt(3)/2.0])
    B = np.array([0.0, 0.0])
    C = np.array([1.0, 0.0])
    return np.vstack([A, B, C])

def local_grid_points(TA, TB, TC, m=3):
    P = {}
    for i in range(m+1):
        for j in range(m+1 - i):
            lamA = 1.0 - (i + j)/m
            lamB = i/m
            lamC = j/m
            P[(i, j)] = lamA*TA + lamB*TB + lamC*TC
    return P

def subdivide_8(tri):
    TA, TB, TC = tri
    P = local_grid_points(TA, TB, TC, m=3)
    upright = []
    for i in range(3):
        for j in range(3 - i):
            if i + j <= 2:
                tloc = np.vstack([P[(i, j)], P[(i+1, j)], P[(i, j+1)]])
                upright.append(tloc)
    inverted = []
    for i in range(2):
        for j in range(2 - i):
            if i + j <= 1:
                tloc = np.vstack([P[(i+1, j)], P[(i+1, j+1)], P[(i, j+1)]])
                inverted.append(tloc)
    # elimină pe cel central (centroid cel mai apropiat de centroidul marelui triunghi)
    T_centroid = tri.mean(axis=0)
    if inverted:
        dists = [np.linalg.norm(t.mean(axis=0) - T_centroid) for t in inverted]
        central_idx = int(np.argmin(dists))
        inverted = [t for k, t in enumerate(inverted) if k != central_idx]
    return upright + inverted

def triangles_at_generation(gen):
    tris = [equilateral_triangle()]
    for _ in range(gen):
        nxt = []
        for tri in tris:
            nxt.extend(subdivide_8(tri))
        tris = nxt
    return tris

def draw_and_save(tris, out_path, dpi=300, pad=0.0, figsize=(6, 5.5)):
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.axis('off')
    polys = PolyCollection(tris, linewidths=0)
    ax.add_collection(polys)
    xs = np.concatenate([t[:,0] for t in tris])
    ys = np.concatenate([t[:,1] for t in tris])
    xmar = 0.05*(xs.max()-xs.min())
    ymar = 0.05*(ys.max()-ys.min())
    ax.set_xlim(xs.min()-xmar, xs.max()+xmar)
    ax.set_ylim(ys.min()-ymar, ys.max()+ymar)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches='tight', pad_inches=pad, dpi=dpi)
    plt.close(fig)

def main():
    print("\\nIFS cu 8 hărți pe triunghi – mod interactiv (linie de comandă)\\n")
    out_format = get_user_input("Format ieșire (png/tif/svg/eps)", 'png', ['png','tif','svg','eps'])
    img_size = int(get_user_input("Dimensiune imagine (256/512/1024/2048/4096)", '1024', ['256','512','1024','2048','4096']))
    dpi = int(get_user_input("DPI pentru salvare", '300', typ=int))
    max_gen = int(get_user_input("Generație finală (ex: 5)", '5', typ=int))
    save_mode = get_user_input("Mod salvare (all/final)", 'final', ['all','final'])
    name_base = get_user_input("Nume bază fișier", 'triangle_ifs8')

    # Scara figurii astfel încât să obținem ~img_size pixeli pe latura lungă
    figsize = (img_size/100, img_size/100)

    if save_mode == 'all':
        print(f"Se salvează toate generațiile 0..{max_gen}...")
        for g in range(max_gen+1):
            tris = triangles_at_generation(g)
            out = os.path.join('examples', f"{name_base}_gen{g}.{out_format}")
            draw_and_save(tris, out, dpi=dpi, figsize=figsize)
            print(f"Salvat: {out} ({len(tris)} triunghiuri)")
    else:
        print(f"Se salvează doar ultima generație (gen={max_gen})...")
        tris = triangles_at_generation(max_gen)
        out = os.path.join('examples', f"{name_base}_gen{max_gen}.{out_format}")
        draw_and_save(tris, out, dpi=dpi, figsize=figsize)
        print(f"Salvat: {out} ({len(tris)} triunghiuri)")

    # Imagine „cheie” pentru articol/README (coerentă cu convenția)
    key = os.path.join('examples', f"triangle_ifs8_gen{max_gen}.png")
    if out_format.lower() == 'png':
        if save_mode == 'all':
            pass  # deja salvat
        else:
            # duplică sub numele standard
            from shutil import copyfile
            copyfile(out, key)
    else:
        # dacă ai salvat tif/svg/eps, mai scoatem și un PNG standard pentru README
        tris = triangles_at_generation(max_gen)
        draw_and_save(tris, key, dpi=dpi, figsize=figsize)
    print(f"Salvat: {key} (pentru README)")

if __name__ == "__main__":
    main()
