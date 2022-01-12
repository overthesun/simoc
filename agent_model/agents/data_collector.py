class AgentDataCollector():

    @classmethod
    def from_agent(cls, agent):
        return cls(agent)

    def __init__(self, agent):
        # Static Fields
        self.agent = agent
        self.name = agent.agent_type
        self.age = [0]
        self.amount = [self.agent.amount]
        self.snapshot_attrs = ['name', 'age', 'amount']
        # Plant-Specific Fields
        for attr in ['lifetime', 'full_amount', 'reproduce']:
            if hasattr(self.agent, attr):
                self.snapshot_attrs.append(attr)
                setattr(self, attr, getattr(self.agent, attr))
        # Dynamic Fields
        for attr, attr_value in self.agent.attrs.items():
            if attr_value == 0:
                continue
            # Storage
            if attr.startswith('char_capacity'):
                if 'storage' not in self.snapshot_attrs:
                    self.snapshot_attrs.append('storage')
                    self.storage = {}
                currency = attr.split('_', 2)[2]
                self.storage[currency] = [self.agent[currency]]
                if 'storage_ratios' not in self.snapshot_attrs:
                    self.snapshot_attrs.append('storage_ratios')
                    self.storage_ratios = {}
                self.storage_ratios[currency] = [self.agent.model.storage_ratios[self.name][currency + '_ratio']]
                if 'capacity' not in self.snapshot_attrs:
                    self.snapshot_attrs.append('capacity')
                    self.capacity = {}
                self.capacity[currency] = dict(value=attr_value,
                                               unit=self.agent.attr_details[attr]['unit'])
                currency_class = self.agent.currency_dict[currency]['class']
                if currency_class not in self.capacity:
                    class_attr = f"char_capacity_{currency_class}"
                    self.capacity[currency_class] = dict(value=self.agent[class_attr],
                                                         unit=self.agent.attr_details[class_attr]['unit'])
            # Growth
            if attr.startswith('char_growth_criteria'):
                self.snapshot_attrs += ['total_growth', 'growth']
                self.total_growth = self.agent.total_growth,
                self.growth = dict(current_growth=[self.agent.current_growth],
                                   growth_rate=[self.agent.growth_rate],
                                   grown=[self.agent.grown],
                                   agent_step_num=[self.agent.agent_step_num])
            # Flows
            if attr.startswith(('in', 'out')):
                if 'flows' not in self.snapshot_attrs:
                    self.snapshot_attrs += ['flows', 'flow_records']
                    self.flows = {}
                    self.flow_records = {}
                currency = attr.split('_', 1)[1]
                self.flows[currency] = [0]
                self.flow_records[currency] = [{}]
                # Buffer
                cr_buffer = self.agent.attr_details[attr]['criteria_buffer']
                if cr_buffer:
                    if 'buffer' not in self.snapshot_attrs:
                        self.snapshot_attrs.append('buffer')
                        self.buffer = {}
                    self.buffer[attr] = [0]
                # Deprive
                deprive_value = self.agent.attr_details[attr]['deprive_value']
                if deprive_value:
                    if 'deprive' not in self.snapshot_attrs:
                        self.snapshot_attrs.append('deprive')
                        self.deprive = {}
                    self.deprive[attr] = [deprive_value * self.amount[0]]
            # Events
            if attr.startswith('event'):
                if 'events' not in self.snapshot_attrs:
                    self.snapshot_attrs += ['events', 'event_multipliers']
                    self.events = {}
                    self.event_multipliers = {}
                event_type = attr.split('_', 1)[1]
                self.events[event_type] = [[]]
                self.event_multipliers[event_type] = ['-']
        # Variation
        if 'initial_variable' in self.agent:
            self.snapshot_attrs.append('initial_variable')
            self.initial_variable = self.agent.initial_variable
        if 'step_variable' in self.agent:
            self.snapshot_attrs.append('step_variable')
            self.step_variable = [1]

    def step(self):
        self.age.append(self.agent.age)
        self.amount.append(self.agent.amount)
        if 'storage' in self.snapshot_attrs:
            for currency, record in self.storage.items():
                record.append(self.agent[currency])
            for currency, record in self.storage_ratios.items():
                record.append(self.agent.model.storage_ratios[self.name][currency + '_ratio'])
        if 'growth' in self.snapshot_attrs:
            for field, record in self.growth.items():
                record.append(self.agent[field])
        if 'flows' in self.snapshot_attrs:
            for currency, record in self.flows.items():
                record.append(self.agent.last_flow[currency])
            for currency, record in self.flow_records.items():
                record.append(self.agent.flows[currency])
        if 'buffer' in self.snapshot_attrs:
            for cr_id, record in self.buffer.items():
                record.append(self.agent.buffer.get(cr_id, 0))
        if 'deprive' in self.snapshot_attrs:
            for currency, record in self.deprive.items():
                record.append(self.agent.deprive.get(currency, 0))
        if 'step_variable' in self.snapshot_attrs:
            self.step_variable.append(self.agent.step_variable)
        if 'events' in self.snapshot_attrs:
            for event, record in self.events.items():
                if event in self.agent.events:
                    record.append(self.agent.events[event])
                    self.event_multipliers[event].append(self.agent.event_multipliers[event])
                else:
                    record.append([])
                    self.event_multipliers[event].append('-')


    def get_data(self, debug=False, clear_cache=False):
        default_fields = ['flows', 'storage', 'growth']
        if debug:
            fields = self.snapshot_attrs
        else:
            fields = [f for f in default_fields if hasattr(self, f)]
        data = {a: getattr(self, a) for a in fields}
        if clear_cache:
            def _clear(section):
                """Recursively clear lists while retaining and dict structures and strs"""
                if type(section) == str:
                    return section
                if type(section) == list:
                    return []
                elif type(section) == dict:
                    return {k: _clear(v) for k, v in section.items()}
            for field in self.snapshot_attrs:
                setattr(self, field, _clear(getattr(self, field)))
        return data
