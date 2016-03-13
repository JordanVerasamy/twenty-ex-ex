from tournamenttracker import TournamentTracker
import config
import pprint

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

K_FACTOR = 32

#order matters here!
tournament_urls = [
	'uwsmashclub-UWMelee25',
	'uwsmashclub-UWmelee26'
]

def get_delta_elo(winner_rating, loser_rating):
	return K_FACTOR / (1 + 10 ** ((winner_rating - loser_rating)/400))

tournament_trackers = map(lambda x: TournamentTracker(CHALLONGE_USERNAME, x, CHALLONGE_API_KEY), tournament_urls)

ratings = {}

for tt in tournament_trackers:
	tt.pull_matches()

	for player in tt.get_all_players():
		if player not in ratings:
			ratings[player] = 1200

	for match in tt.get_all_matches():
		delta_elo = get_delta_elo(ratings[match.winner], ratings[match.loser])
		ratings[match.winner] += delta_elo
		ratings[match.loser] -= delta_elo

for player in sorted(ratings, key=ratings.get, reverse=True):
	print player, ratings[player]
