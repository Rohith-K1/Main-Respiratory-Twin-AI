import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 65)
    ax.axis('off')

    fig.patch.set_facecolor('white')

    arrow_props = dict(arrowstyle='->', lw=2, color='#555555')

    # ------------------ DATA SOURCE ------------------
    rect_source = patches.FancyBboxPatch((2, 22), 18, 20,
        boxstyle="round,pad=1", linewidth=2,
        edgecolor='#2ecc71', facecolor='#eafaf1')
    ax.add_patch(rect_source)

    ax.text(11, 37, "DATA SOURCE", ha='center', fontsize=14, weight='bold')
    ax.text(11, 30, "Ventilator Sensors\nPressure (P), Flow (Q)", ha='center', fontsize=10)

    # ------------------ CORE ENGINE ------------------
    rect_engine = patches.FancyBboxPatch((28, 10), 52, 45,
        boxstyle="round,pad=1", linewidth=2,
        edgecolor='#2980b9', facecolor='#ebf5fb')
    ax.add_patch(rect_engine)

    ax.text(54, 52, "RESPITWIN CORE ENGINE", ha='center', fontsize=16, weight='bold')

    # Physics Model
    rect_physics = patches.FancyBboxPatch((32, 15), 14, 10,
        boxstyle="round,pad=0.5", edgecolor='#3498db', facecolor='white')
    ax.add_patch(rect_physics)

    ax.text(39, 22, "Physics Model", ha='center', fontsize=10, weight='bold')
    ax.text(39, 18, "P = V/C + RQ", ha='center', fontsize=9)

    # Parameter Estimator
    rect_est = patches.FancyBboxPatch((32, 30), 14, 10,
        boxstyle="round,pad=0.5", edgecolor='#8e44ad', facecolor='white')
    ax.add_patch(rect_est)

    ax.text(39, 37, "Estimator", ha='center', fontsize=10, weight='bold')
    ax.text(39, 33, "Find C, R", ha='center', fontsize=9)

    # Diagnosis Agent
    rect_diag = patches.FancyBboxPatch((50, 32), 14, 10,
        boxstyle="round,pad=0.5", edgecolor='#f39c12', facecolor='white')
    ax.add_patch(rect_diag)

    ax.text(57, 38, "Diagnosis Agent", ha='center', fontsize=10, weight='bold')
    ax.text(57, 34, "ARDS / COPD /\nMixed / Normal", ha='center', fontsize=8)

    # Decision Agent
    rect_decision = patches.FancyBboxPatch((50, 18), 14, 10,
        boxstyle="round,pad=0.5", edgecolor='#16a085', facecolor='white')
    ax.add_patch(rect_decision)

    ax.text(57, 25, "Decision Agent", ha='center', fontsize=10, weight='bold')
    ax.text(57, 21, "Adjust P, Vt, PEEP", ha='center', fontsize=8)

    # Safety Layer
    rect_safety = patches.FancyBboxPatch((68, 25), 10, 12,
        boxstyle="round,pad=0.5", edgecolor='#c0392b', facecolor='#fdedec')
    ax.add_patch(rect_safety)

    ax.text(73, 33, "Safety", ha='center', fontsize=10, weight='bold')
    ax.text(73, 28, "Limit Pressure\n(<30 cmH2O)", ha='center', fontsize=8)

    # ------------------ GEN-AI ------------------
    rect_ai = patches.FancyBboxPatch((45, 57), 20, 6,
        boxstyle="round,pad=0.5", edgecolor='#f1c40f', facecolor='#fef9e7')
    ax.add_patch(rect_ai)

    ax.text(55, 60, "Gen-AI Explanation", ha='center', fontsize=11, weight='bold')

    # ------------------ UI ------------------
    rect_ui = patches.FancyBboxPatch((85, 22), 20, 20,
        boxstyle="round,pad=1", edgecolor='#34495e', facecolor='#eaeded')
    ax.add_patch(rect_ui)

    ax.text(95, 37, "CLINICIAN UI", ha='center', fontsize=14, weight='bold')
    ax.text(95, 30, "Graphs\nAI Decisions\nSafety Alerts", ha='center', fontsize=10)

    # ------------------ ARROWS ------------------

    # Data → Physics
    ax.annotate("", xy=(32, 20), xytext=(20, 30), arrowprops=arrow_props)

    # Physics → Estimator
    ax.annotate("", xy=(39, 30), xytext=(39, 25), arrowprops=arrow_props)

    # Estimator → Diagnosis
    ax.annotate("", xy=(50, 35), xytext=(46, 35), arrowprops=arrow_props)

    # Diagnosis → Decision
    ax.annotate("", xy=(57, 28), xytext=(57, 32), arrowprops=arrow_props)

    # Decision → Safety
    ax.annotate("", xy=(68, 28), xytext=(64, 23), arrowprops=arrow_props)

    # Safety → UI
    ax.annotate("", xy=(85, 30), xytext=(78, 30), arrowprops=arrow_props)

    # Estimator → GenAI
    ax.annotate("", xy=(50, 57), xytext=(46, 40),
                arrowprops=dict(arrowstyle='->', linestyle='--', color='#f39c12'))

    # GenAI → UI
    ax.annotate("", xy=(90, 42), xytext=(65, 57),
                arrowprops=dict(arrowstyle='->', linestyle='--', color='#f39c12'))

    # Title
    ax.text(55, 5, "RespiTwin AI: Autonomous Clinical Decision Pipeline",
            ha='center', fontsize=18, weight='bold')

    plt.tight_layout()
    plt.savefig('project_architecture_updated.png', dpi=300)
    print("Generated: project_architecture_updated.png")

# Run
draw_architecture()