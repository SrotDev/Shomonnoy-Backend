#!/usr/bin/env python3
from rtree import index
import os, sys, json, argparse, requests
from typing import Dict, Any, List, Optional
import math
from copy import deepcopy
# ---------- Geometry primitives ----------

class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = float(x)  # x = lon
        self.y = float(y)  # y = lat
    def __repr__(self): return f"Point({self.x:g},{self.y:g})"

class Rectangle:
    __slots__ = ("xmin","ymin","xmax","ymax","id")
    def __init__(self, xmin, ymin, xmax, ymax, rect_id):
        self.xmin = min(xmin, xmax)
        self.xmax = max(xmin, xmax)
        self.ymin = min(ymin, ymax)
        self.ymax = max(ymin, ymax)
        self.id = rect_id
    def bbox(self): return (self.xmin, self.ymin, self.xmax, self.ymax)
    def is_point_inside(self, p, eps=1e-12):
        return (self.xmin - eps <= p.x <= self.xmax + eps and
                self.ymin - eps <= p.y <= self.ymax + eps)
    def get_edges(self):
        return [
            (Point(self.xmin, self.ymin), Point(self.xmax, self.ymin)),  # bottom
            (Point(self.xmin, self.ymax), Point(self.xmax, self.ymax)),  # top
            (Point(self.xmin, self.ymin), Point(self.xmin, self.ymax)),  # left
            (Point(self.xmax, self.ymin), Point(self.xmax, self.ymax)),  # right
        ]

# ---------- Robust segment/segment intersection ----------

EPS = 1e-12

def line_intersection_param(p, q, a, b):
    rx, ry = (q.x - p.x), (q.y - p.y)
    sx, sy = (b.x - a.x), (b.y - a.y)

    rxs = rx * sy - ry * sx
    apx, apy = (a.x - p.x), (a.y - p.y)
    apxs = apx * sy - apy * sx
    apxr = apx * ry - apy * rx

    if abs(rxs) <= EPS:
        if abs(apxr) > EPS:
            return (None, None)  # parallel, non-collinear
        # collinear: project endpoints; pick earliest t
        ts = []
        use_x = abs(rx) >= abs(ry)
        for w in (a, b):
            if use_x:
                if abs(rx) <= EPS: 
                    continue
                t = (w.x - p.x) / rx
            else:
                if abs(ry) <= EPS:
                    continue
                t = (w.y - p.y) / ry
            if -EPS <= t <= 1 + EPS:
                ts.append((max(0.0, min(1.0, t)), Point(w.x, w.y)))
        if not ts:
            return (None, None)
        ts.sort(key=lambda z: z[0])
        return ts[0]
    else:
        t = apxs / rxs
        u = apxr / rxs
        if -EPS <= t <= 1 + EPS and -EPS <= u <= 1 + EPS:
            ix = p.x + t * rx
            iy = p.y + t * ry
            return (max(0.0, min(1.0, t)), Point(ix, iy))
        return (None, None)

def first_hit_with_rect(seg_a, seg_b, rect):
    if rect.is_point_inside(seg_a):
        return (0.0, Point(seg_a.x, seg_a.y))
    t_best, pt_best = None, None
    for e0, e1 in rect.get_edges():
        t, pt = line_intersection_param(seg_a, seg_b, e0, e1)
        if t is not None and (t_best is None or t < t_best):
            t_best, pt_best = t, pt
    return (t_best, pt_best)

# ---------- R-tree build & query ----------

def build_rect_index_from_array_of_arrays(rect_specs):
    """
    rect_specs: list of [xmin, ymin, xmax, ymax, (optional) id]
    If id is omitted, use 1-based index.
    """
    rects = []
    for i, arr in enumerate(rect_specs, start=1):
        if not (len(arr) == 4 or len(arr) == 5):
            raise ValueError(f"Each rectangle must have 4 or 5 elements, got {arr}")
        xmin, ymin, xmax, ymax = arr[:4]
        rect_id = arr[4] if len(arr) == 5 else i
        rects.append(Rectangle(xmin, ymin, xmax, ymax, rect_id))

    def gen():
        for idx, r in enumerate(rects):
            yield (idx, r.bbox(), r)
    idx = index.Index(gen())
    return idx, rects

