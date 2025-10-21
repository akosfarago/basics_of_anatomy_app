class ActorRegistry:
    def __init__(self):
        self.actor_to_name = {}

    def load_mapping(self, mapping: dict):
        """Bulk load actor:name mapping"""
        self.actor_to_name = mapping

    def get_bone_name(self, actor):
        return self.actor_to_name.get(actor, None)

    def get_all_actors(self):
        return list(self.actor_to_name.keys())

    def get_all_names(self):
        return list(self.actor_to_name.values())
