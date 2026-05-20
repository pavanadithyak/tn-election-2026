import json, os
import matplotlib.pyplot as plt
import numpy as np

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open('data/seats_by_region.json') as f:
    data = json.load(f)

regions = [r['name'] for r in data['regions']]
parties = ['TVK', 'DMK', 'AIADMK', 'PMK', 'VCK']
colors = ['#FF6B35', '#ab3500', '#594139', '#FF1493', '#999999']

party_data = {p: [r[p.lower()] for r in data['regions']] for p in parties}

x = np.arange(len(regions))
width = 0.15

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('white')
ax.set_facecolor('#fafaf5')

for i, party in enumerate(parties):
    bars = ax.bar(x + i * width, party_data[party], width,
                  label=party, color=colors[i], edgecolor='white', linewidth=0.5)
    for bar in bars:
        val = bar.get_height()
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    str(val), ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Region', fontsize=14, fontweight='bold')
ax.set_ylabel('Seats Won', fontsize=14, fontweight='bold')
ax.set_title('TVK Won Seats in All 6 Regions', fontsize=20, fontweight='bold', pad=20, color='#333')
ax.set_xticks(x + width * 2)
ax.set_xticklabels(regions, fontsize=12, rotation=0)
ax.legend(fontsize=12, loc='upper right', framealpha=0.9, edgecolor='#ddd')
ax.grid(axis='y', alpha=0.2, linestyle='--')
ax.set_axisbelow(True)
ax.set_ylim(0, max(max(v) for v in party_data.values()) + 5)

plt.tight_layout()
os.makedirs('images', exist_ok=True)
plt.savefig('images/regional_bars.png', dpi=150, bbox_inches='tight', facecolor='white')
print('regional_bars.png generated')
