import requests
import math
from typing import Dict, Any, Optional, Tuple


class ArcGISError(Exception):
    pass


class ArcGISClient:
    def __init__(self, url: str, token: Optional[str] = None, timeout: int = 30):
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.token = token

    # -----------------------------
    # INTERNAL REQUEST WRAPPER
    # -----------------------------
    def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if self.token:
            params["token"] = self.token     # ← ADD TOKEN HERE

        try:
            resp = requests.get(
                f"{self.url}/query", params=params, timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise ArcGISError(f"Network error: {e}")

    # -----------------------------
    # ESRI JSON → GEOJSON CONVERTER
    # -----------------------------
    def _to_geojson(self, arcjson: Dict[str, Any]):
        geojson = {"type": "FeatureCollection", "features": []}

        for f in arcjson.get("features", []):
            attrs = f.get("attributes", {})
            geom = f.get("geometry")

            if not geom:
                gj_geom = None

            elif "x" in geom and "y" in geom:
                gj_geom = {
                    "type": "Point",
                    "coordinates": [geom["x"], geom["y"]],
                }

            elif "rings" in geom:
                gj_geom = {
                    "type": "Polygon",
                    "coordinates": geom["rings"],
                }

            else:
                gj_geom = None

            geojson["features"].append({
                "type": "Feature",
                "properties": attrs,
                "geometry": gj_geom
            })

        return geojson

    # -----------------------------
    # ATTRIBUTE QUERY 
    # -----------------------------
    def query(self, where="1=1", out_fields="*"):
        params = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true",
            "f": "json"
        }

        raw = self._request(params)
        return self._to_geojson(raw)

    # -----------------------------
    # SPATIAL QUERY (BUFFER)
    # -----------------------------
    def query_nearby(self, point: Tuple[float, float], distance_miles: float,
                     where="1=1", out_fields="*"):

        buffer_meters = distance_miles * 1609.344

        geometry = {
            "x": point[0],
            "y": point[1],
            "spatialReference": {"wkid": 4326}
        }

        params = {
            "where": where,
            "geometry": geometry,
            "geometryType": "esriGeometryPoint",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "distance": buffer_meters,
            "units": "esriSRUnit_Meter",
            "outFields": out_fields,
            "returnGeometry": "true",
            "f": "json"
        }

        raw = self._request(params)
        return self._to_geojson(raw)
