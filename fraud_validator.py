import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from fastapi import APIRouter

load_dotenv()

server = os.getenv('DB_SERVER')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

engine = create_engine(f'mysql+pymysql://{username}:{password}@{server}:{port}/{database}')

router = APIRouter()

#thermostats
@router.get("/check-thermostats")
def check_thermostats(site_address: str):
    query = text("""
        SELECT COUNT(*) as order_count
        FROM tgt.seera_application app
        JOIN tgt.seera_applicationmeasures am
            ON am.seera_app_measuresid = app.Id
        JOIN tgt.seera_seeraaddresses site
            ON am.seera_focusproperty = site.Id
        WHERE am.seera_measuregroupcategory = 7
          AND am.seera_measurecategory = 4
          AND app.statuscode NOT IN (234840008, 234840015)
          AND LOWER(site.seera_name) = :site_address
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"site_address": site_address.lower()})
        order_count = result.scalar()
    
    if order_count > 2:
        return {"status": "failed", "message": f"Address already has {order_count} thermostat orders", "order_count": order_count}
    else:
        return {"status": "passed", "message": "Address is within thermostat limit", "order_count": order_count}
    

# packs -- account rule. 
@router.get("/check-packs-account_rule")
def check_account_rule(email: str, year: int):
    query = text("""
        SELECT COUNT(*) as order_count
        FROM tgt.seera_application app
        JOIN tgt.seera_applicationmeasures am
            ON am.seera_app_measuresid = app.Id
        JOIN tgt.account customer
            ON customer.Id = am.seera_customer
        WHERE am.seera_programname LIKE '%%Direct to Customer%%'
          AND LOWER(app.seera_offeringname) = 'packs'
          AND LOWER(customer.emailaddress1) = :email
          AND YEAR(am.createdon) = :year
          AND am.seera_programmeasureidname NOT LIKE '%%Adjustment%%'
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"email": email.lower(), "year": year})
        order_count = result.scalar()
    
    if order_count > 1:
        return {"status": "failed", "message": f"Email already has {order_count} pack orders in {year}", "order_count": order_count}
    else:
        return {"status": "passed", "message": "Email is within pack limit", "order_count": order_count}
    

#packs- site rule

@router.get("/check-packs-site-rule")
def check_packs_site_rule(site_address: str, year: int):
    # SQL query to count pack orders for this site address in this year
    query = text("""
        SELECT COUNT(*) as order_count
        FROM tgt.seera_application app
        JOIN tgt.seera_applicationmeasures am
            ON am.seera_app_measuresid = app.Id
        JOIN tgt.seera_seeraaddresses site
            ON am.seera_focusproperty = site.Id
        WHERE am.seera_programname LIKE '%%Direct to Customer%%'
          AND LOWER(app.seera_offeringname) = 'packs'
          AND LOWER(site.seera_name) = :site_address
          AND YEAR(am.createdon) = :year
          AND am.seera_programmeasureidname NOT LIKE '%%Adjustment%%'
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"site_address": site_address.lower(), "year": year})
        order_count = result.scalar()
    
    if order_count > 1:
        return {"status": "failed", "message": f"Address already has {order_count} pack orders in {year}", "order_count": order_count}
    else:
        return {"status": "passed", "message": "Address is within pack limit", "order_count": order_count}
    


