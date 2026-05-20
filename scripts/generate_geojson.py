import json, os, random
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

random.seed(42)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load constituency results for seat counts per region and ac_no/name mapping
with open('data/constituency_results.json') as f:
    data = json.load(f)

constituencies = data['constituencies']

# Count seats per region
region_seats = {}
for c in constituencies:
    r = c['region']
    if r not in region_seats:
        region_seats[r] = []
    region_seats[r].append(c)

print("Seats per region:")
for r, seats in sorted(region_seats.items()):
    print(f"  {r}: {len(seats)}")

# Regional bounding boxes (from generate_tn_map.py, adjusted)
region_bounds = {
    'Chennai Metro': {'lat': [12.60, 13.30], 'lng': [79.85, 80.35]},
    'North': {'lat': [11.80, 13.30], 'lng': [78.50, 80.00]},
    'Central': {'lat': [10.40, 11.80], 'lng': [78.00, 79.30]},
    'Kongu': {'lat': [10.00, 11.80], 'lng': [76.50, 78.00]},
    'Delta': {'lat': [10.40, 11.80], 'lng': [79.30, 80.00]},
    'South': {'lat': [8.00, 10.40], 'lng': [77.00, 79.50]},
}

# For each region, create a grid of cells and assign them to constituencies
# Use approximate subdivision

features = []
for region_name, seats in sorted(region_seats.items()):
    bounds = region_bounds[region_name]
    n_seats = len(seats)

    lat_min, lat_max = bounds['lat']
    lng_min, lng_max = bounds['lng']
    lat_range = lat_max - lat_min
    lng_range = lng_max - lng_min

    # Determine grid dimensions based on region shape
    # Aim for roughly square cells
    aspect = lng_range / lat_range if lat_range > 0 else 1
    # Try to find integer cols/rows near sqrt(n_seats * aspect)
    best_cols = 1
    best_rows = n_seats
    best_diff = float('inf')
    for cols in range(1, n_seats + 1):
        rows = (n_seats + cols - 1) // cols
        cell_aspect = (lng_range / cols) / (lat_range / rows) if rows > 0 and lat_range > 0 else 0
        diff = abs(cell_aspect - 1.0)
        if diff < best_diff and rows * cols >= n_seats:
            best_diff = diff
            best_cols = cols
            best_rows = rows

    cols = best_cols
    rows = best_rows

    # Create a list of grid cells
    cell_w = lng_range / cols
    cell_h = lat_range / rows

    cells = []
    for row in range(rows):
        for col in range(cols):
            if len(cells) >= n_seats:
                break
            lng0 = lng_min + col * cell_w
            lng1 = lng0 + cell_w
            lat0 = lat_min + row * cell_h
            lat1 = lat0 + cell_h

            # Add slight random jitter for organic look
            jitter = 0.03
            lng0 += random.uniform(-jitter, jitter)
            lng1 += random.uniform(-jitter, jitter)
            lat0 += random.uniform(-jitter, jitter)
            lat1 += random.uniform(-jitter, jitter)

            # Subdivide each cell into 2 triangles for more polygon-like appearance
            # Actually, keep as rectangles with slight corner jitter
            corners = [
                [lng0 + random.uniform(-jitter*0.3, jitter*0.3), lat0 + random.uniform(-jitter*0.3, jitter*0.3)],
                [lng1 + random.uniform(-jitter*0.3, jitter*0.3), lat0 + random.uniform(-jitter*0.3, jitter*0.3)],
                [lng1 + random.uniform(-jitter*0.3, jitter*0.3), lat1 + random.uniform(-jitter*0.3, jitter*0.3)],
                [lng0 + random.uniform(-jitter*0.3, jitter*0.3), lat1 + random.uniform(-jitter*0.3, jitter*0.3)],
            ]
            cells.append(corners)

    # Assign cells to seats (sort seats by ac_no)
    seats_sorted = sorted(seats, key=lambda x: x['ac_no'])
    for i, seat in enumerate(seats_sorted):
        if i < len(cells):
            poly_coords = cells[i]
            feature = {
                'type': 'Feature',
                'properties': {
                    'ac_no': seat['ac_no'],
                    'constituency': seat['constituency'],
                    'region': seat['region'],
                    'party_2026': seat['party_2026'],
                    'party_2021': seat['party_2021'],
                    'winner_2026': seat['winner_2026'],
                    'winner_2021': seat['winner_2021'],
                    'flipped': seat['flipped'],
                    'flip_from': seat['flip_from'],
                    'flip_to': seat['flip_to'],
                    'margin_pct': seat['margin_pct'],
                    'vote_share_2026': seat['vote_share_2026'],
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [poly_coords + [poly_coords[0]]]
                }
            }
            features.append(feature)

    if len(cells) < n_seats:
        print(f"WARNING: {region_name} has {n_seats} seats but only {len(cells)} cells generated")

geojson = {
    'type': 'FeatureCollection',
    'features': features
}

os.makedirs('data', exist_ok=True)
with open('data/tn_constituencies.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False)

print(f"\nGenerated {len(features)} constituency polygons")
print(f"GeoJSON written to data/tn_constituencies.geojson")

# Validate all 233 are present
missing = []
for c in constituencies:
    found = any(f['properties']['ac_no'] == c['ac_no'] for f in features)
    if not found:
        missing.append(c['constituency'])
if missing:
    print(f"WARNING: {len(missing)} constituencies missing from GeoJSON: {missing[:5]}...")
else:
    print("All 233 constituencies accounted for!")