def segment_bbox(a, b):
    return (min(a.x, b.x), min(a.y, b.y), max(a.x, b.x), max(a.y, b.y))

def path_collisions_with_rects(rect_index, stored_rects, line_coords):
    """
    line_coords: list of [lon, lat] coordinates (LineString).
    Returns list of collision dicts.
    """
    hits = []
    for i in range(len(line_coords) - 1):
        a = Point(*line_coords[i])
        b = Point(*line_coords[i+1])
        qbb = segment_bbox(a, b)
        candidates = list(rect_index.intersection(qbb))
        if not candidates: 
            continue
        best_t_for_seg, best_hit = None, None
        for ridx in candidates:
            rect = stored_rects[ridx]
            t, pt = first_hit_with_rect(a, b, rect)
            if t is not None and (best_t_for_seg is None or t < best_t_for_seg):
                best_t_for_seg = t
                best_hit = {'rect_id': rect.id, 'segment_index': i, 'hit_point': pt, 't': t}
        if best_hit:
            hits.append(best_hit)
    return hits

def path_or_multiline_collisions(rect_index, stored_rects, geojson_geom):
    typ = geojson_geom.get("type")
    if typ == "LineString":
        return path_collisions_with_rects(rect_index, stored_rects, geojson_geom["coordinates"])
    elif typ == "MultiLineString":
        all_hits = []
        for part in geojson_geom["coordinates"]:
            all_hits.extend(path_collisions_with_rects(rect_index, stored_rects, part))
        return all_hits
    else:
        raise ValueError("Only LineString or MultiLineString are supported.")

# ---------- Example ----------


#map part



BASE = "https://api.tomtom.com/maps/orbis/routing/calculateRoute"

def parse_latlon(s: str):
    try:
        lat, lon = s.split(",")
        return float(lat.strip()), float(lon.strip())
    except Exception:
        raise argparse.ArgumentTypeError(f"Use 'lat,lon' like 23.777176,90.399452")

def to_geojson_from_points(points: List[Dict[str, float]], props: Dict[str, Any]) -> Dict[str, Any]:
    coords = [[p["longitude"], p["latitude"]] for p in points]  # GeoJSON is [lng,lat]
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": props,
            "geometry": {"type": "LineString", "coordinates": coords}
        }]
    }

def normalize_rect(p1_lon, p1_lat, p2_lon, p2_lat):
    """Return [minLon, minLat, maxLon, maxLat] from any two points."""
    minLon, maxLon = sorted([float(p1_lon), float(p2_lon)])
    minLat, maxLat = sorted([float(p1_lat), float(p2_lat)])
    # basic sanity
    assert -180 <= minLon <= 180 and -180 <= maxLon <= 180
    assert -90 <= minLat <= 90 and -90 <= maxLat <= 90
    return [minLon, minLat, maxLon, maxLat]

def rect_corners(minLon, minLat, maxLon, maxLat):
    """Return corners in lon/lat as dicts."""
    SW = {"longitude": minLon, "latitude": minLat}
    SE = {"longitude": maxLon, "latitude": minLat}  # <-- south-east
    NE = {"longitude": maxLon, "latitude": maxLat}
    NW = {"longitude": minLon, "latitude": maxLat}
    return SW, SE, NE, NW


def meters_per_deg_lon(lat_deg: float) -> float:
    return 111_320.0 * math.cos(math.radians(lat_deg))

def meters_per_deg_lat() -> float:
    return 111_320.0

def _rect_center(rect):  # [minLon, minLat, maxLon, maxLat]
    minLon, minLat, maxLon, maxLat = rect
    return ((minLon + maxLon) / 2.0, (minLat + maxLat) / 2.0)

