import challonge
import time
import config
from tournamenttracker import TournamentTracker

username = config.challonge_username
tournament_url = config.tournament_url
api_key = config.challonge_api_key

tournament_tracker = TournamentTracker(username, tournament_url, api_key)

while True:
	newest_matches = tournament_tracker.pull_matches()
	if newest_matches:
		for condensed_match in newest_matches:
			print(condensed_match)
	else:
		print 'No new matches.'
	time.sleep(5)