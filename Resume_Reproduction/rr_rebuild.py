"""B1: B0 with exactly three switches (OUTLINE 4.3, config.REBUILD).

    1  vol scaling: w proportional to score / sigma, with |w| <= cap, re-demeaned and renormalised
    2  regime multiplier: w x kappa on the asset-days in the scope, under the rolling cut D only
    3  deadband: no trade within eta of the target, eta = multiple x the per-rung scale (engine)

Every switch is followed by re-demeaning and renormalising to gross 2, so B1 keeps B0's mandate:
net 0, gross 2, 5-day overlap, same lag, fill and costs.
"""
import numpy as np
import pandas as pd

import config as C


def demean_renorm(w, gross=C.GROSS):
    w = w.sub(w.mean(axis=1), axis=0)
    g = w.abs().sum(axis=1).replace(0, np.nan)
    return w.mul(gross / g, axis=0)


def vol_scaled(score, sig, cap=C.REBUILD["cap"], gross=C.GROSS, passes=2):
    w = demean_renorm(score / sig, gross)
    for _ in range(passes):
        w = demean_renorm(w.clip(-cap, cap), gross)
    return w


def scope_mask(vlab, slab, scope):
    if scope == "LV/HV corner":
        return (vlab == 0) & (slab == 2)
    if scope == "high-sigma row":
        return slab == 2
    raise ValueError(scope)


def regime_scaled(w, vlab, slab, kappa, scope, gross=C.GROSS):
    if kappa == 1:
        return w
    mult = pd.DataFrame(1.0, index=w.index, columns=w.columns).mask(scope_mask(vlab, slab, scope).fillna(False), kappa)
    return demean_renorm(w * mult, gross)


def targets(score, sig, vlab, slab, vol_scaling=True, kappa=C.REBUILD["kappa"], scope=C.REBUILD["kappa_scope"]):
    """Daily targets before the overlap; switches 1 and 2 can be turned off for the ablation."""
    if vol_scaling:
        w = vol_scaled(score, sig)
    else:
        w = demean_renorm(score)
    w = regime_scaled(w, vlab, slab, kappa, scope)
    return w


def overlap(w, hold=C.HOLD):
    return w.fillna(0.0).rolling(hold, min_periods=1).mean()
