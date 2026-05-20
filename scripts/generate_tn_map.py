import json, os
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Approximate regional polygons within Tamil Nadu bounds
# TN bounds roughly: 8.0-13.5 N, 76.5-80.5 E
regions_geo = {
    'Chennai Metro': Polygon([
        [79.85, 12.60], [80.35, 12.60], [80.35, 13.30],
        [79.85, 13.30], [79.85, 12.60]
    ]),
    'North': Polygon([
        [78.50, 11.80], [80.00, 11.80], [80.00, 13.30],
        [79.85, 13.30], [79.85, 12.60], [79.30, 12.30],
        [78.50, 12.10], [78.50, 11.80]
    ]),
    'Central': Polygon([
        [78.00, 10.40], [79.30, 10.40], [79.30, 11.80],
        [78.50, 11.80], [78.50, 12.10], [78.00, 11.80],
        [78.00, 10.40]
    ]),
    'Kongu': Polygon([
        [76.50, 10.00], [77.80, 10.00], [78.00, 10.40],
        [78.00, 11.80], [77.50, 11.60], [76.50, 11.20],
        [76.50, 10.00]
    ]),
    'Delta': Polygon([
        [79.30, 10.40], [80.00, 10.40], [80.00, 11.80],
        [79.30, 11.80], [79.30, 10.40]
    ]),
    'South': Polygon([
        [77.00, 8.00], [78.50, 8.00], [79.50, 8.50],
        [79.50, 10.00], [78.00, 10.00], [77.00, 9.50],
        [77.00, 8.00]
    ])
}

region_colors = {
    'Chennai Metro': '#FF6B35',
    'North': '#FF1493',
    'Central': '#594139',
    'Kongu': '#ab3500',
    'Delta': '#666666',
    'South': '#999999'
}

region_seats = {}
with open('data/seats_by_region.json') as f:
    sbr = json.load(f)
for r in sbr['regions']:
    region_seats[r['name']] = r

fig, ax = plt.subplots(1, 1, figsize=(14, 11))
fig.patch.set_facecolor('white')
ax.set_facecolor('#fafaf5')

region_order = ['Chennai Metro', 'North', 'Central', 'Kongu', 'Delta', 'South']

for reg in region_order:
    poly = regions_geo[reg]
    color = region_colors[reg]

    if poly.geom_type == 'Polygon':
        xs, ys = poly.exterior.xy
        ax.fill(xs, ys, color=color, alpha=0.6, ec='white', linewidth=2.5, zorder=2)
        ax.plot(xs, ys, color='white', linewidth=2.5, zorder=3)

    centroid = poly.centroid
    seats = region_seats.get(reg)
    if seats:
        total = seats['dmk'] + seats['tvk'] + seats['aiadmk'] + seats['pmk'] + seats['vck']
        lines = [
            f'{reg.upper()}',
            f'{total} Seats',
            f'TVK {seats["tvk"]}  DMK {seats["dmk"]}  AIADMK {seats["aiadmk"]}'
        ]
    else:
        lines = [reg]
    label = '\n'.join(lines)
    ax.text(centroid.x, centroid.y, label,
            fontsize=10, fontweight='bold', color='white',
            ha='center', va='center',
            path_effects=[withStroke(linewidth=2.5, foreground=(0, 0, 0, 0.5))],
            zorder=5,
            linespacing=1.4)

# Title
ax.set_title('Tamil Nadu — Regional Seat Distribution 2026',
             fontsize=18, fontweight='bold', color='#333333', pad=20,
             fontfamily='sans-serif')

# Legend
legend_elements = []
party_colors = {'DMK': '#ab3500', 'TVK': '#FF6B35', 'AIADMK': '#594139', 'PMK': '#FF1493', 'VCK': '#999'}
for party, clr in party_colors.items():
    legend_elements.append(plt.Line2D([0], [0], marker='s', color='w',
                                       markerfacecolor=clr, markersize=10, label=party))
ax.legend(handles=legend_elements, loc='lower left', framealpha=0.9,
          edgecolor='#ddd', fontsize=11, title='Parties',
          title_fontsize=11, ncol=5)

ax.set_aspect('equal')
ax.axis('off')
ax.set_xlim(76.0, 80.8)
ax.set_ylim(7.5, 13.6)

os.makedirs('images', exist_ok=True)
plt.savefig('images/tn_map.png', dpi=150, bbox_inches='tight', facecolor='white')
print('tn_map.png generated')
