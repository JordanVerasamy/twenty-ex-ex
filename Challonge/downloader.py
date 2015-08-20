import challonge
import pprint
import config

username = config.challonge_username
tournament_url = config.tournament_url
api_key = config.challonge_api_key

challonge.set_credentials(username, api_key)

tournament = challonge.tournaments.show(tournament_url)
match_list = challonge.matches.index(tournament["id"])

participant_ids = {}
participant_names = []
participant_records = {}
condensed_matches = []

for participant in challonge.participants.index(tournament["id"]):
	participant_ids[participant["id"]] = participant["display-name"]
	participant_names.append(participant["display-name"])

for match in match_list:
	condensed_match = {"winner" : participant_ids[match["winner-id"]],
	                    "loser" : participant_ids[match["loser-id"]]}
	condensed_matches.append(condensed_match)

for name in participant_names:
	participant_records[name] = {"wins" : 0, "losses" : 0}

for condensed_match in condensed_matches:
	participant_records[condensed_match["winner"]]["wins"] += 1
	participant_records[condensed_match["loser"]]["losses"] += 1

pprint.pprint(participant_records)
	


