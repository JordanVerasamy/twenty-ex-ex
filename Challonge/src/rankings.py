from tournamenttracker import TournamentTracker
import config
import random
import json
import re
import math

### ------------------------------------------- ###

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

# The higher the K-factor, the more drastically ratings change after every individual match.
K_FACTOR = 10

# The number of times the program repeats every tournament.
ITERATIONS = 200

# The number of times the program repeats the entire process
SUPER_ITERATIONS = 2

# Any gap between player ratings that is higher than this threshold marks a new tier.
TIER_THRESHOLD = 25

# The elo that a new player starts at before their first game.
STARTING_ELO = 1200

OUTPUT_FILE = 'rankings'

TOURNAMENT_URLS = [
	'Crossroads3',
	'uwsmashclub-UWmelee28',
	'uwsmashclub-UWmelee29',
	'Crossroads4',
	'Crossroads5'
]

NEW_TOURNAMENTS = [
]

with open('json/alt_tags.json', 'r') as data_file:
	ALT_TAGS = json.load(data_file)

with open('json/ignore.json', 'r') as data_file:
	IGNORE_LIST = json.load(data_file)

with open('json/special_cases.json', 'r') as data_file:
	SPECIAL_CASES = json.load(data_file)

names = []

### ------------------------------------------- ###

# helper for get_updated_elo. returns expected score \in [0,1] between players

def get_expected_score(player_rating, opponent_rating):
	return 1 / (1 + 10 ** ((opponent_rating - player_rating)/400))

# consumes ratings of both players, outputs the amount that the winner's
# elo should increase and the loser's should decrease

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

def get_real_tag(tag, tournament_url):

	if tournament_url in SPECIAL_CASES:
		if tag in SPECIAL_CASES[tournament_url]:
			return SPECIAL_CASES[tournament_url][tag]

	base_tag = tag[tag.find('|')+1:].lower().replace(' ', '')
	base_tag = re.sub('\(\w*\)', '', base_tag)
	for player in ALT_TAGS:
		if base_tag == player.lower().replace(' ', ''):
			return player
		if base_tag in map(lambda x: x.lower().replace(' ', ''), ALT_TAGS[player]):
			return player
	for player in names:
		if base_tag == player.lower().replace(' ', ''):
			return player
	return re.sub('\(\w*\)', '', tag[tag.find('|')+1:].replace(' ', ''))

### ------------------------------------------- ###

# returns true if and only if `tag` is in `ignored` while ignoring case

def ignored(tag):
	return tag.lower() in map(lambda x: x.lower(), IGNORE_LIST)

### ------------------------------------------- ###

def get_score(winner_score, loser_score):
	#return winner_score / float(winner_score + loser_score)
	return math.sqrt(winner_score / float(winner_score + loser_score))

### ------------------------------------------- ###

# computes and returns a single dict mapping players to elo ratings

def compute_single_ratings(tournament_trackers):
	ratings = {}

	for _ in xrange(ITERATIONS):

		for tt in tournament_trackers:

			#print 'discombobulating using {u:25s}\'s gammas...'.format(u=tt.tournament_url)

			# Go through all players in the current tournament, assign them
			# 1200 elo if we don't have any data on them already
			for tag in tt.get_all_players():
				player = get_real_tag(tag, tt.tournament_url)

				if player not in ratings and not ignored(player):
					ratings[player] = STARTING_ELO
				if player not in names and not ignored(player):
					names.append(player)

			# Get a list of all matches from the tournament (we already pulled this from Challonge)
			matches = tt.get_all_matches()
			random.shuffle(matches)

			for match in matches:

				winner = get_real_tag(match.winner, tt.tournament_url)
				loser = get_real_tag(match.loser, tt.tournament_url)

				# Get tags of both players in the current match, calculate how much elo
				# should change hands, then add or deduct as necessary.
				if match.winner_score == match.loser_score: # i.e. if someone was DQ'd or absent
					continue
				if ignored(winner) or ignored(loser):
					continue

				score = get_score(match.winner_score, match.loser_score)

				winner_rating = ratings[winner]
				loser_rating = ratings[loser]

				ratings[winner] = get_updated_elo(winner_rating, loser_rating, score)
				ratings[loser] = get_updated_elo(loser_rating, winner_rating,  1 - score)

			# Every iteration after the first, go through tournaments in a random order
			random.shuffle(tournament_trackers)

	return ratings

### ------------------------------------------- ###

# consumes multiple dicts, each of which maps players to elo ratings, and returns a dict
# that maps players to their average elo ratings

def combine_ratings(ratings_list):
	ret = {}
	for ratings in ratings_list:
		for player in ratings:
			if player in ret:
				ret[player] += ratings[player]
			else:
				ret[player] = ratings[player]
	for player in ret:
		ret[player] /= len(ratings_list)
	return ret

