THIS IS A PERSONAL PORTFOLIO PROJECT

CHOOSE YOUR OWN ADVENTURE TEXT BASED GAME

My goal is to try and apply what I've learned in Python and challenge myself to go further
by building a choose your own adventure game. 

I ultimately settled on a class structure with methods to handle leveling classes. It was ultimately much simpler than trying to approach it with JSON, graph, or tree. 
By implementing class objects I was able to establish a baseline governance for player level and experience gain and a enemy class that levels based on the player level.
I have a base class object to handle combat and experience awards for the player when they defeat an enemy. 
Everything is automated with a hundred lines of code rather than using several hundred
If I were to try and use something more advanced than a class system, it would probably be a database and table, even if it was SQLite. But I haven't started the 
database courses yet and only have minimal experience with SQLite from one Flask course. 

I could always refactor once I get through the database course, but for now this is the simplest solution I could come up with. 

12-17-24

Refactored Classes and Combat system. Added functionality to account for magic and agility bonuses when determining initiative.
Party now manages enemy and player parties
Combat can handle magic damage and healing. 
Roll for initiative! 

I'm building toward allowing more player choice in combat, and will be attempting to build in a save and light menu system. 

I plan to start the tree next. 
