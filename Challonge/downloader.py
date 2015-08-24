import challonge
import pprint
import config
import json

class Tournament:

	def __init__(self, username, tournament_url, api_key):

		self.username = username
		self.tournament_url = tournament_url
		self.api_key = api_key

		self.participant_data = {}
		self.participant_ids = {}
		self.participant_names = []
		self.condensed_matches = []

		self.username = username
		self.tournament_url = tournament_url
		self.api_key = api_key

		challonge.set_credentials(self.username, self.api_key)

	def update_data(self, output_file=None):

		tournament = challonge.tournaments.show(tournament_url)
		match_list = challonge.matches.index(tournament['id'])

		for participant in challonge.participants.index(tournament['id']):
			name = participant['display-name']
			self.participant_ids[participant['id']] = name
			if name not in participant_names:
				self.participant_names.append(name)

		num_participants = len(self.participant_names)

		updated_condensed_matches = []

		for match in match_list:
			if match['state'] == 'complete':
				condensed_match = {'winner' : self.participant_ids[match['winner-id']],
				                    'loser' : self.participant_ids[match['loser-id']],
				                    'round' : match['round']}
				updated_condensed_matches.append(condensed_match)

		num_new_matches = len(updated_condensed_matches) - len(self.condensed_matches)

		new_condensed_matches = updated_condensed_matches[num_new_matches:]

		for name in self.participant_names:
			self.participant_data[name] = {'wins' : 0, 'losses' : 0, 'final_round' : None, 'worst_possible_round' : None}

		for condensed_match in new_condensed_matches:
			winner = condensed_match['winner']
			loser = condensed_match['loser']

			self.participant_data[winner]['wins'] += 1
			self.participant_data[loser]['losses'] += 1

			if self.participant_data[loser]['losses'] == 2:
				self.participant_data[loser]['final_round'] = condensed_match['round']

		if output_file != None:
			with open(output_file, 'w') as out_file:
				json.dump(self.participant_data, out_file)

username = config.challonge_username
tournament_url = config.tournament_url
api_key = config.challonge_api_key

tour = Tournament(username, tournament_url, api_key)
tour.update_data('tournamentdata.txt')