"""
Visualization tools for Riemann zeta function and zeros.

Includes:
- Critical strip phase portraits
- Zero distribution plots
- S(T) and Z(t) plots
- Pair correlation histograms
- GUE comparison
"""

from __future__ import annotations

import mpmath as mp
from mpmath import mp as mp_ctx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from typing import Optional, Callable
from dataclasses import dataclass
from .zeta import zeta, xi_function, riemann_siegel_Z, riemann_siegel_theta, S_function
from .zeros import ZetaZero, find_zeros_up_to


@dataclass
class PlotConfig:
    """Configuration for plots."""
    figsize: tuple = (12, 8)
    dpi: int = 150
    cmap: str = 'RdBu'
    style: str = 'seaborn-v0_8-darkgrid'


def plot_zeta_critical_line(T_max: float = 50, dps: int = 30,
                            config: Optional[PlotConfig] = None,
                            save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot ζ(1/2 + it) on the critical line.
    Shows real and imaginary parts, and |ζ|.
    """
    if config is None:
        config = PlotConfig()
    
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        t_vals = np.linspace(0.1, T_max, 2000)
        zeta_vals = []
        
        for t in t_vals:
            z = zeta(complex(0.5, t))
            zeta_vals.append(complex(z.value))
        
        zeta_vals = np.array(zeta_vals)
        real_vals = zeta_vals.real
        imag_vals = zeta_vals.imag
        abs_vals = np.abs(zeta_vals)
        
        fig, axes = plt.subplots(3, 1, figsize=config.figsize, dpi=config.dpi, sharex=True)
        
        # Real part
        axes[0].plot(t_vals, real_vals, 'b-', linewidth=0.5, label='Re ζ(1/2+it)')
        axes[0].axhline(y=0, color='k', linestyle=':', alpha=0.3)
        axes[0].set_ylabel('Re ζ')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Imaginary part
        axes[1].plot(t_vals, imag_vals, 'r-', linewidth=0.5, label='Im ζ(1/2+it)')
        axes[1].axhline(y=0, color='k', linestyle=':', alpha=0.3)
        axes[1].set_ylabel('Im ζ')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Absolute value
        axes[2].plot(t_vals, abs_vals, 'g-', linewidth=0.5, label='|ζ(1/2+it)|')
        axes[2].set_ylabel('|ζ|')
        axes[2].set_xlabel('t')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # Mark zeros
        zeros = find_zeros_up_to(T_max, dps=25)
        for z in zeros:
            for ax in axes:
                ax.axvline(x=z.gamma, color='k', linestyle='--', alpha=0.2, linewidth=0.5)
        
        fig.suptitle(f'Riemann ζ(1/2 + it) for t ∈ [0, {T_max}]', fontsize=14)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=config.dpi, bbox_inches='tight')
        
        return fig
    finally:
        mp_ctx.dps = old_dps


def plot_riemann_siegel_Z(T_max: float = 100, dps: int = 30,
                          config: Optional[PlotConfig] = None,
                          save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot Riemann-Siegel Z function (real-valued on critical line).
    Zeros correspond to zeta zeros.
    """
    if config is None:
        config = PlotConfig()
    
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        t_vals = np.linspace(0.1, T_max, 5000)
        Z_vals = np.array([float(riemann_siegel_Z(t)) for t in t_vals])
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        ax.plot(t_vals, Z_vals, 'b-', linewidth=0.5)
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.set_xlabel('t')
        ax.set_ylabel('Z(t)')
        ax.set_title(f'Riemann-Siegel Z(t) for t ∈ [0, {T_max}]')
        ax.grid(True, alpha=0.3)
        
        # Mark zeros
        zeros = find_zeros_up_to(T_max, dps=25)
        for z in zeros:
            ax.axvline(x=z.gamma, color='r', linestyle='--', alpha=0.3, linewidth=0.5)
            ax.plot(z.gamma, 0, 'ro', markersize=3)
        
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=config.dpi, bbox_inches='tight')
        return fig
    finally:
        mp_ctx.dps = old_dps


