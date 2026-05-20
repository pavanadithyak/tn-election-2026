import csv, json, os, re
from collections import defaultdict, Counter

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Name mapping: 2021 spelling -> 2026 spelling
NAME_MAP = {
    'Sendamangalam': 'Senthamangalam',
    'Gummidipundi': 'Gummidipoondi',
    'Sholinghur': 'Sholingur',
    'Edapadi': 'Edappadi',
    'Modakurichi': 'Modakkurichi',
    'Coimbatore South': 'Coimbatore (South)',
    'Maduranthakam': 'Madurantakam',
    'Pappireddippatti': 'Pappireddipatti',
    'Mettupalayam': 'Mettuppalayam',
    'Thiruvidamarudur': 'Thiruvidaimarudur',
    'Arakonam': 'Arakkonam',
    'Palayamcottai': 'Palayamkottai',
    'Colachel': 'Colachal',
    'Tiruchirapalli (East)': 'Tiruchirappalli (East)',
    'Rishivandiam': 'Rishivandiyam',
    'Tiruchengode': 'Tiruchengodu',
    'Palacode': 'Palacodu',
    'Nilakottai': 'Nilakkottai',
    'Gudiyatham': 'Gudiyattam',
    'Coimbatore North': 'Coimbatore (North)',
    'Vaniayambadi': 'Vaniyambadi',
    'Villupuram': 'Viluppuram',
    'Orathanad': 'Orathanadu',
    'Ulundurpet': 'Ulundurpettai',
    'Dr. Radhakrishnan Nagar': 'Dr.Radhakrishnan Nagar',
    'Tiruchirapalli (West)': 'Tiruchirappalli (West)',
    'Theayagaraya Nagar': 'Thiyagarayanagar',
    'Arantangi': 'Aranthangi',
    'Thiruthuraipundi': 'Thiruthuraipoondi',
    'Udumalpet': 'Udumalaipettai',
    'Aruppukottai': 'Aruppukkottai',
    'Mudukulathur': 'Mudhukulathur',
    'Sirkali': 'Sirkazhi',
    'Thiruverambur': 'Thiruverumbur',
}

