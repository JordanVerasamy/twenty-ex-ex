import challonge
import time
import config
from tournamenttracker import TournamentTracker
from slackclient import SlackClient

username = config.challonge_username
tournament_url = ''

challonge_api_key = config.challonge_api_key
slack_api_token = config.slack_api_token

channel_name = config.channel_to_connect_to
channel_id = config.channels[channel_name]

tournament_trackers = []
slack_client = SlackClient(slack_api_token)

### ----- COMMANDS RECOGNIZED BY SLACKBOT ----- ###

def info_command(args):
	output_message = 'Here\'s a list of all the tournaments you\'re following right now:\n```'
	output_message += '\n'.join('{}'.format(tt.tournament_url) for tt in tournament_trackers)
	return output_message + '```'

def follow_command(args):
	tournament_trackers.append(TournamentTracker(username, args[0], challonge_api_key))
	return 'Started following `{}`!'.format(args[0])

def unfollow_command(args):
	#Not implemented!
	return 'No longer following `{}`'.format(args[0])

commands = {'info' : info_command,
            'follow' : follow_command,
            'unfollow' : unfollow_command}

### ------------------------------------------- ###

def execute_command(command, args):
	if command == 'help':
		output_message = 'Here\'s a list of available commands:\n```!20xx help\n'
		output_message += '\n'.join('!20xx {}'.format(c) for c in commands)
		output_message = output_message + '```'

	elif command in commands:
		output_message = commands[command](args)
	else:
		output_message = 'Couldn\'t recognize your command. Enter `!20xx help` for more info.'

	slack_client.rtm_send_message(channel_id, output_message)

def create_update_message(message_list, tournament_url):
	update_message = '```Updates about {}:\n\n'.format(tournament_url)
	for condensed_match in new_matches:
		update_message = update_message + str(condensed_match) + '\n'
	return update_message + '```'

### ------------------------------------------- ###

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
				update_message = create_update_message(new_matches, tournament_tracker.tournament_url)
				slack_client.rtm_send_message(channel_id, update_message)
				print 'Sent updates about `{}` to #{}!'.format(tournament_tracker.tournament_url, channel_name)

		time.sleep(3)
else:
	print 'Connection failed.'
