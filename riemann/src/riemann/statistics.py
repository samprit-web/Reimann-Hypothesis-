"""
Statistical analysis tools for Riemann zeta zeros.

Includes:
- GUE (Gaussian Unitary Ensemble) statistics
- Moment computations
- N(T) analysis
- S(T) statistics
- Zero spacing distributions
- Montgomery-Odlyzko pair correlation
- Keating-Snaith moment conjectures
"""

from __future__ import annotations

import mpmath as mp
from mpmath import mp as mp_ctx
import numpy as np
from typing import Optional, Callable
from dataclasses import dataclass
from scipy import stats, integrate, special
from .zeta import zeta, S_function, N_function, riemann_siegel_Z
from .zeros import ZetaZero, find_zeros_up_to, find_first_n_zeros


@dataclass
class MomentResult:
    """Result of moment computation."""
    k: int
    T: float
    value: float
    asymptotic: float
    ratio: float


def compute_moments(T: float, max_k: int = 4, dps: int = 30,
                    method: str = 'trapezoidal') -> list[MomentResult]:
    """
    Compute moments I_k(T) = ∫_0^T |ζ(1/2+it)|^{2k} dt.
    
    Conjectural asymptotics (Keating-Snaith):
    I_k(T) ~ a_k * g_k * T * (log T)^{k²}
    where a_k = product over primes of (1 - 1/p)^{k²} * sum_{m=0}^∞ d_k(p^m)² / p^m
    and g_k = G(k+1)² / G(2k+1) with G Barnes G-function.
    """
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        results = []
        
        for k in range(1, max_k + 1):
            if method == 'trapezoidal':
                # Adaptive sampling
                n_points = min(5000, max(1000, int(T * 5)))
                t_vals = np.linspace(1, T, n_points)
                vals = []
                for t in t_vals:
                    z = zeta(complex(0.5, t))
                    vals.append(abs(complex(z.value))**(2*k))
                vals = np.array(vals)
                moment = np.trapezoid(vals, t_vals)
            elif method == 'simpson':
                n_points = min(5000, max(1000, int(T * 5)))
                if n_points % 2 == 0:
                    n_points += 1
                t_vals = np.linspace(1, T, n_points)
                vals = np.array([abs(zeta(complex(0.5, t)).value)**(2*k) for t in t_vals])
                moment = integrate.simpson(vals, t_vals)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Asymptotic prediction (simplified)
            # Leading term: a_k * g_k * T * (log T)^{k²}
            # For k=1: a_1 = 1, g_1 = 1 -> T log T
            # For k=2: a_2 = ζ(2) * ... , g_2 = 1/12 -> (1/12) T log⁴ T
            logT = np.log(T)
            
            if k == 1:
                asymptotic = T * logT
                a_g = 1.0
            elif k == 2:
                asymptotic = T * logT**4 / 12
                a_g = 1/12
            elif k == 3:
                asymptotic = T * logT**9 / 4320  # g_3 = 1/4320
                a_g = 1/4320
            elif k == 4:
                asymptotic = T * logT**16 / 2217600  # g_4 = 1/2217600
                a_g = 1/2217600
            else:
                # General formula using Barnes G
                from scipy.special import gamma, loggamma
                # g_k = G(k+1)² / G(2k+1)
                # Using known values
                asymptotic = T * logT**(k*k)
                a_g = 1.0
            
            results.append(MomentResult(
                k=k,
                T=T,
                value=float(moment),
                asymptotic=float(asymptotic),
                ratio=float(moment / asymptotic) if asymptotic > 0 else 0
            ))
        
        return results
    finally:
        mp_ctx.dps = old_dps


