const GeoMap = {
  map: null,
  geoLayer: null,
  allFeatures: [],
  partyColors: {
    'TVK': '#FF6B35',
    'DMK': '#DC2626',
    'AIADMK': '#15803D',
    'INC': '#2563EB',
    'BJP': '#EA580C',
    'PMK': '#92400E',
    'VCK': '#4C1D95',
    'CPI': '#B91C1C',
    'CPI(M)': '#991B1B',
    'IUML': '#065F46',
    'DMDK': '#6B7280',
    'AMMK': '#6B7280',
    'NTK': '#6B7280',
  },
  defaultColor: '#888888',

  async init() {
    const container = document.getElementById('map');
    if (!container) return;

    try {
      const resp = await fetch('data/tn_constituencies.geojson');
      const geojson = await resp.json();
      this.allFeatures = geojson.features;

      this.map = L.map('map', {
        center: [10.8, 78.7],
        zoom: 7,
        zoomControl: true,
        attributionControl: false,
      });

      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 12,
        minZoom: 6,
      }).addTo(this.map);

      this.renderLayer();
      this.addLegend();
      this.setupRegionFilter();
      this.setupDashboardSync();

      window.addEventListener('resize', () => {
        if (this.map) this.map.invalidateSize();
      });
    } catch (err) {
      console.error('GeoMap init failed:', err);
      container.innerHTML = '<p style="padding:40px;text-align:center;color:#999;">Map data could not be loaded.</p>';
    }
  },

  getColor(party) {
    return this.partyColors[party] || this.defaultColor;
  },

  renderLayer(filterRegion) {
    if (this.geoLayer) {
      this.map.removeLayer(this.geoLayer);
    }

    let features = this.allFeatures;
    if (filterRegion) {
      features = features.filter(f => f.properties.region === filterRegion);
    }

    this.geoLayer = L.geoJSON({ type: 'FeatureCollection', features }, {
      style: (feature) => ({
        fillColor: this.getColor(feature.properties.party_2026),
        weight: 0.6,
        opacity: 0.8,
        color: '#ffffff',
        fillOpacity: 0.75,
      }),
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const party = p.party_2026;
        const color = this.getColor(party);
        layer.bindPopup(`
          <div style="font-family:'Hanken Grotesk',sans-serif;min-width:200px;">
            <strong style="font-size:16px;">${p.constituency}</strong>
            <div style="font-size:12px;color:#666;margin:4px 0;">AC ${p.ac_no} &middot; ${p.region}</div>
            <div style="margin:8px 0;">
              <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-right:6px;"></span>
              <strong>${party}</strong> — ${p.winner_2026}
            </div>
            <table style="font-size:12px;width:100%;border-collapse:collapse;">
              <tr><td style="padding:2px 0;color:#666;">Vote share</td><td style="text-align:right;font-weight:600;">${p.vote_share_2026}%</td></tr>
              <tr><td style="padding:2px 0;color:#666;">Margin</td><td style="text-align:right;font-weight:600;">${p.margin_pct}%</td></tr>
              <tr><td style="padding:2px 0;color:#666;">2021 winner</td><td style="text-align:right;">${p.winner_2021 || 'N/A'} (${p.party_2021})</td></tr>
              <tr><td style="padding:2px 0;color:#666;">Flipped</td><td style="text-align:right;font-weight:600;color:${p.flipped ? '#FF6B35' : '#15803D'};">${p.flipped ? 'Yes' : 'Hold'}</td></tr>
            </table>
          </div>
        `);
        layer.on('mouseover', () => {
          layer.setStyle({ weight: 2, color: '#333', fillOpacity: 0.9 });
          layer.bringToFront();
        });
        layer.on('mouseout', () => {
          layer.setStyle({ weight: 0.6, color: '#ffffff', fillOpacity: 0.75 });
        });
      }
    }).addTo(this.map);

    if (!filterRegion) {
      this.map.fitBounds(this.geoLayer.getBounds(), { padding: [20, 20] });
    } else {
      this.map.fitBounds(this.geoLayer.getBounds(), { padding: [20, 20] });
    }
  },

  addLegend() {
    const legend = L.control({ position: 'bottomleft' });
    const counted = {};
    this.allFeatures.forEach(f => {
      const p = f.properties.party_2026;
      counted[p] = (counted[p] || 0) + 1;
    });

    legend.onAdd = () => {
      const div = L.DomUtil.create('div', 'map-legend');
      div.style.cssText = 'background:rgba(255,255,255,0.95);padding:12px 16px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.15);font-family:"Hanken Grotesk",sans-serif;font-size:12px;max-height:260px;overflow-y:auto;';
      div.innerHTML = '<strong style="display:block;margin-bottom:6px;font-size:13px;">2026 Winner</strong>';
      const order = ['TVK','DMK','AIADMK','INC','BJP','PMK','VCK','CPI','CPI(M)','IUML','DMDK','AMMK'];
      order.forEach(p => {
        if (counted[p]) {
          div.innerHTML += `<div style="display:flex;align-items:center;gap:6px;padding:2px 0;">
            <span style="display:inline-block;width:12px;height:12px;border-radius:2px;background:${this.getColor(p)};flex-shrink:0;"></span>
            <span>${p}</span>
            <span style="margin-left:auto;color:#999;">${counted[p]}</span>
          </div>`;
        }
      });
      return div;
    };
    legend.addTo(this.map);
  },

  setupRegionFilter() {
    const sel = document.querySelector('[data-map-region]');
    if (!sel) return;

    // Populate with regions
    const regions = [...new Set(this.allFeatures.map(f => f.properties.region))];
    regions.sort();
    regions.forEach(r => {
      const opt = document.createElement('option');
      opt.value = r;
      opt.textContent = r;
      sel.appendChild(opt);
    });

    sel.addEventListener('change', (e) => {
      this.renderLayer(e.target.value || null);
    });
  },

  setupDashboardSync() {
    const regionSelect = document.querySelector('[data-region-select]');
    const mapRegionSelect = document.querySelector('[data-map-region]');
    if (regionSelect && mapRegionSelect) {
      regionSelect.addEventListener('change', (e) => {
        if (e.target.value && mapRegionSelect.value !== e.target.value) {
          mapRegionSelect.value = e.target.value;
          this.renderLayer(e.target.value);
        }
      });
    }
  },
};
