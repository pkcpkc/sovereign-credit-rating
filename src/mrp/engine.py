"""
Minimal Rating Process (MRP) Engine
Implementation of Stomper (2026): "Positioning for Risk-Off: A Methodology for Sovereign Credit Ratings"

Analytic Form:
Stationary points of funding curve xi_theta(d):
  xi'(d) = 0 <=> 1 - h*Phi(z) - (h/sigma)*phi(z) = 0
where z = (ln d - ln(s_bar + bM(theta)) - (mu - theta*sigma)) / sigma.
The roots z_U < z_L depend only on (h, sigma), making band edges and critical theta solves instant.
"""

import math
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

def solve_zM(sigma: float) -> float:
    """
    Solve sigma * (1 - Phi(zM)) = phi(zM) for the unique negative root zM.
    """
    func = lambda z: sigma * (1.0 - norm.cdf(z)) - norm.pdf(z)
    return brentq(func, -12.0, 0.0)

def solve_stationary_z(h: float, sigma: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Solve 1 - h*Phi(z) - (h/sigma)*phi(z) = 0 for the two roots z_U < z_L.
    Dip condition: h * (Phi(z) + (1/sigma)*phi(z)) > 1 for some z.
    """
    func = lambda z: 1.0 - h * norm.cdf(z) - (h / sigma) * norm.pdf(z)
    
    # Evaluate over a range where z goes from -6 to 6
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

def compute_capacity_objects(mu: float, sigma: float, s_bar: float, Rf: float, theta: float, zM: Optional[float] = None) -> Tuple[float, float, float, float]:
    """
    Compute gamma(theta), bM(theta), dM(theta) from equation (13).
    Returns (zM, gamma, bM, dM)
    """
    if zM is None:
        zM = solve_zM(sigma)
    
    # gamma(theta) = (1 - Phi(zM)) * exp(mu - theta*sigma + sigma*zM)
    drift = mu - theta * sigma + sigma * zM
    gamma = (1.0 - norm.cdf(zM)) * math.exp(drift)
    
    # bM(theta) = (s_bar * gamma) / (Rf - gamma)
    if Rf <= gamma:
        bM = 1e6
    else:
        bM = (s_bar * gamma) / (Rf - gamma)
    
    # dM(theta) = (s_bar + bM) * exp(mu - theta*sigma + sigma*zM)
    dM = (s_bar + bM) * math.exp(drift)
    return zM, gamma, bM, dM

def default_prob_P(d: float, mu: float, sigma: float, s_bar: float, Rf: float, theta: float, zM: Optional[float] = None) -> float:
    """
    Default probability function P_theta(d) from equation (14).
    """
    if d <= 0:
        return 0.0
    if zM is None:
        zM = solve_zM(sigma)
    _, _, bM, _ = compute_capacity_objects(mu, sigma, s_bar, Rf, theta, zM)
    drift = mu - theta * sigma
    arg = (math.log(d) - math.log(s_bar + bM) - drift) / sigma
    return float(norm.cdf(arg))

def compute_band_edges(mu: float, sigma: float, s_bar: float, Rf: float, h: float, theta: float, zM: Optional[float] = None) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Compute stationary points dU < dL and band edges nU = xi(dU), nL = xi(dL) from equation (6).
    Returns (dU, dL, nL, nU).
    """
    if zM is None:
        zM = solve_zM(sigma)
    
    zU, zL = solve_stationary_z(h, sigma)
    if zU is None or zL is None:
        return None, None, None, None
        
    _, _, bM, _ = compute_capacity_objects(mu, sigma, s_bar, Rf, theta, zM)
    
    # d = (s_bar + bM) * exp(mu - theta*sigma + sigma*z)
    drift = mu - theta * sigma
    dU = (s_bar + bM) * math.exp(drift + sigma * zU)
    dL = (s_bar + bM) * math.exp(drift + sigma * zL)
    
    nU = (dU * (1.0 - h * norm.cdf(zU))) / Rf
    nL = (dL * (1.0 - h * norm.cdf(zL))) / Rf
    
    return dU, dL, nL, nU

def solve_critical_risk_prices(nt: float, mu: float, sigma: float, s_bar: float, Rf: float, h: float, zM: Optional[float] = None) -> Tuple[Optional[float], Optional[float]]:
    """
    Solve for critical risk prices theta_G(nt) and theta_B(nt) from equation (8):
    theta_G(nt): nU(theta_G) = nt
    theta_B(nt): nL(theta_B) = nt
    """
    if zM is None:
        zM = solve_zM(sigma)
        
    zU, zL = solve_stationary_z(h, sigma)
    if zU is None or zL is None:
        return None, None

    # nU(theta) is strictly decreasing in theta
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
    d3_flag: bool = False
) -> Tuple[str, str]:
    """
    Classify country into native rating class (S1-S3, F1-F4, D1-D3) and letter grade territory.
    """
    if regime == 'safe':
        if exposure <= 0.0001:
            return 'S1', 'AAA/AA+'
        elif exposure <= 0.001:
            return 'S2', 'AA/A+'
        elif exposure <= 0.01:
            return 'S3', 'A/BBB+'
        else:
            return 'S3', 'A/BBB+'
    elif regime == 'fragile':
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
    Evaluate the full 81-corner sensitivity grid over (s_bar, h, theta_hat, nt).
    Returns regime counts, grid breakdown, and worst-corner exposure.
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
                    
                    # Compute theta_G for exposure
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

