from fastapi import FastAPI
import fraud_validator

app = FastAPI()

app.include_router(fraud_validator.router)