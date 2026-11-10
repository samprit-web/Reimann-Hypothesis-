# Riemann Hypothesis: Foundations, Key Steps, and Numerical Exploration

**Status:** The Riemann Hypothesis (RH) is an open Millennium Prize problem. No complete, correct proof or disproof is known. This document records rigorous foundations, a key equivalence derivation, and a finite numerical verification (not a proof).

## 0. Statement
- `ζ(s)=∑_{n≥1} n^{-s}` for `Re(s)>1`, analytically continued to `ℂ \ {1}`.
- **RH:** every nontrivial zero `ρ` of `ζ(s)` satisfies `Re(ρ)=1/2`.

## 1. Euler product ⇒ no zeros for Re(s)>1 (proved)
For `σ=Re(s)>1`, `∑ n^{-σ}` converges absolutely.
1. Unique factorization: `∏_{p≤P}(1-p^{-s})^{-1}=∏_{p≤P}∑_{k≥0}p^{-ks}=∑_{n∈S(P)} n^{-s}`, where `S(P)` are integers with all prime factors `≤P`.
2. Absolute convergence allows `P→∞`, giving `ζ(s)=∏_p (1-p^{-s})^{-1}`.
3. Each factor `1-p^{-s}≠0` and the product converges to a nonzero value for `σ>1`.

**Conclusion:** `ζ(s)≠0` for `Re(s)>1`. (Hadamard/de la Vallée Poussin further prove `ζ(1+it)≠0`, `t≠0`.)

## 2. Continuation, functional equation, zero symmetry (proved)
1. `ζ(s)` extends meromorphically to `ℂ` with a simple pole at `s=1` (residue 1).
2. Completed function `ξ(s)=½ s(s-1)π^{-s/2}Γ(s/2)ζ(s)` is entire (order 1) and satisfies **`ξ(s)=ξ(1-s)`**.
3. Poles of `Γ(s/2)` force **trivial zeros** at `s=-2,-4,…`.
4. By (1) and symmetry `s↦1-s`, all other (**nontrivial**) zeros lie in the **critical strip** `0<Re(s)<1`.
5. Real coefficients and (2) imply zero symmetry: if `ρ` is nontrivial, so are `1-ρ`, `\barρ`, `1-\barρ`.

## 3. Explicit formula link to primes (proved, sketch)
Let `ψ(x)=∑_{n≤x}Λ(n)` (`Λ` = von Mangoldt). From `-ζ'(s)/ζ(s)=∑_{n≥1}Λ(n)n^{-s}` (Re(s)>1) and Perron’s formula (c>1):
1. `ψ_0(x)= (1/2πi)∫_{c-i∞}^{c+i∞} (-ζ'(s)/ζ(s)) x^s/s ds`, where `ψ_0` is `ψ` adjusted at jumps.
2. Shift contour left, summing residues of `(-ζ'/ζ)(x^s/s)`:
   - pole of `ζ` at `s=1` → residue `x`
   - trivial zeros `s=-2m` → residues `-x^{-2m}/(2m)`
   - nontrivial zeros `s=ρ` → residues `-x^ρ/ρ`
   - `s=0` → residue `-ζ'(0)/ζ(0)`
3. Yields **`ψ_0(x)=x - ∑_{ρ} x^ρ/ρ - log(2π) - ½log(1-x^{-2})`** (with convergent interpretation of the zero sum).
4. If `Re(ρ)≤Θ` for all `ρ`, then `|x^ρ|≤x^Θ` and (with zero-density bounds) `ψ(x)=x + O(x^Θ log^2 x)`. Conversely, a bound `ψ(x)-x=O(x^{Θ+ε})` forces `Re(ρ)≤Θ`.

**Equivalence:** RH (`Θ=1/2`) ⇔ `ψ(x)=x + O(x^{1/2} log^2 x)` ⇔ optimal error in the Prime Number Theorem.

## 4. Numerical verification on the critical line (executed)
Using the Riemann–Siegel `Z(t)` (real, `Z(t)=0 ⇔ ζ(1/2+it)=0`) with sign-change bracketing + bisection:

- Script: `riemann/verify_zeros.js` (Node.js)
- Command: `node riemann/verify_zeros.js`
- Result: **21 sign-change zeros found for `0 < Im(ρ) ≤ 80`**, all on `Re(s)=1/2` by construction.
- First ordinates found (vs known): `14.137218` (14.134725), `21.021293` (21.022040), `25.011055` (25.010858), … `77.144697` (77.144840). Differences ~`10^{-4}–10^{-3}` from a low-order `Z(t)`/remainder approximation (not a proof-grade verifier).
- Interpretation: supports RH on this finite range only; **finite numerical checks cannot prove RH**.

## 5. What remains for a complete proof
A proof must show `Re(ρ)=1/2` for **every** nontrivial zero (not infinitely many, not a positive proportion, not up to finite height). Known results—zero-free regions, proportion-on-the-line theorems, and all finite computations—do not exclude a hypothetical zero off the line at sufficiently large height. No verified argument closing this gap exists.
