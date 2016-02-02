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

	def participated(self, player_name):
		return self.winner == player_name or self.loser == player_name


def get_placing(round, player_count):
	thresholds = [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193]
	relevant_threshold = min(filter(lambda x: x >= player_count, thresholds))
	print relevant_threshold



class TournamentTracker:

	def __init__(self, username, tournament_url, api_key, channel):

		self.username = username
		self.tournament_url = tournament_url
		self.api_key = api_key
		self.channel = channel

		self.condensed_matches = []

		self.followed_players = []
		self.all_players = []

		self.participant_ids = {} # keys are IDs, values are names
		self.placings = {} # keys are names, values are placings

		self.initialize_challonge_data()

	def initialize_challonge_data(self):

		challonge.set_credentials(self.username, self.api_key)

		self.tournament = challonge.tournaments.show(self.tournament_url)
		all_players_raw = challonge.participants.index(self.tournament['id'])

		for participant in all_players_raw:
			name = participant['display-name']
			self.participant_ids[participant['id']] = name
			self.all_players.append(name)

	def get_placing(self, round):
		thresholds = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]

		suffixes = {
			1: 'st',
			2: 'nd',
			3: 'rd',
			4: 'th',
			5: 'th',
			6: 'th',
			7: 'th',
			8: 'th',
			9: 'th',
			0: 'th',
		}

		special_cases = {
			13: 'th'
		}

		player_count = len(self.all_players)

		relevant_threshold = min(filter(lambda x: x >= player_count, thresholds))
		thresholds = thresholds[:thresholds.index(relevant_threshold)+1]

		placing = thresholds[len(thresholds)-round-1] + 1

		if placing in special_cases:
			suffix = special_cases[placing]
		else:
			last_digit = placing % 10
			suffix = str(suffixes[last_digit])

		return '{}{}'.format(str(placing), suffix)

	def pull_matches(self): # updates condensed_matches list, returns the new one

		match_list = challonge.matches.index(self.tournament['id'])

		new_matches = []

		for match in match_list:
			if match['state'] == 'complete':
				condensed_match = CondensedMatch(
					self.participant_ids[match['winner-id']],
					self.participant_ids[match['loser-id']],
					match['round'])
				if condensed_match not in self.condensed_matches:
					if condensed_match.winner in self.followed_players or condensed_match.loser in self.followed_players:
						new_matches.append(condensed_match)
					self.condensed_matches.append(condensed_match)
				if condensed_match.round < 0:
					self.placings[condensed_match.loser] = self.get_placing(-condensed_match.round)

		return new_matches

	def get_player_matches(self, player_name):
		player_matches = []
		return filter(lambda match: match.participated(player_name), self.condensed_matches)

	def follow_players(self, *players_to_add):
		self.followed_players.extend(players_to_add)

	def unfollow_players(self, *players_to_remove):
		self.followed_players = filter(lambda player: player not in players_to_remove, self.followed_players)
