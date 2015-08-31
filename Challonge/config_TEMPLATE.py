challonge_username = 'YOUR_NAME_HERE'
tournament_url = 'YOUR_URL_HERE'

challonge_api_key = 'YOUR_KEY_HERE'
slack_api_token = 'YOUR_TOKEN_HERE'

channels = {'NAME' : 'ID', 'NAME' : 'ID'}
channel_to_connect_to = 'NAME'

# Save this as `config.py` and replace the placeholders with their actual values.

# The Challonge username is just your Challonge account name.

# The Challonge tournament URL should contain the subdomain first, if it exists, 
# then the tournament's URL tag. For example, if your tournament is at 
# `contrivedcup.challonge.com/arbitrarytournament` then 
# you would set tournament_url equal to 'contrivedcup-arbitrarytournament', and 
# `challonge.com/mytournament` would be 'mytournament'.

# You can get your Challonge API key from: https://challonge.com/settings/developer

# You can get your Slack API token by adding a Bots integration to your 
# Slack channel and clicking `Configure`.

# Slack channel IDs can be retrieved by querying the server for messages and checking
# the ID returned.