def plot_S_function(T_max: float = 100, dps: int = 30,
                    config: Optional[PlotConfig] = None,
                    save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot S(T) = 1/π arg ζ(1/2 + iT).
    Measures deviation from expected zero count.
    """
    if config is None:
        config = PlotConfig()
    
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        t_vals = np.linspace(1, T_max, 2000)
        S_vals = np.array([float(S_function(t)) for t in t_vals])
        
        fig, axes = plt.subplots(2, 1, figsize=config.figsize, dpi=config.dpi, sharex=True)
        
        axes[0].plot(t_vals, S_vals, 'b-', linewidth=0.5)
        axes[0].axhline(y=0, color='k', linestyle=':', alpha=0.3)
        axes[0].set_ylabel('S(T)')
        axes[0].set_title(f'S(T) = 1/π arg ζ(1/2 + iT) for T ∈ [1, {T_max}]')
        axes[0].grid(True, alpha=0.3)
        
        # Cumulative S1(T) = ∫_0^T S(u) du
        from scipy import integrate
        S1_vals = np.zeros_like(S_vals)
        for i in range(1, len(t_vals)):
            S1_vals[i] = integrate.simpson(S_vals[:i+1], t_vals[:i+1])
        
        axes[1].plot(t_vals, S1_vals, 'r-', linewidth=0.5)
        axes[1].axhline(y=0, color='k', linestyle=':', alpha=0.3)
        axes[1].set_ylabel('S₁(T)')
        axes[1].set_xlabel('T')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=config.dpi, bbox_inches='tight')
        return fig
    finally:
        mp_ctx.dps = old_dps


def plot_critical_strip_phase(sigma_range: tuple = (0, 1), t_range: tuple = (0, 50),
                              resolution: int = 200, dps: int = 25,
                              config: Optional[PlotConfig] = None,
                              save_path: Optional[str] = None) -> plt.Figure:
    """
    Phase portrait of ζ(s) in the critical strip.
    Color = argument, brightness = log|ζ|.
    """
    if config is None:
        config = PlotConfig()
    
    old_dps = mp_ctx.dps
    mp_ctx.dps = dps
    try:
        sigma_min, sigma_max = sigma_range
        t_min, t_max = t_range
        
        sigma_vals = np.linspace(sigma_min, sigma_max, resolution)
        t_vals = np.linspace(t_min, t_max, resolution)
        
        arg_vals = np.zeros((resolution, resolution))
        log_abs_vals = np.zeros((resolution, resolution))
        
        for i, sigma in enumerate(sigma_vals):
            for j, t in enumerate(t_vals):
                s = complex(sigma, t)
                z = zeta(s)
                val = complex(z.value)
                arg_vals[i, j] = np.angle(val)
                log_abs_vals[i, j] = np.log(abs(val) + 1e-10)
        
        fig, axes = plt.subplots(1, 2, figsize=(config.figsize[0]*1.5, config.figsize[1]), dpi=config.dpi)
        
        # Phase (argument)
        im1 = axes[0].imshow(arg_vals.T, extent=[sigma_min, sigma_max, t_min, t_max],
                             origin='lower', aspect='auto', cmap='hsv', vmin=-np.pi, vmax=np.pi)
        axes[0].axvline(x=0.5, color='w', linestyle='--', alpha=0.7)
        axes[0].set_xlabel('Re(s)')
        axes[0].set_ylabel('Im(s)')
        axes[0].set_title('arg ζ(s)')
        plt.colorbar(im1, ax=axes[0], label='Argument')
        
        # Log magnitude
        im2 = axes[1].imshow(log_abs_vals.T, extent=[sigma_min, sigma_max, t_min, t_max],
                             origin='lower', aspect='auto', cmap='RdBu_r')
        axes[1].axvline(x=0.5, color='w', linestyle='--', alpha=0.7)
        axes[1].set_xlabel('Re(s)')
        axes[1].set_ylabel('Im(s)')
        axes[1].set_title('log |ζ(s)|')
        plt.colorbar(im2, ax=axes[1], label='log |ζ|')
        
        fig.suptitle(f'Phase portrait of ζ(s) in critical strip', fontsize=14)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=config.dpi, bbox_inches='tight')
        return fig
    finally:
        mp_ctx.dps = old_dps


def plot_zero_distribution(zeros: list[ZetaZero], max_t: Optional[float] = None,
                           config: Optional[PlotConfig] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot zero distribution and statistics.
    """
    if config is None:
        config = PlotConfig()
    
    gammas = [z.gamma for z in zeros]
    if max_t:
        gammas = [g for g in gammas if g <= max_t]
    
    if len(gammas) < 2:
        print("Need at least 2 zeros for distribution plot")
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=config.figsize, dpi=config.dpi)
    
    # 1. Zero heights
    axes[0, 0].plot(gammas, np.arange(1, len(gammas)+1), 'b-', linewidth=1)
    axes[0, 0].set_xlabel('γ (imaginary part)')
    axes[0, 0].set_ylabel('N(γ)')
    axes[0, 0].set_title('Zero counting function N(T)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Overlay theoretical N(T)
    t_dense = np.linspace(gammas[0], gammas[-1], 200)
    N_theoretical = [t/(2*np.pi)*np.log(t/(2*np.pi)) - t/(2*np.pi) + 7/8 for t in t_dense]
    axes[0, 0].plot(t_dense, N_theoretical, 'r--', alpha=0.7, label='Riemann-von Mangoldt')
    axes[0, 0].legend()
    
    # 2. Gap distribution
    gaps = np.diff(gammas)
    avg_gaps = 2*np.pi / np.log(np.array(gammas[:-1]) / (2*np.pi))
    norm_gaps = gaps / avg_gaps
    
    axes[0, 1].hist(norm_gaps, bins=30, density=True, alpha=0.7, edgecolor='black')
    # GUE prediction
    x = np.linspace(0, max(norm_gaps), 100)
    gue = 1 - (np.sin(np.pi*x)/(np.pi*x))**2
    axes[0, 1].plot(x, gue, 'r-', label='GUE (Montgomery)')
    axes[0, 1].set_xlabel('Normalized gap')
    axes[0, 1].set_ylabel('Density')
    axes[0, 1].set_title('Normalized gap distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. S(T) at zeros
    S_at_zeros = [float(S_function(g)) for g in gammas]
    axes[1, 0].scatter(gammas, S_at_zeros, s=10, alpha=0.6)
    axes[1, 0].axhline(y=0, color='k', linestyle=':', alpha=0.3)
    axes[1, 0].set_xlabel('γ')
    axes[1, 0].set_ylabel('S(γ)')
    axes[1, 0].set_title('S(T) at zero locations')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Lehmer phenomenon: Z'(γ)
    Z_derivs = [abs(z.Z_derivative) for z in zeros if z.Z_derivative != 0]
    if Z_derivs:
        axes[1, 1].hist(np.log10(Z_derivs), bins=30, density=True, alpha=0.7, edgecolor='black')
        axes[1, 1].set_xlabel('log₁₀ |Z\'(γ)|')
        axes[1, 1].set_ylabel('Density')
        axes[1, 1].set_title('Lehmer phenomenon: |Z\'(γ)| distribution')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=config.dpi, bbox_inches='tight')
    return fig


def plot_pair_correlation(zeros: list[ZetaZero], max_gap: float = 3.0,
                          config: Optional[PlotConfig] = None,
                          save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot pair correlation of zero spacings vs GUE prediction.
    """
    if config is None:
        config = PlotConfig()
    
    from .zeros import pair_correlation
    
    centers, hist = pair_correlation(zeros, max_gap=max_gap)
    
    if len(centers) == 0:
        return None
    
    fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
    
    ax.bar(centers, hist, width=centers[1]-centers[0], alpha=0.6, 
           edgecolor='black', label='Zeta zeros (adjacent)')
    
    # GUE prediction
    x = np.linspace(0, max_gap, 200)
    gue = 1 - (np.sin(np.pi*x)/(np.pi*x))**2
    ax.plot(x, gue, 'r-', linewidth=2, label='GUE: 1 - (sin πu/πu)²')
    
    # Poisson (uncorrelated)
    ax.plot(x, np.ones_like(x), 'g--', label='Poisson (uncorrelated)')
    
    ax.set_xlabel('Normalized spacing u')
    ax.set_ylabel('Pair correlation R₂(u)')
    ax.set_title('Pair correlation of normalized zero spacings')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max_gap)
    
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=config.dpi, bbox_inches='tight')
    return fig


def plot_moments(T_max: float = 100, max_k: int = 4,
                 config: Optional[PlotConfig] = None,
                 save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot moments ∫_0^T |ζ(1/2+it)|^{2k} dt.
    """
    if config is None:
        config = PlotConfig()
    
    old_dps = mp_ctx.dps
    mp_ctx.dps = 25
    try:
        t_vals = np.logspace(1, np.log10(T_max), 50)
        
        fig, axes = plt.subplots(2, 2, figsize=config.figsize, dpi=config.dpi)
        axes = axes.flatten()
        
        for idx, k in enumerate(range(1, max_k + 1)):
            if idx >= 4:
                break
            
            moments = []
            for T in t_vals:
                # Simple trapezoidal integration
                n_points = min(1000, int(T * 10))
                t_int = np.linspace(1, T, n_points)
                vals = np.array([abs(zeta(complex(0.5, t)).value)**(2*k) for t in t_int])
                moment = np.trapz(vals, t_int)
                moments.append(moment)
            
            ax = axes[idx]
            ax.loglog(t_vals, moments, 'b-', label=f'k={k}')
            
            # Asymptotic prediction (conjectural)
            # ∫_0^T |ζ|^{2k} ~ C_k T (log T)^{k²}
            if k == 1:
                asymp = t_vals * np.log(t_vals)
            elif k == 2:
                asymp = t_vals * np.log(t_vals)**4
            else:
                asymp = t_vals * np.log(t_vals)**(k*k)
            
            ax.loglog(t_vals, asymp/asymp[-1]*moments[-1], 'r--', alpha=0.7, label=f'Asymptotic ~ T log^{{k²}} T')
            
            ax.set_xlabel('T')
            ax.set_ylabel(f'∫|ζ|²ᵏ dt')
            ax.set_title(f'Moment k={k}')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=config.dpi, bbox_inches='tight')
        return fig
    finally:
        mp_ctx.dps = old_dps


def plot_xi_function(t_range: tuple = (0, 50),
                     config: Optional[PlotConfig] = None,
                     save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot Riemann xi function ξ(1/2+it) (real and entire).
    """
    if config is None:
        config = PlotConfig()
    
    old_dps = mp_ctx.dps
    mp_ctx.dps = 30
    try:
        t_vals = np.linspace(t_range[0], t_range[1], 2000)
        xi_vals = np.array([float(xi_function(complex(0.5, t)).value) for t in t_vals])
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        ax.plot(t_vals, xi_vals, 'b-', linewidth=0.8)
        ax.axhline(y=0, color='k', linestyle=':', alpha=0.3)
        ax.set_xlabel('t')
        ax.set_ylabel('ξ(1/2+it)')
        ax.set_title('Riemann ξ function on critical line (real-valued, entire)')
        ax.grid(True, alpha=0.3)
        
        # Mark zeros
        zeros = find_zeros_up_to(t_range[1], dps=25)
        for z in zeros:
            ax.axvline(x=z.gamma, color='r', linestyle='--', alpha=0.3, linewidth=0.5)
            ax.plot(z.gamma, 0, 'ro', markersize=3)
        
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=config.dpi, bbox_inches='tight')
        return fig
    finally:
        mp_ctx.dps = old_dps


def generate_all_plots(output_dir: str = "/workspace/app/riemann/plots", 
                       T_max: float = 100) -> dict:
    """Generate all standard plots and save to directory."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    print("Generating plots...")
    
    print("  1. ζ(1/2+it) on critical line...")
    fig = plot_zeta_critical_line(T_max, save_path=f"{output_dir}/zeta_critical_line.png")
    results['zeta_critical_line'] = fig
    plt.close(fig)
    
    print("  2. Riemann-Siegel Z(t)...")
    fig = plot_riemann_siegel_Z(T_max, save_path=f"{output_dir}/riemann_siegel_Z.png")
    results['riemann_siegel_Z'] = fig
    plt.close(fig)
    
    print("  3. S(T) function...")
    fig = plot_S_function(T_max, save_path=f"{output_dir}/S_function.png")
    results['S_function'] = fig
    plt.close(fig)
    
    print("  4. Critical strip phase portrait...")
    fig = plot_critical_strip_phase(save_path=f"{output_dir}/critical_strip_phase.png")
    results['critical_strip_phase'] = fig
    plt.close(fig)
    
    print("  5. Zero distribution...")
    zeros = find_zeros_up_to(T_max)
    fig = plot_zero_distribution(zeros, save_path=f"{output_dir}/zero_distribution.png")
    results['zero_distribution'] = fig
    if fig:
        plt.close(fig)
    
    print("  6. Pair correlation...")
    fig = plot_pair_correlation(zeros, save_path=f"{output_dir}/pair_correlation.png")
    results['pair_correlation'] = fig
    if fig:
        plt.close(fig)
    
    print("  7. Moments...")
    fig = plot_moments(T_max, save_path=f"{output_dir}/moments.png")
    results['moments'] = fig
    plt.close(fig)
    
    print("  8. ξ function...")
    fig = plot_xi_function((0, T_max), save_path=f"{output_dir}/xi_function.png")
    results['xi_function'] = fig
    plt.close(fig)
    
    print(f"All plots saved to {output_dir}")
    return results


if __name__ == "__main__":
    generate_all_plots()