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
- Thanks bot
- Thanks for that
- cheers
- cheers bro
- ok thanks!
- perfect thank you
- thanks a bunch for everything
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

## intent:matchmaking_like
- remember my favourite [thing](THING)
- remind me I like [thing](THING)
- remember I like [thing](THING)
- [thing](THING) is something I like
- I love [thing](THING)
- is my favourite [thing](THING)
- I like [thing](THING)
- did you know that I like [thing](THING)
- do you know that I like [thing](THING)
- my favourite [thingtype](THINGTYPE) is [thing](THING)
- I love it when [thing](THING)
- I really like [thing](THING)
- I adore [thing](THING)

## intent:matchmaking_dislike
- don't forget I hate [thing](THING)
- remind me I dislike [thing](THING)
- remember I dislike [thing](THING)
- I don't like [thing](THING)
- I can't stand [thing](THING)
- I hate [thing](THING)
- I'm not a fan of [thing](THING)
- I can't hack [thing](THING)
- I dislike [thing](THING)
- Did you know that I dislike [thing](THING)
- Do you know that I dislike [thing](THING)
- My least favourite [thingtype](THINGTYPE) is [thing](THING)
- I really don't like [thing](THING)
- I despite [thing](THING)
- I can't stand [thing](THING)
- How can anyone like [thing](THING)

## intent:matchmaking_forget_like
- erase my favorite [thing](THING)
- I don't like [thing](THING) any more
- forget what I just told you, I actually don't like [thing](THING)
- forget I like [thing](THING)
- scrap that, I do like [thing](THING)
- forget that I like [thing](THING)
- forget that I like
- I don't like
- I no longer like [thing](THING)
- forget that I said I like [thing](THING)
- forget my like of [thing](THING)

## intent:matchmaking_forget_dislike
- I like [thing](THING) now
- forget what I just told you, I actually don't dislike [thing](THING)
- forget I dislike [thing](THING)
- scrap that, I don't like [thing](THING)
- forget my dislike of [thing](THING)
- I no longer dislike [thing](THING)
- forget that I said I dislike [thing](THING)

## intent:matchmaking_matchmake
- remind us of our favourite
- do any of my friends like [thing](THING)
- who else likes [thing](THING)
- what do my friends and I both like
- what do my friends and I like
- is there anything [friend](FRIEND) and I both enjoy
- what does [friend](FRIEND) like that I also like
- what do [friend](FRIEND) and I both like
- tell me about our common interests
- does [friend](FRIEND) like [thing](THING) too
- who likes [thing](THING)
- who also likes [thing](THING)
- do we both like [thing](THING)
- did you know me and [friend](FRIEND) both like [thing](THING)