###### planning for a Choose Your Own Adventure (CYOA)
I've built out most of the logic at this point, 
there are some areas that are still not feature 
complete. For example, in combat right now the 
only option to choose is to attack. I need to 
build in the rest to include cast spell, check 
inventory, etc. I also need to build an inventory
system to allow for healing outside of the magic 
system and other quality of life offerings. The
game gets more complicated the more I build out but
I am absolutely okay with that. I knew this was 
going to be a challenge when I decided to do it, 
that was the point.

I've written unit tests for everything that is 
written to date. I've debugged all of it and the 
unit test comes back 100% clean. One test skips 
as it should as it is a windows only test and 
I am building on a Linux box.

There is logic to utilize key commands. This is 
to allow the user to press alt keys for options. 
Think 'M' for menu or 'Q' for quit. I would just 
need to implement them into the game loop logic.
When I get around to building the inventory system
I will likely implement a quick button like 'I' for 
inventory. We'll see when I get around to it.

The tree system to control the story progress through
nodes is in place and works, as it has an example
story currently build into it. I haven't actually 
constructed the story I want to use for this game yet
so I think its maybe time to shift focus to that for 
a bit and I can flesh out the established logic as
I go. I don't want to get into a rabbit hole of tech 
debt by endlessly tweaking the logic without ever
actually having a story to run it with. 

This is becoming a very robust game for something that
is going to be played in a terminal in a text-based RPG 
format. I like that, though. I like that I get excited 
while working on it and just want to add more and tweak
more and improve the quality rather than treating it 
like "just a terminal game". 

I am looking into ASCII art now as well to attempt to 
give it some visual appeal. I have zero experience
with ASCII to date so this should be interesting. 
I don't want this to be a boring game just because it
is being told and played entirely through text. 
