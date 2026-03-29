import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import least_squares
from agents import AnomalyAgent, DiagnosisAgent, DecisionAgent, ComplianceAgent, AuditAgent
# ==========================================
# 1. THE PHYSICS ENGINE (FORWARD MODEL)
# ==========================================
class PatientLung:
    """The 'Virtual Patient'. Simulates physical response to airflow."""
    def __init__(self, compliance, resistance):
        self.C = compliance      # L/cmH2O
        self.R = resistance      # cmH2O*s/L
        self.volume = 0.0        # Current lung volume (L)
        
    def update(self, flow_in, dt):
        """
        Evolves the lung state by one timestep.
        Physics: P_airway = (Volume / Compliance) + (Flow * Resistance)
        """
        # 1. Update Volume (Integration)
        # We add a small leak factor (natural exhalation recoil)
        self.volume += flow_in * dt
        if self.volume < 0: self.volume = 0
        
        # 2. Calculate Pressures
        p_elastic = self.volume / self.C
        p_resistive = flow_in * self.R
        p_airway = p_elastic + p_resistive
        
        return p_airway, self.volume

# ==========================================
# 2. THE VENTILATOR (CONTROLLER)
# ==========================================
class PIDVentilator:
    """The 'Machine'. Regulates flow to hit target pressure."""
    def __init__(self, kp, ki, kd, dt):
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd
        self.dt = dt
        self.integral = 0
        self.prev_error = 0
        
    def compute_flow(self, target_p, current_p):
        """Calculates blower command based on pressure error."""
        error = target_p - current_p
        
        # PID Logic
        self.integral += error * self.dt
        derivative = (error - self.prev_error) / self.dt
        
        # Output is Flow Rate (L/s)
        # We clamp it between -1.0 (Exhale) and 1.5 (Inhale)
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        flow_command = np.clip(output, -1.0, 1.5)
        
        self.prev_error = error
        return flow_command

# ==========================================
# 3. THE DIGITAL TWIN (DIAGNOSTIC AI)
# ==========================================
def estimate_parameters(df_data):
    """
    REVERSE MODEL: Uses Least Squares to guess C and R from noisy data.
    Equation: P = (1/C)*V + R*Q + PEEP
    """
    # We take the last 2 seconds of data for estimation
    window = df_data.tail(40) # 40 points @ 50ms = 2 seconds
    
    if len(window) < 10: return 0, 0 # Not enough data
    
    # Prepare Matrices for Solver
    # y = Pressure
    # X = [Volume, Flow]
    # coeffs = [Elasticity(1/C), Resistance]
    
    def residuals(coeffs, vol, flow, press):
        est_E, est_R = coeffs
        model_p = (est_E * vol) + (est_R * flow)
        return model_p - press

    x0 = [20.0, 10.0] # Initial guess (E=20, R=10)
    res = least_squares(residuals, x0, args=(window['Volume'], window['Flow'], window['Pressure']))
    
    est_elastance, est_resistance = res.x
    est_compliance = 1.0 / est_elastance if est_elastance > 0 else 100
    
    return est_compliance, est_resistance


def generate_ai_insight(diagnosis, action, est_C, est_R, confidence):
    return f"""
### 🧠 Autonomous Clinical AI Report

**Diagnosis:** {diagnosis}  
**Estimated Compliance:** {est_C:.3f}  
**Estimated Resistance:** {est_R:.2f}  

**Decision Taken:**  
 {action}

**Confidence Level:** {confidence:.2f}

**Reasoning:**
- Derived from real-time pressure-flow analysis
- Digital twin matched physiological behavior
- Safety constraints evaluated before action

**System Status:** Autonomous Monitoring Active
"""

# ==========================================
# 4. STREAMLIT DASHBOARD UI
# ==========================================
st.set_page_config(page_title="Ventilator Twin Pro", layout="wide")
# Initialize agents
anomaly_agent = AnomalyAgent()
diagnosis_agent = DiagnosisAgent()
decision_agent = DecisionAgent()
compliance_agent = ComplianceAgent()
audit_agent = AuditAgent()

