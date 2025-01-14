from story_content import get_story_content

class StoryNode:
    def __init__(self, node_id, node_type, content, choices):
        self.node_id = node_id
        self.node_type = node_type
        self.content = content
        self.choices = choices
        self.combat_data = None

class StoryTree:
    def __init__(self):
        self.nodes = {}
        self.current_node = None

    def add_node(self, node_id, node_type, content, choices):
        self.nodes[node_id] = StoryNode(node_id, node_type, content, choices)

    def start_story(self, starting_node_id):
        self.current_node = self.nodes[starting_node_id]

    def get_available_choices(self):
        if self.current_node:
            return self.current_node.choices
        return []

def create_story():
    story = StoryTree()
    story_data = get_story_content()

    for node_id, node_data in story_data.items():
        story.add_node(node_id, node_data["type"], node_data["content"], node_data["choices"])
        if node_data["type"] == "combat":
            story.nodes[node_id].combat_data = node_data["content"]

    story.start_story("start")
    return story

def handle_story_progression(story):
    if not story.current_node:
        return None

    current_node = story.current_node
    if current_node.node_type == "combat":
        return current_node.combat_data
    if current_node.node_type in ["narrative", "dialog"]:
        return {
                "type": current_node.node_type,
                "content": current_node.content,
                "choices": current_node.choices
                }
    return None
# not sure if I need this yet or if the code will function without it
def make_choice(story, choice_id):
    if not story.current_node:
        return None

    current_node = story.current_node
    if choice_id not in [choice["id"] for choice in current_node.choices]:
        return None

    for choice in current_node.choices:
        if choice["id"] == choice_id:
            next_node = choice["next_node"]
            story.current_node = story.nodes[next_node]
            return story.current_node
    return None
