"""Effective temperature of per-step velocity noise (plan T3; fixed numerics, noise after the force
update): v_{n+1} = (1 - dt/tau) v_n + sigma xi_n per component, so the stationary variance is
sigma^2 / (1 - (1 - dt/tau)^2) and k_B T_eff = m sigma^2 / (1 - (1 - dt/tau)^2) (exact in discrete time,
speed clamp ignored). w2_noise = dt_scaled multiplies sigma by sqrt(dt / 0.01)."""
import math

M = 80.0
DT_REF = 0.01


def kT_eff(sigma, dt, tau, m=M, mode="per_step"):
    s2 = sigma * sigma * (dt / DT_REF if mode == "dt_scaled" else 1.0)
    return m * s2 / (1.0 - (1.0 - dt / tau) ** 2)


def sigma_for(kT, dt, tau, m=M):
    """Per-step sigma giving k_B T_eff = kT at time step dt."""
    return math.sqrt(kT * (1.0 - (1.0 - dt / tau) ** 2) / m)
