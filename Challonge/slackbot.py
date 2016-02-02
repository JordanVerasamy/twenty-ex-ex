import sys
import traceback
import challonge
import time
import config
import httplib

from tournamenttracker import TournamentTracker
from channelcontroller import ChannelController
from slackclient import SlackClient

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

SLACK_API_TOKEN = config.SLACK_API_TOKEN

KEYWORD = config.KEYWORD
ADMIN_NAME = config.ADMIN_NAME

tournament_trackers = {} # keys are tournament urls, values are tournament tracker objects

slack_client = SlackClient(SLACK_API_TOKEN)
controller = ChannelController(slack_client)

### ------ MISCELLANEOUS NECESSARY STUFF ------ ###

def get_status_code(host, path="/"):
    try:
        conn = httplib.HTTPConnection(host)
        conn.request("HEAD", path)
        return conn.getresponse().status
    except StandardError:
        traceback.print_exc()
        return None

def split_into_args(input_str):
    if not input_str:
        return []

    current_arg = ''
    esc_count = 0
    escaped = False

    for char in input_str:
        if escaped:
            current_arg += char
            escaped = False
        elif char == '\\':
            esc_count += 1
            escaped = True
        elif char == ' ':
            break
        else:
            current_arg += char

    rest_of_string = input_str[len(current_arg) + 1 + esc_count:]

    arg_list = [current_arg]
    arg_list.extend(split_into_args(rest_of_string))

    return arg_list

def tournament_exists(url):
    if '-' in url:
        subdomain = '{}.challonge.com'.format(url[:url.find('-')])
        path = '/{}'.format(url[url.find('-')+1:])
    else:
        subdomain = 'challonge.com'
        path = url
    return get_status_code(subdomain, path)

class TournamentDoesNotExistError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class PlayerNotInTournamentError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class TooFewArgsError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

### ----- COMMANDS RECOGNIZED BY SLACKBOT ----- ###

def help_command(channel, args):
	output_message = 'Here\'s a list of available commands:\n```'
	output_message += '\n'.join('{} {} {}'.format(KEYWORD, c, commands[c]['contract']) for c in commands)
	return output_message + '```'

def status_command(channel, args):
	if not tournament_trackers:
		return 'Not currently tracking any tournaments!'
	output_message = 'Here\'s a list of all the tournaments you\'re tracking right now:\n```'
	output_message += '\n'.join('{}: following {}'.format(url, ', '.join(tournament_trackers[url].followed_players)) for url in tournament_trackers)
	return output_message + '```'

def details_command(channel, args):
	output_message = 'Here\'s a list of all the players in `{}` you\'re following: `'.format(args[0])
	tt = tournament_trackers[args[0]]
	if not tt.followed_players:
		return 'You are not following any players in `{}`'.format(args[0])
	output_message += ', '.join('{}'.format(p) for p in tt.followed_players)
	return output_message + '`'

def history_command(channel, args):
	tournament_url = args[0]
	player_name = args[1]

	if player_name not in tournament_trackers[tournament_url].all_players:
		raise PlayerNotInTournamentError([channel, [player_name]])

	relevant_matches = tournament_trackers[tournament_url].get_player_matches(player_name)

	output_message = '```{}\'s history in {}:\n\n'.format(player_name, tournament_url)
	output_message += '\n'.join(str(match) for match in relevant_matches)

	if player_name in tournament_trackers[tournament_url].placings:
		output_message += '\n\nFinal placing: {}\n'.format(tournament_trackers[tournament_url].placings[player_name])

	output_message += '```'

	return output_message

def track_command(channel, args):
	failed = []

	for tournament_url in args:
		if tournament_url in tournament_trackers:
			controller.subscribe(channel, tournament_url)
		else:
			if tournament_exists(tournament_url):
				tournament_trackers[tournament_url] = TournamentTracker(CHALLONGE_USERNAME, tournament_url, CHALLONGE_API_KEY, channel)
				controller.subscribe(channel, tournament_url)
			else:
				failed.append(tournament_url)

	if failed:
		raise TournamentDoesNotExistError([channel, failed])

	return 'Started tracking `{}`'.format('`, `'.join(args))

def untrack_command(channel, args):
	for tournament_url in args:
		tournament_trackers.pop(tournament_url, None)
		controller.unsubscribe(channel, tournament_url)
	return 'No longer tracking `{}`'.format('`, `'.join(args))

