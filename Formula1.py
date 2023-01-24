import fastf1
import json
import datetime
from json import JSONEncoder
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.palettes import Dark2_5 as palette
import itertools  
import numpy as np
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, PrintfTickFormatter
from bokeh.plotting import figure, show
from bokeh.layouts import row, gridplot 
import pandas as pd
import math

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

    def getEvent(self, year: int, gp):
        if type(year) is not int:
            return {"error": "year should be integer"}
        #if type(gp) is not str:
        #    return {"error": "GrandPrix should be string"}

        keyVal = f"{year}_{gp}"
        if keyVal in self.localCache.keys():
            return self.localCache[keyVal]

        try:
            event = fastf1.get_event(year, gp).to_dict()
            event = json.dumps(event,cls=DateTimeEncoder)
            self.localCache[keyVal] = event
            return event
        except KeyError:
            return {"error": f"year '{year}' is not available in API"}
        

    def getSession(self, year: int, gp:int, ses: str):
        if type(year) is not int:
            return {"error": "year should be integer"}
        if type(ses) is not str:
            return {"error": "Session should be string"}
        print(type(gp))
        keyVal = f"{year}_{gp}_{ses}"
        if keyVal in self.localCache.keys():
            return self.localCache[keyVal]
        try:
            self.session = fastf1.get_session(year, gp, ses)
            self.session.load()
            
        except KeyError:
            return {"error": f"year '{year}' is not available in API"}
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
        dataDrivers = {}
        dataDriversDict = {}
        for driver in drivers:
            dataDrivers[driver], dataDriversDict[driver] = self.getDriver(year,gp,ses,driver)
        return dataDrivers, dataDriversDict

    def getDriver(self, year: int, gp:str, ses: str, driver: str or int):
        keyVal = f"{year}_{gp}_{ses}_{driver}"
        if keyVal in self.localCache.keys():
            return self.localCache[keyVal]

        if self.session is None:
            _ = self.getSession(year,gp,ses)


        driverData = self.session.laps.pick_driver(driver)
        driverDataJson =  json.dumps(driverData,cls=DateTimeEncoder)
        return driverData, driverDataJson
        

    def getFastestLap(self, year: int, gp:str, ses: str, drivers: list, fast, track):
        keyVal = f"{year}_{gp}_{ses}"
        if keyVal not in self.localCache.keys():
            self.getSession(year, gp, ses)
        
        driversData, _ = self.getDrivers(year, gp, ses, drivers)
        
        driversDict = {}
        for driver in drivers:
            fastData = driversData[driver].pick_fastest()
            carData = fastData.get_telemetry().add_distance()
            driversDict[driver] = carData
        self.plotDriver = driversDict
        if fast:
            return self.plot()
        if track:
            return self.plotTrack()

    def plotTrack(self):
        tracksDriver = []
        colors = ["#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027"]
        heatKeys = ["Speed", "nGear","Brake", "Throttle"]
        for j,driver in enumerate(self.plotDriver.keys()):
            plots = []
            for i, heatKey in enumerate(heatKeys):
                heatValue = np.array(self.plotDriver[driver][heatKey]).astype(float)
                x = np.array(self.plotDriver[driver]["X"]).astype(float)
                y = np.array(self.plotDriver[driver]["Y"]).astype(float)
                heatDict = {"x":x,"y":y,"heatValue":heatValue}
                mapper = LinearColorMapper(palette=colors, low=min(0,heatValue.min().astype(int)), high=heatValue.max().astype(int))
                if i == 0:
                    p = figure(width=350, height=250)
                else:
                    p = figure(width=350, height=250,x_range=plots[0].x_range, y_range=plots[0].y_range)
                p.circle(x="x",y="y",source=heatDict,fill_color={'field': "heatValue", 'transform': mapper},line_color=None)
                color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="7px",
                     ticker=BasicTicker(desired_num_ticks=len(colors)),
                     formatter=PrintfTickFormatter(format="%d"),
                     label_standoff=6, border_line_color=None, title=heatKey)
                p.xaxis.major_label_orientation = math.pi/2
                p.add_layout(color_bar, 'right')
                plots.append(p)
            
            tracksDriver.append(json_item(gridplot([plots],toolbar_location="below"),f"myplot{j}"))
        
        return tracksDriver

    def plot(self):
        colors = itertools.cycle(palette)    
        p = figure(title="Race", x_axis_label="Distance [m]", y_axis_label="Speed [km/h]",width=1500, height=500)
        for driver,color in zip(self.plotDriver.keys(), colors):
            p.line(self.plotDriver[driver]["Distance"], self.plotDriver[driver]["Speed"],
                    color=color,
                    legend_label=driver,
                    line_width=2)
        bokehJson = json_item(p,"myplot")
        return bokehJson
    
    def getResult(self, year: int, gp:str, ses: str):
        if type(year) is not int:
            return {"error": "year should be integer"}
        if type(ses) is not str:
            return {"error": "Session should be string"}
        try:
            self.session = fastf1.get_session(year, gp, ses)
            self.session.load()
        except KeyError:
            return {"error": f"year '{year}' is not available in API"}
        except ValueError:
            return {"error": f"Session '{ses}' is not available in API"}
        
        resultDict = self.session.results.to_dict()
        results = []
        for i,num in enumerate(resultDict['DriverNumber']):
            result = {}
            for key in resultDict.keys():
                result[key] = resultDict[key][num]
            results.append(result)
        return results

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime, datetime.timedelta)):
                return obj.isoformat()
        
if __name__ == "__main__":
    f1 = Formula1()
    #schedule = f1.getSchedule(2022)
    event = f1.getEvent(2021,1)
    #session = f1.getSession(2022, "French", "R")
    #driver = f1.getDriver(2022, "French", "R",["LEC"])
    #gg = f1.getTelemetry()
    print(event)


