from typing import Dict, Any
from datetime import datetime

M2_PER_SQMI = 2589988.110336


class ComplianceChecker:
    def __init__(self, min_area_sqmi: float = 2500):
        self.min_area_sqmi = float(min_area_sqmi)

    def _extract_area_sqmi(self, props: Dict[str, Any]):
        if "ALAND" in props:
            return float(props["ALAND"]) / M2_PER_SQMI

        for k in ("AREA_SQMI", "ALAND_SQMI", "area_sqmi"):
            if k in props:
                return float(props[k])

        return None

    def analyze(self, data: Dict[str, Any]):
        features = data.get("features", [])
        non_compliant = []
        total = 0

        for feat in features:
            props = feat.get("properties", {})
            name = props.get("NAME", "UNKNOWN")

            area = self._extract_area_sqmi(props)
            if area is None:
                continue

            total += 1
            shortfall = self.min_area_sqmi - area
            if shortfall > 0:
                non_compliant.append({
                    "name": name,
                    "area_sqmi": round(area, 3),
                    "required_sqmi": self.min_area_sqmi,
                    "shortfall_sqmi": round(shortfall, 3),
                    "recommendation": "Consider consolidation with adjacent counties"
                })

        non_compliant.sort(key=lambda x: x["shortfall_sqmi"], reverse=True)

        return {
            "total_counties_checked": total,
            "non_compliant_count": len(non_compliant),
            "non_compliant_counties": non_compliant,
            "min_area_sqmi": self.min_area_sqmi,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
