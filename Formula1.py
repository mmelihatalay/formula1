import fastf1


class Formula1():

    def __init__(self):
        fastf1.Cache.enable_cache("cache")

    def getSchedule(self, year: int):

        if type(year) is not int:
            return {"error": "year should be integer"}
        schedule = fastf1.get_event_schedule(year).to_dict()
        try:
            if len(schedule["RoundNumber"]) == 0:
                return {"error": f"year '{year}' is not available in API"}
        except KeyError:
            return {"error": "API reference key has been changed"}
        
        return schedule

    def getEvent(self, year: int, gp: str):
        if type(year) is not int:
            return {"error": "year should be integer"}
        if type(gp) is not str:
            return {"error": "GrandPrix should be string"}
        try:
            event = fastf1.get_event(year, gp).to_dict()
            print(event)
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
        
        try:
            session = fastf1.get_session(year, gp, ses)
            session.load()
            return session.results.to_dict()
        except KeyError:
            return {"error": f"year '{year}' is not available in API"}
        except ValueError:
            return {"error": f"'{gp}' GrandPrix is not available in API"}
        except ValueError:
            return {"error": f"Session '{ses}' is not available in API"}
if __name__ == "__main__":
    f1 = Formula1()
    schedule = f1.getSchedule(2021)
    event = f1.getEvent(2021, "French")
    session = f1.getSession(2021, "French", "Q")
    print(event)


