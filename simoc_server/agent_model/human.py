from .baseagent import BaseAgent

class HumanAgent(BaseAgent):
    
    __agent_type_name__ = "Human" #__sprite_mapper__ = HumanSpriteMapper
    thirstPerStep = 10.5 #variable for controling thirst
    hungerPerStep = 10.5 #variable for controling hunger
    hungerthreshold = 40 #variable for controling hunger/eat
    thirstthreshold = 60 #variable for controling thirst/drink
    sleepthreashold = 7  #variable for controling sleep/hours
    workthreashold = 8   #variable for controling work/hours

    status = {
        "Standby": "Standby",
        "Working": "Working",
        "Busy" : "Busy",
        "Sleeping": "Sleeping",
        "Relaxing": "Relaxing",
        "Exporing" : "Exporing"
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
        self.goal_pos = (0,0) #variable for tracking work hours
        self.energy = self.get_agent_type_attribute("max_energy") #calories to burn??
    
    def step(self):
        self.totalsteps += 1
        self.default()
        if self.hunger < HumanAgent.hungerthreshold:
            self.eat()
        if self.thirst < HumanAgent.thirstthreshold:
            self.drink()
        if self.pos is not self.goal_pos:
            self.move()
        pass

    def move(self):
        #move one space at a time
        x, y = self.pos
        dx, dy = self.goal_pos

        if (x - dx) < 0:
            x = x - 1
        elif (x - dx) > 0:
            x = x + 1
        elif (y - dy) < 0:
            y = y - 1
        elif (y - dy) > 0:
            y = y + 1

        self.model.grid.move_agent(self, (x,y))
        pass

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
    def setGoal(self , goal, position):
        self.goal = goal
        self.goal_pos = position
        pass

    def default(self):
        self.thirst = self.thirst - (self.model.minutes_per_step * HumanAgent.thirstPerStep)
        self.hunger = self.hunger - (self.model.minutes_per_step * HumanAgent.hungerPerStep)
        #if self.status == "Sleeping":
        #   sleephours += 1
        #if self.status == "Working" and self.pos is self.goal_pos:
        #if self.status == "StandBy" and self.pos is self.goal_pos:
        #if self.status == "Relaxing" and self.pos is self.goal_pos:
        #if self.status == "Exploring" and self.pos is self.goal_pos:
        #if self.status == "Sleeping" and self.pos is self.goal_pos:
        #if self.status == "Busy" and self.pos is self.goal_pos:
        pass
        
    
HumanAgent.__persisted_attributes__.add("energy")
HumanAgent.__client_attributes__.add("energy")
HumanAgent.__persisted_attributes__.add("thirst")
HumanAgent.__client_attributes__.add("thirst")
HumanAgent.__persisted_attributes__.add("hunger")
HumanAgent.__client_attributes__.add("hunger")
HumanAgent.__persisted_attributes__.add("health")
HumanAgent.__client_attributes__.add("health")
HumanAgent.__persisted_attributes__.add("status")
HumanAgent.__client_attributes__.add("status")
HumanAgent.__persisted_attributes__.add("age")
HumanAgent.__client_attributes__.add("age")
HumanAgent.__persisted_attributes__.add("totalsteps")
