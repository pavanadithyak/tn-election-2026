const DataManager = {
  async loadData() {
    try {
      const [metadata, flipFlows, seatsByRegion, voteShare] = await Promise.all([
        fetch('data/metadata.json').then(r => r.json()),
        fetch('data/flip_flows.json').then(r => r.json()),
        fetch('data/seats_by_region.json').then(r => r.json()),
        fetch('data/vote_share_comparison.json').then(r => r.json())
      ]);
      return { metadata, flipFlows, seatsByRegion, voteShare };
    } catch (error) {
      console.error('Failed to load data:', error);
      return null;
    }
  },

  injectHero(metadata) {
    const el = document.querySelector('[data-stat="election_year"]');
    if (el) el.textContent = metadata.election_year;
  },

  injectSummaryStats(metadata) {
    const voters = document.querySelector('[data-voters]');
    if (voters) voters.textContent = metadata.total_voters;
    const youth = document.querySelector('[data-youth]');
    if (youth) youth.textContent = metadata.youth_percentage + '%';
    const swing = document.querySelector('[data-swing]');
    if (swing) swing.textContent = metadata.swing_seats;
  },

  injectRegionalData(seatsByRegion) {
    const regionSelect = document.querySelector('[data-region-select]');
    if (!regionSelect) return;

    seatsByRegion.regions.forEach(region => {
      const option = document.createElement('option');
      option.value = region.name;
      option.textContent = region.name;
      regionSelect.appendChild(option);
    });

    const updateRegion = (region) => {
      const seatsEl = document.querySelector('[data-region-seats]');
      if (seatsEl) {
        seatsEl.textContent = `${region.dmk + region.tvk + region.aiadmk + region.pmk + region.vck} total seats`;
      }
      const descEl = document.querySelector('[data-region-description]');
      if (descEl) {
        descEl.textContent = `${region.name}: TVK ${region.tvk}, DMK ${region.dmk}, AIADMK ${region.aiadmk}, PMK ${region.pmk}, VCK ${region.vck}`;
      }
    };

    regionSelect.addEventListener('change', (e) => {
      const selected = seatsByRegion.regions.find(r => r.name === e.target.value);
      if (selected) updateRegion(selected);
    });

    if (seatsByRegion.regions.length > 0) {
      updateRegion(seatsByRegion.regions[0]);
      regionSelect.value = seatsByRegion.regions[0].name;
    }
  },

  injectVoteShare(voteShare) {
    const container = document.querySelector('[data-vote-share-container]');
    if (!container) return;

    const majorParties = voteShare.parties.filter(p => p.vs_2026 > 0);
    majorParties.forEach(party => {
      const row = document.createElement('div');
      row.className = 'vote-share-row';
      row.innerHTML = `
        <span class="party-name">${party.party}</span>
        <div class="vote-share-bars">
          <div class="bar bar-2021" style="width: ${Math.max(party.vs_2021, 2)}%;" title="${party.vs_2021}% (2021)"></div>
          <div class="bar bar-2026" style="width: ${Math.max(party.vs_2026, 2)}%;" title="${party.vs_2026}% (2026)"></div>
        </div>
        <span class="vote-share-pct">${party.vs_2026.toFixed(1)}%</span>
        <span class="seats-count">${party.seats_2026} seats</span>
      `;
      container.appendChild(row);
    });
  },

  injectPriorityIssues(metadata) {
    const container = document.querySelector('[data-priority-issues]');
    if (!container) return;

    metadata.key_issues.forEach(issue => {
      const card = document.createElement('div');
      card.className = 'priority-card';
      card.innerHTML = `
        <div class="issue-percentage">${issue.support}%</div>
        <div class="issue-label">${issue.issue}</div>
      `;
      container.appendChild(card);
    });
  },

  injectSankeyData(flipFlows) {
    const totalFlips = document.querySelector('[data-total-flips]');
    if (totalFlips) totalFlips.textContent = flipFlows.total_flips;
    const flipPct = document.querySelector('[data-flip-percentage]');
    if (flipPct) flipPct.textContent = flipFlows.flip_percentage.toFixed(1) + '%';
    const topFlows = document.querySelector('[data-top-flows]');
    if (topFlows && flipFlows.flows) {
      flipFlows.flows.sort((a, b) => b.seats - a.seats).slice(0, 5).forEach(flow => {
        const item = document.createElement('li');
        item.textContent = `${flow.source} → ${flow.target}: ${flow.seats} seats`;
        topFlows.appendChild(item);
      });
    }
  }
};

document.addEventListener('DOMContentLoaded', async () => {
  const data = await DataManager.loadData();
  if (data) {
    DataManager.injectHero(data.metadata);
    DataManager.injectSummaryStats(data.metadata);
    DataManager.injectRegionalData(data.seatsByRegion);
    DataManager.injectVoteShare(data.voteShare);
    DataManager.injectPriorityIssues(data.metadata);
    DataManager.injectSankeyData(data.flipFlows);
  }
});
