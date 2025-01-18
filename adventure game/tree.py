from story_content import get_story_content

class StoryNode:
    def __init__(self, node_id, node_type, content, choices=None):
        self.node_id = node_id
        self.node_type = node_type
        self.content = content
        self.choices = choices if choices else []
        self.combat_data = None

class StoryTree:
    def __init__(self):
        self.nodes = {}
        self.current_node = None

    def add_node(self, node_id, node_type, content, choices):
        self.nodes[node_id] = StoryNode(node_id, node_type, content, choices)

    def start_story(self, start_node):
        self.current_node = self.nodes.get(start_node)
        if not self.current_node:
            print(f"Debug: Start node '{start_node}' not found in nodes")
        else:
            print(f"Debug: Story started at node '{self.current_node.node_type}'")

    def make_choice(self, choice_id):
        if not self.current_node:
            print("Debug: No current node found")
            return None

        current_node = self.current_node
        if choice_id not in [choice["id"] for choice in current_node.choices]:
            return None
    
        for choice in current_node.choices:
            if choice["id"] == choice_id:
                next_node = choice["next_node"]
                self.current_node = self.nodes.get(next_node)
                if self.current_node:
                    print(f"Debug: Moved to node '{next_node}' with type '{self.current_node.node_type}'")
                else:
                    print(f"Debug: Next node '{next_node}' not found in nodes")
                return self.current_node
        return None

    def get_available_choices(self):
        if self.current_node:
            return self.current_node.choices
        return None

def create_story():
    story = StoryTree()
    story_data = get_story_content()
    print(f"Debug: story_data = {story_data}")

    for node_id, node_data in story_data.items():
        choices = node_data.get("choices", []) # checks if a node has choices attached
        story.add_node(node_id, node_data["type"], node_data["content"], choices)
        if node_data["type"] == "combat":
            story.nodes[node_id].combat_data = node_data["content"]
        print(f"Debug: Added node '{node_id}' with choices '{choices}'")

    story.start_story("start")
    print(f"Debug: story started with current_node = {story.current_node}")
    return story

def handle_story_progression(story):
    if not story.current_node:
        return None

    current_node = story.current_node
    print(f"Debug: current_node type = {current_node.node_type}")
    if current_node.node_type == "combat":
        return current_node.combat_data
    if current_node.node_type in ["narrative", "dialog"]:
        return {
                "type": current_node.node_type,
                "content": current_node.content,
                "choices": current_node.choices
                }
    return None