def _rect_dims_m(rect):
    minLon, minLat, maxLon, maxLat = rect
    _, lat = _rect_center(rect)
    w_m = (maxLon - minLon) * meters_per_deg_lon(lat)
    h_m = (maxLat - minLat) * meters_per_deg_lat()
    return w_m, h_m

def _inflate_axis_m(rect, add_w_m: float, add_h_m: float):
    """Inflate by given meters on each side (symmetrically)."""
    minLon, minLat, maxLon, maxLat = rect
    _, lat = _rect_center(rect)
    dlon = add_w_m / meters_per_deg_lon(lat)
    dlat = add_h_m / meters_per_deg_lat()
    return [minLon - dlon, minLat - dlat, maxLon + dlon, maxLat + dlat]

def _ensure_min_dims(rect, min_w_m: float, min_h_m: float):
    """Ensure width/height >= mins (meters) by symmetric inflation."""
    w, h = _rect_dims_m(rect)
    add_w_each = max(0.0, (min_w_m - w) / 2.0)
    add_h_each = max(0.0, (min_h_m - h) / 2.0)
    return _inflate_axis_m(rect, add_w_each, add_h_each)

def _clamp_lat_bounds(rect, lat_min=-80.0, lat_max=80.0):
    """Keep within Orbis latitude limits."""
    minLon, minLat, maxLon, maxLat = rect
    _, cy = _rect_center(rect)
    half_h = (maxLat - minLat) / 2.0
    cy = max(lat_min + half_h, min(lat_max - half_h, cy))
    return [minLon, cy - half_h, maxLon, cy + half_h]

def scale_rect_reasonably(
    rect, *, min_w_m=120.0, min_h_m=120.0, safety_pad_m=60.0
):
    """
    Make rect 'just-big-enough':
      - ensure min width/height (meters)
      - add small safety pad (meters) on each side
      - clamp latitude bounds
    rect: [minLon, minLat, maxLon, maxLat]
    """
    r = _ensure_min_dims(rect, min_w_m, min_h_m)
    r = _inflate_axis_m(r, safety_pad_m, safety_pad_m)
    r = _clamp_lat_bounds(r)
    return r

def build_avoid_rectangles(rects_ll):
    """
    rects_ll: list of [minLon, minLat, maxLon, maxLat]
    Orbis needs SW and NE, but we can also compute SE/NW for validation.
    """
    rectangles = []
    for minLon, minLat, maxLon, maxLat in rects_ll:
        assert minLon < maxLon and minLat < maxLat, "SW must be < NE"
        SW, SE, NE, NW = rect_corners(minLon, minLat, maxLon, maxLat)

        # optional: verify SE is truly south-east of SW
        assert SE["latitude"] < NW["latitude"] and SE["longitude"] > SW["longitude"]

        rectangles.append({
            "southWestCorner": {"latitude": SW["latitude"], "longitude": SW["longitude"]},
            "northEastCorner": {"latitude": NE["latitude"], "longitude": NE["longitude"]},
        })
    return {"avoidAreas": {"rectangles": rectangles}} if rectangles else {}


def request_route(
    api_key: str,
    orig: str,
    dest: str,
    avoid_body: Optional[dict] = None,
    depart: str = "now",
    route_type: str = "fastest",   # classic naming; we’ll map to Orbis
    traffic: bool = True           # True->"live", False->"historical"
) -> Dict[str, Any]:
    url = f"{BASE}/{orig}:{dest}/json"

    # map classic -> Orbis
    route_type_map = {
        "fastest": "fast",
        "shortest": "short",
        "eco": "efficient",
        "efficient": "efficient",
        "thrilling": "thrilling"
    }
    orbis_route_type = route_type_map.get(route_type.lower(), "fast")
    orbis_traffic = "live" if traffic else "historical"

    params = {
        "key": api_key,
        "apiVersion": 2,
        "routeType": orbis_route_type,
        "traffic": orbis_traffic,
        "departAt": depart
    }

    if avoid_body:
        r = requests.post(url, params=params, json=avoid_body, timeout=30)
    else:
        r = requests.get(url, params=params, timeout=30)

    if r.status_code != 200:
        try:
            err = r.json()
        except Exception:
            err = r.text
        raise RuntimeError(f"TomTom error {r.status_code}: {err}")
    return r.json()


