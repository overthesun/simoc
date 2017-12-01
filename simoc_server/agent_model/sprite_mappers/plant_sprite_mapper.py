from .default import DefaultSpriteMapper, SpriteRule, AttributeComparator
import operator

class PlantSpriteMapper(DefaultSpriteMapper):

    def _init_rules(self):
        self.default_sprite = "grown.png"

        # grown rule
        grown_comparator = AttributeComparator("status", operator.eq, "grown")
        self._add_rule(SpriteRule(grown_comparator, "grown.png", offset=(0, -70)))