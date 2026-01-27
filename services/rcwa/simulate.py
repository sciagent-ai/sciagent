"""
S4 RCWA Simulation Core
Provides RCWA simulations for layered periodic structures.
"""

import sys
print(f"simulate.py loading, Python: {sys.executable}", flush=True)

import numpy as np
from typing import Dict, Any, List, Optional

try:
    print("simulate.py: Attempting S4 import...", flush=True)
    import S4
    S4_AVAILABLE = True
    print(f"simulate.py: S4 import SUCCESS, S4_AVAILABLE={S4_AVAILABLE}", flush=True)
except ImportError as e:
    S4_AVAILABLE = False
    print(f"simulate.py: S4 import FAILED: {e}", flush=True)
except Exception as e:
    S4_AVAILABLE = False
    print(f"simulate.py: S4 import EXCEPTION {type(e).__name__}: {e}", flush=True)


def run_rcwa_simulation(
    period: float,
    wavelength: float,
    angle_of_incidence: float,
    polarization: str = "s",
    layers: List[Dict[str, Any]] = None,
    grating_params: Dict[str, Any] = None,
    num_harmonics: int = 21,
    output_orders: List[int] = None
) -> Dict[str, Any]:
    """
    Run an RCWA simulation for a 1D grating structure.

    Parameters:
    -----------
    period : float
        Grating period in nm
    wavelength : float
        Incident wavelength in nm
    angle_of_incidence : float
        Angle of incidence in degrees (from normal)
    polarization : str
        's' (TE) or 'p' (TM) polarization
    layers : list of dict
        Layer stack definition. Each layer has:
        - material: str (e.g., 'silicon', 'air', 'sio2')
        - thickness: float (in nm, None for semi-infinite)
        - pattern: dict (optional, for patterned layers)
            - type: 'grating'
            - fill_factor: float (0-1)
            - material2: str (material in etched regions)
    grating_params : dict (optional)
        Shortcut for simple grating:
        - fill_factor: float
        - depth: float (grating depth in nm)
        - substrate: str (substrate material)
    num_harmonics : int
        Number of Fourier harmonics (odd number, e.g., 21 means -10 to +10)
    output_orders : list of int
        Which diffraction orders to return (default: [-2, -1, 0, 1, 2])

    Returns:
    --------
    dict with:
        - reflection: dict of {order: efficiency} for reflected orders
        - transmission: dict of {order: efficiency} for transmitted orders
        - total_reflection: float
        - total_transmission: float
        - absorption: float
        - parameters: dict of input parameters
    """

    if output_orders is None:
        output_orders = [-2, -1, 0, 1, 2]

    # Material refractive indices (can be extended)
    materials = {
        'air': 1.0,
        'vacuum': 1.0,
        'silicon': 3.88 + 0.02j,  # at 633nm
        'si': 3.88 + 0.02j,
        'sio2': 1.46,
        'glass': 1.5,
        'gold': 0.18 + 3.0j,  # at 633nm
        'silver': 0.13 + 4.0j,  # at 633nm
        'tio2': 2.5,
    }

    # Allow wavelength-dependent silicon
    if wavelength:
        # Simplified dispersion for silicon
        if 400 <= wavelength <= 800:
            # Approximate silicon n,k at visible wavelengths
            n_si = 3.5 + 0.5 * (633 / wavelength)
            k_si = 0.01 + 0.05 * (633 / wavelength) ** 2 if wavelength < 600 else 0.02
            materials['silicon'] = complex(n_si, k_si)
            materials['si'] = materials['silicon']

    def get_eps(material_name: str) -> complex:
        """Get permittivity from material name."""
        n = materials.get(material_name.lower(), 1.0)
        if isinstance(n, complex):
            return n ** 2
        return n ** 2 + 0j

    if not S4_AVAILABLE:
        # Mock mode for testing without S4
        return _mock_simulation(
            period, wavelength, angle_of_incidence, polarization,
            layers, grating_params, output_orders
        )

    # Build the simulation
    # S4 uses period in its own units, we'll normalize to wavelength
    S = S4.New(Lattice=period, NumBasis=num_harmonics)

    # Set the incident wave
    # S4 uses (kx, ky) in units of 2*pi/period
    # For 1D grating with incidence in x-z plane:
    theta_rad = np.radians(angle_of_incidence)
    kx = np.sin(theta_rad) * period / wavelength

    S.SetExcitationPlanewave(
        IncidenceAngles=(angle_of_incidence, 0),  # (theta, phi)
        sAmplitude=1.0 if polarization.lower() == 's' else 0.0,
        pAmplitude=0.0 if polarization.lower() == 's' else 1.0,
    )

    S.SetFrequency(1.0 / wavelength)  # frequency = 1/wavelength in S4

    # Build layer structure
    if grating_params:
        # Simple grating shortcut
        fill_factor = grating_params.get('fill_factor', 0.5)
        depth = grating_params.get('depth', 200)
        substrate = grating_params.get('substrate', 'silicon')

        # Superstrate (incident medium)
        S.AddMaterial('Air', get_eps('air'))
        S.AddMaterial('Si', get_eps('silicon'))
        S.AddMaterial('Substrate', get_eps(substrate))

        # Layers
        S.AddLayer('Incident', 0, 'Air')
        S.AddLayer('Grating', depth, 'Air')
        S.SetRegionRectangle('Grating', 'Si', (0, 0), 0, (fill_factor * period / 2, 0.5))
        S.AddLayer('Substrate', 0, 'Substrate')

    elif layers:
        # Full layer specification
        mat_idx = 0
        for mat_name in set(l.get('material', 'air') for l in layers):
            S.AddMaterial(f'Mat{mat_idx}', get_eps(mat_name))
            mat_idx += 1

        for i, layer in enumerate(layers):
            thickness = layer.get('thickness', 0)
            material = layer.get('material', 'air')
            pattern = layer.get('pattern')

            S.AddLayer(f'Layer{i}', thickness, material)

            if pattern and pattern.get('type') == 'grating':
                ff = pattern.get('fill_factor', 0.5)
                mat2 = pattern.get('material2', 'air')
                S.SetRegionRectangle(
                    f'Layer{i}', mat2,
                    (0, 0), 0, (ff * period / 2, 0.5)
                )
    else:
        # Default: simple silicon grating on silicon substrate
        S.AddMaterial('Air', get_eps('air'))
        S.AddMaterial('Si', get_eps('silicon'))

        S.AddLayer('Incident', 0, 'Air')
        S.AddLayer('Grating', 200, 'Air')
        S.SetRegionRectangle('Grating', 'Si', (0, 0), 0, (period * 0.25, 0.5))
        S.AddLayer('Substrate', 0, 'Si')

    # Get diffraction efficiencies
    reflection = {}
    transmission = {}

    for order in output_orders:
        # GetPowerFlux returns (forward, backward) power
        # For reflection, we look at backward power in incident layer
        # For transmission, we look at forward power in substrate

        try:
            # S4 GetDiffractionOrder returns complex amplitudes
            r_amp = S.GetDiffractionOrder((order, 0), 'Incident')
            t_amp = S.GetDiffractionOrder((order, 0), 'Substrate')

            # Convert to efficiency (|amplitude|^2 * cos correction)
            reflection[order] = float(abs(r_amp[0])**2 + abs(r_amp[1])**2)
            transmission[order] = float(abs(t_amp[0])**2 + abs(t_amp[1])**2)
        except:
            reflection[order] = 0.0
            transmission[order] = 0.0

    # Get total power
    _, back = S.GetPowerFlux('Incident')
    forw, _ = S.GetPowerFlux('Substrate')

    total_r = float(abs(back))
    total_t = float(abs(forw))

    return {
        'reflection': reflection,
        'transmission': transmission,
        'total_reflection': total_r,
        'total_transmission': total_t,
        'absorption': 1.0 - total_r - total_t,
        'parameters': {
            'period': period,
            'wavelength': wavelength,
            'angle_of_incidence': angle_of_incidence,
            'polarization': polarization,
            'num_harmonics': num_harmonics,
        }
    }


