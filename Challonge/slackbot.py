import challonge
import time
import config
from tournamenttracker import TournamentTracker
from pyslack import SlackClient

username = config.challonge_username
tournament_url = config.tournament_url
challonge_api_key = config.challonge_api_key
slack_api_token = config.slack_api_token

tournament_tracker = TournamentTracker(username, tournament_url, challonge_api_key)

client = SlackClient(slack_api_token)
client.chat_post_message('#smash', "I am 20XX-bot. Welcome to the real world.", username='20XX-Bot')

while True:
	newest_matches = tournament_tracker.pull_matches()
	if newest_matches:
		for condensed_match in newest_matches:
			print(condensed_match)
	else:
		print 'No new matches.'
	time.sleep(5)