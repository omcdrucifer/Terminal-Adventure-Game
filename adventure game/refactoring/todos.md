I am refactoring code. Initial code was not great, got caught in a debug loop
started by separating the classes using a parent/child system. Something I'm already
familiar with from previous projects.

Separating the classes also affords me the opportunity to make each class more robust
in addition to avoiding some of the errors I was running into while debugging the 
previous code. In the older code, all player classes were lumped into one Player class
with some checks to try and separate traits. It caused fighters to initialize with
magic traits that they should not have. 

Under the current system, there is a generic Player parent class that houses all the 
shared traits of the subclasses. The child classes represent player classes (Warrior,
Mage, Archer) and their unique traits. This avoids any confusion in the logic and 
allows the characters to be unique.

A similar approach was taken with the NPC, Enemy, and Boss classes. Each has their own
python file and inside that code they all have a similar parent/child structure. 

I decided to govern boss attacks with magic mechanics, as such I reduced their base strength
so that when the game does try to use physical attack logic with strength values, theirs will
be less and they will have to rely more on magic to govern their big attacks. That should allow
them to move slower than the player and give the player weighted odds of success. I am sure
there will be rebalancing whenever I get a chance to test the new combat logic.
