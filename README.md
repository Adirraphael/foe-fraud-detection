Fraud Detection & Validation API

This project detects fraud in residential programs by identifying customers who ordered more packs or smart thermostats than they are entitled to.
I connected to an AWS RDS MySQL database using SQLAlchemy and pulled 180K+ records to analyze pack and thermostat orders. For packs, I flagged accounts where the same email or address placed more than one order in the same calendar year. For thermostats, I flagged addresses that received more than 2 units over the lifetime of the program.

I also built an extra check that flags accounts with suspiciously close house numbers on the same street,  a sign that someone might be gaming the system across multiple addresses.

On top of the analysis, I built a REST API using FastAPI with 3 real-time validation endpoints that can check incoming orders for fraud before they get uploaded to the CRM system.