def _mock_simulation(
    period: float,
    wavelength: float,
    angle_of_incidence: float,
    polarization: str,
    layers: Optional[List[Dict]],
    grating_params: Optional[Dict],
    output_orders: List[int]
) -> Dict[str, Any]:
    """
    Mock simulation for testing without S4.
    Returns physically plausible but not accurate results.
    """
    # Simple physics-based mock
    theta = np.radians(angle_of_incidence)

    # Grating equation: sin(theta_m) = sin(theta_i) + m * lambda / period
    def diffraction_angle(m):
        sin_theta_m = np.sin(theta) + m * wavelength / period
        if abs(sin_theta_m) <= 1:
            return np.degrees(np.arcsin(sin_theta_m))
        return None  # Evanescent

    # Mock efficiencies based on simple model
    fill_factor = 0.5
    depth = 200
    if grating_params:
        fill_factor = grating_params.get('fill_factor', 0.5)
        depth = grating_params.get('depth', 200)

    # Phase depth
    n_eff = 3.88  # silicon
    phase = 2 * np.pi * depth * n_eff / wavelength

    reflection = {}
    transmission = {}

    for order in output_orders:
        angle_m = diffraction_angle(order)
        if angle_m is None:
            reflection[order] = 0.0
            transmission[order] = 0.0
        else:
            # Sinc-squared envelope for grating
            if order == 0:
                base_eff = 0.2
            else:
                # First-order efficiency depends on fill factor and depth
                arg = np.pi * order * fill_factor
                sinc_sq = (np.sin(arg) / arg) ** 2 if arg != 0 else 1.0
                base_eff = 0.3 * sinc_sq * (1 - np.cos(phase)) / 2

            # Split between reflection and transmission
            reflection[order] = base_eff * 0.4
            transmission[order] = base_eff * 0.4

    total_r = sum(reflection.values())
    total_t = sum(transmission.values())

    return {
        'reflection': reflection,
        'transmission': transmission,
        'total_reflection': total_r,
        'total_transmission': total_t,
        'absorption': max(0, 1.0 - total_r - total_t),
        'parameters': {
            'period': period,
            'wavelength': wavelength,
            'angle_of_incidence': angle_of_incidence,
            'polarization': polarization,
        },
        'mock': True,
        'note': 'S4 not available - using physics-based mock'
    }


