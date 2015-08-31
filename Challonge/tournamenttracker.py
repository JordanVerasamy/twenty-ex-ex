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
		bracket = 'loser\'s'
		if self.round > 0:
			bracket = 'winner\'s'
		return '{} defeated {} in {} round {}'.format(self.winner, self.loser, bracket, abs(self.round))

class TournamentTracker:

	def __init__(self, username, tournament_url, api_key):

		self.username = username
		self.tournament_url = tournament_url
		self.api_key = api_key

		challonge.set_credentials(self.username, self.api_key)

		self.condensed_matches = []
		self.num_participants = -1

	def pull_matches(self): # updates condensed_matches list, returns the new one

		tournament = challonge.tournaments.show(self.tournament_url)
		match_list = challonge.matches.index(tournament['id'])
		participant_list = challonge.participants.index(tournament['id'])

		participant_ids = {}
		new_matches = []

		for participant in participant_list:
			name = participant['display-name']
			participant_ids[participant['id']] = name

		self.num_participants = len(participant_list)

		for match in match_list:
			if match['state'] == 'complete':
				condensed_match = CondensedMatch(participant_ids[match['winner-id']], 
				                                 participant_ids[match['loser-id']], 
				                                 match['round'])
				if condensed_match not in self.condensed_matches:
					new_matches.append(condensed_match)
					self.condensed_matches.append(condensed_match)

		return new_matches






















