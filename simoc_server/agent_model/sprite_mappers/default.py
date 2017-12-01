import operator

operator_strings = {
    operator.lt: "less_than",
    operator.le: "less_equal",
    operator.gt: "greater_than",
    operator.ge: "greater_equal",
    operator.eq: "equal"
}

class DefaultSpriteMapper(object):
    _singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singleton or cls._singleton.__class__ != cls:
            cls._singleton = super(DefaultSpriteMapper, cls).__new__(cls, *args, **kwargs)
            cls._singleton.default_sprite = "default.png"
            cls._singleton.rules = []
            cls._singleton._init_rules()
        return cls._singleton

    def _init_rules(self):
        pass

    def _add_rule(self, rule):
        self.rules.append(rule)

    def to_serializable(self):
        d = {
            "default_sprite":self.default_sprite,
        }
        rules_vals = []
        for rule in self.rules:
            rules_vals.append({
                "comparator":{
                    "attr_name":rule.comparator.attr_name,
                    "operator":operator_strings[rule.comparator.op],
                    "value":rule.comparator.value
                },
                "precedence":rule.precedence,
                "offset_x":rule.offset[0],
                "offset_y":rule.offset[1],
                "sprite_path":rule.sprite_path
            })
        d["rules"] = rules_vals
        return d

    def evaluate(self, agent):
        matches = []
        for rule in self.rules:
            if rule.check(agent):
                matches.append(rule)
        return max(matches, key=lambda x: x.precedence)

class SpriteRule(object):
    def __init__(self, comparator, sprite_path, precedence=0, offset=(0,0)):
        self.comparator = comparator
        self.sprite_path = sprite_path
        self.precedence = precedence
        self.offset = offset

    def check(self, agent):
        return self.comparator(agent)

class AttributeComparator(object):

    def __init__(self, attr_name, op, value):
        self.attr_name = attr_name
        self.op = op
        self.value = value

    def check(self, agent):
        return self.op(agent.__dict__[self.attr_name], self.value)



# class CompoundAttributeComparator(object):

#     def __init__(self, sprite_rules):
#         self.sprite_rules = sprite_rules

#     def check(self):
#         for sprite_rule in sprite_rules:
#             if(sprite_rule.check()):
#                 return True
#         return False