def follow_command(channel, args):
	players_to_follow = args[1:]
	tournament_url = args[0]
	failed = []

	if tournament_url not in tournament_trackers:
		raise TournamentDoesNotExistError([channel, [args[0]]])

	tt = tournament_trackers[tournament_url]
	for player_name in players_to_follow:
		if player_name in tt.all_players:
			tt.follow_players(player_name)
		else:
			failed.append(player_name)

	if failed:
		raise PlayerNotInTournamentError([channel, failed])

	return 'Now following `{}` in `{}`!'.format(', '.join('{}'.format(p) for p in players_to_follow), args[0])

def unfollow_command(channel, args):
	players_to_unfollow = args[1:]
	tournament_trackers[args[0]].unfollow_players(players_to_unfollow)
	return 'No longer following `{}` in `{}`!'.format(', '.join('{}'.format(p) for p in players_to_unfollow), args[0])

commands = {
	'help'    : {'function': help_command,     'minargs': 0,  'contract': ''},
	'status'  : {'function': status_command,   'minargs': 0,  'contract': ''},
	'track'   : {'function': track_command,    'minargs': 1,  'contract': '<CHALLONGE_TOURNAMENT_URL>+'},
	'untrack' : {'function': untrack_command,  'minargs': 1,  'contract': '<CHALLONGE_TOURNAMENT_URL>+'},
	'follow'  : {'function': follow_command,   'minargs': 2,  'contract': '<CHALLONGE_TOURNAMENT_URL> <PLAYER_ID>+'},
	'unfollow': {'function': unfollow_command, 'minargs': 2,  'contract': '<CHALLONGE_TOURNAMENT_URL> <PLAYER_ID>+'},
	'details' : {'function': details_command,  'minargs': 1,  'contract': '<CHALLONGE_TOURNAMENT_URL>'},
	'history' : {'function': history_command,  'minargs': 2,  'contract': '<CHALLONGE_TOURNAMENT_URL> <PLAYER_ID>'}
}

### ----------- CORE LOGIC FUNCTIONS ---------- ###

# a user entered a command, so we need to execute it
def execute_command(channel, command, args):
	print 'Received command: `{}` with args: `{}` in channel with ID {}'.format(command, args, channel)
	if command in commands:
		if len(args) < commands[command]['minargs']:
			raise TooFewArgsError([channel, command, len(args), commands[command]['minargs']])
		else:
			output_message = commands[command]['function'](channel, args)
	else:
		output_message = 'Couldn\'t recognize your command. Enter `{} help` for more info.'.format(KEYWORD)
	slack_client.rtm_send_message(channel, output_message)

### ------------ MAIN PROGRAM LOOP ------------ ###

print 'Attempting to connect...'
if slack_client.rtm_connect():
	print 'Connection successful.'
	while True:
		try:
			# read new messages
			new_messages = slack_client.rtm_read()

			# respond to commands, if  necessary
			for message in new_messages:
				if 'text' in message and 'channel' in message:
					channel = message['channel']
					message_body = split_into_args(message['text'])
					if message_body[0] == KEYWORD:
						execute_command(channel, message_body[1], message_body[2:])

			# post updates about tournaments, if necessary
			for tournament_url in tournament_trackers:
				new_matches = tournament_trackers[tournament_url].pull_matches()
				if new_matches:
					controller.publish(tournament_url, new_matches)

		except TournamentDoesNotExistError as e:
			slack_client.rtm_send_message(e.value[0], "The following tournaments were ignored, because they don't seem to exist:")
			slack_client.rtm_send_message(e.value[0], '`{}`'.format(', '.join(e.value[1])))
			traceback.print_exc()

		except PlayerNotInTournamentError as e:
			slack_client.rtm_send_message(e.value[0], "The following players were ignored, because they don't seem to be in the given tournament:")
			slack_client.rtm_send_message(e.value[0], '`{}`'.format(', '.join(e.value[1])))
			traceback.print_exc()

		except TooFewArgsError as e:
			command = e.value[1]
			args_given = e.value[2]
			args_reqd = e.value[3]
			error_message = "`{}` requires {} arguments, but only {} given. Enter `{} help` if you're confused.".format(command, args_reqd, args_given, KEYWORD)
			slack_client.rtm_send_message(e.value[0], error_message)
			traceback.print_exc()

		except Exception:
			print 'Error encountered.'
			#slack_client.rtm_send_message(e.value[0], 'Unhandled error occurred... @{}, look at the logs pls.'.format(ADMIN_NAME))
			traceback.print_exc()
			break

		time.sleep(2)
else:
	print 'Connection failed.'
