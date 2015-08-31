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

tournament_trackers = []
slack_client = SlackClient(slack_api_token)

def follow_tournament(tournament_url):
	tournament_trackers.append(TournamentTracker(username, tournament_url, challonge_api_key))

#def unfollow_tournament(tournament_url):
	#not implemented yet


def execute_command(command, args):
	if command == 'help':
		output_message = 'Here\'s a list of available commands:\n' + '```!20xx help\n' + '!20xx follow\n' + '!20xx unfollow```' 
	elif command == 'follow':
		follow_tournament(args[0])
		output_message = 'Started following `{}`!'.format(args[0])
	elif command == 'unfollow':
		#unfollow_tournament(args[0])
		output_message = 'No longer following `{}`'.format(args[0])
	elif command == 'info':
		output_message = 'Here\'s a list of all the tournaments you\'re following right now:\n```
		for tournament_tracker in tournament_trackers:
			output_message = output_message + '{}\n'.format(tournament_tracker.tournament_url)
		output_message = output_message + '```'
	else:
		output_message = 'Couldn\'t recognize your command. Enter `!20xx help` for more info.'

	slack_client.rtm_send_message(channel_id, output_message)

def create_update_message(message_list, tournament_url):
	update_message = '```Updates about '
	for condensed_match in new_matches:
		update_message = update_message + str(condensed_match) + '\n'
	return update_message + '```'

if slack_client.rtm_connect():
	while True:
		new_messages = slack_client.rtm_read()

		for message in new_messages:
			if 'text' in message and 'channel' in message:
				if message['channel'] == channel_id:
					message_body = message['text'].split(' ')
					if message_body[0] == '!20xx':
						execute_command(message_body[1], message_body[2:])

		for tournament_tracker in tournament_trackers:
			new_matches = tournament_tracker.pull_matches()
			if new_matches:
				slack_client.rtm_send_message(channel_id, create_update_message(new_matches, tournament_tracker.tournament_url))
				print 'Sent updates about `{}` to #{}!'.format(tournament_tracker.tournament_url, channel_name)

		time.sleep(2)
else:
	print "Connection failed."