### ------------------------------------------- ###

# runs compute_single_ratings a bunch of times,
# then combines them all using combine_ratings

def compute_aggregate_ratings(tournament_trackers):
	ratings_list = []

	for i in xrange(SUPER_ITERATIONS):
		ratings_list.append(compute_single_ratings(tournament_trackers))
		print 'completed superiteration {}...'.format(i)

	return combine_ratings(ratings_list)

### ------------------------------------------- ###

# consumes an old ratings dict and a new ratings dict, returns a dict mapping players
# to a string representing how they moved between the old and new ratings

# for example, if a player moved up a lot in the rankings, this will return '+++'

def get_movement(old_ratings, ratings):
	movement = {}
	adj = 0

	old_rankings = sorted(old_ratings, key=old_ratings.get, reverse=True)
	rankings = sorted(ratings, key=ratings.get, reverse=True)

	for player in rankings:
		if player not in old_ratings:
			movement[player] = 'NEW'
			adj += 1
			continue
		difference = old_rankings.index(player) + adj - rankings.index(player)
		if abs(difference) <= 1:
			movement[player] = '   '
		elif difference > 5:
			movement[player] = '+++'
		elif difference < -5:
			movement[player] = '---'
		elif difference > 3:
			movement[player] = '++ '
		elif difference < -3:
			movement[player] = '-- '
		elif difference > 1:
			movement[player] = ' + '
		elif difference < -1:
			movement[player] = ' - '

	return movement

### ------------------------------------------- ###

# write the elo ratings of everyone in ratings in a nice format to OUTPUT_FILE

def write_ratings_to_file(ratings, movement, OUTPUT_FILE):

	count = 1
	last = -1

	with open(OUTPUT_FILE, 'w') as outfile:

		# iterate through all players, sorted by rating
		for player in sorted(ratings, key=ratings.get, reverse=True):

			# If there's a big gap OUTPUT_TYPE = 'HTML'
			if last - ratings[player] > TIER_THRESHOLD:
				outfile.write('---\n')

			if movement:
				outfile.write('{r:3.0f}:  {s:4.0f}  {m}  {p}\n'.format(r=count, s=ratings[player], m=movement[player], p=player))
			else:
				outfile.write('{r:3.0f}:  {s:4.0f}       {p}\n'.format(r=count, s=ratings[player], p=player))

			last = ratings[player]
			count += 1

### ------------------------------------------- ###Tag

def write_ratings_to_html(ratings, movement, OUTPUT_FILE):

	count = 1
	last = -1

	with open(OUTPUT_FILE, 'w') as outfile:

		# iterate through all players, sorted by rating
		for player in sorted(ratings, key=ratings.get, reverse=True):

			outfile.write('<tr>\n')

			# If there's a big gap between the last player and this player, mark the
			# beginning of a new tier. Either way, output their rankings, elo scores, and tags
			#if last - ratings[player] > TIER_THRESHOLD:
			#	outfile.write('---\n')

			if movement:
				outfile.write('<td>{r:3.0f}</td>\n<td>{s:4.0f}</td>\n<td>{m}</td>\n<td>{p}</td>\n'.format(r=count, s=ratings[player], m=movement[player], p=player))
			else:
				outfile.write('<td>{r:3.0f}</td>\n<td>{s:4.0f}</td>\n<td>{p}</td>\n'.format(r=count, s=ratings[player], p=player))

			last = ratings[player]
			count += 1

			outfile.write('</tr>\n')

### ------------------------------------------- ###

print 'mapping constructors...'
tournament_trackers = map(lambda x: TournamentTracker(CHALLONGE_USERNAME, x, CHALLONGE_API_KEY), TOURNAMENT_URLS)
new_tts = map(lambda x: TournamentTracker(CHALLONGE_USERNAME, x, CHALLONGE_API_KEY), NEW_TOURNAMENTS)
print 'done.'

# Pull all match data from Challonge for all tournaments in `tournament_urls`.
# (See the TournamentTracker class for details)
for tt in tournament_trackers + new_tts:
	print 'pulling... {}'.format(tt.tournament_url)
	tt.pull_matches()

# if there are new tournaments, compute ratings with and without them separately (so we can compute movement)
if new_tts:
	old_ratings = compute_aggregate_ratings(tournament_trackers)
	ratings = compute_aggregate_ratings(tournament_trackers + new_tts)
	movement = get_movement(old_ratings, ratings)
else:
	ratings = compute_aggregate_ratings(tournament_trackers)
	movement = False

# print results to file, then exit
write_ratings_to_html(ratings, movement, '{}.html'.format(OUTPUT_FILE))
write_ratings_to_file(ratings, movement, '{}.txt'.format(OUTPUT_FILE))

print '\nfully discombobulated!'
