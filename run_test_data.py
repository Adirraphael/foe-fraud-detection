import pandas as pd
import requests

# Load test data
df = pd.read_csv('test_data.csv')

results = []

for index, row in df.iterrows():
    # Call the endpoint for each address
    response = requests.get(
        "http://127.0.0.1:8000/check-thermostats",
        params={"site_address": row["site_address"]}
    )
    result = response.json()
    
    results.append({
        'site_address': row['site_address'],
        'expected_result': row['expected_result'],
        'actual_result': result['status'],
        'message': result['message'],
        'order_count': result['order_count']
    })
    
    print(f"Row {index + 1}/100 - {result['status']}")

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv('test_results.csv', index=False)

# Summary
correct = len(results_df[results_df['expected_result'] == results_df['actual_result']])
print(f"\nDone! {correct}/100 correct predictions")