import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Nuclear Shielding Lab", layout="wide")

# --- MATERIALS DATABASE (Data for 1.0 MeV Gamma Rays) ---
# mu: Attenuation (cm^-1) | density: g/cm^3 | b_slope: Build-up Factor slope
MATERIALS = {
    "Lead (Pb)": {"mu": 0.771, "density": 11.34, "color": "#7f8c8d", "b_slope": 1.2},
    "Tungsten Heavy Alloy (WHA)": {"mu": 1.250, "density": 18.50, "color": "#2c3e50", "b_slope": 1.1},
    "Depleted Uranium (DU)": {"mu": 1.300, "density": 19.00, "color": "#1abc9c", "b_slope": 1.05},
    "Lead-Antimony Alloy": {"mu": 0.750, "density": 11.00, "color": "#95a5a6", "b_slope": 1.25},
    "Iron (Fe)": {"mu": 0.443, "density": 7.87, "color": "#a04000", "b_slope": 1.8},
    "Concrete (Standard)": {"mu": 0.151, "density": 2.35, "color": "#bdc3c7", "b_slope": 2.5},
    "Water (H2O)": {"mu": 0.070, "density": 1.00, "color": "#3498db", "b_slope": 3.2},
    "Inconel 718": {"mu": 0.480, "density": 8.19, "color": "#f39c12", "b_slope": 1.7},
    "Wood's Metal": {"mu": 0.650, "density": 9.60, "color": "#e74c3c", "b_slope": 1.5},
    "Tantalum (Ta)": {"mu": 0.950, "density": 16.69, "color": "#9b59b6", "b_slope": 1.15}
}

# --- HEADER SECTION ---
st.title(" Nuclear Shielding Design Suite")
st.subheader("Stochastic & Deterministic Radiation Analysis")
st.markdown("""
This tool allows for the comparison of high-Z alloys and structural materials. 
It calculates **Broad-Beam Attenuation** by integrating **Build-up Factors (B)** to account for scattered photons.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Global Simulation Settings")
max_thick = st.sidebar.slider("Max Thickness Analysis (cm)", 10, 100, 50)
st.sidebar.divider()
st.sidebar.info("Calculations based on 1.0 MeV Photon Energy.")

# --- PHYSICS ENGINE ---
def calculate_attenuation(thickness_range, mu, b_slope):
    mfp = mu * thickness_range
    B = 1 + (b_slope * mfp)  # Linear Build-up approximation
    return B * np.exp(-mfp)

# --- LAYOUT: ANALYSIS TABS ---
tab_compare, tab_structural, tab_safety = st.tabs([" Performance Curves", " Mass & Load", " Engineering Standards"])

with tab_compare:
    st.header("Comparative Material Analysis")
    selected_mats = st.multiselect(
        "Select Materials to Compare:", 
        list(MATERIALS.keys()), 
        default=["Lead (Pb)", "Tungsten Heavy Alloy (WHA)", "Concrete", "Iron (Fe)"]
    )
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 5))
    x_vals = np.linspace(0, max_thick, 200)
    
    for name in selected_mats:
        props = MATERIALS[name]
        y_vals = calculate_attenuation(x_vals, props['mu'], props['b_slope'])
        ax.plot(x_vals, y_vals, label=name, color=props['color'], lw=2)
    
    ax.set_yscale('log')
    ax.set_xlabel("Thickness (cm)")
    ax.set_ylabel("Transmission (I/I0)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    st.pyplot(fig)
    
    # Data Table
    st.markdown("### Engineering Reference Data")
    table_data = []
    for m in selected_mats:
        hvl = np.log(2) / MATERIALS[m]['mu']
        tvl = np.log(10) / MATERIALS[m]['mu']
        table_data.append({
            "Material": m,
            "Density (g/cm³)": MATERIALS[m]['density'],
            "HVL (cm)": round(hvl, 2),
            "TVL (cm)": round(tvl, 2)
        })
    st.table(table_data)



with tab_structural:
    st.header("Shielding Logistics & Floor Loading")
    
    c1, c2 = st.columns(2)
    with c1:
        target_mat = st.selectbox("Analyze Material Weight:", list(MATERIALS.keys()))
        target_thick = st.slider("Design Thickness (cm)", 1, max_thick, 10)
    
    with c2:
        wall_h = st.number_input("Wall Height (m)", value=2.5)
        wall_w = st.number_input("Wall Width (m)", value=3.0)
        floor_max = st.number_input("Floor Limit (kg/m²)", value=2000)

    # Calculation logic
    area = wall_h * wall_w
    volume_m3 = area * (target_thick / 100)
    density_kg_m3 = MATERIALS[target_mat]['density'] * 1000
    total_weight = volume_m3 * density_kg_m3
    loading = total_weight / area

    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Total Weight", f"{total_weight:,.0f} kg")
    res2.metric("Surface Load", f"{loading:,.0f} kg/m²")
    
    percent_capacity = (loading / floor_max) * 100
    res3.metric("Floor Capacity Used", f"{percent_capacity:.1f}%")

    if loading > floor_max:
        st.error(f" Structural Failure: Load exceeds floor limit by {loading - floor_max:,.0f} kg/m².")
    else:
        st.success(" Structural Design within safety limits.")



with tab_safety:
    st.header("ALARA & Radiological Safety Guidelines")
    
    st.warning("**Disclaimer:** This is a conceptual design tool. Final designs must be verified via Monte Carlo (MCNP) simulation and approved by a certified Health Physicist.")
    
    st.markdown("""
    ### The Three Pillars of Radiation Protection
    1. **Time:** Minimize duration of exposure.
    2. **Distance:** Maximize distance from source (Inverse Square Law).
    3. **Shielding:** Use high-Z materials to attenuate photon flux.
    
    ### Engineering Best Practices
    * **Avoid 'Streaming':** Ensure there are no direct gaps or "straight line" holes in shielding walls (use 'dog-leg' or interlocking bricks).
    * **Secondary Radiation:** Remember that high-energy gammas can produce secondary electrons and Bremsstrahlung radiation.
    * **Structural Support:** Ensure lead walls are physically supported to prevent "slumping" over time due to high density.
    """)
    
    st.info("**ALARA:** As Low As Reasonably Achievable.")
