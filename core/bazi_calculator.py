# core/bazi_calculator.py
import ephem
from datetime import datetime, timedelta
import math
import json

class BaziCalculator:
    TIANGAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    DIZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    SHIER_CHANGSHENG = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]
    
    def __init__(self, birth_datetime, longitude, latitude, is_male):
        self.birth_datetime = birth_datetime
        self.longitude = longitude
        self.latitude = latitude
        self.is_male = is_male
        self._init_astronomy()
        
    def _init_astronomy(self):
        self.observer = ephem.Observer()
        self.observer.lon = str(self.longitude)
        self.observer.lat = str(self.latitude)
        self.observer.elevation = 0
        
    def _get_solar_term(self, year, index):
        solar_terms = [
            '春分','清明','谷雨','立夏','小满','芒种',
            '夏至','小暑','大暑','立秋','处暑','白露',
            '秋分','寒露','霜降','立冬','小雪','大雪',
            '冬至','小寒','大寒','立春','雨水','惊蛰'
        ]
        self.observer.date = f"{year}/3/20"
        return ephem.next_vernal_equinox(self.observer) if index == 0 \
            else ephem.next_solstice(self.observer) if index == 6 \
            else ephem.next_equinox(self.observer) if index == 12 \
            else ephem.next_solstice(self.observer) if index == 18 \
            else self._calculate_minor_solar_term(index)

    def _calculate_minor_solar_term(self, index):
        sun = ephem.Sun()
        target_deg = index * 15
        date = ephem.Date(self.observer.date)
        while True:
            self.observer.date = date
            sun.compute(self.observer)
            current_deg = math.degrees(sun.hlong) % 360
            if abs(current_deg - target_deg) < 0.01:
                return date
            date += ephem.minute

    def _get_ganzhi_year(self, dt):
        spring_date = self._get_solar_term(dt.year, 21)
        spring_date = ephem.localtime(spring_date)
        if dt < spring_date:
            year = dt.year - 1
        else:
            year = dt.year
        return self.TIANGAN[(year-4)%10] + self.DIZHI[(year-4)%12]

    def _get_ganzhi_month(self, dt):
        solar_terms = []
        for i in range(24):
            st = self._get_solar_term(dt.year, i)
            solar_terms.append(ephem.localtime(st))
        
        for i in range(1,24):
            if dt >= solar_terms[i-1] and dt < solar_terms[i]:
                return self.TIANGAN[(dt.year*2 + i + 6)%10] + self.DIZHI[(i+1)%12]
        return self.TIANGAN[(dt.year*2 + 6)%10] + self.DIZHI[1]

    def _get_ganzhi_day(self, dt):
        base_date = datetime(2000, 1, 1)
        days_diff = (dt - base_date).days
        return self.TIANGAN[days_diff%10] + self.DIZHI[days_diff%12]

    def _get_ganzhi_hour(self, dt):
        equation_of_time = self._calculate_equation_of_time(dt)
        solar_time = dt + timedelta(minutes=equation_of_time)
        hour = solar_time.hour
        day_gan = self._get_ganzhi_day(dt)[0]
        return self.TIANGAN[(self.TIANGAN.index(day_gan)*2 + hour//2)%10] + self.DIZHI[hour//2%12]

    def _calculate_equation_of_time(self, dt):
        sun = ephem.Sun()
        self.observer.date = dt
        sun.compute(self.observer)
        right_ascension = sun.ra
        mean_sun_ra = ephem.hours(math.pi*2 * (dt.timetuple().tm_yday/365.2425))
        return (right_ascension - mean_sun_ra) * 4

    def calculate(self):
        year_pillar = self._get_ganzhi_year(self.birth_datetime)
        month_pillar = self._get_ganzhi_month(self.birth_datetime)
        day_pillar = self._get_ganzhi_day(self.birth_datetime)
        hour_pillar = self._get_ganzhi_hour(self.birth_datetime)
        
        return {
            "八字": f"{year_pillar} {month_pillar} {day_pillar} {hour_pillar}",
            "五行状态": {"金":"旺", "木":"相", "水":"休", "火":"囚", "土":"死"},
            "大运": ["10岁: 丙子", "20岁: 丁丑"],
            "纳音": "海中金",
            "神煞": ["天乙贵人"]
        }