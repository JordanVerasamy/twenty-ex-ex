points_by_placing = {1 : 400,
                     2 : 380,
                     3 : 360,
                     4 : 340,
                     5 : 320,
                     7 : 300,
                     9 : 280,
                    13 : 260,
                    17 : 240,
                    25 : 220,
                    33 : 200,
                    49 : 180,
                    65 : 160,
                    97 : 140,
                   129 : 120}

drafted_teams = {'Life' : ['PPMD', 
                       	   'Shroomed', 
                           'Darkrain'],
              'Salazar' : ['Hungrybox',
                           'Wizzrobe',
                           'PewPewU'],
              'Drolian' : ['Westballz',
                           'S2J',
                           'SFAT'],
                 'Mosh' : ['Mang0',
                           'Plup',
                           'Ken']}

player_placings = {1 : ['PPMD'],
                   2 : ['Mang0'],
                   3 : ['Hungrybox'],
                   4 : ['Westballz'],
                   5 : ['Plup', 
                        'Shroomed'],
                   7 : ['SFAT', 
                        'S2J'],
                   9 : ['Eddy Mexico',
                        'Zhu',
                        'Armada',
                        'Leffen'],
                  13 : ['Darkrain',
                        'Wizzrobe',
                        'Fiction',
                        'Mew2King'],
                  17 : ['Flash',
                        'Jaedong',
                        'Stork',
                        'Bisu'],
                  25 : ['PewPewU',
                        'Ken',
                        'MacD',
                        'Sethlon',
                        'KirbyKaze',
                        'Colbol',
                        'Axe',
                        'aMSa']}

def get_dict_key(dict, value):
	for key in dict:
		if value in dict[key]:
			return key
	#print "Value not found."
	return None

drafter_points_totals = {}

for placing in player_placings:
	for player in player_placings[placing]:
		drafter = get_dict_key(drafted_teams, player)
		if drafter == None:
			continue
		if drafter not in drafter_points_totals:
			drafter_points_totals[drafter] = 0
		drafter_points_totals[drafter] += points_by_placing[get_dict_key(player_placings, player)]

for drafter in drafter_points_totals:
	print '{} earned {} points'.format(drafter, drafter_points_totals[drafter])