from fastapi import FastAPI
from Formula1 import Formula1
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
f1 = Formula1()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/{year}")
async def schedule(year):
    try: 
        year = int(year)
    except ValueError:
        return {"error": f"'{year}' is not a valid year"}
    return f1.getSchedule(year)

@app.get("/{year}/{gp}")
async def event(year,gp):
    try: 
        year = int(year)
    except ValueError:
        return {"error": f"'{year}' is not a valid year"}
    return f1.getEvent(year, gp)

@app.get("/{year}/{gp}/{session}")
async def session(year,gp, session):
    try: 
        year = int(year)
    except ValueError:
        return {"error": f"'{year}' is not a valid year"}
    return f1.getSession(year, gp, session)

@app.get("/{year}/{gp}/{session}/{driver}")
async def driver(year,gp,session,driver):
    try: 
        year = int(year)
    except ValueError:
        return {"error": f"'{year}' is not a valid year"}
        
    return f1.getDriver(year,gp,session,driver)

if __name__ == "__main__":
    uvicorn.run(app,port=8000)