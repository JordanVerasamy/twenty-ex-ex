import sys
import traceback
import challonge
import time
import config
import httplib

from tournamenttracker import TournamentTracker
from slackclient import SlackClient

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

SLACK_API_TOKEN = config.SLACK_API_TOKEN

CHANNEL_NAME = config.CHANNEL_TO_CONNECT_TO
CHANNEL_ID = config.CHANNELS[CHANNEL_NAME]

KEYWORD = config.KEYWORD
ADMIN_NAME = config.ADMIN_NAME

tournament_trackers = []

slack_client = SlackClient(slack_api_token)

### ------------------------------------------- ###

def get_status_code(host, path="/"):
    try:
        conn = httplib.HTTPConnection(host)
        conn.request("HEAD", path)
        return conn.getresponse().status
    except StandardError:
        traceback.print_exc()
        return None

class TournamentDoesNotExistError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

### ----- COMMANDS RECOGNIZED BY SLACKBOT ----- ###

def help_command(args):
	output_message = 'Here\'s a list of available commands:\n```'
	output_message += '\n'.join('{} {} {}'.format(keyword, c, commands[c]['contract']) for c in commands)
	return output_message + '```'

def status_command(args):
	if not tournament_trackers:
		return 'Not currently following any tournaments!'
	output_message = 'Here\'s a list of all the tournaments you\'re following right now:\n```'
	output_message += '\n'.join('{}: following {}'.format(tt.tournament_url, tt.players) for tt in tournament_trackers)
	return output_message + '```'

def details_command(args):
	output_message = 'Here\'s a list of all the players in `{}` you\'re following: `'.format(args[0])
	for tt in tournament_trackers:
		if tt.tournament_url == args[0]:
			if not tt.players:
				return 'You are not following any players in `{}`'.format(args[0])
			output_message += ', '.join('{}'.format(p) for p in tt.players)
	return output_message + '`'

def track_command(args): #TODO: make this work with Challonge subdomains
	failed = []
	for tournament_url in args:
		status_code = get_status_code('challonge.com', '/{}'.format(tournament_url))
		print status_code
		if status_code == 200:
			tournament_trackers.append(TournamentTracker(challonge_username, tournament_url, challonge_api_key))
		else:
			failed.append(tournament_url)
	if failed:
		raise TournamentDoesNotExistError(failed)

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

commands = {
	'help'    : {'function': help_command,     'contract': ''},
	'status'  : {'function': status_command,   'contract': ''},
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
	slack_client.rtm_send_message(CHANNEL_ID, output_message)

def create_update_message(message_list, tournament_url, players):
	update_message = '```Updates about {}:\n\n'.format(tournament_url)
	update_message += '\n'.join(str(match) for match in message_list)
	return update_message + '```'

### ------------------------------------------- ###

print 'Attempting to connect...'
if slack_client.rtm_connect():
	print 'Connection successful.'
	while True:
		try:
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
					update_message = create_update_message(new_matches, tournament_tracker.tournament_url, tournament_tracker.players)
					slack_client.rtm_send_message(channel_id, update_message)

		except TournamentDoesNotExistError as e:
			slack_client.rtm_send_message(CHANNEL_ID, "Your command failed to execute because the following tournaments don't exist:")
			slack_client.rtm_send_message(CHANNEL_ID, '`{}`'.format(', '.join(e.value)))
			traceback.print_exc()

		except Exception:
			print 'Error encountered.'
			slack_client.rtm_send_message(CHANNEL_ID, 'Error encountered... @{}, look at the logs pls.'.format(ADMIN_NAME))
			#exc_type, exc_value, exc_traceback = sys.exc_info()
    		#lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    		#print ''.join('!! ' + line for line in lines)
			traceback.print_exc()
			break

		time.sleep(2)
else:
	print 'Connection failed.'
