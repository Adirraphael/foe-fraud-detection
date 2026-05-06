import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import re


load_dotenv()

server = os.getenv('DB_SERVER')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')


engine = create_engine(f'mysql+pymysql://{username}:{password}@{server}:{port}/{database}')

print("Connected")


query = """
SELECT
    am.seera_app_measuresid                         AS measure_id,
    LOWER(app.seera_name)                           AS app_name,
    am.seera_programname                            AS program,
    am.seera_programmeasureidname                   AS measure_name,
    am.createdon                                    AS created_on,
    am.statuscode                                   AS status_code,
    LOWER(customer.emailaddress1)                   AS email,
    LOWER(customer.telephone1)                      AS phone,
    LOWER(customer.name)                            AS account_name,
    LOWER(am.seera_paymentaddressname)              AS payee_address,
    LOWER(site.seera_name)                          AS site_address
FROM tgt.seera_application app
JOIN tgt.seera_applicationmeasures am
    ON am.seera_app_measuresid = app.Id
JOIN tgt.seera_seeraaddresses site
    ON am.seera_focusproperty = site.Id
JOIN tgt.account customer
    ON customer.Id = am.seera_customer
WHERE am.seera_programname LIKE '%%Direct to Customer%%'
  AND LOWER(app.seera_offeringname) = 'packs'
  AND YEAR(am.createdon) IN (2025, 2026)
  AND customer.emailaddress1 IS NOT NULL
  AND am.seera_programmeasureidname NOT LIKE '%%Adjustment%%'
ORDER BY am.createdon DESC
"""

#save locally from aws
df = pd.read_sql(query, engine)
#df.to_csv('raw_packs_data.csv', index=False)



#print(f"Total rows: {len(df)}")
#print(df.head())


# Task 1 Packs 
# Account rule 
df['year'] = pd.to_datetime(df['created_on']).dt.year

account_violations = (
    df.groupby(['email', 'year'])
    .agg(order_count=('measure_id', 'count'),
         account_name=('account_name', 'first'))
    .reset_index()
)

account_violations = account_violations[account_violations['order_count'] > 1]

#print("Account rule violations:")
#print(account_violations)


# site rule 
site_violations = (
    df.groupby(['site_address', 'year'])
    .agg(order_count=('measure_id', 'count'),
         email=('email', 'first'),
         account_name=('account_name', 'first'))
    .reset_index()
)

site_violations = site_violations[site_violations['order_count'] > 1]

#print("Site rule violations:")
#print(site_violations)

# csv exports
#account_violations.to_csv('account_rule_violations.csv', index=False)
#print(f"Account rule violations: {len(account_violations)} rows saved")

#site_violations.to_csv('site_rule_violations.csv', index=False)
#print(f"Site rule violations: {len(site_violations)} rows saved")

#bonus
# Extract house number and street name from site_address
def parse_address(address):
    if pd.isna(address):
        return None, None
    match = re.match(r'^(\d+)\s+(.+)$', str(address).strip())
    if match:
        return int(match.group(1)), match.group(2).strip()
    return None, None

df['house_number'], df['street_name'] = zip(*df['site_address'].map(parse_address))


df_parsed = df.dropna(subset=['house_number', 'street_name'])


flagged_accounts = []

for (account, street), group in df_parsed.groupby(['account_name', 'street_name']):
    house_numbers = sorted(group['house_number'].unique())
    # Check if any two house numbers are within 10 of each other
    suspicious = set()
    for i in range(len(house_numbers)):
        for j in range(i+1, len(house_numbers)):
            if abs(house_numbers[j] - house_numbers[i]) <= 10:
                suspicious.add(house_numbers[i])
                suspicious.add(house_numbers[j])
    
    if suspicious:
        flagged_accounts.append({
            'account_name': account,
            'street_name': street,
            'suspicious_house_numbers': ', '.join(str(int(n)) for n in sorted(suspicious)),
            'count': len(suspicious)
        })

bonus_violations = pd.DataFrame(flagged_accounts)
#print("Bonus violations:")
#print(bonus_violations)

#csv export
#bonus_violations.to_csv('address_proximity_violations.csv', index=False)
#print(f"Bonus violations: {len(bonus_violations)} rows saved")


# Task 2 Thermostats
query_thermostats = """
SELECT
    LOWER(site.seera_name)                              AS site_address,
    LOWER(customer.emailaddress1)                       AS email,
    LOWER(customer.name)                                AS account_name,
    LOWER(customer.telephone1)                          AS phone,
    am.seera_programmeasureidname                       AS measure_name,
    am.createdon                                        AS created_on,
    am.statuscode                                       AS status_code,
    LOWER(app.seera_name)                               AS app_name,
    am.seera_app_measuresid                             AS measure_id
FROM tgt.seera_application app
JOIN tgt.seera_applicationmeasures am
    ON am.seera_app_measuresid = app.Id
JOIN tgt.seera_seeraaddresses site
    ON am.seera_focusproperty = site.Id
JOIN tgt.account customer
    ON customer.Id = am.seera_customer
WHERE customer.emailaddress1 IS NOT NULL
  AND am.seera_measuregroupcategory = 7
  AND am.seera_measurecategory = 4
  AND app.statuscode NOT IN (234840008, 234840015)
ORDER BY site.seera_name, am.createdon
"""
 
# save locally from aws
df_thermostats = pd.read_sql(query_thermostats, engine)
#df_thermostats.to_csv('raw_thermostats_data.csv', index=False)
 
 
print(f"Total thermostat rows: {len(df_thermostats)}")
 
 
thermostat_violations = (
    df_thermostats.groupby('site_address')
    .agg(order_count=('measure_id', 'count'),
         email=('email', 'first'),
         account_name=('account_name', 'first'))
    .reset_index()
)
 
thermostat_violations = thermostat_violations[thermostat_violations['order_count'] > 2]
 
thermostat_violations.to_csv('thermostat_violations.csv', index=False)
#print(f"Thermostat violations: {len(thermostat_violations)} rows saved")