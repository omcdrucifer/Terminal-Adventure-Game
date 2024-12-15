THIS IS A PERSONAL PORTFOLIO PROJECT

CHOOSE YOUR OWN ADVENTURE TEXT BASED GAME

My goal is to try and apply what I've learned in Python and challenge myself to go further
by building a choose your own adventure game using a combination of a tree system to control
narrative flow and a graph system to manage combat. 

I'd like to try and implement some form of RNG if possible as well. We shall see how far I get
and how long it takes to achieve it. 

For now, until I have something more substantial to show, the repo will be kept private.

Still trying to nail down methods. Currently experimenting with JSON and trees for the player, enemy and combat values. Story is 100% going to be a tree

I decided a graph would be unneccesary for this project. 

I ultimately settled on a class structure with methods to handle leveling classes. It was ultimately much simpler than trying to approach it with JSON, graph, or tree. 
By implementing class objects I was able to establish a baseline governance for player level and experience gain and a enemy class that levels based on the player level.
I have a base class object to handle combat and experience awards for the player when they defeat an enemy. 
Everything is automated with a hundred lines of code rather than using several hundred
If I were to try and use something more advanced than a class system, it would probably be a database and table, even if it was SQLite. But I haven't started the 
database courses yet and only have minimal experience with SQLite from one Flask course. 

I could always refactor once I get through the database course, but for now this is the simplest solution I could come up with. 
