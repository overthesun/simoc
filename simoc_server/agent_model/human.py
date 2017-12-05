import math
from .baseagent import BaseAgent
from .plants import PlantAgent

class HumanAgent(BaseAgent):

    __agent_type_name__ = "human" #__sprite_mapper__ = HumanSpriteMapper
    thirstPerStep = 10.5 #variable for controling thirst
    hungerPerStep = 10.5 #variable for controling hunger
    hungerthreshold = 40 #variable for controling hunger/eat
    thirstthreshold = 60 #variable for controling thirst/drink
    sleepthreashold = 7  #variable for controling sleep/hours
    workthreashold = 8   #variable for controling work/hours

    __persisted_attributes__ = ["energy", "thirst", "hunger", "health", "status", "age", "totalsteps"]
    __client_attributes__ = ["energy", "thirst", "hunger", "health", "status", "age"]

    status = {
        "Standby": "Standby",
        "Working": "Working",
        "Busy" : "Busy",
        "Sleeping": "Sleeping",
        "Relaxing": "Relaxing",
        "Exporing" : "Exporing",
        "Harvesting":"Harvesting",
        "Planting":"Planting"
        }

    def init_new(self):
        self.age = 18
        self.workhours = 0  #variable for tracking work hours
        self.workhours = 0  #variable for tracking work hours
        self.sleephours = 7 #variable for tracking sleephours
        self.explorehours = 0#variable for tracking explore hours
        self.sleepstep = 0  #variable for tracking last sleep step
        self.workstep = 0   #variable for tracking last workstep
        self.relaxstep = 0  #variable for tracking last relax step
        self.totalsteps = 0 #variable for tracking total step
        self.thirst = 100   #variable for tracking thirst
        self.hunger = 100   #variable for tracking hunger
        self.happiness = 100 #variable for tracking happiness
        self.health = 100   #variable for tracking health
        self.goal = HumanAgent.status["Standby"] #variable for tracking work hours
        self.status = HumanAgent.status["Standby"] #variable for tracking work hours
        self.goal_pos = None #variable for tracking work hours
        self.energy = self.get_agent_type_attribute("max_energy") #calories to burn??

    def step(self):
        self.totalsteps += 1
        self.default()
        self.find_goal()
        if self.hunger < HumanAgent.hungerthreshold:
            self.eat()
        if self.thirst < HumanAgent.thirstthreshold:
            self.drink()
        if self.pos is not self.goal_pos:
            self.move()
        else:
            self.handle_goal_reached()

    def move(self):
        #move one space at a time
        x, y = self.pos
        dx, dy = self.goal_pos
        print(x,y)
        print(dx,dy)
        print("----")

        if (x - dx) < 0:
            x = x - 1
        elif (x - dx) > 0:
            x = x + 1
        elif (y - dy) < 0:
            y = y - 1
        elif (y - dy) > 0:
            y = y + 1

        self.model.grid.move_agent(self, (x,y))

    #method to eat
    def eat(self):
        self.hunger += (100 - self.hunger)
        pass

    #method to drink
    def drink(self):
        self.thirst += (100 - self.thirst)
        pass

    # method to sleep
    def sleep(self):
        # Add to sleep hours subtract from work hours
        # set goal_pos
        pass

    # method to work
    def work(self):
        #Add to work hours subtract from sleep
        #set goal_pos

        pass

    # method to explore
    def explore(self):
        #Add to explore hours subtrsct supplies and happiness/health
        # set goal_pos
        pass

    # method to relax
    def relax(self):
        # set goal_pos
        pass

    # method to set goal
    def set_goal(self , goal, position):
        self.goal = goal
        self.goal_pos = position
        pass

    def default(self):
        self.thirst = self.thirst - (self.model.minutes_per_step * thirstPerStep)
        self.hunger = self.hunger - (self.model.minutes_per_step * hungerPerStep)
        #if self.status == "Sleeping":
        #   sleephours += 1
        #if self.status == "Working" and self.pos is self.goal_pos:
        #if self.status == "StandBy" and self.pos is self.goal_pos:
        #if self.status == "Relaxing" and self.pos is self.goal_pos:
        #if self.status == "Exploring" and self.pos is self.goal_pos:
        #if self.status == "Sleeping" and self.pos is self.goal_pos:
        #if self.status == "Busy" and self.pos is self.goal_pos:
        pass

    def find_goal(self):
        if(self.goal_pos is None):
            plants = self.model.get_agents(PlantAgent)
            harvestable = [plant for plant in plants if plant.status == "grown"]
            closest = None
            closest_distance = None
            for plant in harvestable:
                distance = get_distance_to(plant.pos)
                if(closest is None or distance < closest_distance):
                    closest = plant
                    closest_distance = distance
            if closest is not None:
                self.set_goal(closest, status["Harvesting"])
            else:
                neighborhood = model.grid.get_neighborhood(self.pos,
                    moore=True,
                    include_center=True,
                    radius=2)
                closest_empty = None
                closest_distance = None
                for cell in neighborhood:
                    cell_contents = model.grid.get_cell_list_contents(cell)
                    no_plants = True
                    for content in cell_contents:
                        if isinstance(conent, PlantAgent):
                            no_plants = False
                            break
                    distance = get_distance_to(cell.pos)
                    if no_plants and closest_empty is None or \
                            closest_distance < distance:
                        closest_empty = cell
                if closest_empty is not None:
                    self.set_goal(closest, status["Planting"])
                else:
                    heading = self.pos(random.randrange(2), random.randrange(2))
                    self.set_goal(heading, self.set_goal(heading, status["Exploring"]))

    def handle_goal_reached(self):
        if self.goal == status["Harvesting"]:
            cell_contents = self.model.get_cell_list_contents()
            for content in cell_contents:
                if isinstance(content, PlantAgent) and content.status == "grown":
                    self.model.remove(content)
        elif self.goal == status["Planting"]:
            cell_contents = self.model.get_cell_list_contents()
            has_plants = False
            for content in cell_contents:
                if isinstance(content, PlantAgent) and content.status == "grown":
                    has_plants = True
                    break
            if not has_plants:
                self.model.add_agent(PlantAgent(), self.pos)

        self.goal_pos = None
        self.status = HumanAgent.status["Standby"]

    def get_distance_to(self, pos):
        # TODO move this elsewhere
        distance = math.sqrt((self.pos[0] - pos[0])**2 + \
                            (self.pos[1] - pos[1])**2)

