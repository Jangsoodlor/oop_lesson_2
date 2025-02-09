import csv
import os

class CSV_Read:
    def __init__(self, filename) -> None:
        self._list = []
        self.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(self.__location__, filename + '.csv')) as f:
            rows = csv.DictReader(f)
            for r in rows:
                self._list.append(dict(r))

    @property
    def get_list(self):
        return self._list

class DB:
    def __init__(self):
        self.database = []

    def insert(self, table):
        self.database.append(table)

    def search(self, table_name):
        for table in self.database:
            if table.table_name == table_name:
                return table
        return None

import copy
class Table:
    def __init__(self, table_name, table):
        self.table_name = table_name
        self.table = table

    def join(self, other_table, common_key):
        joined_table = Table(self.table_name + '_joins_' + other_table.table_name, [])
        for item1 in self.table:
            for item2 in other_table.table:
                if item1[common_key] == item2[common_key]:
                    dict1 = copy.deepcopy(item1)
                    dict2 = copy.deepcopy(item2)
                    dict1.update(dict2)
                    joined_table.table.append(dict1)
        return joined_table

    def filter(self, condition):
        filtered_table = Table(self.table_name + '_filtered', [])
        for item1 in self.table:
            if condition(item1):
                filtered_table.table.append(item1)
        return filtered_table

    def __is_float(self, element):
        if element is None: 
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False

    def aggregate(self, function, aggregation_key):
        temps = []
        for item1 in self.table:
            if self.__is_float(item1[aggregation_key]):
                temps.append(float(item1[aggregation_key]))
            else:
                temps.append(item1[aggregation_key])
        return function(temps)
    
    def select(self, attributes_list):
        temps = []
        for item1 in self.table:
            dict_temp = {}
            for key in item1:
                if key in attributes_list:
                    dict_temp[key] = item1[key]
            temps.append(dict_temp)
        return temps
    
    def pivot_table(self, keys_to_pivot_list, keys_to_aggreagte_list, aggregate_func_list):
        # First create a list of unique values for each key
        unique_values_list = []
        for key in keys_to_pivot_list:
            _list = []
            for d in self.select(keys_to_pivot_list):
                if d.get(key) not in _list:
                    _list.append(d.get(key))
            unique_values_list.append(_list)
            
        # Here is an example of of unique_values_list for
        # keys_to_pivot_list = ['embarked', 'gender', 'class']
        # unique_values_list =
        # [['Southampton', 'Cherbourg', 'Queenstown'], ['M', 'F'], ['3', '2','1']]

        # Get the combination of unique_values_list
        # You will make use of the function you implemented in Task 2

        from combination_gen import gen_comb_list
        comb = gen_comb_list(unique_values_list)

        # code that makes a call to combination_gen.gen_comb_list

        # Example output:
        # [['Southampton', 'M', '3'],
        #  ['Cherbourg', 'M', '3'],
        #  ...
        #  ['Queenstown', 'F', '1']]

        # code that filters each combination
        pivoted = []
        for i in comb:
            temp = self.filter(lambda x: x[keys_to_pivot_list[0]] == i[0])
            for j in range(1, len(keys_to_pivot_list)):
                temp = temp.filter(lambda x: x[keys_to_pivot_list[j]] == i[j])
            temp_list = []
            for a in range(len(keys_to_aggreagte_list)):
                result = temp.aggregate(aggregate_func_list[a], keys_to_aggreagte_list[a])
                temp_list.append(result)
            pivoted.append([i, temp_list])
        return pivoted
        # for each filter table applies the relevant aggregate functions
        # to keys to aggregate
        # the aggregate functions is listed in aggregate_func_list
        # to keys to aggregate is listed in keys_to_aggreagte_list

        # return a pivot table


    def __str__(self):
        return self.table_name + ':' + str(self.table)

table1 = Table('cities', CSV_Read('Cities').get_list)
table2 = Table('countries', CSV_Read('Countries').get_list)
table3 = Table('players', CSV_Read('Players').get_list)
table4 = Table('teams', CSV_Read('Teams').get_list)
table5 = Table('titanic', CSV_Read('Titanic').get_list)
my_DB = DB()
my_DB.insert(table1)
my_DB.insert(table2)
my_DB.insert(table3)
my_DB.insert(table4)
my_DB.insert(table5)

players = my_DB.search('players')
players_f = players.filter(lambda x: 'ia' in x['team'] 
                               and int(x['minutes']) < 200 
                               and int(x['passes']) > 100)\
                            .select(['surname', 'team', 'position'])
print('player on a team with “ia” in the team name played less \
than 200 minutes and made more than 100 passes')
print(players_f)
print()

