import json
import plotly.graph_objects as go
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open('data/flip_flows.json') as f:
    data = json.load(f)

flows = data['flows']

all_nodes = []
node_map = {}
for flow in flows:
    for key in ('source', 'target'):
        if key not in node_map:
            idx = len(all_nodes)
            node_map[key] = idx
            all_nodes.append(key)

# Re-index
node_set = set()
for f in flows:
    node_set.add(f['source'])
    node_set.add(f['target'])
all_nodes = list(node_set)

colors = {
    'TVK': '#FF6B35',
    'DMK': '#ab3500',
    'AIADMK': '#594139',
    'PMK': '#FF1493',
    'VCK': '#999999',
    'NTK': '#666666',
    'INC': '#dddddd',
    'BJP': '#333333'
}

node_colors = [colors.get(n, '#ccc') for n in all_nodes]

fig = go.Figure(data=[go.Sankey(
    arrangement='fixed',
    node=dict(
        pad=20,
        thickness=24,
        line=dict(color='rgba(0,0,0,0.1)', width=1),
        label=all_nodes,
        color=node_colors,
        hovertemplate='%{label}<extra></extra>'
    ),
    link=dict(
        source=[all_nodes.index(f['source']) for f in flows],
        target=[all_nodes.index(f['target']) for f in flows],
        value=[f['seats'] for f in flows],
        label=[f'{f["source"]} → {f["target"]}: {f["seats"]} seats' for f in flows],
        color=['rgba(255,107,53,0.3)' if f['target'] == 'TVK'
               else 'rgba(171,53,0,0.3)' if f['target'] == 'DMK'
               else 'rgba(89,65,57,0.3)' if f['target'] == 'AIADMK'
               else 'rgba(255,20,147,0.3)' if f['target'] == 'PMK'
               else 'rgba(0,0,0,0.15)' for f in flows],
        hovertemplate='%{label}<extra></extra>'
    )
)])

fig.update_layout(
    title=dict(
        text='Seat Flow Between Parties — 2021 → 2026',
        font=dict(size=20, family='Arial, sans-serif', color='#333333'),
        x=0.5
    ),
    font=dict(family='Arial, sans-serif', size=12, color='#333333'),
    width=1280,
    height=700,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=40, r=40, t=80, b=40)
)

os.makedirs('images', exist_ok=True)
fig.write_image('images/sankey.png', scale=2)
print('sankey.png generated')
