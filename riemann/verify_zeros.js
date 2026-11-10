/**
 * Numerical verification: first nontrivial zeros of ζ(s) lie on Re(s)=1/2.
 * Riemann-Siegel Z(t): real for real t, Z(t)=0 <=> ζ(1/2 + i t)=0.
 */

function theta(t) {
  // Stirling asymptotic for Riemann-Siegel theta
  const it = 1/t, it2 = it*it, it4 = it2*it2, it6 = it4*it2;
  return (t/2) * Math.log(t/(2*Math.PI)) - t/2 - Math.PI/8 + it/48 + 7*it2*it/(5760) + 31*it4*it/(80640);
}

function C0(p) { return Math.cos(2*Math.PI*(p*p - p - 1/16)); }
function C1(p) { // - (1/(96π^2)) Φ'''(p) approx coefficients
  const pi = Math.PI;
  return (-1/(96*pi*pi)) * ((1/3)*Math.pow(2*pi,3)*0 + 0); // simplified below
}
// Gabcke/standard coefficients for R
function Rterm(tau, N) {
  const p = tau - N;
  const z = 1 - 2*p;
  // C0..C4 coefficients (Odlyzko/standard)
  const c0 = Math.cos(2*Math.PI*(p*p - p - 1/16)) / Math.cos(2*Math.PI*p);
  const c1 = (1/12) * Math.pow(Math.PI, -0.5) * 0; // not used in this form
  // Use standard explicit remainder:
  // R = (-1)^(N-1) * tau^(-1/2) * sum C_j * tau^(-j/2)
  const tp = Math.pow(tau, -0.5);
  const pi = Math.PI;
  const C = [];
  C[0] = Math.cos(2*pi*(p*p - p - 1/16)) / Math.cos(2*pi*p);
  // C1
  C[1] = -(1/(96*pi*pi)) * (
    (Math.cos(2*pi*(p*p - p - 1/16 + 3/8 - 1/2))) // placeholder
  );
  // Better: use known high-accuracy coefficients (Gabcke)
  // Φ(z) = cos(π/2*(z^2+3/4)) / cos(π*z), z=1-2p gives same as c0 above? use standard:
  // C0(p)=cos(2π(p^2-p-1/16))/cos(2πp)
  // C1(p)=-(1/(2^5*3*π^2))* (d^3/dp^3 cos(2π(p^2-p-1/16))/cos(2πp)) — use numeric derivative of C0 block
  function C0v(pv){ return Math.cos(2*Math.PI*(pv*pv - pv - 1/16))/Math.cos(2*Math.PI*pv); }
  function d3(f,x){ const h=1e-5; return (f(x+2*h)-2*f(x+h)+2*f(x-h)-f(x-2*h))/(2*h*h*h); }
  function d5(f,x){ const h=2e-4; return (f(x+3*h)-4*f(x+2*h)+5*f(x+h)-5*f(x-h)+4*f(x-2*h)-f(x-3*h))/(2*Math.pow(h,5)); }
  const c0n = C0v(p);
  const c1n = -(1/(Math.pow(2,5)*3*Math.pow(pi,2))) * d3(C0v,p);
  const c2n = (1/(Math.pow(2,11)*Math.pow(3,2)*Math.pow(pi,4))) * d5(C0v,p) + (1/(Math.pow(2,6)*Math.pow(pi,2))) * d3(C0v,p); // rough
  // simpler robust: use only C0,C1 with better C1
  const c1b = (1/(16*Math.PI*Math.PI)) * (C0v(p+1e-6)+C0v(p-1e-6)-2*c0n)/(1e-12) * 0; // ignore
  // revert to reliable: c0 + small correction via numeric C1
  const c1c = -(1/(96*pi*pi)) * d3(C0v,p);
  let R = Math.pow(-1, N-1) * tp * (c0n + c1c*Math.pow(tau,-1));
  return R;
}

function Z(t) {
  if (t < 1e-10) return -1.4603545088095868;
  const tau = Math.sqrt(t/(2*Math.PI));
  const N = Math.floor(tau);
  const th = theta(t);
  let sum = 0;
  for (let n = 1; n <= N; n++) sum += Math.cos(th - t*Math.log(n)) / Math.sqrt(n);
  sum *= 2;
  let R = 0;
  const p = tau - N;
  if (Math.abs(Math.cos(2*Math.PI*p)) > 1e-8) {
    R = Rterm(tau, N);
  }
  return sum + R;
}

function findZeros(tMin, tMax, step = 0.02) {
  const zeros = [];
  let t = tMin, prevZ = Z(t);
  while (t < tMax) {
    const t2 = Math.min(t + step, tMax);
    const curZ = Z(t2);
    if (prevZ * curZ <= 0) {
      let a = t, b = t2, fa = prevZ, fb = curZ;
      for (let i = 0; i < 100; i++) {
        const m = (a+b)/2, fm = Z(m);
        if (Math.abs(fm) < 1e-14 || (b-a) < 1e-12) { a = b = m; fa = fb = fm; break; }
        if (fa * fm <= 0) { b = m; fb = fm; } else { a = m; fa = fm; }
      }
      const z = (a+b)/2;
      if (zeros.length === 0 || Math.abs(z - zeros[zeros.length-1]) > 1e-6) zeros.push(z);
    }
    t = t2; prevZ = curZ;
  }
  return zeros;
}

const known = [14.134725141734693,21.022039638771554,25.010857580145688,30.424876125859513,32.935061587739189,37.586178158825671,40.918719012147495,43.327073280914999,48.005150881167159,49.773832477672302,52.970321477714460,56.446247697063394,59.347044002602353,60.831778524609809,65.112544048081606,67.079810529494173,69.546401711173979,72.067157674481907,75.704690699083933,77.144840068874805];
const found = findZeros(1, 80, 0.02);
console.log('Verified nontrivial zeros on the critical line Re(s)=1/2 (via Z(t) sign changes)');
console.log(' idx |       t (found)       |      t (known)        |  |Z(t)|      | diff');
console.log('-----+-----------------------+-----------------------+--------------+----------');
let ok = 0;
for (let i = 0; i < Math.min(found.length, known.length); i++) {
  const z = found[i], k = known[i], diff = Math.abs(z-k), absZ = Math.abs(Z(z));
  if (diff < 5e-4 && absZ < 1e-6) ok++;
  console.log(String(i+1).padStart(4)+' | '+z.toFixed(12).padStart(21)+' | '+k.toFixed(12).padStart(21)+' | '+absZ.toExponential(3).padStart(12)+' | '+diff.toExponential(3));
}
console.log(`\nFound ${found.length} zeros with 0 < Im(ρ) <= 80.`);
console.log(`Matched ${ok}/${Math.min(found.length,known.length)} to known ordinates (|Δt|<5e-4, |Z|<1e-6).`);
console.log('Each is on Re(s)=1/2 (detected as a real zero of Z(t)).');
console.log('NOTE: Numerical verification up to finite height supports RH but does not prove it.');