def gue_spacing_distribution(s: np.ndarray, beta: int = 2) -> np.ndarray:
    """
    GUE (beta=2) spacing distribution (Wigner surmise approximation).
    p(s) = (32/π²) s² exp(-4s²/π) for GUE
    """
    if beta == 1:  # GOE
        return (np.pi/2) * s * np.exp(-np.pi * s**2 / 4)
    elif beta == 2:  # GUE
        return (32/np.pi**2) * s**2 * np.exp(-4 * s**2 / np.pi)
    elif beta == 4:  # GSE
        return (2**18 / (3**6 * np.pi**3)) * s**4 * np.exp(-64 * s**2 / (9 * np.pi))
    else:
        raise ValueError("beta must be 1, 2, or 4")


def gue_pair_correlation(u: np.ndarray) -> np.ndarray:
    """
    GUE pair correlation function: R₂(u) = 1 - (sin(πu)/πu)²
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        result = 1 - (np.sin(np.pi * u) / (np.pi * u))**2
        result[u == 0] = 0  # limit as u→0
    return result


def number_variance(L: float, zeros: list[ZetaZero]) -> float:
    """
    Number variance Σ²(L) = ⟨(N(I) - L)²⟩ for intervals of length L (in mean spacing units).
    
    GUE prediction: Σ²(L) = (1/π²) (log(2πL) + γ + 1) + O(1/L) for large L
    """
    if len(zeros) < 2:
        return 0
    
    gammas = np.array([z.gamma for z in zeros])
    # Normalize to unit mean spacing
    normalized = []
    for i, g in enumerate(gammas):
        avg_spacing = 2 * np.pi / np.log(g / (2 * np.pi))
        normalized.append(g / avg_spacing)
    normalized = np.array(normalized)
    
    # Count zeros in intervals of length L
    max_pos = normalized[-1]
    n_intervals = int(max_pos / L)
    if n_intervals < 10:
        return 0
    
    counts = []
    for i in range(n_intervals):
        start = i * L
        end = (i + 1) * L
        count = np.sum((normalized >= start) & (normalized < end))
        counts.append(count)
    
    counts = np.array(counts)
    mean_count = np.mean(counts)
    variance = np.var(counts)
    
    return variance


def compute_number_variance(zeros: list[ZetaZero], 
                            L_max: float = 10.0,
                            n_L: int = 50) -> tuple[np.ndarray, np.ndarray]:
    """Compute number variance for a range of L values."""
    L_vals = np.logspace(-1, np.log10(L_max), n_L)
    variances = []
    
    for L in L_vals:
        var = number_variance(L, zeros)
        variances.append(var)
    
    return L_vals, np.array(variances)


def n_t_analysis(zeros: list[ZetaZero], T_max: Optional[float] = None) -> dict:
    """
    Analyze zero counting function N(T) vs Riemann-von Mangoldt formula.
    """
    gammas = np.array([z.gamma for z in zeros])
    if T_max:
        gammas = gammas[gammas <= T_max]
    
    if len(gammas) < 2:
        return {}
    
    # Compute S(T) at zero locations
    S_vals = np.array([float(S_function(g)) for g in gammas])
    
    # Theoretical N(T) without S(T)
    N_smooth = gammas/(2*np.pi) * np.log(gammas/(2*np.pi)) - gammas/(2*np.pi) + 7/8
    N_actual = np.arange(1, len(gammas)+1)
    
    # Error
    error = N_actual - N_smooth
    
    return {
        'gammas': gammas,
        'N_actual': N_actual,
        'N_smooth': N_smooth,
        'S_values': S_vals,
        'error': error,
        'max_error': float(np.max(np.abs(error))),
        'rms_error': float(np.sqrt(np.mean(error**2))),
        'mean_S': float(np.mean(S_vals)),
        'std_S': float(np.std(S_vals)),
    }


def s_t_statistics(T_max: float, n_samples: int = 1000, dps: int = 30) -> dict:
    """
    Statistical properties of S(T) on [1, T_max].
    """
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        t_vals = np.linspace(1, T_max, n_samples)
        S_vals = np.array([float(S_function(t)) for t in t_vals])
        
        return {
            'mean': float(np.mean(S_vals)),
            'std': float(np.std(S_vals)),
            'min': float(np.min(S_vals)),
            'max': float(np.max(S_vals)),
            'skew': float(stats.skew(S_vals)),
            'kurtosis': float(stats.kurtosis(S_vals)),
            'median': float(np.median(S_vals)),
            'percentiles': {
                '1%': float(np.percentile(S_vals, 1)),
                '5%': float(np.percentile(S_vals, 5)),
                '95%': float(np.percentile(S_vals, 95)),
                '99%': float(np.percentile(S_vals, 99)),
            }
        }
    finally:
        mp_ctx.dps = old_dps


def s1_t_growth(T_max: float, dps: int = 30) -> tuple[float, float]:
    """
    Compute S₁(T) = ∫_0^T S(u) du and its growth.
    Known: S₁(T) = O(log T) unconditionally, O(log T / log log T) assuming RH.
    """
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        n_points = min(5000, int(T_max * 5))
        t_vals = np.linspace(1, T_max, n_points)
        S_vals = np.array([float(S_function(t)) for t in t_vals])
        S1 = integrate.simpson(S_vals, t_vals)
        
        # Theoretical bounds
        bound_uncond = np.log(T_max)
        bound_rh = np.log(T_max) / np.log(np.log(T_max))
        
        return float(S1), float(S1 / bound_uncond)
    finally:
        mp_ctx.dps = old_dps


def test_gue_hypothesis(zeros: list[ZetaZero]) -> dict:
    """
    Comprehensive test of GUE hypothesis for zeta zeros.
    """
    if len(zeros) < 10:
        return {'error': 'Need at least 10 zeros'}
    
    # Normalized gaps
    gammas = np.array([z.gamma for z in zeros])
    gaps = np.diff(gammas)
    avg_gaps = 2 * np.pi / np.log(gammas[:-1] / (2 * np.pi))
    norm_gaps = gaps / avg_gaps
    
    # KS test against GUE
    # GUE cdf for spacing (approximate)
    def gue_cdf(s):
        # Numerical integration of Wigner surmise
        from scipy import integrate
        return np.array([integrate.quad(gue_spacing_distribution, 0, x)[0] for x in s])
    
    # Compare empirical CDF with GUE
    sorted_gaps = np.sort(norm_gaps)
    ecdf = np.arange(1, len(sorted_gaps)+1) / len(sorted_gaps)
    gue_cdf_vals = gue_cdf(sorted_gaps)
    
    ks_stat = np.max(np.abs(ecdf - gue_cdf_vals))
    
    # Pair correlation
    from .zeros import pair_correlation
    centers, hist = pair_correlation(zeros, max_gap=3.0)
    gue_pc = gue_pair_correlation(centers)
    
    # Number variance
    L_vals, var_vals = compute_number_variance(zeros, L_max=5.0)
    # GUE prediction for large L: (1/π²)(log(2πL) + γ + 1)
    gamma_euler = 0.5772156649
    gue_var = (1/np.pi**2) * (np.log(2*np.pi*L_vals) + gamma_euler + 1)
    
    return {
        'ks_statistic': float(ks_stat),
        'mean_normalized_gap': float(np.mean(norm_gaps)),
        'var_normalized_gap': float(np.var(norm_gaps)),
        'pair_correlation_mse': float(np.mean((hist - gue_pc)**2)),
        'number_variance': {
            'L': L_vals.tolist(),
            'empirical': var_vals.tolist(),
            'gue_prediction': gue_var.tolist(),
        },
        'n_zeros': len(zeros),
    }


def keating_snaith_moments(max_k: int = 6) -> dict:
    """
    Keating-Snaith moment conjectures for ζ(1/2+it).
    
    I_k(T) ~ a_k g_k T (log T)^{k²}
    where g_k = G(k+1)² / G(2k+1) with G = Barnes G-function
    and a_k = product_p (1-1/p)^{k²} sum_{m=0}^∞ d_k(p^m)² / p^m
    
    Returns dict with g_k values and asymptotic coefficients.
    """
    from scipy.special import gamma
    
    # Barnes G-function values: G(1)=1, G(2)=1, G(3)=1, G(4)=2, G(5)=12, G(6)=288, G(7)=34560
    G = {1: 1, 2: 1, 3: 1, 4: 2, 5: 12, 6: 288, 7: 34560, 8: 2488320, 9: 1254113280}
    
    results = {}
    for k in range(1, max_k + 1):
        g_k = (G.get(k+1, gamma(k+1))**2) / G.get(2*k+1, gamma(2*k+1))
        
        # a_k values (known for small k)
        a_k = {1: 1.0, 2: 2/3, 3: 8/15, 4: 256/425, 5: 16384/5313}[k] if k <= 5 else 1.0
        
        results[k] = {
            'g_k': g_k,
            'a_k': a_k,
            'a_g': a_k * g_k,
            'exponent': k*k,
            'leading_coeff': a_k * g_k,
        }
    
    return results


def compute_zero_density(zeros: list[ZetaZero], sigma: float = 0.5, 
                         T_range: tuple = (0, 100)) -> dict:
    """
    Zero density estimates N(σ, T) = #{ρ = β + iγ : β > σ, |γ| ≤ T}.
    """
    gammas = np.array([z.gamma for z in zeros])
    # For RH, all zeros have σ = 0.5 exactly
    # This is trivial under RH; interesting for σ > 0.5
    
    if sigma <= 0.5:
        # Under RH, N(σ, T) = N(T) for σ < 0.5
        count = np.sum((gammas >= T_range[0]) & (gammas <= T_range[1]))
        return {'count': int(count), 'sigma': sigma, 'note': 'Under RH, all non-trivial zeros have Re=1/2'}
    
    # For σ > 0.5, we can't compute directly without finding off-line zeros
    return {'sigma': sigma, 'note': 'Off-line zero search not implemented'}


def run_full_statistical_analysis(T_max: float = 1000, n_zeros: int = 100) -> dict:
    """Run complete statistical analysis suite."""
    print(f"Running statistical analysis up to T={T_max}...")
    
    # Get zeros
    print("  Finding zeros...")
    zeros = find_first_n_zeros(n_zeros)
    print(f"  Found {len(zeros)} zeros")
    
    results = {}
    
    print("  Computing moments...")
    results['moments'] = compute_moments(T_max, max_k=4)
    
    print("  Analyzing N(T)...")
    results['n_t'] = n_t_analysis(zeros, T_max)
    
    print("  Computing S(T) statistics...")
    results['s_t'] = s_t_statistics(T_max)
    
    print("  Computing S₁(T)...")
    s1, s1_ratio = s1_t_growth(T_max)
    results['s1_t'] = {'S1': s1, 'ratio_to_log_T': s1_ratio}
    
    print("  Testing GUE hypothesis...")
    results['gue'] = test_gue_hypothesis(zeros)
    
    print("  Keating-Snaith predictions...")
    results['keating_snaith'] = keating_snaith_moments()
    
    print("  Zero density...")
    results['density'] = compute_zero_density(zeros)
    
    return results


if __name__ == "__main__":
    # Quick test
    zeros = find_first_n_zeros(20)
    print(f"Found {len(zeros)} zeros")
    
    stats = test_gue_hypothesis(zeros)
    print(f"KS statistic: {stats['ks_statistic']:.4f}")
    print(f"Mean normalized gap: {stats['mean_normalized_gap']:.4f}")
    print(f"Pair correlation MSE: {stats['pair_correlation_mse']:.6f}")
    
    moments = compute_moments(100, max_k=3)
    for m in moments:
        print(f"k={m.k}: I={m.value:.2f}, asymptotic={m.asymptotic:.2f}, ratio={m.ratio:.4f}")
    
    ks = keating_snaith_moments(6)
    for k, v in ks.items():
        print(f"k={k}: a_k*g_k={v['a_g']:.6f}, exponent={v['exponent']}")