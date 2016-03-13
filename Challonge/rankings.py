from tournamenttracker import TournamentTracker
import config
import pprint

CHALLONGE_USERNAME = config.CHALLONGE_USERNAME
CHALLONGE_API_KEY = config.CHALLONGE_API_KEY

K_FACTOR = 32

#order matters here!
tournament_urls = [
	'uwsmashclub-UWmelee23',
	'uwsmashclub-UWMelee24',
	'uwsmashclub-UWMelee25',
	'uwsmashclub-UWmelee26',
	'uwsmashclub-UWmelee27',
	'uwsmashclub-UWmelee28'
]

alt_tags = {
	'Simba' : ['Poor|Simba', 'CUB | Simba'],
	'Rabbit' : ['UW SOUP CHAMPION | Campbell', 'KW SECONDARIES CHAMPION| Rabbit'],
	'OT Eric' : ['BLT Eric'],
	'Gerb' : ['Not the netplay marth instead the puff gerb', 'gerb'],
	'MurphyPrime' : ['LP KW Champ|MurphyPrime'],
	'GarbagePrince' : ['GarbageLord'],
	'Eidolon' : ['Eidolm@ster'],
	'G Pipes' : ['Gpipes', 'GPipes', 'Jee Pipes'],
	'lonebutterfish' : ['Mike Oxwelling', 'Haxfn$', 'Dixon Cider'],
	'RageCage' : ['Despite all my Rage I am Still Just a Rat in the Cage'],
	'Wakening' : ['Wakeningg'],
	'Mosh' : ['#2 Barrie|Marth/Fox Pro'],
	'LetsDuet' : ['Jason "LetsDuet" Young'],
	'Phlow' : ['Flow'],
	'IceBallz' : ['Iceballz'],
	'FUTANARI IDOL' : ['placeholder for andrew\'s dumbass tag'],
	'Freedomm' : ['Youngster Joey'],
	'JusttheTipper' : ['5-0\'d by Eon']
}

def get_delta_elo(winner_rating, loser_rating):
	return K_FACTOR / (1 + 10 ** ((winner_rating - loser_rating)/400))

def get_real_tag(tag):
	if tag in alt_tags:
		return tag
	for player in alt_tags:
		if tag in alt_tags[player]:
			return player
	return tag

tournament_trackers = map(lambda x: TournamentTracker(CHALLONGE_USERNAME, x, CHALLONGE_API_KEY), tournament_urls)

ratings = {}

for tt in tournament_trackers:
	tt.pull_matches()

	for tag in tt.get_all_players():
		player = get_real_tag(tag)
		if player not in ratings:
			ratings[player] = 1200

	for match in tt.get_all_matches():
		winner = get_real_tag(match.winner)
		loser = get_real_tag(match.loser)
		delta_elo = get_delta_elo(ratings[winner], ratings[loser])
		ratings[winner] += delta_elo
		ratings[loser] -= delta_elo

for player in sorted(ratings, key=ratings.get, reverse=True):
	print player, ratings[player]
