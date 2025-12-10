from arcgis_client import ArcGISClient
from compliance_checker import ComplianceChecker
from session_manager import SessionManager


FEATURE_URL = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties/FeatureServer/0"


def pretty_print_geojson_head(gj):
    fcount = len(gj.get("features", []))
    print(f"JSON features: {fcount}")


def demo():
    client = ArcGISClient(FEATURE_URL)
    checker = ComplianceChecker(min_area_sqmi=2500)
    sm = SessionManager()

    print("Querying Texas counties...")
    texas = client.query(where="STATE_NAME = 'Texas'", out_fields="*")
    pretty_print_geojson_head(texas)

    report = checker.analyze(texas)
    print(f"Total counties checked: {report['total_counties_checked']}")
    print(f"Non-compliant count: {report['non_compliant_count']}")

    print("Querying counties within 50 miles of Austin...")
    austin_results = client.query_nearby(
        point=(-97.7431, 30.2672),
        distance_miles=50,
        out_fields="*"
    )
    pretty_print_geojson_head(austin_results)

    session_name = "Texas_Counties_Analysis"
    print("Saving session...")
    session_path = sm.save(
        name=session_name,
        query_params={"where": "STATE_NAME = 'Texas'"},
        results=texas,
        compliance_report=report,
        user="ram07.nsdi@gmail.com"
    )
    print(f"Session saved at: {session_path}")


if __name__ == "__main__":
    demo()
