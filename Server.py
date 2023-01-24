from fastapi import FastAPI, Query
from typing import List, Union, Optional
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
    gg = f1.plot()
    print(gg)
    return gg

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
        gp = int(gp)
    except ValueError:
        return {"error": f"'{year}' is not a valid year"}
    return f1.getEvent(year, gp)
"""
@app.get("/{year}/{gp}/{session}")
async def session(year,gp, session):
    try: 
        year = int(year)
    except ValueError:
        return {"error": f"'{year}' is not a valid year"}
    return f1.getSession(year, gp, session)"""

@app.get("/{year}/{gp}/{session}")
async def session(year,gp,session,drivers: List[Union[int,str]] = Query(None), fast = False, result = False, track = False):
    if fast == True and result == True:
        return {"error": "fastest lap and result cannot be requested at the same time"}
    try: 
        year = int(year)
        gp = int(gp)
    except ValueError:
        return {"error": f"'{year}' is not a valid year"}
    
    if result:
        return f1.getResult(year, gp, session)
    
    if not drivers:
        return f1.getSession(year, gp, session)
    
    if fast or track:
        return f1.getFastestLap(year,gp,session,drivers, fast, track)
    
    _, driversDataDict = f1.getDrivers(year,gp,session,drivers)
    return driversDataDict

@app.get("/plot")
async def plot():
    gg = f1.plot()
    print(gg)
    return gg

if __name__ == "__main__":
    uvicorn.run(app,port=8000)