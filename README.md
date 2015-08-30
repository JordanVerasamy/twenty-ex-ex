twenty-ex-ex
============

`twenty-ex-ex` is a tool to make Super Smash Bros. Melee-related activities easier. It uses the [Challonge API](http://api.challonge.com/v1) to pull data about tournaments, then displays that data in useful ways. Currently, there are two main functions planned for this bot:

1. Make fantasy drafting way easier.
------------------------------------

Each player will be able to enter their drafted team, and a script will update a page constantly with the most up-to-date scores that each drafter has earned from his players. Gone are the days of manually tabulating each player's scores and summing them to track whose fantasy team is doing the best!

2. Provide live updates on tournaments in Slack.
------------------------------------------------

During UW Smash Club weeklies, those of us who aren't attending might want to keep track of how their friends are doing in the tournament, without having to constantly refresh the Challonge page. This tool will use [Slack incoming webhooks](https://api.slack.com/incoming-webhooks) to post updates about your friends' results weeklies as soon as they happen, so you'll never be out of the loop. Eventually, it could be extended to work for pro tournaments as well.
