import json

# also need to trim nbsp characters from names

player_data = json.load(open("raw_player_data.json"))[0]
winners_qualified = player_data["winners-qual"][0]
losers_qualified = player_data["losers-qual"][0]

player_data["losers-r5"].remove(losers_qualified)
player_data["winners-r4"].remove(winners_qualified)

f = open('adj_player_data.json', 'w')
f.write(json.dumps(player_data))