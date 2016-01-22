import challonge

class CondensedMatch:

	def __init__(self, winner, loser, rnd):
		self.winner = winner
		self.loser = loser
		self.round = rnd

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.winner == other.winner and self.loser == other.loser and self.round == other.round
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		bracket = 'loser\'s' if self.round < 0 else 'winner\'s'
		return '{} defeated {} in {} round {}'.format(self.winner, self.loser, bracket, abs(self.round))

class TournamentTracker:

	def __init__(self, username, tournament_url, api_key, channel):

		self.username = username
		self.tournament_url = tournament_url
		self.api_key = api_key
		self.channel = channel

		self.condensed_matches = []

		self.followed_players = []
		self.all_players = []

		self.participant_ids = {}

		self.initialize_challonge_data()

	def initialize_challonge_data(self):

		challonge.set_credentials(self.username, self.api_key)

		self.tournament = challonge.tournaments.show(self.tournament_url)
		all_players_raw = challonge.participants.index(self.tournament['id'])

		for participant in all_players_raw:
			name = participant['display-name']
			self.participant_ids[participant['id']] = name
			self.all_players.append(name)

	def pull_matches(self): # updates condensed_matches list, returns the new one

		match_list = challonge.matches.index(self.tournament['id'])

		new_matches = []

		for match in match_list:
			if match['state'] == 'complete':
				condensed_match = CondensedMatch(
					self.participant_ids[match['winner-id']],
					self.participant_ids[match['loser-id']],
					match['round'])
				if condensed_match not in self.condensed_matches and (condensed_match.winner in self.followed_players or condensed_match.loser in self.followed_players):
					new_matches.append(condensed_match)
					self.condensed_matches.append(condensed_match)

		return new_matches

	def follow_players(self, *players_to_add):
		self.followed_players.extend(players_to_add)

	def unfollow_players(self, *players_to_remove):
		self.followed_players = filter(lambda x: x not in players_to_remove, self.followed_players)
