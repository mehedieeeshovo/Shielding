import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nuclear Shielding & Build-up Lab", layout="wide")

# --- MATERIALS DATABASE (Data for 1.0 MeV Photons) ---
# mu: Linear Attenuation (cm^-1) | b_factor_ref: Approximate build-up slope
# Lead (Pb), Tungsten (W), Iron (Fe), Concrete, Water (H2O)
MATERIALS = {
    "Lead (Pb)": {"mu": 0.771, "color": "#7f8c8d", "b_slope": 1.2},
    "Tungsten (W)": {"mu": 1.250, "color": "#2c3e50", "b_slope": 1.1},
    "Iron (Fe)": {"mu": 0.443, "color": "#a04000", "b_slope": 1.8},
    "Concrete": {"mu": 0.151, "color": "#bdc3c7", "b_slope": 2.5},
    "Water": {"mu": 0.070, "color": "#3498db", "b_slope": 3.2}
}

st.title(" Advanced Radiation Shielding & Build-up Analysis")
st.markdown("""
This tool simulates **Broad-Beam Attenuation**, accounting for scattered radiation through 
the **Build-up Factor ($B$)**. Without build-up, shielding requirements are often dangerously underestimated.
""")

# --- SIDEBAR ---
st.sidebar.header("Calculation Settings")
max_thick = st.sidebar.slider("Max Analysis Thickness (cm)", 10, 100, 50)
energy_mev = st.sidebar.selectbox("Source Energy", ["0.5 MeV", "1.0 MeV", "2.0 MeV"])

# --- PHYSICS LOGIC ---
def calculate_attenuation(thickness_range, mu, b_slope, use_buildup=True):
    # Mean free paths (mfp)
    mfp = mu * thickness_range
    # Linear Build-up Approximation: B = 1 + (b_slope * mfp)
    B = 1 + (b_slope * mfp) if use_buildup else 1.0
    # Transmission (I/I0)
    transmission = B * np.exp(-mfp)
    return transmission

# --- VISUALIZATION ---
st.subheader("📊 Comparative Attenuation Curves (Broad-Beam)")

fig, ax = plt.subplots(figsize=(12, 6))
x_vals = np.linspace(0, max_thick, 200)

for name, props in MATERIALS.items():
    y_vals = calculate_attenuation(x_vals, props['mu'], props['b_slope'])
    ax.plot(x_vals, y_vals, label=name, color=props['color'], lw=2.5)

ax.set_yscale('log') # Standard for shielding curves
ax.set_ylim(1e-4, 1.1)
ax.set_xlabel("Shield Thickness (cm)")
ax.set_ylabel("Transmission Ratio ($I/I_0$)")
ax.grid(True, which="both", ls="-", alpha=0.2)
ax.set_title("Photon Attenuation with Scatter Build-up Correction")
ax.legend()
st.pyplot(fig)



# --- DATA TABLE & INSIGHTS ---
st.divider()
cols = st.columns(len(MATERIALS))

for i, (name, props) in enumerate(MATERIALS.items()):
    hvl = np.log(2) / props['mu']
    tenth_value = np.log(10) / props['mu']
    cols[i].metric(name, f"{hvl:.2f} cm")
    cols[i].caption(f"HVL (Half-Value Layer)")
    cols[i].write(f"**TVL:** {tenth_value:.1f} cm")

st.info("""
**Engineering Note:** The **Build-up Factor** accounts for photons that undergo Compton scattering 
within the shield but are still redirected toward the detector. As seen in the curves, 
lighter materials like **Water** and **Concrete** have much higher build-up slopes compared to **Lead**.
""")
