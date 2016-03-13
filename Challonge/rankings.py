from tournamenttracker import TournamentTracker
import config
import random
import json
import pprint

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

K_FACTOR = 10

#order matters here!
tournament_urls = [
	'uwsmashclub-UWMelee25',
	'uwsmashclub-UWmelee26',
	'uwsmashclub-UWmelee27',
	'Crossroads2',
	'Crossroads3',
	'uwsmashclub-UWmelee28'
]

with open('alt_tags.json', 'r') as data_file:
	alt_tags = json.load(data_file)

pprint.pprint(alt_tags)

def get_delta_elo(winner_rating, loser_rating):
	return K_FACTOR / (1 + 10 ** ((winner_rating - loser_rating)/400))

def get_real_tag(tag):
	for player in alt_tags:
		if tag[tag.find('|')+1:].lower().replace(' ', '') == player.lower().replace(' ', ''):
			return player
		if tag[tag.find('|')+1:].lower().replace(' ', '') in map(lambda x: x.lower().replace(' ', ''), alt_tags[player]):
			return player
	return tag[tag.find('|')+1:].replace(' ', '')

tournament_trackers = map(lambda x: TournamentTracker(CHALLONGE_USERNAME, x, CHALLONGE_API_KEY), tournament_urls)

ratings = {}

for tt in tournament_trackers:
	print 'pulling... {}'.format(tt.tournament_url)
	tt.pull_matches()

for _ in range(1):
	random.shuffle(tournament_trackers)
	for tt in tournament_trackers:
		print 'discombobulating using {}\'s gammas...'.format(tt.tournament_url)

		for tag in tt.get_all_players():
			player = get_real_tag(tag)
			if player not in ratings:
				ratings[player] = 1200

		matches = tt.get_all_matches()
		random.shuffle(matches)

		for match in matches:
			winner = get_real_tag(match.winner)
			loser = get_real_tag(match.loser)
			delta_elo = get_delta_elo(ratings[winner], ratings[loser])
			ratings[winner] += delta_elo
			ratings[loser] -= delta_elo

print ''

for player in sorted(ratings, key=ratings.get, reverse=True):
	print player, ratings[player]
