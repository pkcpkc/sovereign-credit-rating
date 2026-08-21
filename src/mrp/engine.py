"""
Minimal Rating Process (MRP) Engine — v1.0 Specification
Implementation of Alex Stomper (2026): "The Minimal Rating Process: Sovereign Credit Ratings from Risk-Off Positioning"

Architecture:
- Six Calibration Tasks (Annual): C1 (mu_r, sigma), C2 (e_MRP, mu), C3 (s_bar, s_t), C4 (R^f), C5 (h), C6 (theta_inf, sigma_theta)
- Seven Rating Tasks (Monthly): R1 (n_t), R2 (theta_hat), R3 (Capacity objects), R4 (Band edges & regime), R5 (Exits), R6 (Rating class), R7 (Outlook & publication)

Analytical Stationary Solver:
Stationary points of the funding curve xi_theta(d):
  xi'(d) = 0 <=> 1 - h*Phi(z) - (h/sigma)*phi(z) = 0
where z = (ln d - ln(s_bar + bM(theta)) - (mu - theta*sigma)) / sigma.
The roots z_U < z_L depend solely on (h, sigma), enabling closed-form instant evaluations of band edges and critical risk prices.
"""

import math
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

# ----------------------------------------------------------------------
# Core Analytical Solvers
# ----------------------------------------------------------------------

def solve_zM(sigma: float) -> float:
    """
    Task R3 solver: Solve sigma * (1 - Phi(zM)) = phi(zM) for the unique negative root zM.
    At sigma = 0.03, zM = -2.28.
    """
    func = lambda z: sigma * (1.0 - norm.cdf(z)) - norm.pdf(z)
    return brentq(func, -12.0, 0.0)

