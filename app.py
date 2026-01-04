import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Nuclear Shielding Lab", layout="wide")

# --- MATERIALS DATABASE ---
# Verified Keys for 1.0 MeV Gamma Analysis
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

st.title(" Nuclear Shielding Design Suite")
st.markdown("### Broad-Beam Attenuation & Structural Logistics")

# --- SIDEBAR ---
st.sidebar.header("Global Settings")
max_thick = st.sidebar.slider("Max Analysis Thickness (cm)", 10, 100, 50)

# --- PHYSICS ENGINE ---
def calculate_attenuation(thickness_range, mu, b_slope):
    mfp = mu * thickness_range
    B = 1 + (b_slope * mfp)  # Linear Build-up Factor
    return B * np.exp(-mfp)

# --- ANALYSIS TABS ---
tab_compare, tab_structural, tab_safety = st.tabs([" Performance Curves", " Mass & Load", " Engineering Standards"])

with tab_compare:
    st.header("Material Attenuation Analysis")
    
    # SAFE SELECTION LOGIC: This prevents the StreamlitAPIException
    available_options = list(MATERIALS.keys())
    default_vals = ["Lead (Pb)", "Tungsten Heavy Alloy (WHA)", "Iron (Fe)", "Concrete (Standard)"]
    
    # Double-check that defaults actually exist in options to prevent crashes
    validated_defaults = [d for d in default_vals if d in available_options]

    selected_mats = st.multiselect(
        "Select Materials to Compare:", 
        options=available_options, 
        default=validated_defaults
    )
    
    if selected_mats:
        fig, ax = plt.subplots(figsize=(10, 5))
        x_vals = np.linspace(0, max_thick, 200)
        
        for name in selected_mats:
            props = MATERIALS[name]
            y_vals = calculate_attenuation(x_vals, props['mu'], props['b_slope'])
            ax.plot(x_vals, y_vals, label=name, color=props['color'], lw=2)
        
        ax.set_yscale('log')
        ax.set_xlabel("Thickness (cm)")
        ax.set_ylabel("Transmission (I/I0)")
        ax.set_title("Photon Transmission Ratio vs. Shield Depth")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        st.pyplot(fig)
        
        # Engineering Data Table
        st.markdown("#### Calculated Attenuation Metrics")
        table_data = []
        for m in selected_mats:
            hvl = np.log(2) / MATERIALS[m]['mu']
            tvl = np.log(10) / MATERIALS[m]['mu']
            table_data.append({
                "Material": m,
                "HVL (cm)": round(hvl, 2),
                "TVL (cm)": round(tvl, 2),
                "Density (g/cm³)": MATERIALS[m]['density']
            })
        st.table(table_data)
    else:
        st.warning("Please select at least one material to view the analysis.")



with tab_structural:
    st.header("Shielding Weight & Floor Capacity")
    
    col1, col2 = st.columns(2)
    with col1:
        target_mat = st.selectbox("Analyze Material:", available_options)
        target_thick = st.slider("Design Thickness (cm)", 1, max_thick, 10)
    
    with col2:
        wall_h = st.number_input("Wall Height (m)", value=2.0)
        wall_w = st.number_input("Wall Width (m)", value=3.0)
        floor_max = st.number_input("Floor Load Limit (kg/m²)", value=1500)

    # Engineering Math
    area = wall_h * wall_w
    volume_m3 = area * (target_thick / 100)
    density_kg_m3 = MATERIALS[target_mat]['density'] * 1000
    total_weight = volume_m3 * density_kg_m3
    loading = total_weight / area

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Weight", f"{total_weight:,.0f} kg")
    m2.metric("Floor Load", f"{loading:,.0f} kg/m²")
    m3.metric("Capacity Used", f"{(loading/floor_max)*100:.1f}%")

    if loading > floor_max:
        st.error(f" STRUCTURAL ALERT: Floor load exceeded by {loading - floor_max:,.0f} kg/m².")
    else:
        st.success(" Design is structurally safe for standard floor loading.")



with tab_safety:
    st.header(" Safety Standards & ALARA")
    st.info("**ALARA:** As Low As Reasonably Achievable (Time, Distance, Shielding).")
    
    st.markdown("""
    ### Shielding Integrity Instructions:
    1. **Avoid Direct Paths:** Never design shielding with straight-through gaps for cables or pipes. Use 'Z-plugs' or 'Dog-legs'.
    2. **Material Uniformity:** Ensure cast materials like Concrete have no air pockets (voids), which allow radiation 'streaming'.
    3. **Secondary Effects:** High-Z materials like Lead can produce secondary X-rays (Fluorescence). Ensure a low-Z 'cladding' is used if necessary.
    
    ### Disclaimer
    This tool is for **Preliminary Design Estimation**. Final shielding for nuclear facilities must be verified using 3D Monte Carlo simulations (MCNP/GEANT4).
    """)
