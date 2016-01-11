import challonge
import time
import config
from tournamenttracker import TournamentTracker
from slackclient import SlackClient

challonge_username = config.challonge_username
challonge_api_key = config.challonge_api_key

slack_api_token = config.slack_api_token

channel_name = config.channel_to_connect_to
channel_id = config.channels[channel_name]

keyword = config.keyword

tournament_trackers = []

slack_client = SlackClient(slack_api_token)

### ----- COMMANDS RECOGNIZED BY SLACKBOT ----- ###

def help_command(args):
	output_message = 'Here\'s a list of available commands:\n```'
	output_message += '\n'.join('{} {} {}'.format(keyword, c, commands[c]['contract']) for c in commands)
	return output_message + '```'

def info_command(args):
	output_message = 'Here\'s a list of all the tournaments you\'re following right now:\n```'
	output_message += '\n'.join('{}: following {}'.format(tt.tournament_url, tt.players) for tt in tournament_trackers)
	return output_message + '```'

def track_command(args):
	for tournament_url in args:
		tournament_trackers.append(TournamentTracker(challonge_username, tournament_url, challonge_api_key))
	return 'Started tracking `{}`'.format('`, `'.join(args))

def untrack_command(args):
	global tournament_trackers
	tournament_trackers = filter(lambda tt: tt.tournament_url not in args, tournament_trackers)
	return 'No longer tracking `{}`'.format('`, `'.join(args))

def follow_command(args):
	players_to_follow = args[1:]
	for tt in tournament_trackers:
		if tt.tournament_url == args[0]:
			tt.follow_players(players_to_follow)
	return 'Now following `{}` in `{}`!'.format(', '.join('{}'.format(p) for p in players_to_follow), args[0])

def unfollow_command(args):
	players_to_unfollow = args[1:]
	for tt in tournament_trackers:
		if tt.tournament_url == args[0]:
			tt.unfollow_players(players_to_unfollow)
	return 'No longer following `{}` in `{}`!'.format(', '.join('{}'.format(p) for p in players_to_unfollow), args[0])

def details_command(args):
	for tt in tournament_trackers:
		#print tt
		#print args[0]
		if tt.tournament_url == args[0]:
			return tt.players

commands = {
	'help'    : {'function': help_command,     'contract': ''},
	'info'    : {'function': info_command,     'contract': ''},
	'track'   : {'function': track_command,    'contract': '<CHALLONGE_TOURNAMENT_URL>*'},
	'untrack' : {'function': untrack_command,  'contract': '<CHALLONGE_TOURNAMENT_URL>*'},
	'follow'  : {'function': follow_command,   'contract': '<CHALLONGE_TOURNAMENT_URL> <PLAYER_ID>*'},
	'unfollow': {'function': unfollow_command, 'contract': '<CHALLONGE_TOURNAMENT_URL> <PLAYER_ID>*'},
	'details' : {'function': details_command,  'contract': '<CHALLONGE_TOURNAMENT_URL>'}
}

### ------------------------------------------- ###

def execute_command(command, args):
	if command in commands:
		output_message = commands[command]['function'](args)
	else:
		output_message = 'Couldn\'t recognize your command. Enter `{} help` for more info.'.format(keyword)
	slack_client.rtm_send_message(channel_id, output_message)

def create_update_message(message_list, tournament_url):
	update_message = '```Updates about {}:\n\n'.format(tournament_url)
	update_message += '\n'.join(str(match) for match in message_list)
	return update_message + '```'

### ------------------------------------------- ###

if slack_client.rtm_connect():
	while True:
		new_messages = slack_client.rtm_read()

		for message in new_messages:
			if 'text' in message and 'channel' in message:
				if message['channel'] == channel_id:
					message_body = message['text'].split(' ')
					if message_body[0] == keyword:
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
