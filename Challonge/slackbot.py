import challonge
import time
import config
from tournamenttracker import TournamentTracker
from slackclient import SlackClient

username = config.challonge_username
tournament_url = config.tournament_url

challonge_api_key = config.challonge_api_key
slack_api_token = config.slack_api_token

channel_name = config.channel_to_connect_to
channel_id = config.channels[channel_name]

tournament_tracker = TournamentTracker(username, tournament_url, challonge_api_key)
slack_client = SlackClient(slack_api_token)

def execute_command(command):
	slack_client.rtm_send_message(channel_id, 'executing command {}'.format(command))

def create_update_message(message_list):
	update_message = '```'
	for condensed_match in new_matches:
		update_message = update_message + str(condensed_match) + '\n'
	return update_message + '```'

if slack_client.rtm_connect():
	while True:
		new_messages = slack_client.rtm_read()
		new_matches = tournament_tracker.pull_matches()

		for message in new_messages:
			if 'text' in message and message['channel'] == channel_id and message['text'][:5] == '!20xx':
				execute_command(message['text'][5:])

		if new_matches:
			update_message = create_update_message(new_matches)
			slack_client.rtm_send_message(channel_id, update_message)
			print 'Sent updates to #{}!'.format(channel_name)
		else:
			print 'No new matches.'

		time.sleep(2)
else:
	print "Connection failed."