def merger(places_to_avoid):
    # setting necessary variables
    api_key = os.getenv("TOMTOM_API_KEY")
    if not api_key:
        print("ERROR: set TOMTOM_API_KEY environment variable.", file=sys.stderr)
        sys.exit(2)

    # TomTom wants lat,lon (NOT lon,lat)
    orig_str = "23.7767759,90.3996056"   # Dhaka area: lat,lon
    dest_str = "23.8104016,90.4125185"   # lat,lon

    avoid_body = None
    if places_to_avoid:
        # Make sure build_avoid_rectangles builds polygons with [lon,lat] pairs,
        # but the spec array you pass in should be [minLon, minLat, maxLon, maxLat]
        avoid_body = build_avoid_rectangles(places_to_avoid)

    try:
        if avoid_body:
            data = request_route(
                api_key=api_key,
                orig=orig_str,
                dest=dest_str,
                avoid_body=avoid_body,
                depart="now",
                route_type="fastest",
                traffic=True
            )
        else:
            data = request_route(
                api_key=api_key,
                orig=orig_str,
                dest=dest_str,
                depart="now",
                route_type="fastest",
                traffic=True
            )

        route = data["routes"][0]
        summary = route["summary"]
        km = summary["lengthInMeters"] / 1000.0
        mins = summary["travelTimeInSeconds"] / 60.0
        print(f"Route ≈ {km:.2f} km, {mins:.1f} min (traffic-aware)")

        # Extract polyline points from the first leg
        points = route["legs"][0]["points"]  # [{'latitude':..,'longitude':..}, ...]
        #json file
        gj = to_geojson_from_points(points, props=summary)

        geometry = gj["features"][0]["geometry"]
        with open("route.geojson", "w", encoding="utf-8") as f:
            json.dump(gj, f, ensure_ascii=False, indent=2)
        print("Saved route to route.geojson")

        return geometry  # <-- return so caller can use it
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # rectangle spec must be [minLon, minLat, maxLon, maxLat]
    rect_specs = [
        [1,1,1,1],
        [90.399345,23.791977, 90.401485,23.793821],
        #[ 90.406921, 23.791024, 90.410397 ,23.789537]
        #[90.401165, 23.800938, 90.402385, 23.801392]
        
    ]
   # rect_specs = [[90.4010, 23.8007, 90.4035, 23.8023]]
    for i in range(len(rect_specs)):
        scaled = scale_rect_reasonably(rect_specs[i], min_w_m=120, min_h_m=120, safety_pad_m=60)
        rect_specs[i] = scaled
    print(rect_specs)
    idx, rects = build_rect_index_from_array_of_arrays(rect_specs)

    places_to_avoid = None
    while True:
        path_geometry = merger(places_to_avoid)   # now returns geometry
        #print(path_geometry)
        # break  # remove this if you want to iterate until no collisions
        #break;
        collisions = path_or_multiline_collisions(idx, rects, path_geometry)
        if not collisions:
            print("✅ Path does NOT collide with any avoid-rectangle.")
            break
        else:
            print(f"⚠️  Path collides with {len(collisions)} rectangle(s):")
            for h in collisions:
                print(f"  - Rect ID {h['rect_id']} at segment {h['segment_index']} "
                      f"near {h['hit_point']} (t={h['t']:.3f})")
                if places_to_avoid is None:
                    places_to_avoid = []
                places_to_avoid.append(rect_specs[h['rect_id'] - 1])

        if places_to_avoid and len(places_to_avoid) > 10:
            break
