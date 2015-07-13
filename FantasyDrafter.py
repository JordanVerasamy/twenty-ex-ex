import challonge
import pprint

username = "KT_Life"
tournament_url = "ceogaming-2015_melee_final"
api_key = "SBGoBPpd6ZvAqqsSwimUfvjc7SjNjQ1TBPHRjaBv"

challonge.set_credentials(username, api_key)
tournament = challonge.tournaments.show(tournament_url)
participant_id_list = map(lambda x: x["id"], challonge.participants.index(tournament["id"]))


match_list = challonge.matches.index(tournament["id"])

pprint.pprint(tournament)