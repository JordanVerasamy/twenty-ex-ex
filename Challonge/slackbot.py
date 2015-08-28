import challonge
import time
import config
from tournamenttracker import TournamentTracker
from slackclient import SlackClient

username = config.challonge_username
tournament_url = config.tournament_url
challonge_api_key = config.challonge_api_key
slack_api_token = config.slack_api_token

tournament_tracker = TournamentTracker(username, tournament_url, challonge_api_key)
slack_client = SlackClient(slack_api_token)

if slack_client.rtm_connect():
	while True:
		new_messages = slack_client.rtm_read()
		new_matches = tournament_tracker.pull_matches()

		for message in new_messages:
			if 'text' in message:
				if message['text'] == 'pls 20xx me' and message['channel'] == 'C051SG90S':
					slack_client.rtm_send_message('C051SG90S', 'you have been 20xx\'d')

		if new_matches:
			update_message = '```'
			for condensed_match in new_matches:
				update_message = update_message + str(condensed_match) + '\n'
			update_message = update_message + '```'
			slack_client.rtm_send_message('C051SG90S', update_message)
		else:
			print 'No new matches.'

		time.sleep(2)
else:
	print "Connection failed."