teams = my_DB.search('teams')
teams_top = teams.filter(lambda x: int(x['ranking']) <= 10).aggregate(lambda y: sum(y) / len(y), 'games')
teams_kak = teams.filter(lambda x: int(x['ranking']) > 10).aggregate(lambda y: sum(y) / len(y), 'games')
print('The average number of games played for teams ranking below 10')
print(teams_top)
print('The average number of games played for teams ranking above or equal 10')
print(teams_kak)
print()

mid_pass = players.filter(lambda x: x['position'] == 'midfielder').aggregate(lambda y: sum(y) / len(y), 'passes')
fwd_pass = players.filter(lambda x: x['position'] == 'forward').aggregate(lambda y: sum(y) / len(y), 'passes')
print('The average number of passes made by forwards')
print(fwd_pass)
print('The average number of passes made by midfielders')
print(mid_pass)
print()

titanic = my_DB.search('titanic')
third_class_fare = titanic.filter(lambda x: x['class'] == '3').aggregate(lambda y: sum(y) / len(y), 'fare')
first_class_fare = titanic.filter(lambda x: x['class'] == '1').aggregate(lambda y: sum(y) / len(y), 'fare')
print('The average fare paid by passengers in the first class')
print(first_class_fare)
print('The average fare paid by passengers in the third class')
print(third_class_fare)
print()

survive_m = titanic.filter(lambda x: x['gender'] == 'M' and x['survived'] == 'yes').aggregate(lambda y: len(y), 'fare')
all_m = titanic.filter(lambda x: x['gender'] == 'M').aggregate(lambda y: len(y), 'fare')
print('The survival rate of male passengers')
print(survive_m/all_m * 100, '%')

survive_f = titanic.filter(lambda x: x['gender'] == 'F' and x['survived'] == 'yes').aggregate(lambda y: len(y), 'fare')
all_f = titanic.filter(lambda x: x['gender'] == 'F').aggregate(lambda y: len(y), 'fare')
print('The survival rate of female passengers')
print(survive_f/all_f * 100, '%')
print()

male_southampton = titanic.filter(lambda x: x['gender'] == 'M' and x['embarked'] == 'Southampton').aggregate(lambda y: len(y), 'fare')
print('The total number of male passengers embarked at Southampton')
print(male_southampton)

my_pivot = titanic.pivot_table(['embarked', 'gender', 'class'], 
                          ['fare', 'fare', 'fare', 'last'], 
                          [lambda x: min(x), lambda x: max(x), lambda x: sum(x)/len(x), lambda x: len(x)])
print(my_pivot)
# my_table1 = my_DB.search('cities')

# print("Test filter: only filtering out cities in Italy")
# my_table1_filtered = my_table1.filter(lambda x: x['country'] == 'Italy')
# print(my_table1_filtered)
# print()

# print("Test select: only displaying two fields, city and latitude, for cities in Italy")
# my_table1_selected = my_table1_filtered.select(['city', 'latitude'])
# print(my_table1_selected)
# print()

# print("Calculting the average temperature without using aggregate for cities in Italy")
# temps = []
# for item in my_table1_filtered.table:
#     temps.append(float(item['temperature']))
# print(sum(temps)/len(temps))
# print()

# print("Calculting the average temperature using aggregate for cities in Italy")
# print(my_table1_filtered.aggregate(lambda x: sum(x)/len(x), 'temperature'))
# print()

# print("Test join: finding cities in non-EU countries whose temperatures are below 5.0")
# my_table2 = my_DB.search('countries')
# my_table3 = my_table1.join(my_table2, 'country')
# my_table3_filtered = my_table3.filter(lambda x: x['EU'] == 'no').filter(lambda x: float(x['temperature']) < 5.0)
# print(my_table3_filtered.table)
# print()
# print("Selecting just three fields, city, country, and temperature")
# print(my_table3_filtered.select(['city', 'country', 'temperature']))
# print()

# print("Print the min and max temperatures for cities in EU that do not have coastlines")
# my_table3_filtered = my_table3.filter(lambda x: x['EU'] == 'yes').filter(lambda x: x['coastline'] == 'no')
# print("Min temp:", my_table3_filtered.aggregate(lambda x: min(x), 'temperature'))
# print("Max temp:", my_table3_filtered.aggregate(lambda x: max(x), 'temperature'))
# print()

# print("Print the min and max latitude for cities in every country")
# for item in my_table2.table:
#     my_table1_filtered = my_table1.filter(lambda x: x['country'] == item['country'])
#     if len(my_table1_filtered.table) >= 1:
#         print(item['country'], my_table1_filtered.aggregate(lambda x: min(x), 'latitude'), my_table1_filtered.aggregate(lambda x: max(x), 'latitude'))
# print()
