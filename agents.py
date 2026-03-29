
class AnomalyAgent:
    def detect(self, est_C, baseline_C, est_R, baseline_R):
        anomaly = False
        reason = []

        if abs(est_C - baseline_C) / baseline_C > 0.2:
            anomaly = True
            reason.append("Compliance deviation")

        if abs(est_R - baseline_R) / baseline_R > 0.3:
            anomaly = True
            reason.append("Resistance deviation")

        return anomaly, reason


class DiagnosisAgent:
    def diagnose(self, est_C, est_R):

        # Mixed pathology
        if est_C < 0.03 and est_R > 20:
            return "Mixed Pathology (ARDS + COPD)"

        # ARDS
        elif est_C < 0.03:
            return "ARDS (Stiff Lung)"

        # COPD
        elif est_R > 20:
            return "COPD (Obstructive)"

        # Hypercompliant
        elif est_C > 0.08 and est_R < 10:
            return "Hypercompliant Lung (Overdistension Risk)"

        # Normal
        else:
            return "Normal"


class DecisionAgent:
    def decide(self, diagnosis, est_C, est_R, target_P, target_Vt, peep_P):

        # Default (no change)
        new_P = target_P
        new_Vt = target_Vt
        new_PEEP = peep_P

        # ARDS (Low Compliance)
        if diagnosis == "ARDS (Stiff Lung)":
            new_Vt = max(0.3, target_Vt * 0.7)
            new_P = max(10, target_P - 5)
            new_PEEP = min(10, peep_P + 2)

        # COPD (High Resistance)
        elif diagnosis == "COPD (Obstructive)":
            new_Vt = target_Vt
            new_P = min(40, target_P + 2)
            new_PEEP = max(2, peep_P - 1)

        # Mixed Pathology (ARDS + COPD)
        elif diagnosis == "Mixed Pathology (ARDS + COPD)":
            new_Vt = max(0.3, target_Vt * 0.6)
            new_P = max(10, target_P - 5)
            new_PEEP = min(10, peep_P + 1)

        # Hypercompliant Lung (Overdistension Risk)
        elif diagnosis == "Hypercompliant Lung (Overdistension Risk)":
            new_Vt = max(0.3, target_Vt * 0.6)
            new_P = max(10, target_P - 3)
            new_PEEP = peep_P  # keep stable

        # Normal
        else:
            pass  # keep original settings

        return new_P, new_Vt, new_PEEP

class ComplianceAgent:
    def check(self, pressure, limit=30):
        if pressure > limit:
            return "BLOCK", f"Pressure {pressure:.1f} exceeds limit"
        return "SAFE", "Within limits"


class AuditAgent:
    def log(self, time, diagnosis, input_params, adjusted_params, reason, confidence):
        return {
            "time": round(time, 2),
            "diagnosis": diagnosis,

            "input_settings": {
                "Pressure": round(input_params["P"], 2),
                "Tidal Volume": round(input_params["Vt"], 2),
                "PEEP": round(input_params["PEEP"], 2)
            },

            "adjusted_settings": {
                "Pressure": round(adjusted_params["P"], 2),
                "Tidal Volume": round(adjusted_params["Vt"], 2),
                "PEEP": round(adjusted_params["PEEP"], 2)
            },

            "reason": reason,
            "confidence": round(confidence, 2)
        }