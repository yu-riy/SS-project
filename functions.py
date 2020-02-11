import requests
import urllib.request
import time
import os
from bs4 import BeautifulSoup
from os import walk
from datetime import datetime

PATH = "/home/yurii/python/project/data/"

class Money:

    def __init__(self):
        self.currency_names = {}
        self.filenames = []
    
    #Основная функция, которая парсит УРЛ с таблицей курса валют на сайте НБУ
    def get_data(self):
        time_now = datetime.now()
        f_time = time_now.strftime("%d.%m.%Y")
        url = f"https://bank.gov.ua/markets/exchangerates/?date={f_time}&period=daily"
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", attrs = {"id" : "exchangeRates"})
        rows = table.find_all("tr")

        parsed_data = []

        for column in rows:
            raw_columns = column.find_all("td")
            columns = [each.text.strip() for each in raw_columns]
            parsed_data.append(columns)

        #currency_names = {}
        time_now = datetime.now()
        formated_time = time_now.strftime("%d/%m/%Y %H:%M:%S")

        parsed_data.pop(0)
        for each in parsed_data:
            
            self.currency_names[each[1]] = formated_time, each[2] ,each[3], each[4]
        return(self.currency_names)

    #Вспомогательная функция, которая выводит список файлов в локальной базе      
    def get_filenames(self):
        
        #filenames = []
        for (dirpath, dirnames, filename) in walk(PATH):
            for each in filename:
                self.filenames.append(each[:-4])
        return(self.filenames)

    #Функция, которая проверяет, есть ли на сайте НБУ валюты, что не входят в нашу базу
    #и проводит первичное наполнение файла для такой валюты
    def check_if_new(self, currency_names, filenames):
        
        currency_names_list = list(currency_names.keys())
        if set(currency_names_list) == set(filenames):
            print("Таблица актуальна, нечего добавлять")
            
        else:
            os.chdir(PATH)
            for each in currency_names.keys():
                if each not in filenames:
                    newfilename = f"{each}.txt"
                    print(f"Обнаружена новая валюта {each}, добавление...")
                    new_file = open(newfilename, "a")
                    data_to_write = currency_names.get(f"{each}")
                    new_file.write(",".join(data_to_write))
                    new_file.close()


    def get_updates(self, currency_names, filenames):
        os.chdir(PATH)
        counter = 0
        for each in filenames:
            filename = f"{each}.txt"
            with open(filename, "a") as current_file:
                data_to_write ="\n" + ",".join(currency_names.get(f"{each}"))
                current_file.write(data_to_write)
            counter += 1
        print(f"Операция завершена, добавлено записей: {counter}")

    #Функция вывода актуального списка валют с сайта НБУ      
    def print_currency_names(self):
        actual = self.get_data()
        currency_names = set(actual.keys())
        for each in currency_names:
            print(f"{each} : {actual[each][2]}")

class Currency(Money):
    def __init__(self, currency_name):
        self.currency_name = currency_name
        Money.__init__(self)
        
    #Функция вывода содержимого файла по выбраной валюте
    def get_currency_actual(self, currency_name, lines_number="all"):
        os.chdir(PATH)
        filename = f"{currency_name}.txt"
        with open(filename, "r") as current_file:
            lines = current_file.readlines()
            
            if lines_number == "all":
                for each in lines:
                    row = [elem for elem in (each.strip()).split(",", 3)]
                    joined = " | ".join(row)
                    print(joined)
            else:
                lines_to_print = lines[-lines_number:]
                for each in lines_to_print:
                    print(each)

    #Функция вывода минимального и максимального значения валюты
    def get_extremum(self, currency_name):
        os.chdir(PATH)
        filename = f"{currency_name}.txt"
        with open(filename, "r") as current_file:
            lines = current_file.readlines()
            rows = []
            for each in lines:
                    row = [elem for elem in (each.strip()).split(",", 3)]
                    rows.append(row)
            currency_values = {elem[0] : elem[3] for elem in rows}
            min_value = min(currency_values, key = currency_values.get)
            max_value = max(currency_values, key = currency_values.get)
            for key, value in currency_values.items():
                if key == min_value:
                    print(f"Минимальный курс зафиксирован {min_value} и составлял {value}")
                if key == max_value:
                    print(f"Максимальный курс зафиксирован {max_value} и составлял {value}")
