import challonge
import time
import config
from tournamenttracker import TournamentTracker
from slackclient import SlackClient

username = config.challonge_username
#tournament_url = config.tournament_url
tournament_url = ''

challonge_api_key = config.challonge_api_key
slack_api_token = config.slack_api_token

channel_name = config.channel_to_connect_to
channel_id = config.channels[channel_name]

tournament_tracker = TournamentTracker(username, tournament_url, challonge_api_key)
slack_client = SlackClient(slack_api_token)

def execute_command(command, args):
	output_message = ''
	# slack_client.rtm_send_message(channel_id, 
	#                               'executing command `{}` with args `{}`'.format(command, args))
	if command == 'help':
		output_message = 'Here\'s a list of available commands:\n' + '```!20xx help\n' + '!20xx follow\n' + '!20xx unfollow```' 
	elif command == 'follow':
		tournament_tracker.tournament_url = args[0]
		output_message = 'Started following `{}`!'.format(args[0])
	elif command == 'unfollow':
		tournament_tracker.tournament_url = ''
		output_message = 'No longer following any tournament.'

	slack_client.rtm_send_message(channel_id, output_message)

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
			if 'text' in message and 'channel' in message:
				if message['channel'] == channel_id:
					message_body = message['text'].split(' ')
					if message_body[0] == '!20xx':
						execute_command(message_body[1], message_body[2:])

		if new_matches:
			slack_client.rtm_send_message(channel_id, create_update_message(new_matches))
			print 'Sent updates to #{}!'.format(channel_name)
		else:
			print 'No new matches.'

		time.sleep(2)
else:
	print "Connection failed."