def load_csv(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def get_winners(rows):
    winners = {}
    for r in rows:
        c = r['constituency']
        votes = int(r['votes'])
        if c not in winners or votes > winners[c][3]:
            winners[c] = (r['constituency'], int(r['ac_number']), r['candidate'], votes, r['party'], r.get('region', ''), r.get('reserved', ''))
    return winners

rows21 = load_csv('C:/Users/dell/tn election/data/tn_2021_results.csv')
rows26 = load_csv('C:/Users/dell/tn election/data/tn_2026_results.csv')

winners21 = get_winners(rows21)
winners26 = get_winners(rows26)

# Map 2021 names to 2026 names
winners21_mapped = {}
for name, data in winners21.items():
    mapped = NAME_MAP.get(name, name)
    winners21_mapped[mapped] = data

# Build per-constituency result
all_constituencies = {}
used_21 = set()

# Start with 2026 constituencies
for name, (cname, ac_no, candidate, votes, party, region, reserved) in winners26.items():
    prev = winners21_mapped.get(name)
    party_2021 = prev[4] if prev else 'NEW'
    votes_2021 = prev[3] if prev else 0
    party_2026 = party
    votes_2026 = votes
    flipped = (party_2021 != party_2026)
    flip_from = party_2021 if flipped else ''
    flip_to = party_2026 if flipped else ''
    if prev:
        used_21.add(prev[0])

    # Compute vote margin (top 2 candidates in 2026 for this constituency)
    candidates_26 = [r for r in rows26 if r['constituency'] == name]
    candidates_26.sort(key=lambda x: int(x['votes']), reverse=True)
    margin_votes = int(candidates_26[0]['votes']) - int(candidates_26[1]['votes']) if len(candidates_26) > 1 else 0
    total_votes_26 = sum(int(r['votes']) for r in candidates_26)
    vote_share_26 = round(votes_2026 / total_votes_26 * 100, 1) if total_votes_26 else 0
    margin_pct = round(margin_votes / total_votes_26 * 100, 1) if total_votes_26 else 0

    # 2021 vote share
    candidates_21 = [r for r in rows21 if r['constituency'] == name or NAME_MAP.get(r['constituency'], '') == name or r['constituency'] == (list(NAME_MAP.keys())[list(NAME_MAP.values()).index(name)] if name in NAME_MAP.values() else '')]
    # Simplified: just use the 2021 total for this constituency
    total_votes_21 = sum(int(r['votes']) for r in [x for x in rows21 if x['constituency'] == prev[0]]) if prev else 0
    vote_share_21 = round(votes_2021 / total_votes_21 * 100, 1) if total_votes_21 > 0 and prev else 0

    all_constituencies[name] = {
        'ac_no': int(ac_no),
        'constituency': name,
        'region': region,
        'reserved': reserved,
        'winner_2021': prev[2] if prev else '',
        'winner_2026': candidate,
        'party_2021': party_2021,
        'party_2026': party_2026,
        'votes_2021': votes_2021,
        'votes_2026': votes_2026,
        'vote_share_2021': vote_share_21,
        'vote_share_2026': vote_share_26,
        'margin_votes': margin_votes,
        'margin_pct': margin_pct,
        'flipped': flipped,
        'flip_from': flip_from,
        'flip_to': flip_to,
    }

# Output
os.makedirs('data', exist_ok=True)
constituencies_sorted = sorted(all_constituencies.values(), key=lambda x: x['ac_no'])
with open('data/constituency_results.json', 'w', encoding='utf-8') as f:
    json.dump({'constituencies': constituencies_sorted}, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(constituencies_sorted)} constituencies to data/constituency_results.json")

# Compute aggregate stats
total = len(constituencies_sorted)
flipped_count = sum(1 for c in constituencies_sorted if c['flipped'])
flip_pct = round(flipped_count / total * 100, 1)
print(f"Total: {total}, Flipped: {flipped_count} ({flip_pct}%)")

# Party seat counts 2026
party_seats_26 = Counter(c['party_2026'] for c in constituencies_sorted)
print("2026 Seats:", dict(party_seats_26.most_common()))

# Party seat counts 2021
party_seats_21 = Counter(c['party_2021'] for c in constituencies_sorted if c['party_2021'] != 'NEW')
print("2021 Seats:", dict(party_seats_21.most_common()))

# Vote share totals 2026
total_votes_26_party = defaultdict(int)
total_votes_all_26 = 0
for r in rows26:
    total_votes_26_party[r['party']] += int(r['votes'])
    total_votes_all_26 += int(r['votes'])
print(f"\nTotal votes 2026: {total_votes_all_26}")
for p in ['TVK','DMK','AIADMK','INC','BJP','PMK','VCK','CPI','CPI(M)','IUML','DMDK','AMMK','NTK']:
    if p in total_votes_26_party:
        print(f"  {p}: {total_votes_26_party[p]} ({total_votes_26_party[p]/total_votes_all_26*100:.1f}%)")

# Vote share totals 2021
total_votes_21_party = defaultdict(int)
total_votes_all_21 = 0
for r in rows21:
    total_votes_21_party[r['party']] += int(r['votes'])
    total_votes_all_21 += int(r['votes'])
print(f"\nTotal votes 2021: {total_votes_all_21}")

# Generate flip_flows
flip_flows = defaultdict(int)
for c in constituencies_sorted:
    if c['flipped']:
        key = (c['flip_from'], c['flip_to'])
        flip_flows[key] += 1

flows_list = [{'source': k[0], 'target': k[1], 'seats': v} for k, v in sorted(flip_flows.items(), key=lambda x: -x[1])]
print(f"\nFlip flows ({len(flows_list)}):")
for f in flows_list:
    print(f"  {f['source']} -> {f['target']}: {f['seats']}")

# Update vote_share_comparison.json
major_parties_2026 = ['TVK','DMK','AIADMK','INC','BJP','PMK','VCK','CPI','CPI(M)','IUML','DMDK','AMMK','NTK']
vote_share_parties = []
for p in major_parties_2026:
    vs_21 = round(total_votes_21_party.get(p, 0) / total_votes_all_21 * 100, 1) if total_votes_all_21 else 0
    vs_26 = round(total_votes_26_party.get(p, 0) / total_votes_all_26 * 100, 1) if total_votes_all_26 else 0
    seats_21 = party_seats_21.get(p, 0)
    seats_26 = party_seats_26.get(p, 0)
    vote_share_parties.append({
        'party': p, 'vs_2021': vs_21, 'vs_2026': vs_26,
        'seats_2021': seats_21, 'seats_2026': seats_26
    })
with open('data/vote_share_comparison.json', 'w', encoding='utf-8') as f:
    json.dump({'parties': vote_share_parties}, f, indent=2, ensure_ascii=False)
print("\nUpdated data/vote_share_comparison.json")

# Update seats_by_region.json
region_data = defaultdict(lambda: defaultdict(int))
for c in constituencies_sorted:
    region_data[c['region']][c['party_2026']] += 1
regions_list = []
for r in sorted(region_data.keys()):
    d = region_data[r]
    entry = {'name': r}
    for party_key in ['dmk','tvk','aiadmk','pmk','vck']:
        entry[party_key] = d.get(party_key.upper(), 0)
    # Add other parties
    other_total = sum(d.values()) - sum(d.get(p.upper(), 0) for p in ['DMK','TVK','AIADMK','PMK','VCK'])
    entry['others'] = other_total
    regions_list.append(entry)
with open('data/seats_by_region.json', 'w', encoding='utf-8') as f:
    json.dump({'regions': regions_list}, f, indent=2, ensure_ascii=False)
print("Updated data/seats_by_region.json")

# Update flip_flows.json
flip_flows_out = {
    'flows': flows_list,
    'total_flips': flipped_count,
    'flip_percentage': flip_pct
}
with open('data/flip_flows.json', 'w', encoding='utf-8') as f:
    json.dump(flip_flows_out, f, indent=2, ensure_ascii=False)
print("Updated data/flip_flows.json")

# Update metadata.json
with open('data/metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)
metadata['total_seats'] = total
metadata['total_constituencies'] = total
metadata['tvk_emergence'] = {"2021": vote_share_parties[0]['vs_2021'] if vote_share_parties[0]['party'] == 'TVK' else 0.0, "2026": next(p['vs_2026'] for p in vote_share_parties if p['party'] == 'TVK')}
metadata['dmk_change'] = {"2021": next(p['vs_2021'] for p in vote_share_parties if p['party'] == 'DMK'), "2026": next(p['vs_2026'] for p in vote_share_parties if p['party'] == 'DMK')}
with open('data/metadata.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
print("Updated data/metadata.json")

# Generate per-constituency party color mapping
PARTY_COLORS = {
    'TVK': '#FF6B35', 'DMK': '#DC2626', 'AIADMK': '#15803D',
    'INC': '#2563EB', 'BJP': '#EA580C', 'PMK': '#92400E',
    'VCK': '#4C1D95', 'CPI': '#B91C1C', 'CPI(M)': '#991B1B',
    'IUML': '#065F46', 'DMDK': '#6B7280', 'AMMK': '#6B7280',
    'NTK': '#6B7280'
}