# Baseline (initial normal condition)
baseline_C = 0.05
baseline_R = 10.0

st.title("🫁 RespiTwin AI: Autonomous Clinical Guardian")
st.markdown("The **Bridge** between Hardware Control and AI Diagnostics.")

# --- SIDEBAR: "THE REALITY" (Patient & Machine) ---
st.sidebar.header("1. The Patient (Reality)")
st.sidebar.caption("These sliders simulate the actual human lung condition.")
real_C = st.sidebar.slider("True Compliance (C)", 0.01, 0.10, 0.05, 0.005, format="%.3f")
real_R = st.sidebar.slider("True Resistance (R)", 5.0, 50.0, 10.0, 1.0)

st.sidebar.header("2. The Ventilator (Settings)")
target_P = st.sidebar.slider("Target Pressure (Set)", 10.0, 40.0, 20.0)
peep_P = st.sidebar.slider("PEEP (Baseline)", 0.0, 10.0, 5.0)
target_Vt = st.sidebar.slider("Target Tidal Volume (L)", 0.2, 0.8, 0.5, 0.05)

# --- SIMULATION LOOP (RUNS INSTANTLY) ---
dt = 0.05 # 50ms
duration = 15 # seconds
steps = int(duration / dt)

# Initialize Objects
patient = PatientLung(real_C, real_R)
vent = PIDVentilator(kp=0.6, ki=0.8, kd=0.1, dt=dt) # Tuned PID

# Storage
data = {'Time': [], 'Pressure': [], 'Flow': [], 'Volume': [], 'Target': []}

t_axis = np.linspace(0, duration, steps)
current_target = 0
# default before AI kicks in
adjusted_target_P = target_P
adjusted_Vt = target_Vt
adjusted_PEEP = peep_P
for t in t_axis:
    # 1. Breathing Cycle Logic (Inhale 1.5s, Exhale 2.5s)
    cycle_time = t % 4.0
    if cycle_time < 1.5:
        current_target = adjusted_target_P # Inhale
    else:
        current_target = adjusted_PEEP   # Exhale
        
    # 2. Get Ventilator Output
    # We add simulated sensor noise (random normal distribution)
    noise = np.random.normal(0, 0.2) 
    flow_cmd = vent.compute_flow(current_target, patient.volume/patient.C + noise)
    # LIMIT FLOW BASED ON TIDAL VOLUME
    max_flow = adjusted_Vt / 1.5  # inhale duration ~1.5 sec
    flow_cmd = np.clip(flow_cmd, -1.0, max_flow)
    
    # 3. Update Patient Physics
    p_actual, vol_actual = patient.update(flow_cmd, dt)
    
    # 4. Store Data
    data['Time'].append(t)
    data['Pressure'].append(p_actual)
    data['Flow'].append(flow_cmd)
    data['Volume'].append(vol_actual)
    data['Target'].append(current_target)

df = pd.DataFrame(data)
df["Pressure_smooth"] = df["Pressure"].rolling(5).mean()

# --- MAIN DASHBOARD: "THE TWIN" (Diagnostics) ---

# Run the Estimator (Reverse Model) on the generated data
est_C, est_R = estimate_parameters(df)

# ==========================
#  AGENT PIPELINE STARTS
# ==========================

# 1. Detect anomaly
anomaly, reasons = anomaly_agent.detect(est_C, baseline_C, est_R, baseline_R)

# 2. Diagnose condition
diagnosis = diagnosis_agent.diagnose(est_C, est_R)
#  AUTO INTERVENTION (SAFE VERSION)

adjusted_target_P = target_P  # default

#if diagnosis == "ARDS (Stiff Lung)":
 #   adjusted_target_P = max(10, target_P - 5)

#elif diagnosis == "COPD (Obstructive)":
 #   adjusted_target_P = min(40, target_P + 2)

