from tournamenttracker import TournamentTracker
import config
import random
import json
import re

### ------------------------------------------- ###

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

# The higher the K-factor, the more drastically ratings change after every individual match.
K_FACTOR = 15

# The number of times the program repeats every tournament.
ITERATIONS = 100

# Any gap between player ratings that is higher than this threshold marks a new tier.
TIER_THRESHOLD = 45

# The elo that a new player starts at before their first game.
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

with open('alt_tags.json', 'r') as data_file:
	alt_tags = json.load(data_file)

with open('ignore.json', 'r') as data_file:
	ignored = json.load(data_file)

tournament_trackers = map(lambda x: TournamentTracker(CHALLONGE_USERNAME, x, CHALLONGE_API_KEY), tournament_urls)
ratings = {}

### ------------------------------------------- ###

# consumes ratings of both players, outputs the amount that the winner's
# elo should increase and the loser's should decrease

def get_delta_elo(winner_rating, loser_rating):
	return K_FACTOR / (1 + 10 ** ((winner_rating - loser_rating)/400))

### ------------------------------------------- ###

# consumes the tag used by a player in tournament, returns that player's actual tag
# --uses the alt_tags list to figure out which players owns a given alternate tag
# --ignores whitespace and sponsor tags
# --ignores anything in enclosed in parentheses, such as pool placing or seed number
#
# for example, here's a tag: '(p8)ST | Life(s2)'
# get_real_tag would return 'Life'.

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


# Pull all match data from Challonge for all tournaments in `tournament_urls`.
# (See the TournamentTracker class for details)
for tt in tournament_trackers:
	print 'pulling... {}'.format(tt.tournament_url)
	tt.pull_matches()

for _ in range(ITERATIONS):

	# Every iteration, go through tournaments in a random order
	random.shuffle(tournament_trackers)

	for tt in tournament_trackers:
		print 'discombobulating using {u:25s}\'s gammas...'.format(u=tt.tournament_url)

		# Go through all players in the current tournament, assign them
		# 1200 elo if we don't have any data on them already
		for tag in tt.get_all_players():
			player = get_real_tag(tag)
			if player not in ratings and player not in ignored:
				ratings[player] = STARTING_ELO

		# Get a list of all matches from the tournament (we already pulled this from Challonge)
		matches = tt.get_all_matches()
		random.shuffle(matches)

		for match in matches:
			# Get tags of both players in the current match, calculate how much elo
			# should change hands, then add or deduct as necessary.
			if match.winner in ignored or match.loser in ignored:
				continue
			winner = get_real_tag(match.winner)
			loser = get_real_tag(match.loser)
			delta_elo = get_delta_elo(ratings[winner], ratings[loser])
			ratings[winner] += delta_elo
			ratings[loser] -= delta_elo

count = 1
last = -1

# iterate through all players, sorted by rating
for player in sorted(ratings, key=ratings.get, reverse=True):

	# If there's a big gap between the last player and this player, mark the
	# beginning of a new tier. Either way, output their rankings, elo scores, and tags
	if last - ratings[player] > TIER_THRESHOLD:
		print '---'
	print '{r:3.0f}:  {s:4.0f}  {p}'.format(r=count, s=ratings[player], p=player)

	last = ratings[player]
	count += 1
