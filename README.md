THIS IS A PERSONAL PORTFOLIO PROJECT

CHOOSE YOUR OWN ADVENTURE TEXT BASED GAME

This CYOA is written entirely in Python and is meant to play
like an old school text based RPG.

To date it has logic for:
    - Character Classes: Player, NPC, Enemy, Boss
    - Combat: Solo, Group, handles initiative
    - Party: Party system can manage both player and enemy parties
    - Story: Tree system to control story flow
    - Game Loop: Menu system and game control flow
    - Save States: Creates save states with JSON
    - Keymap: Allows me to map buttons to quick menus

Some key features are:
    - Boss scaling: bosses are scaled by the number of party members + 1
    - World scaling: NPCs and non-boss enemies scale to the player's level
    - Classes: Currently there are 3 playable classes and three supporting
    classes, and six enemy classes (3 boss and 3 non-boss)
    - Menu system: The game loop logic includes menus for:
        - Starting a game
        - Creating a game
        - Creating a save
        - Loading a save
        - Combat choices
        - Story choices
        - Quitting the game
    - Rest system: Resting will restore the player's mana and health
    scales to the appropriate player level
    - Party management: The party logic allows for adding and removing
    members of a party. This allows for recruiting in story and removing
    party members either if deceased or having abandoned the party. 

A lot of what is in place is boiler plate and can/should be built out.
For example there are only three spells available for each magic class.
I want/should build out a spell system that allows learning more spells
as the character levels. I may consider allowing more classes in the 
future but for now I think I should leave it where it is. I have logic
in place that is currently not being implemented to allow me to impose
a level cap if I feel that it is necessary to do so. 
