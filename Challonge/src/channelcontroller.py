class ChannelController:

	def __init__(self, slack_client):
		self._channel_directory = {} # keys are tournament urls, values are lists of channel ids that are following it
		self._slack_client = slack_client

	def publish(self, normalize_url, tournament_url, new_data):
		match_list = new_data['new_matches']
		elim = new_data['newly_eliminated_players']

		for channel in self._channel_directory[tournament_url]:
			update_info = 'Updates about {}:\n\n'.format(normalize_url(tournament_url))
			update_body = '```'
			update_body += '\n'.join(str(match) for match in match_list)
			if elim:
				update_body += '\n\n'
				update_body += '\n'.join('{}\'s final placing: {}'.format(player, elim[player]) for player in elim)
			update_body += '```'
			print 'Sent updates about `{}` to `{}`'.format(tournament_url, channel)
			self._slack_client.rtm_send_message(channel, update_info)
			self._slack_client.rtm_send_message(channel, update_body)

	def subscribe(self, channel, tournament_url):
		if tournament_url in self._channel_directory:
			self._channel_directory[tournament_url].append(channel)
		else:
			self._channel_directory[tournament_url] = [channel]

	def unsubscribe(self, channel, tournament_url):
		if tournament_url in self._channel_directory:
			self._channel_directory[tournament_url].remove(channel)
		else:
			self._channel_directory.pop(tournament_url, None)
