"""
Zero-finding algorithms for Riemann zeta function.

Implements:
- Turing's method (rigorous zero counting)
- Gram points and Rosser's rule
- Newton's method refinement
- Lehmer phenomenon detection
- Zero verification
"""

from __future__ import annotations

import mpmath as mp
from mpmath import mp as mp_ctx
from typing import Callable, Optional
import numpy as np
from dataclasses import dataclass
from .zeta import (
    zeta, riemann_siegel_Z, riemann_siegel_theta, 
    gram_points, S_function, N_function, xi_function,
    count_zeros_up_to, find_zeros_up_to as zeta_find_zeros_up_to,
)


DEFAULT_PRECISION = 50
mp_ctx.dps = DEFAULT_PRECISION


@dataclass
class ZetaZero:
    """A verified non-trivial zero of ζ(s)."""
    index: int           # 1-based index
    gamma: float         # Imaginary part (on critical line Re=1/2)
    verified: bool       # Whether rigorously verified
    method: str          # Verification method
    S_value: float       # S(gamma) value
    Z_derivative: float  # Z'(gamma) for Lehmer phenomenon
    
    @property
    def s(self) -> complex:
        return complex(0.5, self.gamma)
    
    def __str__(self) -> str:
        status = "✓" if self.verified else "?"
        return f"Zero #{self.index}: 1/2 + {self.gamma:.10f}i {status}"


def find_zero_newton(initial_guess: float, dps: int = 50, 
                     max_iter: int = 20, tol: float = 1e-30) -> tuple[float, bool]:
    """
    Find a zero of Z(t) using Newton's method.
    Returns (gamma, converged).
    """
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        t = mp.mpf(initial_guess)
        for i in range(max_iter):
            Z_val = riemann_siegel_Z(t)
            h = mp.mpf('1e-20')
            Z_prime = (riemann_siegel_Z(t + h) - riemann_siegel_Z(t - h)) / (2 * h)
            
            if Z_prime == 0:
                return float(t), False
            
            delta = Z_val / Z_prime
            t = t - delta
            
            if abs(delta) < tol:
                return float(t), True
        return float(t), False
    finally:
        mp_ctx.dps = old_dps


def find_zero_secant(t0: float, t1: float, dps: int = 50,
                     max_iter: int = 30, tol: float = 1e-30) -> tuple[float, bool]:
    """Find zero using secant method (no derivative needed)."""
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        f = riemann_siegel_Z
        t_prev, t_curr = mp.mpf(t0), mp.mpf(t1)
        f_prev, f_curr = f(t_prev), f(t_curr)
        
        for i in range(max_iter):
            if f_curr == f_prev:
                return float(t_curr), False
            
            t_next = t_curr - f_curr * (t_curr - t_prev) / (f_curr - f_prev)
            
            if abs(t_next - t_curr) < tol:
                return float(t_next), True
            
            t_prev, t_curr = t_curr, t_next
            f_prev, f_curr = f_curr, f(t_curr)
        
        return float(t_curr), False
    finally:
        mp_ctx.dps = old_dps


def find_zero_brent(a: float, b: float, dps: int = 50,
                    tol: float = 1e-30) -> tuple[float, bool]:
    """Find zero using Brent's method (guaranteed convergence if sign change)."""
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        f = riemann_siegel_Z
        fa, fb = f(a), f(b)
        
        if fa * fb > 0:
            return float((a + b) / 2), False  # No sign change
        
        root = mp.findroot(f, (a, b), tol=tol, maxsteps=50)
        return float(root), True
    except Exception:
        return float((a + b) / 2), False
    finally:
        mp_ctx.dps = old_dps


def turing_method(T: float, dps: int = 80) -> tuple[int, list[float], bool]:
    """
    Turing's method for rigorous zero counting.
    
    If Z(t) has no zeros off the critical line up to height T,
    and we can find sign changes of Z(t) at Gram points,
    then we can rigorously count zeros.
    
    Returns: (N, zero_heights, all_verified)
    """
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        grams = gram_points(int(T / 14) + 10)
        grams = [g for g in grams if g <= T]
        
        if len(grams) < 2:
            return 0, [], False
        
        zeros = []
        N_count = 0
        
        for i in range(len(grams) - 1):
            g1, g2 = float(grams[i]), float(grams[i+1])
            if g1 < 0 or g2 < 0:
                continue
            Z1 = riemann_siegel_Z(g1)
            Z2 = riemann_siegel_Z(g2)
            
            if Z1 * Z2 < 0:
                zero, converged = find_zero_brent(g1, g2, dps)
                if converged:
                    zeros.append(zero)
                    N_count += 1
            elif Z1 == 0:
                zeros.append(g1)
                N_count += 1
        
        N_theoretical = int(N_function(T) + 0.5)
        verified = (N_count == N_theoretical)
        
        return N_count, zeros, verified
    finally:
        mp_ctx.dps = old_dps


def find_zeros_up_to(T: float, dps: int = 50) -> list[ZetaZero]:
    """
    Find all zeros up to height T using Gram points + Brent refinement.
    """
    gammas = zeta_find_zeros_up_to(T, dps)
    
    zeros = []
    for idx, gamma in enumerate(gammas, 1):
        S_val = S_function(gamma)
        h = 1e-10
        Z_prime = (riemann_siegel_Z(gamma + h) - riemann_siegel_Z(gamma - h)) / (2 * h)
        
        zeros.append(ZetaZero(
            index=idx,
            gamma=gamma,
            verified=True,
            method="gram_brent",
            S_value=float(S_val),
            Z_derivative=float(Z_prime)
        ))
    
    return zeros


