from .default import DefaultSpriteMapper, SpriteRule, AttributeComparator
import operator

class PlantSpriteMapper(DefaultSpriteMapper):

    def _init_rules(self):
        self.default_sprite = "plants/grown.png"

        # planted rule
        grown_comparator = AttributeComparator("status", operator.eq, "planted")
        self._add_rule(SpriteRule(grown_comparator, "plants/seedling.png", offset=(0, 0)))

        # grown rule
        grown_comparator = AttributeComparator("status", operator.eq, "grown")
        self._add_rule(SpriteRule(grown_comparator, "plants/grown.png", offset=(0, -70)))