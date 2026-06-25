import os
import csv

CURRENT_DIR = os.path.abspath(__file__)
PROJECT_ROOT = CURRENT_DIR
for _ in range(3):  # go up 3 levels
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)
DATA_PATH = os.path.join(PROJECT_ROOT, "data")
PROCESSED_PATH = os.path.join(DATA_PATH, "processed")

def load_csv_as_dict(file_path, key_col):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return {row[key_col]: row for row in reader}

def load_csv_as_list(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def get_rounds():
    if not os.path.isdir(PROCESSED_PATH):
        raise FileNotFoundError(f"Processed path not found: {PROCESSED_PATH}")
    rounds = []
    for d in os.listdir(PROCESSED_PATH):
        if d.startswith('R') and d[1:].isdigit():
            rounds.append(int(d[1:]))
    rounds.sort()
    return rounds


def create_r0_if_needed():
    r0_dir = os.path.join(PROCESSED_PATH, "R0")
    r0_path = os.path.join(r0_dir, "playerinfo.csv")
    # Always create/update R0
    r1_dir = os.path.join(PROCESSED_PATH, "R1")
    r1_players_path = os.path.join(r1_dir, "players.csv")
    if not os.path.exists(r1_players_path):
        return
    r1_players = load_csv_as_list(r1_players_path)
    os.makedirs(r0_dir, exist_ok=True)
    with open(r0_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Team', 'Name', 'Total_Points', 'Total_Cost_Cap', 'Swaps_Made', 'Swaps_Rem', 'LL', '3X', 'NN', 'WC', 'AP', 'FF'])
        for p in r1_players:
            writer.writerow([p['Team'], p['Name'], 0, 100.0, 0, 2, '', '', '', '', '', ''])

def process_round(n):
    prev_n = n - 1
    prev_dir = os.path.join(PROCESSED_PATH, f"R{prev_n}")
    prev_info_path = os.path.join(prev_dir, "playerinfo.csv")
    prev_players_path = os.path.join(prev_dir, "players.csv")
    race_dir = os.path.join(PROCESSED_PATH, f"R{n}")
    players_path = os.path.join(race_dir, "players.csv")
    drivers_path = os.path.join(race_dir, "drivers.csv")
    constructors_path = os.path.join(race_dir, "constructors.csv")
    
    prev_info = load_csv_as_dict(prev_info_path, 'Team') if os.path.exists(prev_info_path) else {}
    prev_players = load_csv_as_dict(prev_players_path, 'Team') if os.path.exists(prev_players_path) else {}
    players = load_csv_as_list(players_path) if os.path.exists(players_path) else []
    drivers = load_csv_as_dict(drivers_path, 'Name') if os.path.exists(drivers_path) else {}
    constructors = load_csv_as_dict(constructors_path, 'Name') if os.path.exists(constructors_path) else {}
    
    # Build price dict
    price_dict = {}
    for d in drivers.values():
        price_dict[d['Name'].upper()] = float(d['Price'])
    for c in constructors.values():
        price_dict[c['Name'].upper()] = float(c['Price'])
    # Normalize
    if 'RED' in price_dict:
        price_dict['RBR'] = price_dict['RED']
    if 'RAC' in price_dict:
        price_dict['RBS'] = price_dict['RAC']
    
    prev_prev_players_path = os.path.join(PROCESSED_PATH, f"R{n-2}", "players.csv")
    prev_prev_players = (
        load_csv_as_dict(prev_prev_players_path, 'Team')
        if n > 2 and os.path.exists(prev_prev_players_path)
        else {}
    )

    # Load previous round's prices for Final Fix cost cap adjustment
    prev_drivers_path = os.path.join(prev_dir, "drivers.csv")
    prev_constructors_path = os.path.join(prev_dir, "constructors.csv")
    prev_drivers = load_csv_as_dict(prev_drivers_path, 'Name') if os.path.exists(prev_drivers_path) else {}
    prev_constructors = load_csv_as_dict(prev_constructors_path, 'Name') if os.path.exists(prev_constructors_path) else {}

    prev_price_dict = {}
    for d in prev_drivers.values():
        prev_price_dict[d['Name'].upper()] = float(d['Price'])
    for c in prev_constructors.values():
        prev_price_dict[c['Name'].upper()] = float(c['Price'])
    if 'RED' in prev_price_dict:
        prev_price_dict['RBR'] = prev_price_dict['RED']
    if 'RAC' in prev_price_dict:
        prev_price_dict['RBS'] = prev_price_dict['RAC']

    output = []
    for p in players:
        team = p['Team']
        name = p['Name']
        prev_i = prev_info.get(team, {'Total_Points': '0', 'Swaps_Made': '0'})
        prev_p = prev_players.get(team, {})
        
        total_points = int(float(prev_i['Total_Points'])) + int(float(p['Points']))
        remaining = float(p['Remaining_Cost_Cap'])
        
        # Check if Limitless was used this round
        limitless_used = 'Limitless' in p.get('Chips', '')

        # Check if Final Fix was used this round
        final_fix_used = 'Final Fix' in p.get('Chips', '')
        
        # Determine teams to use for cost calculation
        if limitless_used:
            # Use previous round's team
            dri_list = [prev_p.get(f'Dri{i}', '') for i in range(1, 6)]
            con_list = [prev_p.get(f'Con{i}', '') for i in range(1, 3)]
        else:
            # Use current round's team (also correct base for Final Fix before adjustment)
            dri_list = [p[f'Dri{i}'] for i in range(1, 6)]
            con_list = [p[f'Con{i}'] for i in range(1, 3)]
        
        dri_prices = sum(price_dict.get(d.upper(), 0) for d in dri_list)
        con_prices = sum(price_dict.get(c.upper(), 0) for c in con_list)
        total_cost_cap = remaining + dri_prices + con_prices

        # Final Fix cost cap adjustment:
        # players.csv stores the post-fix team (Nor in Dri slots), but the original
        # driver (Pia) was the one on the team during the race. We correct for the
        # price changes of both drivers between the previous and current round:
        #   + (Pia_curr - Pia_prev)  — Pia's price movement still affects the cap
        #   - (Nor_curr - Nor_prev)  — Nor's price movement must be undone
        if final_fix_used and p.get('DriFixedOut', ''):
            original_driver, replaced_driver = [x.strip() for x in p['DriFixedOut'].split('<-')]
            orig_curr = price_dict.get(original_driver.upper(), 0)
            orig_prev = prev_price_dict.get(original_driver.upper(), 0)
            repl_curr = price_dict.get(replaced_driver.upper(), 0)
            repl_prev = prev_price_dict.get(replaced_driver.upper(), 0)
            total_cost_cap += (orig_curr - orig_prev) - (repl_curr - repl_prev)
        
        # swaps_made = 0
        # if n > 1 and prev_p:
        #     current_drivers = {p[f'Dri{i}'] for i in range(1, 6)}
        #     prev_drivers = {prev_p.get(f'Dri{i}', '') for i in range(1, 6)}
        #     driver_changes = len(current_drivers - prev_drivers)
            
        #     current_con = {p[f'Con{i}'] for i in range(1, 3)}
        #     prev_con = {prev_p.get(f'Con{i}', '') for i in range(1, 3)}
        #     con_changes = len(current_con - prev_con)
            
        #     swaps_made = driver_changes + con_changes
        
        # prev_swaps_rem = int(float(prev_i.get('Swaps_Rem', '2')))
        # swaps_rem = 2 if n <= 1 else min(3, prev_swaps_rem + 2)

        # ---------- SWAP LOGIC ----------
        # Detect chips
        chip_str = p.get('Chips', '')
        limitless_used = 'Limitless' in chip_str
        wildcard_used = 'Wildcard' in chip_str

        # Detect chips from previous round
        prev_chip_str = prev_p.get('Chips', '')
        prev_was_limitless = 'Limitless' in prev_chip_str
        prev_was_final_fix = 'Final Fix' in prev_chip_str

        # Select base team for comparison
        base_team = None

        if n > 1:
            if prev_was_limitless:
                # Compare with R(n-2)
                prev_prev_p = prev_prev_players.get(team, {})
                base_team = prev_prev_p
            else:
                # Normal case: compare with R(n-1)
                base_team = prev_p

        # ----- Compute swaps made (set-based, position-independent) -----
        swaps_made = 0

        if base_team:
            current_drivers = {
                p.get(f'Dri{i}', '').strip()
                for i in range(1, 6)
            }
            previous_drivers = {
                base_team.get(f'Dri{i}', '').strip()
                for i in range(1, 6)
            }

            # Current round used Final Fix: players.csv has Nor (replacement) in Dri slots,
            # but the pre-fix team (with Pia) is what we compare against the previous team.
            if final_fix_used and p.get('DriFixedOut', ''):
                orig, repl = [x.strip() for x in p['DriFixedOut'].split('<-')]
                if repl in current_drivers:
                    current_drivers.discard(repl)
                    current_drivers.add(orig)

            # Previous round used Final Fix: base_team's players.csv also has Nor in Dri slots,
            # but again the pre-fix team (with Pia) is the meaningful comparison baseline.
            if prev_was_final_fix and base_team.get('DriFixedOut', ''):
                orig, repl = [x.strip() for x in base_team['DriFixedOut'].split('<-')]
                if repl in previous_drivers:
                    previous_drivers.discard(repl)
                    previous_drivers.add(orig)

            current_constructors = {
                p.get(f'Con{i}', '').strip()
                for i in range(1, 3)
            }
            previous_constructors = {
                base_team.get(f'Con{i}', '').strip()
                for i in range(1, 3)
            }

            driver_changes = len(current_drivers - previous_drivers)
            constructor_changes = len(current_constructors - previous_constructors)

            swaps_made = driver_changes + constructor_changes

        # ----- Compute swaps remaining -----
        prev_swaps_rem = int(float(prev_i.get('Swaps_Rem', '2')))

        if n <= 1:
            swaps_rem = 2

        elif limitless_used or wildcard_used:
            # Reset after chip usage
            swaps_rem = 2

        else:
            swaps_rem = max(
                2,
                min(3, prev_swaps_rem + 2 - swaps_made)
            )
        
        chips = {'LL': '', '3X': '', 'NN': '', 'WC': '', 'AP': '', 'FF': ''}
        chip_str = p.get('Chips', '')
        if chip_str:
            if 'Limitless' in chip_str:
                chips['LL'] = f'R{n}'
                swaps_rem = 2  # Special Case: reset swaps remaining if Limitless used
            if 'x3 Boost' in chip_str:
                chips['3X'] = f'R{n}'
            if 'No Negative' in chip_str:
                chips['NN'] = f'R{n}'
            if 'Wildcard' in chip_str:
                chips['WC'] = f'R{n}'
                swaps_rem = 2  # Special Case: reset swaps remaining if Wildcard used
            if 'Auto Pilot' in chip_str:
                chips['AP'] = f'R{n}'
            if 'Final Fix' in chip_str:
                chips['FF'] = f'R{n}'
        
        # Make chips stick from previous rounds
        for key in chips:
            if prev_i.get(key, ''):
                chips[key] = prev_i[key]
        
        output.append({
            'Team': team,
            'Name': name,
            'Total_Points': total_points,
            'Total_Cost_Cap': f"{total_cost_cap:.1f}",
            'Swaps_Made': swaps_made,
            'Swaps_Rem': swaps_rem,
            'LL': chips['LL'],
            '3X': chips['3X'],
            'NN': chips['NN'],
            'WC': chips['WC'],
            'AP': chips['AP'],
            'FF': chips['FF']
        })
    
    # Sort output by Total_Points descending
    output = sorted(output, key=lambda x: x['Total_Points'], reverse=True)
    
    output_path = os.path.join(race_dir, "playerinfo.csv")
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Team', 'Name', 'Total_Points', 'Total_Cost_Cap', 'Swaps_Made', 'Swaps_Rem', 'LL', '3X', 'NN', 'WC', 'AP', 'FF'])
        writer.writeheader()
        writer.writerows(output)

def player_formatter():
    rounds = get_rounds()
    create_r0_if_needed()
    if 0 not in rounds:
        rounds = [0] + rounds
    for n in sorted(rounds):
        if n == 0:
            continue
        process_round(n)

if __name__ == '__main__':
    player_formatter()