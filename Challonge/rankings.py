from tournamenttracker import TournamentTracker
import config
import random
import json
import re

### ------------------------------------------- ###

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

# The higher the K-factor, the more drastically ratings change after every individual match.
K_FACTOR = 50

# The number of times the program repeats every tournament.
ITERATIONS = 400

# Any gap between player ratings that is higher than this threshold marks a new tier.
TIER_THRESHOLD = 30

# The elo that a new player starts at before their first game.
STARTING_ELO = 1200

### ------------------------------------------- ###

tournament_urls = [
	'uwsmashclub-UWMelee25',
	'uwsmashclub-UWmelee26',
	'uwsmashclub-UWmelee27',
	#'Crossroads2',
	#'Crossroads3',
	'uwsmashclub-UWmelee28',
	#'uwsmashclub-UWArcadian3'
]

with open('alt_tags.json', 'r') as data_file:
	alt_tags = json.load(data_file)

with open('ignore.json', 'r') as data_file:
	ignored = json.load(data_file)

tournament_trackers = map(lambda x: TournamentTracker(CHALLONGE_USERNAME, x, CHALLONGE_API_KEY), tournament_urls)

names = []
ratings = {}

### ------------------------------------------- ###

# consumes ratings of both players, outputs the amount that the winner's
# elo should increase and the loser's should decrease

def get_expected_score(player_rating, opponent_rating):
	return 1 / (1 + 10 ** ((opponent_rating - player_rating)/400))

def get_updated_elo(player_rating, opponent_rating, score):
	expected_score = get_expected_score(player_rating, opponent_rating)
	return player_rating + K_FACTOR * (score - expected_score)

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
	for player in names:
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

	for tt in tournament_trackers:
		print 'discombobulating using {u:25s}\'s gammas...'.format(u=tt.tournament_url)

		# Go through all players in the current tournament, assign them
		# 1200 elo if we don't have any data on them already
		for tag in tt.get_all_players():
			player = get_real_tag(tag)
			if player not in ratings and player not in ignored:
				ratings[player] = STARTING_ELO
			if player not in names and player not in ignored:
				names.append(player)

		# Get a list of all matches from the tournament (we already pulled this from Challonge)
		matches = tt.get_all_matches()
		random.shuffle(matches)

		for match in matches:
			# Get tags of both players in the current match, calculate how much elo
			# should change hands, then add or deduct as necessary.
			if match.winner_score == match.loser_score: # i.e. if someone was DQ'd or absent
				continue
			if match.winner in ignored or match.loser in ignored:
				continue

			winner = get_real_tag(match.winner)
			loser = get_real_tag(match.loser)
			score = match.winner_score / float((match.winner_score + match.loser_score))

			winner_rating = ratings[winner]
			loser_rating = ratings[loser]

			ratings[winner] = get_updated_elo(winner_rating, loser_rating, score)
			ratings[loser] = get_updated_elo(loser_rating, winner_rating,  1 - score)

		# Every iteration after the first, go through tournaments in a random order
		random.shuffle(tournament_trackers)

count = 1
last = -1

with open('players.txt', 'w') as outfile:

	# iterate through all players, sorted by rating
	for player in sorted(ratings, key=ratings.get, reverse=True):

		# If there's a big gap between the last player and this player, mark the
		# beginning of a new tier. Either way, output their rankings, elo scores, and tags
		if last - ratings[player] > TIER_THRESHOLD:
			outfile.write('---\n')
		outfile.write('{r:3.0f}:  {s:4.0f}  {p}\n'.format(r=count, s=ratings[player], p=player))

		last = ratings[player]
		count += 1

print '\nfully discombobulated!'
