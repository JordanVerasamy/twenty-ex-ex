from tournamenttracker import TournamentTracker

class ChannelController:

	def __init__(self, slack_client):
		self.channel_directory = {} # keys are tournament urls, values are channel ids that are following it
		self.slack_client = slack_client

	def publish(self, tournament_tracker):
		new_matches = tournament_tracker.pull_matches()
		for channel in channel_directory[tournament_tracker.tournament_url]:
			update_message = '```Updates about {}:\n\n'.format(tournament_tracker.tournament_url)
			update_message += '\n'.join(str(match) for match in new_matches)
			update_message += '```'
			print 'Sent updates about `{}` to `{}`'.format(tournament_tracker.tournament_url, CHANNEL_NAME)
			self.slack_client.rtm_send_message(channel, update_message)

	def subscribe(self, channel, tournament_url):
		self.channel_directory[tournament_url] = channel

	def unsubscribe(self, channel, tournament_url):
		self.channel_directory[tournament_url].pop(channel, None)
