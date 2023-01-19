import fastf1
import json
import datetime
from json import JSONEncoder

class Formula1():

    def __init__(self):
        fastf1.Cache.enable_cache("cache")
        self.session = None
        self.localCache = {}

    def getSchedule(self, year: int):

        if type(year) is not int:
            return {"error": "year should be integer"}

        keyVal = str(year)
        if keyVal in self.localCache.keys():
            return self.localCache[keyVal]
        
        schedule = fastf1.get_event_schedule(year).to_dict()
        try:
            if len(schedule["RoundNumber"]) == 0:
                return {"error": f"year '{year}' is not available in API"}
        except KeyError:
            return {"error": "API reference key has been changed"}
        
        races = []
        for i,_ in enumerate(schedule['OfficialEventName']):
            race = {}
            for key in schedule.keys():
                race[key] = schedule[key][i]
            races.append(race)
        
        self.localCache[keyVal] = races
        return races

    def getEvent(self, year: int, gp: str):
        if type(year) is not int:
            return {"error": "year should be integer"}
        if type(gp) is not str:
            return {"error": "GrandPrix should be string"}

        keyVal = f"{year}_{gp}"
        if keyVal in self.localCache.keys():
            return self.localCache[keyVal]

        try:
            event = fastf1.get_event(year, gp).to_dict()
            self.localCache[keyVal] = event
            return event
        except KeyError:
            return {"error": f"year '{year}' is not available in API"}
        except ValueError:
            return {"error": f"'{gp}' GrandPrix is not available in API"}
        

    def getSession(self, year: int, gp:str, ses: str):
        if type(year) is not int:
            return {"error": "year should be integer"}
        if type(gp) is not str:
            return {"error": "GrandPrix should be string"}
        if type(ses) is not str:
            return {"error": "Session should be string"}
        keyVal = f"{year}_{gp}_{ses}"
        if keyVal in self.localCache.keys():
            return self.localCache[keyVal]
        try:
            self.session = fastf1.get_session(year, gp, ses)
            self.session.load()
            
        except KeyError:
            return {"error": f"year '{year}' is not available in API"}
        except ValueError:
            return {"error": f"'{gp}' GrandPrix is not available in API"}
        except ValueError:
            return {"error": f"Session '{ses}' is not available in API"}
        
        data = self.session.results.to_dict()
        drivers = []
        for driverNo in data["DriverNumber"].keys():
            driver = {}
            for key in data.keys():
                driver[key] = data[key][driverNo]
            drivers.append(driver)

        self.localCache[keyVal] = drivers
        return drivers

    def getDrivers(self, year: int, gp:str, ses: str, drivers: list):
        data = []
        for driver in drivers:
            data.append(self.getDriver(year,gp,ses,driver))
        return data

    def getDriver(self, year: int, gp:str, ses: str, driver: str or int):
        keyVal = f"{year}_{gp}_{ses}_{driver}"
        if keyVal in self.localCache.keys():
            return self.localCache[keyVal]

        if self.session is None:
            _ = self.getSession(year,gp,ses)


        self.driverData = self.session.laps.pick_driver(driver)
        driverDataDict = self.driverData.to_dict()
        laps = []
        for lapNo in driverDataDict["LapNumber"].keys():
            lap = {}
            for key in driverDataDict.keys():
                lap[key] = driverDataDict[key][lapNo]
            laps.append(lap)

        laps =  json.dumps(laps,cls=DateTimeEncoder)
        self.localCache[keyVal] = laps
        return laps
    
# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime, datetime.timedelta)):
                return obj.isoformat()
        
if __name__ == "__main__":
    f1 = Formula1()
    #schedule = f1.getSchedule(2022)
    #event = f1.getEvent(2022, "French")
    session = f1.getSession(2022, "French", "R")
    driver = f1.getDriver("VET")
    print(driver)


