# encoding=utf-8

import pymongo
import numpy as np
import random
import csv
import json
import sys
import os
from barnum import gen_data
from matplotlib import pyplot as plt
from src.db import connect
conn = connect('localhost:27017')
db = conn.get_database

SIGMA = 10
# Number of players created via draft
NUM_OF_PLAYERS = 450

# Player attributes
player_attribute_keys = ("offense",
                         "defense",
                         "athleticism",
                         "attitude")

# Player offense attributes
player_offense_keys = ("puck_control",
                       "deking",
                       "hand_eye_coordination",
                       "offensive_awareness",
                       "passing",
                       "shooting_accuracy",
                       "shooting_power")

# Player defense attributes
player_defense_keys = ("body_checking",
                       "stick_checking",
                       "defensive_awareness",
                       "shot_blocking",
                       "positioning")

# Player athleticism attributes
player_athleticism_keys = ("acceleration",
                           "agility",
                           "balance",
                           "durability",
                           "endurance",
                           "top_speed",
                           "strength")

# Player attitude attributes
player_attitude_keys = ("leadership",
                        "aggressiveness",
                        "poise",
                        "self_control",
                        "confidence",
                        "work_ethic")

# List of teams
teams_list = ["Nashville Predators",
              "Anaheim Ducks",
              "San Jose Sharks",
              "Montreal Canadiens",
              "Vancouver Canucks",
              "Toronto Maple Leafs",
              "Los Angeles Kings",
              "New York Rangers",
              "New York Islanders",
              "Washington Capitals",
              "Carolina Hurricanes",
              "Florida Panthers",
              "Tampa Bay Lightning",
              "Winnipeg Jets",
              "Dallas Stars",
              "Calgary Flames",
              "Edmonton Oilers",
              "Arizona Coyotes",
              "St. Louis Blues",
              "Chicago Blackhawks",
              "Minnesota Wild",
              "Colorado Avalanche",
              "Boston Bruins",
              "Ottawa Senators",
              "Pittsburgh Penguins",
              "Philadelphia Flyers",
              "Detroit Red Wings",
              "New Jersey Devils",
              "Columbus Blue Jackets"]


def cls():
    """
    Clear the CLI
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class Player(object):
    """ A player of a hockey team.

    Attributes:
        first_name: A string representing player's first name.
        last_name: A string representing player's last name.
        overall : An integer representing player's potential overall ability.
        draft_year : An integer representing player's draft year.
    """

    def __init__(self, overall, first_name, last_name, draft_year):
        self.id = id
        self.overall = overall
        self.first_name = first_name
        self.last_name = last_name
        self.draft_year = draft_year
        self.drafted_by = None
        self.attributes = []
        self.attributes = dict.fromkeys(player_attribute_keys, None)
        self.attributes["offense"] = dict.fromkeys(player_offense_keys, None)
        self.attributes["defense"] = dict.fromkeys(player_defense_keys, None)
        self.attributes["athleticism"] = dict.fromkeys(player_athleticism_keys, None)
        self.attributes["attitude"] = dict.fromkeys(player_attitude_keys, None)

    def get_overall(self):
        return self.overall


# Create player overalls according to Poisson-distribution
def create_players_via_draft_batch_overalls(mean, number_of_players):
    return np.random.poisson(mean, size=number_of_players).tolist()


# Create player attributes derived from the overall
def create_player_attributes(draft_class):
    draft_class_with_attrs = []
    i = 0
    """Yield successive n-sized chunks from l."""
    while i < len(draft_class):
        draft_class_with_attrs.append(draft_class[i:i + 1])
        i += 1
    return draft_class_with_attrs


# Create a value for a player attribute from a normal distribution
def generate_number(mean):
    x = np.random.normal(mean, SIGMA)
    while x > mean+4 or x < mean-4:
        x = np.random.normal(mean, SIGMA)
    return x

# dump teams_list to json
def get_teams_json():
    return json.dumps(teams_list)

def get_player_names(num_of_players):
    names = []
    with open('player_names.csv', 'rb') as f:
        reader = csv.reader(f)
        try:
            for row in reader:
                print(row)
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % ('player_names.csv', reader.line_num, e))
        random.randint(1, 10)


def create_players_via_draft_batch(start, end):
    list_of_players = []
    players_overalls = create_player_attributes(create_players_via_draft_batch_overalls(72, NUM_OF_PLAYERS))
    number_of_draft_classes = range(start, end)
    # gen names for each player:
    list_of_names = get_player_names(number_of_draft_classes * NUM_OF_PLAYERS)
    for year in number_of_draft_classes:
        for i in range(NUM_OF_PLAYERS):
            potential_overall = int(players_overalls[i][0])
            name = gen_data.create_name()
            list_of_players.append(Player(name=name,
                                          potential_overall=potential_overall,
                                          draft_year=year,
                                          drafted_by=None))
            i += 1
        print("Year: ", year)
        print("Num of players: ", i)
        year += 1

    return list_of_players

def create_draft_order():
    """

    """
    draft_template = dict.fromkeys(("year", "order"), None)
    draft_order_list = list(range(1, 31))
    draft_template["order"] = dict.fromkeys(draft_order_list, None)
    random_draft_order = random.sample(teams_list, len(teams_list))
    i = 0
    for team in teams_list:
        draft_template["order"][i+1] = random_draft_order[i]
        i += 1
    return draft_template

def draft_players_to_teams(draft_year):
    """
    1. Query all players, order by potential
    2. Random draft order to each team
    3. Assign draft info to each player
    """
    # draft results to roster later on
    draft_order = create_draft_order()
    # print(draft_order)
    cursor = db.players.find({"draft_year": draft_year}).sort([("potential_overall", pymongo.DESCENDING)])
    # Initialize a bulk op for updating the players' draft info
    bulk = db.players.initialize_unordered_bulk_op()
    draft_num = 1
    for player in cursor:
        bulk.find({"_id": player["_id"]}).\
            update({"$set": {"drafted_by": draft_order["order"][draft_num]}})
        draft_num += 1
        if draft_num >= 31:
            draft_num = 1
    bulk.execute()

def main():
    while True:
        try:
            # cls()
            print("Commands:")
            print("1. Create a draft class of players.")
            print("2. Create multiple draft classes.")
            print("3. Create multiple draft classes and save them to MongoDB.")
            print("4. Create teams and save them to MongoDB.")
            print("5. Draft the players to each team according to potential and "
                  "update the drafted_by-field on MongoDB.")
            # print("6. Update the attributes for each player")
            print("0. Exit.")
            value = input()

            if value == "1":
                samples = create_players_via_draft_batch_overalls(70, NUM_OF_PLAYERS)
                print(samples)
                count, bins, ignored = plt.hist(samples, 40, normed=True)
                plt.show()

            elif value == "2":
                players = create_players_via_draft_batch(start=2015, end=2016)

            elif value == "3":
                db.players.insert_many(create_players_via_draft_batch(start=2015, end=2016))

            elif value == "4":
                db.teams.insert_many(get_teams_json())

            elif value == "5":
                draft_players_to_teams(2015)

            elif value == "0":
                client.close()
                break

        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        except ValueError:
            print("Could not convert data to an integer.")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

if __name__ == '__main__':
    main()