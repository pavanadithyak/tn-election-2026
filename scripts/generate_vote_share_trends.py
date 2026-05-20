import json, os
import matplotlib.pyplot as plt
import numpy as np

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open('data/vote_share_comparison.json') as f:
    data = json.load(f)

major = ['TVK', 'DMK', 'AIADMK', 'PMK', 'VCK']
colors = {'TVK': '#FF6B35', 'DMK': '#ab3500', 'AIADMK': '#594139', 'PMK': '#FF1493', 'VCK': '#999999'}
linewidths = {'TVK': 4, 'DMK': 2.5, 'AIADMK': 2.5, 'PMK': 1.5, 'VCK': 1.5}

fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor('white')
ax.set_facecolor('#fafaf5')

for party in major:
    row = next(p for p in data['parties'] if p['party'] == party)
    vals = [row['vs_2021'], row['vs_2026']]
    lw = linewidths.get(party, 2)
    alpha = 1.0 if party == 'TVK' else 0.6
    ax.plot([2021, 2026], vals, marker='o', linewidth=lw, markersize=10,
            label=party, color=colors[party], alpha=alpha, zorder=5 if party == 'TVK' else 1)

    if party == 'TVK':
        ax.annotate(f'TVK\n{row["vs_2026"]:.1f}%',
                    xy=(2026, row['vs_2026']),
                    xytext=(2026.3, row['vs_2026'] + 2),
                    fontsize=13, fontweight='bold', color=colors[party],
                    arrowprops=dict(arrowstyle='->', color=colors[party], lw=1.5))
    elif party in ('DMK', 'AIADMK'):
        ax.annotate(f'{row["vs_2026"]:.1f}%',
                    xy=(2026, row['vs_2026']),
                    xytext=(2026.1, row['vs_2026'] - 1.5),
                    fontsize=10, fontweight='bold', color=colors[party], alpha=0.7)

ax.set_title('The TVK Emergence: 0% → 34.9% in One Cycle', fontsize=20, fontweight='bold', pad=20, color='#333')
ax.set_xlabel('Election Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Vote Share (%)', fontsize=14, fontweight='bold')
ax.set_xticks([2021, 2026])
ax.set_xticklabels(['2021', '2026'], fontsize=13)
ax.set_xlim(2020.5, 2026.8)
ax.set_ylim(-2, 42)
ax.legend(fontsize=11, loc='upper left', framealpha=0.9, edgecolor='#ddd')
ax.grid(alpha=0.2, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
os.makedirs('images', exist_ok=True)
plt.savefig('images/vote_share_trends.png', dpi=150, bbox_inches='tight', facecolor='white')
print('vote_share_trends.png generated')
