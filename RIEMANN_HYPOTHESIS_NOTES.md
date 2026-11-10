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

## 6. Next proved step: no zeros on Re(s)=1 (Hadamard–de la Vallée Poussin, 1896)
This is a key rigorous advance beyond the Euler-product region, but it does **not** imply RH.

**Theorem.** `ζ(1 + it) ≠ 0` for all real `t ≠ 0`.

**Proof steps (Mertens/trigonometric form):**
1. For `σ > 1`, `log ζ(s) = ∑_{p} ∑_{m≥1} \frac{p^{-ms}}{m}`, hence  
   `Re log ζ(σ + it) = log|ζ(σ + it)| = ∑_{p,m} \frac{p^{-mσ}}{m} cos(m t \log p)`.
2. Trigonometric inequality: for any real `θ`, `3 + 4 cos θ + cos 2θ = 2(1 + cos θ)^2 ≥ 0`.
3. Set `θ = m t \log p`, multiply by `p^{-mσ}/m ≥ 0`, sum over `p,m`:  
   `3 log|ζ(σ)| + 4 log|ζ(σ + it)| + log|ζ(σ + 2it)| ≥ 0`, so  
   `|ζ(σ)^3 · ζ(σ + it)^4 · ζ(σ + 2it)| ≥ 1` for all `σ > 1`, `t ∈ ℝ`.
4. Suppose for contradiction `ζ(1 + it_0) = 0` with `t_0 ≠ 0`. As `σ → 1^+`:
   - `ζ(σ) = \frac{1}{σ-1} + O(1)` (simple pole) ⇒ `|ζ(σ)^3| = O((σ-1)^{-3})`.
   - zero at `1+it_0` ⇒ `ζ(σ + it_0) = O(σ-1)` ⇒ `|ζ(σ + it_0)^4| = O((σ-1)^4)`.
   - analyticity at `1 + 2it_0` (not a pole) ⇒ `|ζ(σ + 2it_0)| = O(1)`.
5. Product is `O(σ-1) → 0` as `σ → 1^+`, contradicting step 3. Therefore no zero lies on `Re(s)=1`.

**Consequence.** Combined with §1–2, all nontrivial zeros lie in `0 < Re(ρ) < 1`. Stronger zero-free regions exist (e.g. Vinogradov–Korobov: `σ ≥ 1 - c/((log|t|)^{2/3}(log log|t|)^{1/3})`), still far from `Re(ρ)=1/2`.

## 7. Status toward a final complete proof
A complete proof of RH would require showing **every** nontrivial zero satisfies `Re(ρ)=1/2`. No known argument closes this gap:
- **Partial results:** infinitely many zeros on the line (Hardy), positive proportion on the line (Selberg/Levinson/Conrey), and zero-free regions exclude strips near `Re(s)=1` but not off-line zeros arbitrarily close to `1/2`.
- **Numerical evidence:** zeros verified on the line to extremely large heights (finite; cannot imply “all”).
- **Equivalences/criteria** (§3, Li’s criterion, etc.) are logically equivalent to RH but not proven.

**Conclusion:** Steps 1–6 and the numerical check in §4 are rigorous/constructive progress, but a final complete proof of the Riemann Hypothesis does not follow from them and is not currently known.

## 8. Theoretical attempt toward a proof (Li’s criterion) and the gap
This section outlines a rigorous equivalence that reduces RH to an explicit positivity statement, then identifies why current theory does not close it. **This is not a complete proof.**

### 8.1 Setup (proved)
Let `ξ(s)=½ s(s-1)π^{-s/2}Γ(s/2)ζ(s)` be entire of order 1 with `ξ(s)=ξ(1-s)` and zeros exactly the nontrivial zeros `ρ` of `ζ` (symmetric about `Re(s)=1/2` and the real axis). By Hadamard factorization,
`ξ(s)=ξ(0) ∏_{ρ} (1 - s/ρ) e^{s/ρ}` (with pairing giving convergence). Define the Stieltjes/Keiper–Li coefficients
`λ_n = \frac{1}{(n-1)!}\frac{d^n}{ds^n}\!\left[s^{n-1}\log ξ(s)\right]_{s=1}`, `n≥1`.

### 8.2 Zero-sum representation (proved)
Differentiating `log ξ` yields the absolutely-convergent (in paired sense) identity
`λ_n = ∑_{ρ} \left[1 - \left(1 - \frac{1}{ρ}\right)^n\right]`, summed over all nontrivial zeros `ρ`.
- Conjugate/symmetry pairing makes `λ_n ∈ ℝ`.
- Equivalent forms (via `ρ ↦ 1-ρ`) give `λ_n = ∑_{ρ} [1 - (ρ/(ρ-1))^n]` as well.

### 8.3 Li’s criterion (proved equivalence, Li 1997; Bombieri–Lagarias 1999)
**Theorem.** RH holds ⇔ `λ_n > 0` for every `n ≥ 1` (equivalently `λ_n ≥ 0` for all `n`).

*Necessity (RH ⇒ positivity), idea:* if `Re(ρ)=1/2`, write `ρ=1/2+iγ`. Then `|1-1/ρ|=|(ρ-1)/ρ|=1`, so `1-1/ρ = e^{iθ_ρ}` with `θ_ρ≠0 (mod 2π)` for nontrivial zeros, and each term contributes `1 - cos(nθ_ρ) - i sin(nθ_ρ)`; symmetric pairing yields a nonnegative real sum, with strict positivity from nonzero terms.

*Sufficiency (positivity ⇒ RH), idea:* if some `Re(ρ)>1/2`, then `|1-1/ρ|>1` or the geometry of terms forces `λ_n` to take negative/oscillatory values for large `n` (Bombieri–Lagarias give a precise growth/positivity argument for general sequences satisfying the same functional symmetry).

Thus a complete theoretical proof of RH is equivalent to proving `λ_n > 0` for all `n`.

### 8.4 Why this does not close RH (the gap)
1. **Positivity is unproved:** No argument establishes `λ_n ≥ 0` for all `n` without assuming RH or an equivalent hypothesis. Known results give asymptotics/partial positivity but not uniform positivity.
2. **Off-line zero obstruction:** A single zero `ρ_0` with `Re(ρ_0)≠1/2` would make `|1-1/ρ_0|` or `|ρ_0/(ρ_0-1)|` differ from 1, and its contribution dominates/perturbs `λ_n` for large `n`; excluding this for every zero is exactly RH.
3. **Equivalent reformulations are not proofs:** Weil’s positivity criterion, Beurling–Nyman/Báez-Duarte criteria, and de Bruijn–Newman/Polya approaches similarly translate RH into an analytic/positivity/spectral statement whose truth is unknown. Each reduces RH to a concrete conjecture but supplies no verified mechanism forcing it.

### 8.5 Conclusion of the attempt
Li’s criterion provides a sharp theoretical target: prove `λ_n(ξ)>0` ∀n. All steps above are rigorous; the final positivity claim is equivalent to RH and remains unproved. Therefore this theoretical path, as with all known paths, reaches a precise but currently unbridged gap rather than a complete proof.
