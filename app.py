import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import modesolverpy.mode_solver as ms
import modesolverpy.structure as st

st.title("Photonic Modes Display")

# User inputs
wavelength = st.slider("Wavelength (nm)", 1000, 2000, 1550)
width = st.slider("Waveguide width (nm)", 200, 1000, 500)
height = st.slider("Waveguide height (nm)", 100, 500, 220)

if st.button("Compute Mode"):
    # Define structure
    x_step = 0.02
    y_step = 0.02
    wg_width = width / 1e3  # convert to um
    wg_height = height / 1e3
    sub_height = 0.5
    sub_width = 2.0
    clad_height = 0.5
    n_sub = 1.44
    n_wg = 3.47
    n_clad = 1.0
    wavelength_um = wavelength / 1e3
    angle = 0.0
    film_thickness = 0.0

    # Create structure
    struct = st.RidgeWaveguide(wavelength_um, x_step, y_step, wg_width, wg_height, sub_height, sub_width, clad_height, n_sub, n_wg, n_clad, angle, film_thickness)

    # Solve for modes
    solver = ms.ModeSolverFullyVectorial(4)
    solver.solve(struct)

    # Get mode
    mode = solver.modes[0]

    # Plot
    fig, ax = plt.subplots()
    mode.plot(ax=ax)
    st.pyplot(fig)