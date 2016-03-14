from tournamenttracker import TournamentTracker
import config
import random
import json
import pprint
import re

### ------------------------------------------- ###

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

K_FACTOR = 35
ITERATIONS = 100
TIER_THRESHOLD = 60
STARTING_ELO = 1200

### ------------------------------------------- ###

tournament_urls = [
	'uwsmashclub-UWMelee25',
	'uwsmashclub-UWmelee26',
	'uwsmashclub-UWmelee27',
	'Crossroads2',
	'Crossroads3',
	'uwsmashclub-UWmelee28',
	'uwsmashclub-UWArcadian3'
]

tournament_trackers = map(lambda x: TournamentTracker(CHALLONGE_USERNAME, x, CHALLONGE_API_KEY), tournament_urls)
ratings = {}

### ------------------------------------------- ###

def get_delta_elo(winner_rating, loser_rating):
	return K_FACTOR / (1 + 10 ** ((winner_rating - loser_rating)/400))

def get_real_tag(tag):
	base_tag = tag[tag.find('|')+1:].lower().replace(' ', '')
	base_tag = re.sub('\(\w*\)', '', base_tag)
	for player in alt_tags:
		if base_tag == player.lower().replace(' ', ''):
			return player
		if base_tag in map(lambda x: x.lower().replace(' ', ''), alt_tags[player]):
			return player
	for player in ratings:
		if base_tag == player.lower().replace(' ', ''):
			return player
	return re.sub('\(\w*\)', '', tag[tag.find('|')+1:].replace(' ', ''))

### ------------------------------------------- ###

with open('alt_tags.json', 'r') as data_file:
	alt_tags = json.load(data_file)

for tt in tournament_trackers:
	print 'pulling... {}'.format(tt.tournament_url)
	tt.pull_matches()

for _ in range(ITERATIONS):

	random.shuffle(tournament_trackers)

	for tt in tournament_trackers:
		print 'discombobulating using {}\'s gammas...'.format(tt.tournament_url)

		for tag in tt.get_all_players():
			player = get_real_tag(tag)
			if player not in ratings:
				ratings[player] = STARTING_ELO

		matches = tt.get_all_matches()
		random.shuffle(matches)

		for match in matches:
			winner = get_real_tag(match.winner)
			loser = get_real_tag(match.loser)
			delta_elo = get_delta_elo(ratings[winner], ratings[loser])
			ratings[winner] += delta_elo
			ratings[loser] -= delta_elo

print ''
count = 1
last = -1

for player in sorted(ratings, key=ratings.get, reverse=True):

	if last - ratings[player] > TIER_THRESHOLD:
		print '---'

	print '{r:3.0f}:  {s:4.0f}  {p}'.format(r=count, s=ratings[player], p=player)
	last = ratings[player]
	count += 1
