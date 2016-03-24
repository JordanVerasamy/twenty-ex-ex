import sys
import traceback
import challonge
import time
import os
import config
import httplib
import urllib2
import json

from tournamenttracker import TournamentTracker
from channelcontroller import ChannelController
from slackclient import SlackClient

### ----- CONSTANT AND GLOBAL DEFINITIONS ----- ###

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

SLACK_API_TOKEN = config.SLACK_API_TOKEN

KEYWORD = config.KEYWORD
ADMIN_NAME = config.ADMIN_NAME

TIMEZONE = config.TIMEZONE

tournament_trackers = {} # keys are tournament urls, values are tournament tracker objects

log_file = open(config.LOG_NAME, 'w')

recent_channel = None

slack_client = SlackClient(SLACK_API_TOKEN)
controller = ChannelController(slack_client)

### ------ MISCELLANEOUS NECESSARY STUFF ------ ###

def message_slack(channel, message):
	recent_channel = channel
	slack_client.rtm_send_message(channel, message)

def print_to_log(message):
	os.environ['TZ'] = TIMEZONE
	time.tzset()
	print '{}: {}'.format(time.asctime(), message)
	log_file.write('{}: {}\n'.format(time.asctime(), message))

def normalize_url(url):
	if '-' in url:
		subdomain = '{}.challonge.com'.format(url[:url.find('-')])
		path = '/{}'.format(url[url.find('-')+1:])
	else:
		subdomain = 'challonge.com'
		path = '/{}'.format(url)
	return subdomain + path

def get_status_code(host, path="/"):
	try:
		conn = httplib.HTTPConnection(host)
		conn.request("HEAD", path)
		return conn.getresponse().status
	except StandardError:
		traceback.print_exc()
		return None

def tournament_exists(url):
	if '-' in url:
		subdomain = '{}.challonge.com'.format(url[:url.find('-')])
		path = '/{}'.format(url[url.find('-')+1:])
	else:
		subdomain = 'challonge.com'
		path = '/{}'.format(url)
	return get_status_code(subdomain, path) == 200

# splits the input_str by spaces, except when the space is preceded by a backslash
# essentially implements basic character escaping
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

class TournamentDoesNotExistError(Exception):
	def __init__(self, channel, tournaments):
		self.channel = channel
		self.tournaments = tournaments

class TournamentNotTrackedError(Exception):
	def __init__(self, channel, tournament):
		self.channel = channel
		self.tournament = tournament

class PlayerNotInTournamentError(Exception):
	def __init__(self, channel, players):
		self.channel = channel
		self.players = players

class TooFewArgsError(Exception):
	def __init__(self, channel, command, args_given, args_reqd):
		self.channel = channel
		self.command = command
		self.args_given = args_given
		self.args_reqd = args_reqd

### ----- COMMANDS RECOGNIZED BY SLACKBOT ----- ###

def help_command(channel, args):
	output_message = 'Here\'s a list of available commands:\n```'
	output_message += '\n'.join('{} {} {}'.format(KEYWORD, c, commands[c]['contract']) for c in commands)
	return output_message + '```'

def status_command(channel, args):
	if not tournament_trackers:
		return 'Not currently tracking any tournaments!'
	output_message = 'Here\'s a list of all the tournaments you\'re tracking right now:\n```'
	output_message += '\n'.join('{}: following {}'.format(url, ', '.join(tournament_trackers[url].get_followed_players())) for url in tournament_trackers)
	return output_message + '```'

def details_command(channel, args):
	tt = tournament_trackers[args[0]]
	output_message = '\nHere\'s a list of all the players in {}:\n```'.format(normalize_url(args[0]))
	output_message += '\n'.join(map(lambda x: '{}{}{}'.format(x, ' ({})'.format(tt.get_placing(x)) if tt.get_placing(x) else '', ' (followed)' if x in tt.get_followed_players() else ''), tt.get_all_players()))
	output_message += '```\n'
	return output_message

def history_command(channel, args):
	tournament_url = args[0]
	player_name = args[1]

	if tournament_url not in tournament_trackers:
		raise TournamentNotTrackedError(channel, tournament_url)

	if player_name not in tournament_trackers[tournament_url].get_all_players():
		raise PlayerNotInTournamentError(channel, [player_name])

	relevant_matches = tournament_trackers[tournament_url].get_player_matches(player_name)
	output_message = '{}\'s history in {}:\n\n```'.format(player_name, normalize_url(tournament_url))
	output_message += '\n'.join(str(match) for match in relevant_matches)

	if tournament_trackers[tournament_url].get_placing(player_name):
		output_message += '\n\nFinal placing: {}\n'.format(tournament_trackers[tournament_url].get_placing(player_name))

	output_message += '```'

	return output_message

def track_command(channel, args):
	failed = []

	for tournament_url in args:
		if tournament_url in tournament_trackers:
			controller.subscribe(channel, tournament_url)
		else:
			if tournament_exists(tournament_url):
				tournament_trackers[tournament_url] = TournamentTracker(CHALLONGE_USERNAME, tournament_url, CHALLONGE_API_KEY)
				controller.subscribe(channel, tournament_url)
			else:
				failed.append(tournament_url)

	if failed:
		raise TournamentDoesNotExistError(channel, failed)

	return 'Started tracking `{}`'.format('`, `'.join(args))

def untrack_command(channel, args):
	for tournament_url in args:
		tournament_trackers.pop(tournament_url, None)
		controller.unsubscribe(channel, tournament_url)
	return 'No longer tracking {}'.format('`, `'.join(args))

