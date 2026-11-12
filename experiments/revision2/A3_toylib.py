"""A3 helper: the lone blocker in the string-method potential U of experiments/BAR/bar.py, integrated with the
code's fixed-numerics update (code/sim/core/simulation.py, w2_numerics = "fixed"):
    v' = clamp(v + dt (F(x)/m - v/tau)),  v' <- clamp(v' + sigma xi),  x' = x + dt v',
F = -grad U (alone: drive c |x - g| with c = m v0 / tau, wall terms; density 0), clamp = speed cap 2 v0,
sigma = teff.sigma_for(kT, dt, tau). U is tabulated on a 4 mm grid (x 8.0-10.12 m, y 3.0-7.0 m) and the force is
the bilinear interpolation of its central-difference gradient. Escape = x >= 10 m (runlib.escape). The other
parts of the code force (TTC, ORCA, crush, wall friction) are zero for the blocker alone at density 0 away
from contact, so this toy differs from the production run only through the grid and the absence of the
corner rule. Used by A3_arrhenius.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev2lib  # noqa: E402,F401
from rev2lib import np  # noqa: E402
import bar  # noqa: E402
from sim.core.world import agents_to_walls  # noqa: E402

X0, X1, Y0, Y1, DG = 8.0, 10.12, 3.0, 7.0, 0.004


def grid_U(f):
    xs = np.arange(X0, X1 + 1e-9, DG)
    ys = np.arange(Y0, Y1 + 1e-9, DG)
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    P = np.column_stack([XX.ravel(), YY.ravel()])
    r = f.r[0]
    u = f.c[0] * np.linalg.norm(P - bar.G, axis=1)
    d, _ = agents_to_walls(P, f.world.walls)
    u += np.sum(bar.A * bar.B * np.exp((r - d) / bar.B) + 0.5 * bar.K * np.maximum(0, r - d) ** 2, axis=1)
    return xs, ys, u.reshape(XX.shape)


class Toy:
    def __init__(self, f):
        self.xs, self.ys, self.U = grid_U(f)
        gx, gy = np.gradient(self.U, DG, DG)
        self.nx, self.ny = len(self.xs), len(self.ys)
        self.FF = np.stack([-gx.ravel(), -gy.ravel()], 1)
        self.m, self.tau, self.vmax = float(f.m[0]), float(f.tau[0]), 2.0 * float(f.v0[0])

    def force(self, x, y):
        fx = np.clip((x - X0) / DG, 0, self.nx - 1.001)
        fy = np.clip((y - Y0) / DG, 0, self.ny - 1.001)
        i = fx.astype(int)
        j = fy.astype(int)
        a = (fx - i)[:, None]
        b = (fy - j)[:, None]
        q = i * self.ny + j
        FF, ny = self.FF, self.ny
        o = (1 - a) * ((1 - b) * FF[q] + b * FF[q + 1]) + a * ((1 - b) * FF[q + ny] + b * FF[q + ny + 1])
        return o[:, 0], o[:, 1]

    def run(self, x0, kT, dt, T_max, N, seed, clamp=True, xesc=10.0, check_every=5):
        """N independent blockers from x0 at rest; returns escape times (nan = censored at T_max)."""
        rng = np.random.default_rng(seed)
        sig = np.sqrt(kT * (1 - (1 - dt / self.tau) ** 2) / self.m)
        x = np.full(N, float(x0[0]))
        y = np.full(N, float(x0[1]))
        vx = np.zeros(N)
        vy = np.zeros(N)
        idx = np.arange(N)
        tesc = np.full(N, np.nan)
        first = np.full(N, np.nan)
        nsteps = int(round(T_max / dt))
        k = 0
        a = 1.0 - dt / self.tau
        while k < nsteps and len(idx):
            fx, fy = self.force(x, y)
            vx = a * vx + (dt / self.m) * fx
            vy = a * vy + (dt / self.m) * fy
            if clamp:
                s = np.hypot(vx, vy)
                sc = np.minimum(1.0, self.vmax / np.maximum(s, 1e-12))
                vx *= sc
                vy *= sc
            n = len(idx)
            vx += sig * rng.standard_normal(n)
            vy += sig * rng.standard_normal(n)
            if clamp:
                s = np.hypot(vx, vy)
                sc = np.minimum(1.0, self.vmax / np.maximum(s, 1e-12))
                vx *= sc
                vy *= sc
            x += dt * vx
            y += dt * vy
            k += 1
            e = x >= xesc
            if e.any():
                new = e & np.isnan(first[idx])
                first[idx[new]] = k * dt
            if k % check_every == 0 or k == nsteps:
                done = ~np.isnan(first[idx])
                if done.any():
                    tesc[idx[done]] = first[idx[done]]
                    keep = ~done
                    x, y, vx, vy, idx = x[keep], y[keep], vx[keep], vy[keep], idx[keep]
        return tesc


def harmonic_1d(kspring, m, tau, kT, dt, n_steps, N, seed, burn=2000):
    """1-D harmonic well under the same update; returns (k <x^2> / kT, m <v^2> / kT) after burn-in."""
    rng = np.random.default_rng(seed)
    sig = np.sqrt(kT * (1 - (1 - dt / tau) ** 2) / m)
    x = np.zeros(N)
    v = np.zeros(N)
    a = 1.0 - dt / tau
    sx = sv = 0.0
    cnt = 0
    for k in range(n_steps):
        v = a * v - (dt * kspring / m) * x + sig * rng.standard_normal(N)
        x = x + dt * v
        if k >= burn:
            sx += float(np.dot(x, x))
            sv += float(np.dot(v, v))
            cnt += N
    return kspring * sx / cnt / kT, m * sv / cnt / kT