def run_mrp_pipeline(
    country_data: Dict[str, Any],
    global_data: Dict[str, Any],
    da2_state: str = 'watch',
    da1_qualitative_outlook: Optional[str] = None,
    da1_rationale: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run complete Minimal Rating Process (MRP) pipeline for a country.
    """
    mu = country_data['mu_hat']
    sigma = country_data['sigma_hat']
    s_bar = country_data['s_bar']
    s_t = country_data['planned_primary_balance_pct'] / 100.0
    Rf = country_data['rf_gross']
    h = country_data['haircut_baseline']
    nt = country_data['gfn_gdp_pct'] / 100.0
    spread_obs_bps = country_data.get('spread_10y_bps', 50.0)
    
    theta_hat = global_data['theta_hat']
    theta_inf = global_data.get('theta_inf', 0.30)
    sigma_theta = global_data.get('sigma_theta', 0.25)
    zt = global_data.get('z_vix', 0.0)

    # 1. Capacity objects
    zM, gamma, bM, dM = compute_capacity_objects(mu, sigma, s_bar, Rf, theta_hat)
    
    # 2. Refinancing & Face value due
    face_val_due = nt + s_t
    
    # 3. Model spread
    dt_issued = nt * Rf
    p_dt = default_prob_P(dt_issued, mu, sigma, s_bar, Rf, theta_hat, zM)
    psi_model_bps = h * p_dt * 10000.0
    
    # 4. Band edges & Regime
    dU, dL, nL, nU = compute_band_edges(mu, sigma, s_bar, Rf, h, theta_hat, zM)
    
    if nL is not None and nt < nL:
        regime = 'safe'
    elif nL is not None and nU is not None and nL <= nt <= nU:
        regime = 'fragile'
    else:
        regime = 'distressed'

    # 5. Critical prices & Distances
    theta_G, theta_B = solve_critical_risk_prices(nt, mu, sigma, s_bar, Rf, h, zM)
    
    delta_G = (theta_G - theta_hat) if theta_G is not None else None
    delta_B = (theta_hat - theta_B) if theta_B is not None else None
    
    # 6. Tail Exposure probability
    if theta_G is not None:
        if da2_state == 'eligible':
            # Truncated factor distribution: bad equilibrium deleted for rating purposes
            exposure = 0.0
        else:
            exposure = float(1.0 - norm.cdf((theta_G - theta_inf) / sigma_theta))
    else:
        exposure = 1.0

    # 7. Fiscal exit time X_fisc
    # nL at theta_inf
    _, _, nL_inf, _ = compute_band_edges(mu, sigma, s_bar, Rf, h, theta_inf, zM)
    if nL_inf is not None and (s_bar - s_t) > 0:
        x_fisc = max(nt - nL_inf, 0.0) / (s_bar - s_t)
    else:
        x_fisc = 0.0

    # 8. Rating classification
    p_theta_B = float(norm.cdf((theta_B - theta_inf) / sigma_theta)) if theta_B is not None else None
    rating_class, letter_grade = classify_rating(regime, exposure, x_fisc, p_theta_B)

    # 9. Sensitivity Grid
    grid_res = compute_sensitivity_grid(mu, sigma, Rf=Rf, theta_inf=theta_inf, sigma_theta=sigma_theta)

    # 10. Outlook (DA1)
    model_trajectory = 'negative' if (country_data.get('headline_deficit_gdp_pct', 0) > 3.0 or s_t < 0) else 'stable'
    final_outlook = da1_qualitative_outlook if da1_qualitative_outlook is not None else model_trajectory

    return {
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
