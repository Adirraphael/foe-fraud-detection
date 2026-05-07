import pandas as pd

# Load your existing data
violations = pd.read_csv('thermostat_violations.csv')  # addresses that should FAIL
raw = pd.read_csv('raw_thermostats_data.csv')  # addresses to pick passing ones from

# Get 30 failing addresses (already have 3+ orders)
failing = violations.head(30)[['site_address', 'email', 'account_name']]
failing['expected_result'] = 'failed'

# Get passing addresses - ones with only 1 order
raw_counts = raw.groupby('site_address')['measure_id'].count().reset_index()
raw_counts.columns = ['site_address', 'order_count']
passing_addresses = raw_counts[raw_counts['order_count'] == 1]['site_address']

# Get 70 passing addresses
passing = raw[raw['site_address'].isin(passing_addresses)][['site_address', 'email', 'account_name']].drop_duplicates('site_address').head(70)
passing['expected_result'] = 'passed'

# Combine and shuffle
test_data = pd.concat([failing, passing], ignore_index=True).sample(frac=1).reset_index(drop=True)

print(f"Total rows: {len(test_data)}")
print(f"Expected fails: {len(test_data[test_data['expected_result'] == 'failed'])}")
print(f"Expected passes: {len(test_data[test_data['expected_result'] == 'passed'])}")

test_data.to_csv('test_data.csv', index=False)
print("test_data.csv created!")