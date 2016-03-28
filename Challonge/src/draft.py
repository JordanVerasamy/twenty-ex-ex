import json
import pprint

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

drafters = {
	'Life',
	'Drolian',
	'Root'
}

players = [
	{
		'name' : 'S2J',
		'drafter' : 'Life',
		'worst_possible_placing' : 17
	},
	{
		'name' : 'Armada',
		'drafter' : 'Drolian',
		'worst_possible_placing' : 3
	},
	{
		'name' : 'Westballz',
		'drafter' : 'Root',
		'worst_possible_placing' : 13
	},
	{
		'name' : 'Mew2King',
		'drafter' : 'Life',
		'worst_possible_placing' : 5
	},
	{
		'name' : 'Axe',
		'drafter' : 'Drolian',
		'worst_possible_placing' : 17
	},
	{
		'name' : 'Leffen',
		'drafter' : 'Root',
		'worst_possible_placing' : 2
	},
]

for drafter in drafters:
	for player in players:
		if player['drafter'] == drafter:
			drafters[drafter] += points_by_placing[player['worst_possible_placing']]
	print '{} earns {} points at fewest.'.format(drafter, drafters[drafter])