def jsonify_command(channel, args):
	for tournament_url in args:
		tournament_trackers[tournament_url].pull_matches()
		matches = tournament_trackers[tournament_url].get_all_matches()
		results = []
		for match in matches:
			if match.round > 0:
				ccmatch = {'winner': match.winner, 'loser': match.loser}
				results.append(ccmatch)
		for match in matches:
			if match.round < 0:
				ccmatch = {'winner': match.winner, 'loser': match.loser}
				results.append(ccmatch)
		with open('matchresults_{}.json'.format(tournament_url), 'w') as outfile:
			json.dump(results, outfile)
	return 'Successfully jsonified!'

def follow_command(channel, args):
	players_to_follow = args[1:]
	tournament_url = args[0]
	failed = []

	if tournament_url not in tournament_trackers:
		raise TournamentNotTrackedError(channel, args[0])

	tt = tournament_trackers[tournament_url]
	for player_name in players_to_follow:
		if player_name in tt.get_all_players():
			tt.follow_players(player_name)
		else:
			failed.append(player_name)

	if failed:
		raise PlayerNotInTournamentError(channel, failed)

	return 'Now following {} in {}!'.format(', '.join('{}'.format(p) for p in players_to_follow), normalize_url(args[0]))

def unfollow_command(channel, args):
	players_to_unfollow = args[1:]
	tournament_trackers[args[0]].unfollow_players(players_to_unfollow)
	return 'No longer following {} in `{}`!'.format(', '.join('{}'.format(p) for p in players_to_unfollow), args[0])

commands = {
	'help'    : {'function': help_command,     'minargs': 0,  'contract': ''},
	'status'  : {'function': status_command,   'minargs': 0,  'contract': ''},
	'track'   : {'function': track_command,    'minargs': 1,  'contract': '<CHALLONGE_TOURNAMENT_URL>+'},
	'untrack' : {'function': untrack_command,  'minargs': 1,  'contract': '<CHALLONGE_TOURNAMENT_URL>+'},
	'jsonify' : {'function': jsonify_command,  'minargs': 1,  'contract': '<CHALLONGE_TOURNAMENT_URL>+'},
	'follow'  : {'function': follow_command,   'minargs': 2,  'contract': '<CHALLONGE_TOURNAMENT_URL> <PLAYER_ID>+'},
	'unfollow': {'function': unfollow_command, 'minargs': 2,  'contract': '<CHALLONGE_TOURNAMENT_URL> <PLAYER_ID>+'},
	'details' : {'function': details_command,  'minargs': 1,  'contract': '<CHALLONGE_TOURNAMENT_URL>'},
	'history' : {'function': history_command,  'minargs': 2,  'contract': '<CHALLONGE_TOURNAMENT_URL> <PLAYER_ID>'}
}

### ----------- CORE LOGIC FUNCTIONS ---------- ###

# a user entered a command, so we need to execute it
def execute_command(channel, command, args):
	print_to_log('Received command: `{}` with args: `{}` in channel with ID {}'.format(command, args, channel))
	if command in commands:
		if len(args) < commands[command]['minargs']:
			raise TooFewArgsError(channel, command, len(args), commands[command]['minargs'])
		else:
			output_message = commands[command]['function'](channel, args)
	else:
		output_message = 'Couldn\'t recognize your command. Enter `{} help` for more info.'.format(KEYWORD)
	print_to_log('Sending message {} to channel with ID {}'.format(output_message, channel))
	message_slack(channel, output_message)

### ------------ MAIN PROGRAM LOOP ------------ ###

print_to_log('Attempting to connect...')
if slack_client.rtm_connect():
	print_to_log('Connection successful.')
	counter = 0
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
						recent_channel = channel
						execute_command(channel, message_body[1], message_body[2:])

			# every tenth iteration, post updates about tournaments, if necessary
			if counter >= 10:
				counter = 0
				for tournament_url in tournament_trackers:
					new_data = tournament_trackers[tournament_url].pull_matches()
					if new_data:
						print_to_log('updates about {}! sent them to slack.'.format(new_data))
						controller.publish(normalize_url, tournament_url, new_data)

		except TournamentDoesNotExistError as e:
			message_slack(e.channel, "The following tournaments were ignored, because they don't seem to exist:")
			message_slack(e.channel, '`{}`'.format(', '.join(e.tournaments)))
			print_to_log(traceback.format_exc())

		except TournamentNotTrackedError as e:
			message_slack(e.channel, '{} is not currently tracked. Try `!20xx track {}`'.format(normalize_url(e.tournament), e.tournament))
			print_to_log(traceback.format_exc())

		except PlayerNotInTournamentError as e:
			message_slack(e.channel, "The following players were ignored, because they don't seem to be in the given tournament:")
			message_slack(e.channel, '`{}`'.format(', '.join(e.players)))
			print_to_log(traceback.format_exc())

		except TooFewArgsError as e:
			error_message = "`{}` requires {} arguments, but only {} given. Enter `{} help` if you're confused.".format(e.command, e.args_reqd, e.args_given, KEYWORD)
			message_slack(e.channel, error_message)
			print_to_log(traceback.format_exc())

		except urllib2.URLError, e:
			print_to_log('URL error encountered.')
			if recent_channel:
				message_slack(recent_channel, 'URL error occurred. Something weird with trying to pull from Challonge. Look into it, @{}.'.format(ADMIN_NAME))
			print_to_log(traceback.format_exc())

		except Exception:
			print_to_log('Error encountered.')
			if recent_channel:
				message_slack(recent_channel, 'Unhandled error occurred... @{}, look at the logs pls.'.format(ADMIN_NAME))
			print_to_log(traceback.format_exc())
			break

		counter += 1
		time.sleep(0.5)
else:
	print 'Connection failed.'
