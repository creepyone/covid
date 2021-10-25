from typing import Sequence
import pandas as pd
import matplotlib.pyplot as plt

CSV_GLOBAL_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'


class DataLoader:

    def __init__(self, url):
        self.url: str = url
        self.df: pd.DataFrame = pd.DataFrame()
        self.file_name: str = ''
        self.update_data()

    def update_data(self) -> None:
        """Creates csv file and writes data from github csv"""
        self.df = pd.read_csv(self.url)
        self.file_name = self.df.columns[-1].replace('/', '.') + '.csv'
        self.df.to_csv(self.file_name, index=True)


class NoInfoException(Exception):
    pass


class DataReader:
    """To read local data"""

    def __init__(self, src):
        self.df = pd.read_csv(src)


class Analyzer:
    """To get info from data"""

    def __init__(self, data_reader: DataReader):
        self.df = data_reader.df

    def get_country_names(self) -> pd.Series:
        return self.df["Country/Region"]

    def last_sick_total_info(self) -> pd.DataFrame:
        """Returns total sick for all countries"""
        return pd.concat([self.get_country_names(), self.df.iloc[:, -1:]], axis=1).set_index("Country/Region")

    def total_sick_for_country(self, country_name: str) -> dict | None:
        """Returns total sick for specific country"""
        try:
            countries_total = self.last_sick_total_info()
            return {country_name: countries_total.loc[country_name].iloc[0]}
        except NoInfoException:
            return None

    def last_sick_per_day(self):
        """Returns last ill per day for all countries"""
        last = self.last_sick_total_info()
        pre_last = pd.concat([self.get_country_names(), self.df.iloc[:, -2:-1]], axis=1, copy=True).set_index(
            'Country/Region')
        ill_last_day = last[last.columns[0]] - pre_last[pre_last.columns[0]]
        return ill_last_day

    def last_sick_per_day_for_country(self, country_name):
        """Returns last ill per day for specific country"""
        try:
            ill_last_day = self.last_sick_per_day().loc[country_name]
            return {country_name: ill_last_day}
        except NoInfoException:
            return None

    def get_info_by_date(self, month: int, day: int, year: int) -> pd.Series | None:
        """Returns all data for specific date"""
        try:
            return pd.concat([self.get_country_names(), self.df[f'{month}/{day}/{year}']], axis=1)
        except NoInfoException:
            return None

    def last_sick_total_for_many_countries(self, list_of_countries: Sequence):
        info = dict()
        for country in list_of_countries:
            info.update(self.total_sick_for_country(country))
        return info

    def last_sick_per_day_for_many_countries(self, list_of_countries: Sequence):
        info = dict()
        for country in list_of_countries:
            info.update(self.last_sick_per_day_for_country(country))
        return info

    def total_last_n_days(self, days=1):
        """
        Returns total numbers of sick for last n days.
        Used for plotting
        """
        frame = pd.concat([self.get_country_names(), self.df.iloc[:, -days:-days + 1]], axis=1)
        for i in range(days - 1, 0, -1):
            frame = pd.concat([frame, self.df.iloc[:, -i:-i + 1]], axis=1)
        frame = pd.concat([frame, self.df.iloc[:, -1:]], axis=1).set_index("Country/Region")
        return frame

    def per_day_last_n_days(self, days=1):
        total_frame = self.total_last_n_days(days + 1)
        frame = pd.DataFrame(index=total_frame.index)
        for i in range(days):
            frame[total_frame.columns[i + 1]] = total_frame[total_frame.columns[i + 1]] - total_frame[
                total_frame.columns[i]]
        return frame


class Plotter:
    def __init__(self, analyze: Analyzer):
        self.analyze = analyze


# data = DataLoader(CSV_GLOBAL_URL)
data = DataReader('10.24.21.csv')
analyzer = Analyzer(data)
# print(analyzer.last_sick_total_for_many_countries(["Russia", "Japan"]))
# print(analyzer.last_sick_per_day_for_many_countries(["Russia", "Japan"]))
print(analyzer.total_last_n_days(5))
print(analyzer.per_day_last_n_days(1))