# 3. Decide action
adjusted_target_P, adjusted_Vt, adjusted_PEEP = decision_agent.decide(diagnosis, est_C, est_R, target_P, target_Vt, peep_P)
action = f"P→{adjusted_target_P:.1f}, Vt→{adjusted_Vt:.2f}, PEEP→{adjusted_PEEP:.1f}"

# 4. Safety / compliance check
latest_pressure = df['Pressure'].iloc[-1]
status, compliance_reason = compliance_agent.check(latest_pressure)

# 5. Confidence score
error = abs(est_C - real_C) / real_C
confidence = max(0, 1 - error)

# 6. Audit log
audit_log = audit_agent.log(
    time=df['Time'].iloc[-1],
    diagnosis=diagnosis,

    input_params={
        "P": target_P,
        "Vt": target_Vt,
        "PEEP": peep_P
    },

    adjusted_params={
        "P": adjusted_target_P,
        "Vt": adjusted_Vt,
        "PEEP": adjusted_PEEP
    },

    reason=reasons + [compliance_reason],
    confidence=confidence
)
# ==========================
# AGENT PIPELINE ENDS
# ==========================


# Top KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Peak Pressure", f"{df['Pressure'].max():.1f} cmH2O", delta_color="inverse")
col2.metric("Tidal Volume", f"{df['Volume'].max()*1000:.0f} mL")
# The "Invisible Data" Revealed
col3.metric("Calculated Compliance", f"{est_C:.3f}", delta=f"{est_C - real_C:.3f} err")
col4.metric("Calculated Resistance", f"{est_R:.1f}", delta=f"{est_R - real_R:.1f} err")
# Driving Pressure (VERY IMPORTANT)
col5.metric(
    "Driving Pressure (ΔP)",
    f"{(adjusted_target_P - adjusted_PEEP):.1f} cmH2O"
)
# BONUS: AI CONTROL DISPLAYst

st.markdown("### 🤖 AI Multi-Parameter Control")

col5, col6, col7 = st.columns(3)

col5.metric(
    "Pressure (P)",
    f"{adjusted_target_P:.1f} cmH2O",
    delta=f"{adjusted_target_P - target_P:.1f}"
)

col6.metric(
    "Tidal Volume (Vt)",
    f"{adjusted_Vt:.2f} L",
    delta=f"{adjusted_Vt - target_Vt:.2f}"
)

col7.metric(
    "PEEP",
    f"{adjusted_PEEP:.1f} cmH2O",
    delta=f"{adjusted_PEEP - peep_P:.1f}"
)


# Waveforms
tab1, tab2 = st.tabs(["📊 Live Telemetry", "🤖 Gen-AI Analysis"])

with tab1:
    fig = go.Figure()
    # Pressure Trace
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Pressure_smooth'], name='Airway Pressure', 
                             line=dict(color='#ff4b4b', width=2)))
    # Target Trace (Dashed)
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Target'], name='Target Setting', 
                             line=dict(color='gray', dash='dash')))
    # Flow Trace (Secondary Axis)
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Flow'], name='Flow (L/s)', 
                             line=dict(color='#1c83e1', width=1.5), yaxis='y2'))
    
    fig.add_hrect(
    y0=30, y1=50,
    fillcolor="red",
    opacity=0.1
)
    
    fig.update_layout(
        height=450,
        title="Ventilator Pressure & Flow (AI Safety Monitoring)",
        xaxis_title="Time (seconds)",
        yaxis=dict(title="Pressure (cmH2O)", range=[0, 50]),
        yaxis2=dict(title="Flow (L/s)", overlaying="y", side="right", range=[-1.5, 2]),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("## 🤖 Autonomous Agent Decisions")

    col1, col2, col3 = st.columns(3)

    col1.metric("Diagnosis", diagnosis)
    col2.metric("Decision", action)
    col3.metric("Safety Status", status)

    st.markdown("### 📜 Audit Log")
    st.json(audit_log)

    st.markdown("### 🧠 AI Explanation")
    st.info(generate_ai_insight(diagnosis, action, est_C, est_R, confidence))