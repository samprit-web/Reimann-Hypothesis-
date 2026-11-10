"""
Riemann Hypothesis Research Toolkit

A computational framework for exploring the Riemann zeta function,
its zeros, and related mathematical structures.

Modules:
- zeta: High-precision zeta function evaluation
- zeros: Zero-finding algorithms
- visualize: Plotting and visualization
- statistics: Statistical analysis of zeros
- literature: Literature review database
"""

from .zeta import (
    zeta, zeta_mpmath, zeta_euler_maclaurin, zeta_riemann_siegel,
    zeta_functional_equation, xi_function, riemann_siegel_Z,
    riemann_siegel_theta, gram_points, S_function, N_function,
    ZetaResult, set_precision, get_precision, verify_functional_equation,
    count_zeros_up_to, find_zeros_up_to,
)
from .zeros import (
    find_zero_newton, find_zero_secant, find_zero_brent,
    turing_method, find_zeros_up_to, find_first_n_zeros,
    verify_zero_rigorously, detect_lehmer_phenomenon,
    compute_zero_statistics, pair_correlation, ZetaZero,
)
from .visualize import (
    plot_zeta_critical_line, plot_riemann_siegel_Z, plot_S_function,
    plot_critical_strip_phase, plot_zero_distribution,
    plot_pair_correlation, plot_moments, plot_xi_function,
    generate_all_plots, PlotConfig,
)
from .statistics import (
    compute_moments, gue_spacing_distribution, gue_pair_correlation,
    number_variance, compute_number_variance, n_t_analysis,
    s_t_statistics, s1_t_growth, test_gue_hypothesis,
    keating_snaith_moments, compute_zero_density,
    run_full_statistical_analysis, MomentResult,
)
from .literature import (
    LiteratureDatabase, Paper, ApproachCategory, ResultStatus,
    init_database, KEY_PAPERS,
)

__version__ = "0.1.0"
__author__ = "Riemann Research Project"

__all__ = [
    # zeta
    "zeta", "zeta_mpmath", "zeta_euler_maclaurin", "zeta_riemann_siegel",
    "zeta_functional_equation", "xi_function", "riemann_siegel_Z",
    "riemann_siegel_theta", "gram_points", "S_function", "N_function",
    "ZetaResult", "set_precision", "get_precision", "verify_functional_equation",
    "count_zeros_up_to", "find_zeros_up_to",
    # zeros
    "find_zero_newton", "find_zero_secant", "find_zero_brent",
    "turing_method", "find_zeros_up_to", "find_first_n_zeros",
    "verify_zero_rigorously", "detect_lehmer_phenomenon",
    "compute_zero_statistics", "pair_correlation", "ZetaZero",
    # visualize
    "plot_zeta_critical_line", "plot_riemann_siegel_Z", "plot_S_function",
    "plot_critical_strip_phase", "plot_zero_distribution",
    "plot_pair_correlation", "plot_moments", "plot_xi_function",
    "generate_all_plots", "PlotConfig",
    # statistics
    "compute_moments", "gue_spacing_distribution", "gue_pair_correlation",
    "number_variance", "compute_number_variance", "n_t_analysis",
    "s_t_statistics", "s1_t_growth", "test_gue_hypothesis",
    "keating_snaith_moments", "compute_zero_density",
    "run_full_statistical_analysis", "MomentResult",
    # literature
    "LiteratureDatabase", "Paper", "ApproachCategory", "ResultStatus",
    "init_database", "KEY_PAPERS",
]