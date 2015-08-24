import challonge
import pprint
import config
import json

username = config.challonge_username
tournament_url = config.tournament_url
api_key = config.challonge_api_key

def download_data(username, tournament_url, api_key, output_file):

	challonge.set_credentials(username, api_key)

	tournament = challonge.tournaments.show(tournament_url)
	match_list = challonge.matches.index(tournament['id'])

	participant_ids = {}
	participant_names = []
	participant_data = {}
	condensed_matches = []

	for participant in challonge.participants.index(tournament['id']):
		participant_ids[participant['id']] = participant['display-name']
		participant_names.append(participant['display-name'])

	num_participants = len(participant_names)

	for match in match_list:
		if match['state'] == 'complete':
			condensed_match = {'winner' : participant_ids[match['winner-id']],
			                    'loser' : participant_ids[match['loser-id']],
			                    'round' : match['round']}
			condensed_matches.append(condensed_match)

	for name in participant_names:
		participant_data[name] = {'wins' : 0, 'losses' : 0, 'final_round' : None, 'worst_possible_round' : None}

	for condensed_match in condensed_matches:
		winner = condensed_match['winner']
		loser = condensed_match['loser']

		participant_data[winner]['wins'] += 1
		participant_data[loser]['losses'] += 1

		# need some way to compute the worst possible round... this is a hack
		# that lets me test the other functionality in the meantime
		participant_data[winner]['worst_possible_round'] = condensed_match['round']
		participant_data[loser]['worst_possible_round'] = condensed_match['round']
		# DELETE THIS EVENTUALLY

		if participant_data[loser]['losses'] == 2:
			participant_data[loser]['final_round'] = condensed_match['round']

	with open(output_file, 'w') as out_file:
	    json.dump(participant_data, out_file)

download_data(username, tournament_url, api_key, 'participant_data.txt')
