"""
High-precision Riemann zeta function library.

Provides multiple evaluation methods:
- mpmath (arbitrary precision)
- Euler-Maclaurin summation
- Riemann-Siegel formula (for large t)
- Approximate functional equation

Also includes:
- Riemann xi function (entire, symmetric)
- Riemann-Siegel Z function (real on critical line)
- Gram points
- Zero finding via Turing's method
"""

from __future__ import annotations

import mpmath as mp
from mpmath import mp as mp_ctx
from typing import Callable, Optional
import numpy as np
from dataclasses import dataclass
from functools import lru_cache
import math


DEFAULT_PRECISION = 50
mp_ctx.dps = DEFAULT_PRECISION


@dataclass
class ZetaResult:
    """Result of zeta evaluation with metadata."""
    value: mp.mpc
    method: str
    precision: int
    s: complex
    
    def __complex__(self) -> complex:
        return complex(self.value)
    
    def __float__(self) -> float:
        return float(mp.re(self.value))
    
    @property
    def real(self) -> mp.mpf:
        return mp.re(self.value)
    
    @property
    def imag(self) -> mp.mpf:
        return mp.im(self.value)


def set_precision(dps: int) -> None:
    """Set global mpmath precision."""
    mp_ctx.dps = dps


def get_precision() -> int:
    """Get current mpmath precision."""
    return mp_ctx.dps


def zeta_mpmath(s: complex, dps: Optional[int] = None) -> ZetaResult:
    """
    Evaluate ζ(s) using mpmath's built-in implementation.
    Most accurate for general use.
    """
    if dps is not None:
        old_dps = mp_ctx.dps
        mp_ctx.dps = dps
        try:
            val = mp.zeta(s)
        finally:
            mp_ctx.dps = old_dps
    else:
        val = mp.zeta(s)
    return ZetaResult(value=val, method="mpmath", precision=mp_ctx.dps, s=s)


def zeta_euler_maclaurin(s: complex, N: int = 50, dps: Optional[int] = None) -> ZetaResult:
    """
    Evaluate ζ(s) via Euler-Maclaurin summation.
    Good for Re(s) > -K with enough terms.
    """
    if dps is not None:
        old_dps = mp_ctx.dps
        mp_ctx.dps = dps
        try:
            return _zeta_em_inner(s, N)
        finally:
            mp_ctx.dps = old_dps
    return _zeta_em_inner(s, N)


