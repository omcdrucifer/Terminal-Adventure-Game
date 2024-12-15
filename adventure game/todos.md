###### planning for a Choose Your Own Adventure (CYOA)

The narrative will have to use a tree node system to control story flow

I decided JSON will be a better approach for stat tracking, so no graphs needed.

This is a big undertaking, but I want to give myself experience with a larger code base

and a more complex task.

I've worked with graphs before, but have little experience with trees, the challenge will be good. 

I'll need a story outline at least before I can start structuring the tree. 

The combat system can be built without the story as long as I know what kind of characters/enemies the 

game will feature. 

I've settled on class objects to handle players, enemies, and combat
I tried JSON and graphs and dicts. It just seemed too complicated for what could
be automated with classes. 

The story narrative flow will still be controlled by a tree. This will allow me to
implement choice into the flow.

The enemies will award experience and the player can level up. 
There is currently no cap on levels, the enemy values and xp values increment with each
new level.

This may need to be refactored at some point but I won't be doing much refactoring until I
have at lease some kind of baseline for each element of the game and can run some tests.