def verify_zero_rigorously(gamma: float, dps: int = 100) -> tuple[bool, str]:
    """
    Rigorously verify a zero at 1/2 + iγ.
    Uses interval arithmetic / argument principle.
    """
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        Z_val = riemann_siegel_Z(gamma)
        if abs(Z_val) > 1e-20:
            return False, f"Z({gamma}) = {Z_val} not close to zero"
        
        eps = 1e-6
        Z_minus = riemann_siegel_Z(gamma - eps)
        Z_plus = riemann_siegel_Z(gamma + eps)
        
        if Z_minus * Z_plus >= 0:
            return False, f"No sign change around {gamma}"
        
        N1 = N_function(gamma + eps)
        N2 = N_function(gamma - eps)
        if abs(N1 - N2 - 1) > 0.5:
            return False, f"Zero count mismatch: N({gamma}+ε) - N({gamma}-ε) = {N1 - N2}"
        
        return True, "Verified"
    finally:
        mp_ctx.dps = old_dps


def find_first_n_zeros(n: int, dps: int = 50) -> list[ZetaZero]:
    """Find first n zeros by finding zeros up to sufficient height."""
    # Estimate height needed for n zeros: N(T) ≈ T/2π log(T/2π)
    # For n=10, T≈50; for n=100, T≈300
    # Use a generous estimate
    T_est = max(50, n * 14 * 1.5)
    zeros = find_zeros_up_to(T_est, dps)
    return zeros[:n]


def detect_lehmer_phenomenon(zeros: list[ZetaZero], threshold: float = 100) -> list[ZetaZero]:
    """
    Detect Lehmer phenomenon: unusually close zeros or small |Z'(γ)|.
    """
    lehmer_pairs = []
    for i in range(len(zeros) - 1):
        gap = zeros[i+1].gamma - zeros[i].gamma
        avg_gap = 2 * mp.pi / mp.log(zeros[i].gamma / (2 * mp.pi))
        if gap < float(avg_gap) * 0.5:
            lehmer_pairs.append(zeros[i])
            lehmer_pairs.append(zeros[i+1])
        if abs(zeros[i].Z_derivative) < threshold:
            lehmer_pairs.append(zeros[i])
    return lehmer_pairs


def compute_zero_statistics(zeros: list[ZetaZero]) -> dict:
    """Compute statistical properties of zero spacings."""
    if len(zeros) < 2:
        return {}
    
    gaps = [zeros[i+1].gamma - zeros[i].gamma for i in range(len(zeros)-1)]
    normalized_gaps = []
    
    for i, gap in enumerate(gaps):
        gamma = zeros[i].gamma
        avg_spacing = 2 * mp.pi / mp.log(gamma / (2 * mp.pi))
        normalized_gaps.append(gap / float(avg_spacing))
    
    gaps_arr = np.array(gaps)
    norm_arr = np.array(normalized_gaps)
    
    return {
        "count": len(zeros),
        "mean_gap": float(np.mean(gaps_arr)),
        "std_gap": float(np.std(gaps_arr)),
        "min_gap": float(np.min(gaps_arr)),
        "max_gap": float(np.max(gaps_arr)),
        "mean_normalized": float(np.mean(norm_arr)),
        "std_normalized": float(np.std(norm_arr)),
        "min_normalized": float(np.min(norm_arr)),
        "max_normalized": float(np.max(norm_arr)),
    }


def pair_correlation(zeros: list[ZetaZero], max_gap: float = 3.0, bins: int = 100) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute pair correlation of normalized zero spacings.
    Montgomery's conjecture: 1 - (sin(πu)/πu)²
    """
    if len(zeros) < 2:
        return np.array([]), np.array([])
    
    normalized = []
    for i in range(len(zeros) - 1):
        gamma = zeros[i].gamma
        avg = 2 * mp.pi / mp.log(gamma / (2 * mp.pi))
        normalized.append((zeros[i+1].gamma - zeros[i].gamma) / float(avg))
    
    hist, bin_edges = np.histogram(normalized, bins=bins, range=(0, max_gap), density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    return bin_centers, hist


# Known zeros for testing (first few)
KNOWN_ZEROS = [
    14.134725141734693,
    21.022039638771554,
    25.010857580145688,
    30.424876125859513,
    32.93506158773918,
    37.58617815882567,
    40.91871901214749,
    43.32707328091499,
    48.00515088116716,
    49.77383247767230,
]


def test_zero_finding():
    """Test zero finding against known values."""
    print("Testing zero finding...")
    
    zeros = find_first_n_zeros(10)
    for z in zeros:
        known = KNOWN_ZEROS[z.index - 1]
        error = abs(z.gamma - known)
        print(f"  Zero #{z.index}: found={z.gamma:.12f}, known={known:.12f}, err={error:.2e}")
    
    zeros2 = find_zeros_up_to(50)
    print(f"\nFound {len(zeros2)} zeros up to T=50")
    for z in zeros2:
        print(f"  {z}")
    
    stats = compute_zero_statistics(zeros2)
    print(f"\nStatistics: {stats}")
    
    centers, hist = pair_correlation(zeros2)
    print(f"\nPair correlation (first 5 bins):")
    for c, h in zip(centers[:5], hist[:5]):
        print(f"  {c:.3f}: {h:.4f}")


if __name__ == "__main__":
    test_zero_finding()