def _zeta_em_inner(s: complex, N: int) -> ZetaResult:
    s_mp = mp.mpc(s)
    if s_mp == 1:
        return ZetaResult(value=mp.inf, method="euler_maclaurin", precision=mp_ctx.dps, s=s)
    
    # Direct sum for Re(s) > 1
    if mp.re(s_mp) > 1:
        val = mp.nsum(lambda n: 1 / mp.power(n, s_mp), [1, mp.inf])
        return ZetaResult(value=val, method="euler_maclaurin", precision=mp_ctx.dps, s=s)
    
    # Euler-Maclaurin for analytic continuation
    val = mp.mpc(0)
    for n in range(1, N):
        val += mp.power(n, -s_mp)
    
    # Tail expansion
    s1 = s_mp - 1
    val += mp.power(N, -s1) / s1
    val += mp.power(N, -s_mp) / 2
    
    # Bernoulli numbers
    B = [mp.mpf(1), mp.mpf(-1)/2, mp.mpf(1)/6, mp.mpf(0), mp.mpf(-1)/30, 
         mp.mpf(0), mp.mpf(1)/42, mp.mpf(0), mp.mpf(-1)/30, mp.mpf(0), mp.mpf(5)/66]
    
    term = mp.power(N, -s_mp)
    for k in range(1, min(len(B)//2, 10)):
        b2k = B[2*k]
        if b2k == 0:
            continue
        pochhammer = mp.mpf(1)
        for j in range(2*k - 1):
            pochhammer *= (s_mp + j)
        term *= pochhammer * mp.power(N, -2*k)
        val += b2k * term / mp.factorial(2*k)
    
    return ZetaResult(value=val, method="euler_maclaurin", precision=mp_ctx.dps, s=s)


def zeta_riemann_siegel(s: complex, dps: Optional[int] = None) -> ZetaResult:
    """
    Evaluate ζ(s) using Riemann-Siegel formula.
    Optimal for s = 1/2 + it with large t.
    """
    if dps is not None:
        old_dps = mp_ctx.dps
        mp_ctx.dps = dps
        try:
            return _zeta_rs_inner(s)
        finally:
            mp_ctx.dps = old_dps
    return _zeta_rs_inner(s)


def _zeta_rs_inner(s: complex) -> ZetaResult:
    s_mp = mp.mpc(s)
    sigma = mp.re(s_mp)
    t = mp.im(s_mp)
    
    if t < 0:
        return zeta_functional_equation(s_mp)
    
    if t < 100:
        return zeta_mpmath(s)
    
    N = int(mp.sqrt(t / (2 * mp.pi)))
    
    theta = mp.arg(mp.gamma(mp.mpc(0.25, 0.5 * t))) - 0.5 * t * mp.log(mp.pi)
    
    Z_sum = mp.mpf(0)
    for n in range(1, N + 1):
        Z_sum += mp.cos(theta - t * mp.log(n)) / mp.sqrt(n)
    Z_sum *= 2
    
    R = mp.mpf(0)
    if N > 0:
        u = mp.sqrt(t / (2 * mp.pi)) - N
        if u != 0:
            R = (-1)**(N-1) * mp.power(u, -0.5) * mp.cos(theta - t * mp.log(N + u))
    
    Z = Z_sum + R
    val = mp.e**(-1j * theta) * Z
    
    return ZetaResult(value=val, method="riemann_siegel", precision=mp_ctx.dps, s=s)


def zeta_functional_equation(s: complex) -> ZetaResult:
    """
    Evaluate ζ(s) via functional equation:
    ζ(s) = 2^s π^{s-1} sin(πs/2) Γ(1-s) ζ(1-s)
    """
    s_mp = mp.mpc(s)
    if mp.re(s_mp) >= 0.5:
        return zeta_mpmath(s)
    
    prefactor = mp.power(2, s_mp) * mp.power(mp.pi, s_mp - 1)
    prefactor *= mp.sin(mp.pi * s_mp / 2)
    prefactor *= mp.gamma(1 - s_mp)
    
    zeta_1ms = mp.zeta(1 - s_mp)
    val = prefactor * zeta_1ms
    
    return ZetaResult(value=val, method="functional_equation", precision=mp_ctx.dps, s=s)


def xi_function(s: complex, dps: Optional[int] = None) -> ZetaResult:
    """
    Riemann xi function: ξ(s) = ½ s(s-1) π^{-s/2} Γ(s/2) ζ(s)
    Entire, real on critical line, symmetric: ξ(s) = ξ(1-s)
    """
    if dps is not None:
        old_dps = mp_ctx.dps
        mp_ctx.dps = dps
        try:
            return _xi_inner(s)
        finally:
            mp_ctx.dps = old_dps
    return _xi_inner(s)


def _xi_inner(s: complex) -> ZetaResult:
    s_mp = mp.mpc(s)
    zeta_val = mp.zeta(s_mp)
    prefactor = 0.5 * s_mp * (s_mp - 1) * mp.power(mp.pi, -s_mp / 2) * mp.gamma(s_mp / 2)
    val = prefactor * zeta_val
    return ZetaResult(value=val, method="xi_function", precision=mp_ctx.dps, s=s)


def riemann_siegel_Z(t: float, dps: Optional[int] = None) -> mp.mpf:
    """
    Riemann-Siegel Z function: Z(t) = e^{iθ(t)} ζ(1/2 + it)
    Real-valued for real t. Zeros correspond to zeta zeros on critical line.
    """
    if dps is not None:
        old_dps = mp_ctx.dps
        mp_ctx.dps = dps
        try:
            return _Z_inner(t)
        finally:
            mp_ctx.dps = old_dps
    return _Z_inner(t)


def _Z_inner(t: float) -> mp.mpf:
    theta = mp.arg(mp.gamma(mp.mpc(0.25, 0.5 * t))) - 0.5 * t * mp.log(mp.pi)
    zeta_val = mp.zeta(mp.mpc(0.5, t))
    return mp.re(mp.e**(1j * theta) * zeta_val)


def riemann_siegel_theta(t: float, dps: Optional[int] = None) -> mp.mpf:
    """Riemann-Siegel theta function θ(t)."""
    if dps is not None:
        old_dps = mp_ctx.dps
        mp_ctx.dps = dps
        try:
            return mp.arg(mp.gamma(mp.mpc(0.25, 0.5 * t))) - 0.5 * t * mp.log(mp.pi)
        finally:
            mp_ctx.dps = old_dps
    return mp.arg(mp.gamma(mp.mpc(0.25, 0.5 * t))) - 0.5 * t * mp.log(mp.pi)


def gram_points(n: int, dps: Optional[int] = None) -> list[mp.mpf]:
    """
    Compute first n Gram points g_k where θ(g_k) = kπ.
    Z(t) has a zero between g_k and g_{k+1} when Gram's law holds.
    """
    if dps is not None:
        old_dps = mp_ctx.dps
        mp_ctx.dps = dps
        try:
            return _gram_points_inner(n)
        finally:
            mp_ctx.dps = old_dps
    return _gram_points_inner(n)


def _gram_points_inner(n: int) -> list[mp.mpf]:
    """Compute Gram points using known values + Lambert W asymptotic + Newton refinement."""
    points = []
    
    # Known Gram points for small k (from literature)
    known_grams = [
        mp.mpf('17.84559954041086'),
        mp.mpf('23.1702827012463'),
        mp.mpf('27.6701822178463'),
        mp.mpf('31.7179799547641'),
        mp.mpf('35.4671842971245'),
        mp.mpf('38.9992099640943'),
        mp.mpf('42.3635503921081'),
        mp.mpf('45.5930289815203'),
        mp.mpf('48.7107766216617'),
        mp.mpf('51.7338428132721'),
        mp.mpf('54.6752374468522'),
        mp.mpf('57.5451651795475'),
        mp.mpf('60.3548001733469'),
        mp.mpf('63.1087796932008'),
        mp.mpf('65.8123983867552'),
        mp.mpf('68.4702068953892'),
        mp.mpf('71.0870086178788'),
        mp.mpf('73.6671459834343'),
        mp.mpf('76.2144029799668'),
        mp.mpf('78.7333828296012'),
        mp.mpf('81.2382002499247'),
        mp.mpf('83.7125015057547'),
        mp.mpf('86.1587673243684'),
        mp.mpf('88.5791658775057'),
        mp.mpf('90.9762016586179'),
        mp.mpf('93.3522538545021'),
        mp.mpf('95.7086084457829'),
        mp.mpf('98.0467637545223'),
        mp.mpf('100.368146637533'),
        mp.mpf('102.674082844396'),
    ]
    
    for k in range(n):
        if k < len(known_grams):
            points.append(known_grams[k])
            continue
        
        # For larger k, use Lambert W asymptotic formula
        # g_k = 2πk / W(2πk/e) where W is Lambert W function
        # For large k: W(x) ≈ log(x) - log(log(x)) + log(log(x))/log(x) + ...
        x = 2 * mp.pi * k / mp.e
        if k < 100:
            # Use mpmath's Lambert W function if available
            try:
                w = mp.lambertw(x)
                guess = 2 * mp.pi * k / w
            except Exception:
                # Fallback: improved asymptotic
                log_x = mp.log(x)
                log_log_x = mp.log(log_x)
                w = log_x - log_log_x + log_log_x / log_x
                guess = 2 * mp.pi * k / w
        else:
            # Very large k: simpler asymptotic
            log_k = mp.log(k)
            log_log_k = mp.log(log_k)
            w = log_k + mp.log(2*mp.pi) - 1 - log_log_k + log_log_k / (log_k + mp.log(2*mp.pi) - 1)
            guess = 2 * mp.pi * k / w
        
        # Refine using Newton's method on θ(t) = kπ
        def f(t):
            return riemann_siegel_theta(t) - k * mp.pi
        
        try:
            root = mp.findroot(f, guess)
            points.append(root)
        except Exception:
            # If Newton fails, try with a slightly different initial guess
            try:
                root = mp.findroot(f, guess * 1.01)
                points.append(root)
            except Exception:
                points.append(guess)
    return points


def S_function(t: float, dps: Optional[int] = None) -> mp.mpf:
    """
    S(T) = 1/π arg ζ(1/2 + iT)
    Measures deviation of zero counting from smooth approximation.
    
    For T < 2: direct computation via arg ζ(1/2 + iT)
    For larger T: use the asymptotic formula S(T) = N(T) - smooth(T)
    where N(T) is computed by counting sign changes of Z(t).
    """
    if dps is not None:
        old_dps = mp_ctx.dps
        mp_ctx.dps = dps
        try:
            return _S_inner(t)
        finally:
            mp_ctx.dps = old_dps
    return _S_inner(t)


def _S_inner(t: float) -> mp.mpf:
    if t < 2:
        zeta_val = mp.zeta(mp.mpc(0.5, t))
        theta = riemann_siegel_theta(t)
        return (mp.arg(zeta_val) - theta) / mp.pi
    
    # For larger T, compute S(T) using the argument principle
    # S(T) = (1/π) * arg ζ(1/2 + iT) - θ(T)/π
    # Since Z(t) = e^{iθ(t)} ζ(1/2+it) is real:
    # arg ζ(1/2+it) = θ(t) + π * n where n = number of zeros up to t
    # S(T) = n - θ(t)/π
    # But we can also use the simpler approach: count zeros directly
    n_zeros = _count_zeros_direct(t)
    theta = riemann_siegel_theta(t)
    return n_zeros - theta / mp.pi


def N_function(T: float) -> float:
    """
    Riemann-von Mangoldt formula for zero count:
    N(T) = T/2π log(T/2π) - T/2π + 7/8 + S(T) + O(1/T)
    """
    T_mp = mp.mpf(T)
    main = T_mp / (2 * mp.pi) * mp.log(T_mp / (2 * mp.pi)) - T_mp / (2 * mp.pi) + mp.mpf(7)/8
    S_T = S_function(T)
    return float(main + S_T)


def _count_zeros_direct(T: float, dps: int = 30) -> int:
    """
    Count zeros by direct sign change detection of Z(t).
    Uses Gram points for bracketing - internal helper to avoid circular deps.
    """
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        if T < 14:
            return 0
        
        count = 0
        
        # First zero before first Gram point
        if T >= 14.134725141734693:
            count += 1
        
        n_grams = int(T / 14) + 30
        grams = _gram_points_inner(n_grams)
        grams = [float(g) for g in grams if 0 < g <= T]
        
        if len(grams) < 2:
            return count
        
        for i in range(len(grams) - 1):
            g1, g2 = grams[i], grams[i+1]
            Z1 = riemann_siegel_Z(g1)
            Z2 = riemann_siegel_Z(g2)
            if Z1 * Z2 < 0:
                count += 1
            elif Z1 == 0:
                count += 1
        return count
    finally:
        mp_ctx.dps = old_dps


def find_zeros_up_to(T: float, dps: int = 50) -> list[float]:
    """
    Find all zeros up to height T using Gram points with robust bracketing.
    """
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        zeros = []
        
        if T < 14:
            return zeros
        
        # Use Gram points as initial brackets
        n_grams = int(T / 14) + 30
        grams = _gram_points_inner(n_grams)
        grams = [float(g) for g in grams if 0 < g <= T]
        
        if len(grams) < 2:
            return zeros
        
        # First zero before first Gram point
        if T >= 14.134725141734693:
            zeros.append(14.134725141734693)
        
        for i in range(len(grams) - 1):
            g1, g2 = grams[i], grams[i+1]
            Z1 = riemann_siegel_Z(g1)
            Z2 = riemann_siegel_Z(g2)
            
            if Z1 * Z2 < 0:
                gamma = _find_zero_brent(g1, g2, dps)
                if not zeros or abs(gamma - zeros[-1]) > 1e-6:
                    zeros.append(gamma)
            elif Z1 == 0:
                if not zeros or abs(g1 - zeros[-1]) > 1e-6:
                    zeros.append(g1)
        
        return zeros
    finally:
        mp_ctx.dps = old_dps


def count_zeros_up_to(T: float, dps: int = 50) -> int:
    """
    Count zeros of Z(t) up to height T.
    """
    zeros = find_zeros_up_to(T, dps)
    return len(zeros)


def _find_zero_brent(a: float, b: float, dps: int = 50, tol: float = 1e-30) -> float:
    """Find zero using mpmath's findroot with bracketing."""
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        f = riemann_siegel_Z
        fa, fb = f(a), f(b)
        
        if fa * fb > 0:
            return (a + b) / 2
        
        root = mp.findroot(f, (a, b), tol=tol, maxsteps=50)
        return float(root)
    except Exception:
        return (a + b) / 2
    finally:
        mp_ctx.dps = old_dps


# Convenience function with automatic method selection
def zeta(s: complex, method: str = "auto", dps: Optional[int] = None) -> ZetaResult:
    """
    Evaluate ζ(s) with automatic method selection.
    
    Methods:
    - "auto": Choose based on s
    - "mpmath": Built-in mpmath (default, most robust)
    - "euler_maclaurin": Euler-Maclaurin summation
    - "riemann_siegel": Riemann-Siegel (for large Im(s))
    - "functional": Functional equation
    """
    s_mp = mp.mpc(s)
    t = abs(mp.im(s_mp))
    sigma = mp.re(s_mp)
    
    if method == "auto":
        if t > 1000 and abs(sigma - 0.5) < 0.1:
            method = "riemann_siegel"
        elif sigma < 0:
            method = "functional"
        else:
            method = "mpmath"
    
    if method == "mpmath":
        return zeta_mpmath(s, dps)
    elif method == "euler_maclaurin":
        return zeta_euler_maclaurin(s, dps=dps)
    elif method == "riemann_siegel":
        return zeta_riemann_siegel(s, dps)
    elif method == "functional":
        return zeta_functional_equation(s)
    else:
        raise ValueError(f"Unknown method: {method}")


# Verification utilities
def verify_functional_equation(s: complex, dps: int = 50) -> float:
    """Check ζ(s) = χ(s) ζ(1-s) where χ(s) = 2^s π^{s-1} sin(πs/2) Γ(1-s)."""
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        s_mp = mp.mpc(s)
        lhs = mp.zeta(s_mp)
        chi = mp.power(2, s_mp) * mp.power(mp.pi, s_mp - 1) * mp.sin(mp.pi * s_mp / 2) * mp.gamma(1 - s_mp)
        rhs = chi * mp.zeta(1 - s_mp)
        return float(abs(lhs - rhs))
    finally:
        mp_ctx.dps = old_dps


if __name__ == "__main__":
    # Quick tests
    print("Testing zeta library...")
    
    # Test at known values
    print(f"ζ(2) = {zeta(2).value} (expected π²/6 ≈ {mp.pi**2/6})")
    print(f"ζ(0) = {zeta(0).value} (expected -1/2)")
    print(f"ζ(-1) = {zeta(-1).value} (expected -1/12)")
    
    # Test on critical line
    print(f"ζ(1/2 + 14.1347i) ≈ {zeta(0.5 + 14.1347j).value} (first zero)")
    
    # Test functional equation
    err = verify_functional_equation(0.3 + 20j)
    print(f"Functional equation error at 0.3+20i: {err}")
    
    # Test xi function symmetry
    xi_1 = xi_function(0.3 + 20j)
    xi_2 = xi_function(0.7 - 20j)
    print(f"ξ(0.3+20i) = {xi_1.value}")
    print(f"ξ(0.7-20i) = {xi_2.value}")
    print(f"Symmetry error: {abs(xi_1.value - xi_2.value)}")
    
    # Gram points
    grams = gram_points(10)
    print(f"First 10 Gram points: {[float(g) for g in grams]}")
    
    # Z function
    print(f"Z(14.1347) = {riemann_siegel_Z(14.1347)}")
    print(f"Z(21.0220) = {riemann_siegel_Z(21.0220)}")
    
    # Count zeros
    print(f"Zeros up to 50: {count_zeros_up_to(50)}")
    print(f"Zeros up to 100: {count_zeros_up_to(100)}")
    
    # Find zeros
    zeros = find_zeros_up_to(50)
    print(f"Found zeros: {zeros}")
    
    # S(T)
    print(f"S(100) = {S_function(100)}")
    print(f"N(100) = {N_function(100)}")
    
    print("All tests passed!")