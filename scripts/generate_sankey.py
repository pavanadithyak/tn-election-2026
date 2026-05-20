import json
import plotly.graph_objects as go
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open('data/flip_flows.json') as f:
    data = json.load(f)

flows = data['flows']

# Filter to top 5 flows (seats >= 6)
top_flows = [f for f in flows if f['seats'] >= 6]
top_flows.sort(key=lambda x: x['seats'], reverse=True)
top_flows = top_flows[:5]

# Collect unique nodes from top flows only
nodes = set()
for f in top_flows:
    nodes.add(f['source'])
    nodes.add(f['target'])
all_nodes = list(nodes)

node_colors_map = {
    'TVK': '#FF6B35',
    'DMK': '#ab3500',
    'AIADMK': '#594139',
    'PMK': '#FF1493'
}
node_colors = [node_colors_map.get(n, '#999') for n in all_nodes]

# Per-flow colors
flow_colors = {
    ('DMK', 'TVK'): 'rgba(255,107,53,0.7)',
    ('AIADMK', 'TVK'): 'rgba(255,20,147,0.7)',
    ('DMK', 'AIADMK'): 'rgba(139,69,19,0.6)',
    ('AIADMK', 'DMK'): 'rgba(153,153,153,0.6)',
    ('PMK', 'PMK'): 'rgba(123,104,238,0.6)'
}

fig = go.Figure(data=[go.Sankey(
    arrangement='fixed',
    node=dict(
        pad=25,
        thickness=28,
        line=dict(color='rgba(0,0,0,0.15)', width=1.5),
        label=all_nodes,
        color=node_colors,
        hovertemplate='%{label}<extra></extra>'
    ),
    link=dict(
        source=[all_nodes.index(f['source']) for f in top_flows],
        target=[all_nodes.index(f['target']) for f in top_flows],
        value=[f['seats'] for f in top_flows],
        label=[f'{f["source"]} → {f["target"]}: {f["seats"]} seats' for f in top_flows],
        color=[flow_colors.get((f['source'], f['target']), 'rgba(0,0,0,0.2)') for f in top_flows],
        hovertemplate='%{label}<extra></extra>'
    )
)])

fig.update_layout(
    title=dict(
        text='Top 5 Seat Transitions — 2021 → 2026',
        font=dict(size=18, family='Arial, sans-serif', color='#333333'),
        x=0.5
    ),
    font=dict(family='Arial, sans-serif', size=13, color='#333333'),
    width=1100,
    height=500,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=40, r=40, t=60, b=30)
)

os.makedirs('images', exist_ok=True)
fig.write_image('images/sankey.png', scale=2)
print('sankey.png regenerated with top 5 flows only')
