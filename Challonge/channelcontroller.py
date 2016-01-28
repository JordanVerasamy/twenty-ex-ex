class ChannelController:

	def __init__(self, slack_client):
		self.channel_directory = {} # keys are tournament urls, values are lists of channel ids that are following it
		self.slack_client = slack_client

	def publish(self, tournament_url, match_list):
		for channel in self.channel_directory[tournament_url]:
			update_message = '```Updates about {}:\n\n'.format(tournament_url)
			update_message += '\n'.join(str(match) for match in match_list)
			update_message += '```'
			print 'Sent updates about `{}` to `{}`'.format(tournament_url, channel)
			self.slack_client.rtm_send_message(channel, update_message)

	def subscribe(self, channel, tournament_url):
		if tournament_url in self.channel_directory:
			self.channel_directory[tournament_url].append(channel)
		else:
			self.channel_directory[tournament_url] = [channel]

	def unsubscribe(self, channel, tournament_url):
		if tournament_url in self.channel_directory:
			self.channel_directory[tournament_url].remove(channel)
		else:
			self.channel_directory.pop(tournament_url, None)
