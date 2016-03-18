from barnum import gen_data
import numpy as np
import random
import sys
import os
from matplotlib import pyplot as plt
import pymongo
client = pymongo.MongoClient('localhost:27017')
db = client.dev

SIGMA = 10
# Number of players created via draft
NUM_OF_PLAYERS = 450

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
    os.system('cls' if os.name == 'nt' else 'clear')

# Create an empty json shell for the player data
# [May be redundant]
def create_player(potential_overall, name, draft_year, drafted_by):
    keys = ("attributes", "potential_overall", "id", "name", "draft_year")
    player = dict.fromkeys(keys, None)
    attribute_keys = ("offense", "defense", "athleticism", "attitude")
    offense_keys = ("puck_control",
                    "deking",
                    "hand_eye_coordination",
                    "offensive_awareness",
                    "passing",
                    "shooting_accuracy",
                    "shooting_power")
    defense_keys = ("body_checking",
                    "stick_checking",
                    "defensive_awareness",
                    "shot_blocking",
                    "positioning")
    athleticism_keys = ("acceleration",
                        "agility",
                        "balance",
                        "durability",
                        "endurance",
                        "top_speed",
                        "strength")
    attitude_keys = ("leadership",
                     "aggressiveness",
                     "poise",
                     "self_control",
                     "confidence",
                     "work_ethic")
    player["attributes"] = dict.fromkeys(attribute_keys, None)
    player["attributes"]["offense"] = dict.fromkeys(offense_keys, None)
    player["attributes"]["defense"] = dict.fromkeys(defense_keys, None)
    player["attributes"]["athleticism"] = dict.fromkeys(athleticism_keys, None)
    player["attributes"]["attitude"] = dict.fromkeys(attitude_keys, None)
    player["potential_overall"] = potential_overall
    player["draft_year"] = draft_year
    player["drafted_by"] = drafted_by
    player["name"] = name
    return player

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
    x = np.random.normal_variate(mean, SIGMA)
    while x > mean+4 or x < mean-4:
        x = np.random.normalvariate(mean, SIGMA)
    return x

def get_teams_json():
    teams = []
    for val in range(len(teams_list)):
        elements =  {}
        elements['team'] = teams_list[val]
        # uuid.uuid4 should have a seed to be safe from generating two identical IDs
        # elements['id'] = str(uuid.uuid4())
        teams.append(elements)
    return teams

def create_players_via_draft_batch(start, end):
    list_of_players = [{}]
    players_overalls = create_player_attributes(create_players_via_draft_batch_overalls(72, NUM_OF_PLAYERS))
    for year in range(start, end):
        for i in range(NUM_OF_PLAYERS):
            potential_overall = int(players_overalls[i][0])
            name = gen_data.create_name()
            list_of_players.append(create_player(name=name,
                                                 potential_overall=potential_overall,
                                                 draft_year=year,
                                                 drafted_by=None))
            i += 1
        print("Year: ", year)
        print("Num of players: ", i)
        year += 1

    return list_of_players

def create_draft_order():
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
    bulk = db.players.initialize_unordered_bulk_op();
    draft_num = 1
    for player in cursor:
        bulk.find({"_id": player["_id"]}).\
            update({"$set": {"drafted_by": draft_order["order"][draft_num]}})
        draft_num += 1
        if draft_num >= 31:
            draft_num = 1
    results = bulk.execute()

if __name__ == "__main__":

    #
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
