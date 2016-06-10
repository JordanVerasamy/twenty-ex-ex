NOTE: This is currently hosted at http://jordanverasamy.github.io/twenty-ex-ex/

twenty-ex-ex
============

`twenty-ex-ex` is a tool to make Super Smash Bros. Melee-related activities easier. It uses the [Challonge API](http://api.challonge.com/v1) to pull data about tournaments, then displays that data in useful ways. Currently, there are three main functions planned for this bot:

### 1. (Done!) Compute Elo rankings for every player in a Smash community


The UW Smash Club community wanted a way to track players' skill against each other, so that tournaments could be seeded accurately. This repository provides a tool that automatically computes skill ratings for individual players, given a list of tournaments on Challonge. It can even handle a single player using many different tags in different tournaments!

### 2. (Done!) Provide live updates on tournaments in Slack.

During UW Smash Club weeklies, those of us who aren't attending might want to keep track of how their friends are doing in the tournament, without having to constantly refresh the Challonge page. This tool provides a [bot user](https://api.slack.com/bot-users) (built with the [Slack Real Time Messaging API](https://api.slack.com/rtm)) to post updates about your friends' results weeklies as soon as they happen, so you'll never be out of the loop. Eventually, it could be extended to work for pro tournaments as well.

### 3. (In progress) Make fantasy drafting way easier.

Each player will be able to enter their drafted team, and a script will update a page constantly with the most up-to-date scores that each drafter has earned from his players. Gone are the days of manually tabulating each player's scores and summing them to track whose fantasy team is doing the best!
