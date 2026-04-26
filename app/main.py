from fastapi import FastAPI

app = FastAPI(title="Fraud Detection Platform")

@app.get("/")
def root():
    return {"message": "Fraud Detection API is running"}