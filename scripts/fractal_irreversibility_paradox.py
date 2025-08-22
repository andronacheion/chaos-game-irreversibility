
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

Path('examples').mkdir(parents=True, exist_ok=True)

def get_user_input(prompt, default=None, choices=None, typ=str):
    while True:
        val = input(f"{prompt} [{default}]: ") or default
        try:
            if choices and val not in choices:
                print(f"Alege dintre: {choices}")
            else:
                return typ(val)
        except Exception:
            print("Valoare invalidă.")

def chaos_game_sierpinski(vertices, n_points, seed=None):
    rng = np.random.default_rng(seed)
    current_point = vertices[0].copy()
    points = []
    choices = []
    for _ in range(n_points):
        v = int(rng.integers(0, 3))
        chosen_vertex = vertices[v]
        current_point = (current_point + chosen_vertex) / 2.0
        points.append(current_point.copy())
        choices.append(v)
    return np.array(points), choices

def reverse_chaos_game(vertices, points, choices):
    # Derulează înapoi: pentru ultimele m puncte, calculează pozițiile anterioare
    reverse_points = []
    for pt, v in zip(points[::-1], choices[::-1]):
        vertex = vertices[v]
        prev_point = 2*pt - vertex
        reverse_points.append(prev_point)
    return np.array(reverse_points)

def set_triangle_axes(ax):
    """Fixează limitele la triunghiul echilateral din [0,1]x[0, sqrt(3)/2] pentru consistență."""
    ax.set_aspect('equal')
    ax.axis('off')
    xmin, xmax = 0.0, 1.0
    ymin, ymax = 0.0, np.sqrt(3)/2.0
    # Mică margine uniformă
    xmar = 0.05*(xmax - xmin)
    ymar = 0.05*(ymax - ymin)
    ax.set_xlim(xmin - xmar, xmax + xmar)
    ax.set_ylim(ymin - ymar, ymax + ymar)

def save_scatter(pts, color, out_path, img_size, dpi=100, s=0.05):
    fig, ax = plt.subplots(figsize=(img_size/100.0, img_size/100.0), dpi=dpi)
    if pts.size > 0:
        ax.scatter(pts[:,0], pts[:,1], s=s, color=color)
    set_triangle_axes(ax)  # <- axe fixe pentru toate imaginile (gen0 inclusiv)
    plt.tight_layout(pad=0)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

def main():
    print("\nParadoxul Reversibilității Fractale – Chaos Game + Reverse (CLI cu mod de salvare)\n")
    out_format  = get_user_input("Format ieșire (png/tif/svg/eps)", 'png', ['png', 'tif', 'svg', 'eps'])
    img_size    = int(get_user_input("Dimensiune imagine (256/512/1024/2048/4096)", '1024', ['256','512','1024','2048','4096']))
    n_points    = int(get_user_input("Număr de puncte (ex: 50000)", '50000', typ=int))
    save_mode   = get_user_input("Mod salvare (all/final)", 'final', ['all','final'])
    seed_txt    = get_user_input("Seed aleator (gol=aleator)", '', typ=str)
    seed        = None if seed_txt == '' else int(seed_txt)

    # Triunghi echilateral în [0,1]x[0,1]
    vertices = np.array([
        [0.5, np.sqrt(3)/2.0],
        [0.0, 0.0],
        [1.0, 0.0],
    ])

    print("\nSe generează Sierpiński prin chaos game...")
    points, choices = chaos_game_sierpinski(vertices, n_points, seed=seed)

    if save_mode == 'all':
        # k = număr de snapshots; pentru g=0 folosim m=0 (imagini coerente, fără autoscalare)
        k = int(get_user_input("Număr de generații (snapshots) 0..k", '5', typ=int))
        for g in range(k+1):
            m = int(n_points * g / max(1, k))  # m poate fi 0 pentru g=0
            fwd = points[:m]                        # primele m puncte (forward)
            rev = reverse_chaos_game(vertices, points[-m:], choices[-m:]) if m > 0 else np.empty((0,2))

            fwd_path = os.path.join('examples', f"fractal_chaosgame_gen{g}.{out_format}")
            rev_path = os.path.join('examples', f"reverse_fractal_chaosgame_gen{g}.{out_format}")
            save_scatter(fwd, 'black',   fwd_path, img_size)
            save_scatter(rev, 'crimson', rev_path, img_size)
            print(f"Salvat: {fwd_path} | {rev_path} (g={g}, m={m})")

        # mapăm și „finalul” la numele standard pentru README (gen=k)
        final_g = k
        final_fwd = os.path.join('examples', f"fractal_chaosgame_gen{final_g}.{out_format}")
        final_rev = os.path.join('examples', f"reverse_fractal_chaosgame_gen{final_g}.{out_format}")
        # dacă formatul e PNG, link-ul e deja conform; altfel scoatem și PNG standard suplimentar
        if out_format.lower() != 'png':
            # exportă PNG-uri standard pentru README
            save_scatter(points, 'black',   "examples/fractal_chaosgame.png", img_size, dpi=300, s=0.05)
            rev_full = reverse_chaos_game(vertices, points, choices)
            save_scatter(rev_full, 'crimson', "examples/reverse_fractal_chaosgame.png", img_size, dpi=300, s=0.05)
        else:
            # pentru PNG, duplicăm ultimul frame ca numele standard
            import shutil
            shutil.copyfile(final_fwd, "examples/fractal_chaosgame.png")
            shutil.copyfile(final_rev, "examples/reverse_fractal_chaosgame.png")
        print("Salvat: examples/fractal_chaosgame.png și examples/reverse_fractal_chaosgame.png")

    else:
        # Doar finalul
        fwd_path = os.path.join('examples', f"fractal_chaosgame.{out_format}")
        rev_path = os.path.join('examples', f"reverse_fractal_chaosgame.{out_format}")
        save_scatter(points, 'black',   fwd_path, img_size)
        rev_full = reverse_chaos_game(vertices, points, choices)
        save_scatter(rev_full, 'crimson', rev_path, img_size)
        print(f"Salvat: {fwd_path} | {rev_path}")

        # PNG-urile standard pentru README
        if out_format.lower() != 'png':
            save_scatter(points,      'black',   "examples/fractal_chaosgame.png", img_size, dpi=300, s=0.05)
            save_scatter(rev_full,    'crimson', "examples/reverse_fractal_chaosgame.png", img_size, dpi=300, s=0.05)
        else:
            import shutil
            shutil.copyfile(fwd_path, "examples/fractal_chaosgame.png")
            shutil.copyfile(rev_path, "examples/reverse_fractal_chaosgame.png")
        print("Salvat: examples/fractal_chaosgame.png și examples/reverse_fractal_chaosgame.png")

    # Dimensiunea fractală teoretică
    fd = np.log(3.0)/np.log(2.0)
    print(f"\nDimensiunea fractală teoretică (Hausdorff/Moran): {fd:.5f}")
    print("\nGata! gen0 forward și gen0 reverse au aceleași axe și aspect (fără deformări).")

if __name__ == "__main__":
    main()
