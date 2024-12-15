# Tree Node for the story system
class TreeNode:
    def __init__(self, story_piece):
        self.story_piece = story_piece
        self.choices = []

    def add_child(self, node):
        self.choices.append(node)

    def traverse(self):
        story_node = self
        print(story_node.story_piece)
        while story_node.choices != []:
            choice = input("Enter 1 or 2 to continue the story: ")
            if choice not in ['1', '2']:
                print("Please enter a valid choice: 1 or 2. ")
            else:
                chosen_index = int(choice) - 1
                chosen_child = story_node.choices[chosen_index]
                story_node = chosen_child
                print(story_node.story_piece)
                
# Story elements would be built out either here or in another file and
# the tree would be built from nodes of story chunks

user_choice = input("What is your name?: ")
print(f"Hello, {user_choice}!")

#class StoryNode:
#    def __init__(self, description):
#        self.description = description
#        self.choices = {}

#    def add_choice(self, choice, node):
#        self.choices[choice] = node