def optimize_grating(
    target_order: int,
    target_type: str,  # 'reflection' or 'transmission'
    wavelength: float,
    angle_of_incidence: float,
    polarization: str = 's',
    period_range: tuple = (300, 800),
    fill_factor_range: tuple = (0.2, 0.8),
    depth_range: tuple = (50, 500),
    num_samples: int = 20
) -> Dict[str, Any]:
    """
    Grid search optimization for grating parameters.

    Returns best parameters and efficiency for maximizing
    diffraction into a specific order.
    """
    best_efficiency = 0.0
    best_params = {}
    all_results = []

    periods = np.linspace(period_range[0], period_range[1], num_samples)
    fill_factors = np.linspace(fill_factor_range[0], fill_factor_range[1], num_samples)
    depths = np.linspace(depth_range[0], depth_range[1], num_samples)

    for period in periods:
        for ff in fill_factors:
            for depth in depths:
                result = run_rcwa_simulation(
                    period=period,
                    wavelength=wavelength,
                    angle_of_incidence=angle_of_incidence,
                    polarization=polarization,
                    grating_params={
                        'fill_factor': ff,
                        'depth': depth,
                        'substrate': 'silicon'
                    },
                    output_orders=[target_order]
                )

                if target_type == 'reflection':
                    eff = result['reflection'].get(target_order, 0)
                else:
                    eff = result['transmission'].get(target_order, 0)

                all_results.append({
                    'period': period,
                    'fill_factor': ff,
                    'depth': depth,
                    'efficiency': eff
                })

                if eff > best_efficiency:
                    best_efficiency = eff
                    best_params = {
                        'period': period,
                        'fill_factor': ff,
                        'depth': depth
                    }

    return {
        'best_params': best_params,
        'best_efficiency': best_efficiency,
        'target_order': target_order,
        'target_type': target_type,
        'wavelength': wavelength,
        'angle_of_incidence': angle_of_incidence,
        'polarization': polarization,
        'num_evaluated': len(all_results)
    }