def solve_stationary_z(h: float, sigma: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Task R4 solver: Solve 1 - h*Phi(z) - (h/sigma)*phi(z) = 0 for the two roots z_U < z_L.
    The dip condition (Eq. 6) holds when h * (Phi(z) + (1/sigma)*phi(z)) > 1 for some z.
    """
    func = lambda z: 1.0 - h * norm.cdf(z) - (h / sigma) * norm.pdf(z)
    
    grid = np.linspace(-6.0, 6.0, 300)
    vals = [func(z) for z in grid]
    
    roots = []
    for i in range(len(vals) - 1):
        if vals[i] * vals[i+1] <= 0:
            try:
                r = brentq(func, grid[i], grid[i+1])
                roots.append(r)
            except Exception:
                pass
    if len(roots) >= 2:
        return min(roots[0], roots[1]), max(roots[0], roots[1])
    return None, None

# ----------------------------------------------------------------------
# Calibration Task Functions (C1 - C6)
# ----------------------------------------------------------------------

def calibrate_inflation_differential(
    mu_r: float,
    pi_u: float,
    e_hat: float = 0.0
) -> Tuple[float, float, float]:
    """
    Task C2 (Inflation: the differential e):
    e_MRP = min{0, e_hat}
    mu = mu_r + pi_u + e_MRP
    Returns (e_hat, e_MRP, mu)
    """
    e_mrp = min(0.0, e_hat)
    mu_hat = mu_r + pi_u + e_mrp
    return e_hat, e_mrp, mu_hat

def compute_inflation_capacity_derivative(
    gamma: float,
    s_bar: float,
    Rf: float
) -> float:
    """
    Task C2 sensitivity derivative:
    dbM / de = (gamma * s_bar * Rf) / (Rf - gamma)^2
    Measures pp of GDP of capacity lost per 100bp of negative inflation differential.
    """
    if Rf <= gamma:
        return float('inf')
    return (gamma * s_bar * Rf) / ((Rf - gamma) ** 2)

# ----------------------------------------------------------------------
# Rating Tasks Functions (R1 - R7)
# ----------------------------------------------------------------------

def compute_refinancing_need(
    debt_stock_pct: float,
    short_term_debt_pct: float,
    wam_years: float,
    deficit_pct: float
) -> float:
    """
    Task R1 (Measure refinancing need n_t):
    n_t approx ((d_stock - b_ST) / WAM) + b_ST + def
    All numbers in decimal shares of GDP.
    """
    d_stock = debt_stock_pct / 100.0 if debt_stock_pct > 1.0 else debt_stock_pct
    b_st = short_term_debt_pct / 100.0 if short_term_debt_pct > 1.0 else short_term_debt_pct
    wam = max(wam_years, 0.1)
    d_def = deficit_pct / 100.0 if abs(deficit_pct) > 1.0 else deficit_pct
    
    return ((d_stock - b_st) / wam) + b_st + d_def

def estimate_distress_risk_price(
    vix_monthly: float,
    mV: float = 2.70,
    sV: float = 0.40,
    theta_inf: float = 0.30,
    sigma_theta: float = 0.25
) -> Tuple[float, float]:
    """
    Task R2 (Estimate market price of distress risk theta_hat):
    z_t = (ln V_t - m_V) / s_V
    theta_hat = max{0, theta_inf + sigma_theta * z_t}
    Returns (z_t, theta_hat)
    """
    ln_vix = math.log(max(vix_monthly, 1.0))
    z_t = (ln_vix - mV) / sV
    theta_hat = max(0.0, theta_inf + sigma_theta * z_t)
    return z_t, theta_hat

def compute_capacity_objects(
    mu: float,
    sigma: float,
    s_bar: float,
    Rf: float,
    theta: float,
    zM: Optional[float] = None
) -> Tuple[float, float, float, float]:
    """
    Task R3 (Capacity objects):
    gamma(theta) = (1 - Phi(zM)) * exp(mu - theta*sigma + sigma*zM)
    bM(theta) = (s_bar * gamma(theta)) / (Rf - gamma(theta))
    dM(theta) = (s_bar + bM(theta)) * exp(mu - theta*sigma + sigma*zM)
    Returns (zM, gamma, bM, dM)
    """
    if zM is None:
        zM = solve_zM(sigma)
    
    drift = mu - theta * sigma + sigma * zM
    gamma = (1.0 - norm.cdf(zM)) * math.exp(drift)
    
    if Rf <= gamma:
        bM = 1e6
    else:
        bM = (s_bar * gamma) / (Rf - gamma)
    
    dM = (s_bar + bM) * math.exp(drift)
    return zM, gamma, bM, dM

def default_prob_P(
    d: float,
    mu: float,
    sigma: float,
    s_bar: float,
    Rf: float,
    theta: float,
    zM: Optional[float] = None
) -> float:
    """
    Default probability function P_theta(d) from Eq. (10).
    """
    if d <= 0:
        return 0.0
    if zM is None:
        zM = solve_zM(sigma)
    _, _, bM, _ = compute_capacity_objects(mu, sigma, s_bar, Rf, theta, zM)
    drift = mu - theta * sigma
    arg = (math.log(d) - math.log(s_bar + bM) - drift) / sigma
    return float(norm.cdf(arg))

def compute_band_edges(
    mu: float,
    sigma: float,
    s_bar: float,
    Rf: float,
    h: float,
    theta: float,
    zM: Optional[float] = None
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Task R4 (Band edges and regime):
    Computes dU < dL and nU = xi(dU), nL = xi(dL) from Eq. (7).
    Returns (dU, dL, nL, nU).
    """
    if zM is None:
        zM = solve_zM(sigma)
    
    zU, zL = solve_stationary_z(h, sigma)
    if zU is None or zL is None:
        return None, None, None, None
        
    _, _, bM, _ = compute_capacity_objects(mu, sigma, s_bar, Rf, theta, zM)
    
    drift = mu - theta * sigma
    dU = (s_bar + bM) * math.exp(drift + sigma * zU)
    dL = (s_bar + bM) * math.exp(drift + sigma * zL)
    
    nU = (dU * (1.0 - h * norm.cdf(zU))) / Rf
    nL = (dL * (1.0 - h * norm.cdf(zL))) / Rf
    
    return dU, dL, nL, nU

def solve_critical_risk_prices(
    nt: float,
    mu: float,
    sigma: float,
    s_bar: float,
    Rf: float,
    h: float,
    zM: Optional[float] = None
) -> Tuple[Optional[float], Optional[float]]:
    """
    Task R5 (Critical risk prices):
    Solves for theta_G(nt) and theta_B(nt) from Eq. (11):
    theta_G(nt): nU(theta_G) = nt
    theta_B(nt): nL(theta_B) = nt
    """
    if zM is None:
        zM = solve_zM(sigma)
        
    zU, zL = solve_stationary_z(h, sigma)
    if zU is None or zL is None:
        return None, None

    def nU_diff(th):
        _, _, bM, _ = compute_capacity_objects(mu, sigma, s_bar, Rf, th, zM)
        drift = mu - th * sigma
        dU = (s_bar + bM) * math.exp(drift + sigma * zU)
        nU = (dU * (1.0 - h * norm.cdf(zU))) / Rf
        return nU - nt

    def nL_diff(th):
        _, _, bM, _ = compute_capacity_objects(mu, sigma, s_bar, Rf, th, zM)
        drift = mu - th * sigma
        dL = (s_bar + bM) * math.exp(drift + sigma * zL)
        nL = (dL * (1.0 - h * norm.cdf(zL))) / Rf
        return nL - nt

    theta_G = None
    try:
        theta_G = brentq(nU_diff, -5.0, 15.0)
    except Exception:
        pass

    theta_B = None
    try:
        theta_B = brentq(nL_diff, -5.0, 15.0)
    except Exception:
        pass

    return theta_G, theta_B

def classify_rating(
    regime: str,
    exposure: float,
    x_fisc: float,
    p_theta_B: Optional[float] = None,
    d3_flag: bool = False,
    branch: str = 'good'
) -> Tuple[str, str]:
    """
    Task R6 (Rating class):
    Native thresholds with probability semantics (No notches):
    - safe:
        S1: Exposure <= 0.01%
        S2: Exposure <= 0.1%
        S3: Exposure <= 1%
    - fragile (G):
        F1: Exposure <= 5% and X_fisc <= 2y
        F2: Exposure <= 15%
        F3: Exposure <= 30%
        F4: Exposure > 30%
    - distressed / bad branch (B):
        D1: P[theta < theta_B] >= 25%
        D2: P[theta < theta_B] < 25%
        D3: nt > nU(theta) on 90% range
    Returns (native_class, letter_grade_benchmark)
    """
    if regime == 'safe':
        if exposure <= 0.0001:
            return 'S1', 'AAA/AA+'
        elif exposure <= 0.001:
            return 'S2', 'AA/A+'
        else:
            return 'S3', 'A/BBB+'
            
    elif regime == 'fragile':
        if branch == 'bad':
            # Fragile country pricing on bad branch defaults into distressed grading
            if p_theta_B is not None and p_theta_B >= 0.25:
                return 'D1', 'CCC'
            else:
                return 'D2', 'CC/C'
        else:
            if exposure <= 0.05 and x_fisc <= 2.0:
                return 'F1', 'BBB'
            elif exposure <= 0.15:
                return 'F2', 'BB'
            elif exposure <= 0.30:
                return 'F3', 'B'
            else:
                return 'F4', 'CCC+'
                
    else: # distressed
        if d3_flag:
            return 'D3', 'imminent SD'
        if p_theta_B is not None and p_theta_B >= 0.25:
            return 'D1', 'CCC'
        else:
            return 'D2', 'CC/C'

def compute_sensitivity_grid(
    mu: float,
    sigma: float,
    s_bar_values: List[float] = [0.015, 0.020, 0.025],
    h_values: List[float] = [0.20, 0.30, 0.50],
    theta_values: List[float] = [0.0, 0.30, 0.60],
    nt_values: List[float] = [0.12, 0.14, 0.16],
    Rf: float = 1.02,
    theta_inf: float = 0.30,
    sigma_theta: float = 0.25
) -> Dict[str, Any]:
    """
    Task R7: Evaluate sensitivity grid over s_bar x h x theta_hat x nt (81 corners).
    """
    zM = solve_zM(sigma)
    counts = {'safe': 0, 'fragile': 0, 'distressed': 0}
    max_exposure = 0.0
    worst_corner = None
    corners = []

    for s_b in s_bar_values:
        for h_val in h_values:
            for th in theta_values:
                _, _, nL, nU = compute_band_edges(mu, sigma, s_b, Rf, h_val, th, zM)
                for n_val in nt_values:
                    corner_regime = 'unknown'
                    corner_exp = 0.0
                    th_G = None
                    if nL is not None and nU is not None:
                        if n_val < nL:
                            corner_regime = 'safe'
                        elif nL <= n_val <= nU:
                            corner_regime = 'fragile'
                        else:
                            corner_regime = 'distressed'
                    
                    th_G, _ = solve_critical_risk_prices(n_val, mu, sigma, s_b, Rf, h_val, zM)
                    if th_G is not None:
                        corner_exp = float(1.0 - norm.cdf((th_G - theta_inf) / sigma_theta))
                    
                    if corner_regime in counts:
                        counts[corner_regime] += 1
                    
                    if corner_exp > max_exposure:
                        max_exposure = corner_exp
                        worst_corner = {
                            's_bar': s_b,
                            'h': h_val,
                            'theta': th,
                            'nt': n_val,
                            'theta_G': th_G,
                            'exposure': corner_exp,
                            'regime': corner_regime
                        }

                    corners.append({
                        's_bar': s_b,
                        'h': h_val,
                        'theta': th,
                        'nt': n_val,
                        'nL': nL,
                        'nU': nU,
                        'theta_G': th_G,
                        'exposure': corner_exp,
                        'regime': corner_regime
                    })

    return {
        'total_corners': len(corners),
        'counts': counts,
        'worst_corner': worst_corner,
        'worst_exposure_pct': max_exposure * 100.0,
        'corners': corners
    }

# ----------------------------------------------------------------------
# Complete MRP Pipeline Execution
# ----------------------------------------------------------------------

def run_mrp_pipeline(
    country_data: Dict[str, Any],
    global_data: Dict[str, Any],
    da2_state: str = 'watch',
    da1_qualitative_outlook: Optional[str] = None,
    da1_rationale: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute full MRP Specification v1.0 pipeline.
    """
    # Calibration Inputs (C1 - C6)
    mu_r = country_data.get('mu_r', 0.014) # Real growth drift
    pi_u = country_data.get('pi_u', 0.020) # Union inflation anchor
    e_hat = country_data.get('inflation_diff_projected', 0.0) # Task C2 projected differential
    
    # Task C2: Inflation differential and drift
    e_hat, e_mrp, mu = calibrate_inflation_differential(mu_r, pi_u, e_hat)
    if 'mu_hat' in country_data:
        mu = country_data['mu_hat'] # Allow override if calibrated directly

    sigma = country_data['sigma_hat'] # Task C1 volatility
    s_bar = country_data['s_bar'] # Task C3 capacity
    s_t = country_data['planned_primary_balance_pct'] / 100.0 # Task C3 plan
    Rf = country_data['rf_gross'] # Task C4 safe rate
    h = country_data['haircut_baseline'] # Task C5 haircut

    theta_inf = global_data.get('theta_inf', 0.30) # Task C6
    sigma_theta = global_data.get('sigma_theta', 0.25) # Task C6
    mV = global_data.get('mV', 2.70)
    sV = global_data.get('sV', 0.40)

    # Rating Inputs (R1 - R2)
    # Task R1: Refinancing need
    nt = country_data['gfn_gdp_pct'] / 100.0
    spread_obs_bps = country_data.get('spread_10y_bps', 50.0)
    
    # Task R2: Estimate theta_hat
    theta_hat = global_data.get('theta_hat', 0.30)
    zt = global_data.get('z_vix', 0.0)

    # Task R3: Capacity objects
    zM, gamma, bM, dM = compute_capacity_objects(mu, sigma, s_bar, Rf, theta_hat)
    d_derivative_e = compute_inflation_capacity_derivative(gamma, s_bar, Rf)
    
    # Refinancing & Face value due
    face_val_due = nt + s_t
    dt_issued = nt * Rf
    p_dt = default_prob_P(dt_issued, mu, sigma, s_bar, Rf, theta_hat, zM)
    psi_model_bps = h * p_dt * 10000.0

    # Task R4: Band edges and regime
    dU, dL, nL, nU = compute_band_edges(mu, sigma, s_bar, Rf, h, theta_hat, zM)
    
    if nL is not None and nt < nL:
        regime = 'safe'
        branch = 'safe'
    elif nL is not None and nU is not None and nL <= nt <= nU:
        regime = 'fragile'
        branch = 'bad' if spread_obs_bps > 500.0 else 'good'
    else:
        regime = 'distressed'
        branch = 'bad'

    # Task R5: Exits
    theta_G, theta_B = solve_critical_risk_prices(nt, mu, sigma, s_bar, Rf, h, zM)
    delta_G = (theta_G - theta_hat) if theta_G is not None else None
    delta_B = (theta_hat - theta_B) if theta_B is not None else None

    # Task R5: Tail Exposure
    if theta_G is not None:
        if da2_state == 'eligible':
            exposure = 0.0 # Truncated factor distribution deletes bad equilibrium
        else:
            exposure = float(1.0 - norm.cdf((theta_G - theta_inf) / sigma_theta))
    else:
        exposure = 1.0

    # Task R5: Fiscal exit time X_fisc
    _, _, nL_inf, _ = compute_band_edges(mu, sigma, s_bar, Rf, h, theta_inf, zM)
    if nL_inf is not None and (s_bar - s_t) > 0:
        x_fisc = max(nt - nL_inf, 0.0) / (s_bar - s_t)
    else:
        x_fisc = 0.0

    p_theta_B = float(norm.cdf((theta_B - theta_inf) / sigma_theta)) if theta_B is not None else None

    # D3 check on 90% range of factor distribution: theta_90 = theta_inf - 1.645*sigma_theta
    theta_90_low = theta_inf - 1.645 * sigma_theta
    _, _, _, nU_90 = compute_band_edges(mu, sigma, s_bar, Rf, h, theta_90_low, zM)
    d3_flag = bool(nU_90 is not None and nt > nU_90)

    # Task R6: Rating class
    rating_class, letter_grade = classify_rating(
        regime=regime,
        exposure=exposure,
        x_fisc=x_fisc,
        p_theta_B=p_theta_B,
        d3_flag=d3_flag,
        branch=branch
    )

    # Task R7: Sensitivity Grid (81 corners)
    grid_res = compute_sensitivity_grid(mu, sigma, Rf=Rf, theta_inf=theta_inf, sigma_theta=sigma_theta)

    # Task R7: Outlook (DA1)
    model_trajectory = 'negative' if (country_data.get('headline_deficit_gdp_pct', 0) > 3.0 or s_t < 0) else 'stable'
    final_outlook = da1_qualitative_outlook if da1_qualitative_outlook is not None else model_trajectory

    return {
        'spec_version': 'mrp-v1.0.0',
        'calibration_tasks': {
            'C1': {'mu_r': mu_r, 'sigma_hat': sigma},
            'C2': {'pi_u': pi_u, 'e_hat': e_hat, 'e_MRP': e_mrp, 'mu_hat': mu, 'dbM_de': d_derivative_e},
            'C3': {'s_bar': s_bar, 's_t': s_t},
            'C4': {'Rf': Rf},
            'C5': {'h': h},
            'C6': {'theta_inf': theta_inf, 'sigma_theta': sigma_theta, 'mV': mV, 'sV': sV}
        },
        'rating_tasks': {
            'R1': {'nt': nt, 'gross_debt_pct': country_data.get('gross_debt_gdp_pct', 81.0), 'wam_years': country_data.get('wam_years', 11.45)},
            'R2': {'zt_vix': zt, 'theta_hat': theta_hat},
            'R3': {'zM': zM, 'gamma': gamma, 'bM': bM, 'dM': dM, 'p_dt': p_dt, 'psi_model_bps': psi_model_bps},
            'R4': {'dU': dU, 'dL': dL, 'nL': nL, 'nU': nU, 'regime': regime, 'branch': branch, 'spread_obs_bps': spread_obs_bps},
            'R5': {'theta_G': theta_G, 'theta_B': theta_B, 'delta_G': delta_G, 'delta_B': delta_B, 'exposure': exposure, 'x_fisc': x_fisc, 'p_theta_B': p_theta_B},
            'R6': {'class': rating_class, 'letter_grade': letter_grade, 'da2_eligibility_state': da2_state},
            'R7': {'outlook': final_outlook, 'outlook_rationale': da1_rationale or 'Model-based projected n-path expansion + EDP watch status.'}
        },
        'inputs': {
            'country_id': country_data.get('country_id', 'AUT'),
            'country_name': country_data.get('name', 'Austria'),
            'mu_hat': mu,
            'sigma_hat': sigma,
            's_bar': s_bar,
            's_t': s_t,
            'rf_gross': Rf,
            'haircut': h,
            'nt': nt,
            'gross_debt_pct': country_data.get('gross_debt_gdp_pct', 81.0),
            'short_term_debt_pct': country_data.get('short_term_debt_gdp_pct', 2.0),
            'wam_years': country_data.get('wam_years', 11.45),
            'headline_deficit_pct': country_data.get('headline_deficit_gdp_pct', 4.3),
            'observed_spread_10y_bps': spread_obs_bps,
            'zt_vix': zt,
            'theta_hat': theta_hat,
            'theta_inf': theta_inf,
            'sigma_theta': sigma_theta
        },
        'derived_objects': {
            'zM': zM,
            'gamma': gamma,
            'bM': bM,
            'dM': dM,
            'face_val_due': face_val_due,
            'p_dt': p_dt,
            'model_spread_bps': psi_model_bps,
            'dU': dU,
            'dL': dL,
            'nL': nL,
            'nU': nU,
            'theta_G': theta_G,
            'theta_B': theta_B,
            'delta_G': delta_G,
            'delta_B': delta_B,
            'exposure': exposure,
            'x_fisc': x_fisc
        },
        'rating': {
            'regime': regime,
            'class': rating_class,
            'letter_grade': letter_grade,
            'da2_eligibility_state': da2_state,
            'da1_outlook': final_outlook,
            'outlook_rationale': da1_rationale or 'Model-based projected n-path expansion + EDP watch status.'
        },
        'sensitivity_grid': grid_res
    }
