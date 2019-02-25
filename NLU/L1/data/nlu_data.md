<!--- Make sure to update this training data file with more training examples from https://forum.rasa.com/t/grab-the-nlu-training-dataset-and-starter-packs/903 --> 

## intent:bye <!--- The label of the intent --> 
- Bye 			<!--- Training examples for intent 'bye'--> 
- Goodbye
- See you later
- Bye bot
- Goodbye friend
- bye
- bye for now
- catch you later
- gotta go
- See you
- goodnight
- have a nice day
- i'm off
- see you later alligator
- we'll speak soon

## intent:greet
- Hi
- Hey
- Hi bot
- Hey bot
- Hello
- Good morning
- hi again
- hi folks
- hi Mister
- hi pal!
- hi there
- greetings
- hello everybody
- hello is anybody there
- hello robot

## intent:thank
- Thanks
- Thank you
- Thank you so much
- Thanks for that
- cheers
- ok thanks!
- thanks for the help
- thanks a lot
- amazing, thanks
- cool, thanks
- cool thank you

## intent:affirm
- yes
- yes sure
- absolutely
- for sure
- yes yes yes
- definitely

<!-- BOT 1: MATCHMAKING -->

<!-- ## intent:matchmaking_like
- remember my favourite 
- remind me I like 
- remember I like 
-  is something I like
- I love 
- is my favourite 
- I like 
- did you know that I like 
- do you know that I like 
- my favourite [thingtype](THINGTYPE) is 
- I love it when 
- I really like 
- I adore 

## intent:matchmaking_dislike
- don't forget I hate 
- remind me I dislike 
- remember I dislike 
- I don't like 
- I can't stand 
- I hate 
- I'm not a fan of 
- I can't hack 
- I dislike 
- Did you know that I dislike 
- Do you know that I dislike 
- My least favourite [thingtype](THINGTYPE) is 
- I really don't like 
- I despite 
- I can't stand 
- How can anyone like 

## intent:matchmaking_forget_like
- erase my favorite 
- I don't like  any more
- forget what I just told you, I actually don't like 
- forget I like 
- scrap that, I do like 
- forget that I like 
- forget that I like
- I don't like
- I no longer like 
- forget that I said I like 
- forget my like of 

## intent:matchmaking_forget_dislike
- I like  now
- forget what I just told you, I actually don't dislike 
- forget I dislike 
- scrap that, I don't like 
- forget my dislike of 
- I no longer dislike 
- forget that I said I dislike 

## intent:matchmaking_matchmake
- remind us of our favourite
- do any of my friends like 
- who else likes 
- what do my friends and I both like
- what do my friends and I like
- is there anything [friend](FRIEND) and I both enjoy
- what does [friend](FRIEND) like that I also like
- what do [friend](FRIEND) and I both like
- tell me about our common interests
- does [friend](FRIEND) like  too
- who likes
- who also likes
- do we both like
- did you know me and [friend](FRIEND) both like -->

<!-- BOT 2: CALENDAR -->

<!--
Unification of PERSONAL and FACILITY calendars.
We will make distinctions between the two at the next layer, and in speech.
-->
## intent:calendar_events_today
- what's on my schedule?
- what's happening in the care home today?
- what events are on today?
- what can I do today?
- what is there to do today?
- is there anything on today?
- what do I have on today?
- what am I doing today?
- what is on my calendar today?
- do I have any events today?
- am I doing anything today?
- what do I have to remember to do today?

## intent:calendar_upcoming_visitors
- is there one scheduled to visit?
- is there one scheduled to visit me today?
- is anyone coming to see me?
- is anyone coming to see me today?
- is anyone coming to see me this week?
- who is coming over today?
- am I having any visitors?
- is anyone coming over?
- who is coming round today?
- is anyone coming round today?

<!--
## intent:calendar_event_search
- find on my schedule
- when am I doing
- when am I going to
- tell me when
- on my calendar
- when is
-->

## intent:calendar_event_search_bingo
- find [bingo](EVENT) on my schedule
- find [bingo](EVENT) on my schedule today
- when am I going to [bingo](EVENT)
- when is [bingp](EVENT)
- what day is [bingo](EVENT)
- what time is [bingp](EVENT)

## intent:calendar_event_search_lunch
- find [lunch](EVENT) on my schedule
- find [lunch](EVENT) on my schedule today
- what time is [lunch](EVENT)
- when is [lunch](EVENT)
- when is [lunch](EVENT) today

## intent:calendar_event_search_dinner
- find [dinner](EVENT) on my schedule
- find [dinner](EVENT) on my schedule today
- what time is [dinner](EVENT)
- when is [dinner](EVENT)
- when is [dinner](EVENT) today

## intent:calendar_event_search_film
- find [film](EVENT) on my schedule
- find [film](EVENT) on my schedule today
- what time [film](EVENT) on today
- what time is [film](EVENT) on today
- what time is there a [film](EVENT) on today
- what time are [film](EVENT) on
- what time [film](EVENT) on
- what time is [film](EVENT) on
- what time is there a [film](EVENT) on
- what time are [film](EVENT) on

## intent:calendar_event_friend_today
- what is my friend [friend](FRIEND) doing today
- what is [friend](FRIEND) doing today
- what is [friend](FRIEND)'s schedule
- is [friend](FRIEND) free today
- what is [frient](FRIEND) up to today
- is [friend](FRIEND) busy today

<!-- BOT 3: RECALL QUIZ -->

<!-- SYNONYMS -->

## synonym:friend
- mark
- ronnie
- alex
- rain
- florence
- matthew
- beata
- abubaker
- bakry
- jack
- victor

## synonym:film
- movie
- movies
- film
- films
- talkies