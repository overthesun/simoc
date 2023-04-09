class AgentDataCollector():

    @classmethod
    def from_agent(cls, agent):
        return cls(agent)

    def __init__(self, agent):
        # Static Fields
        self.agent = agent
        self.name = agent.agent_type
        self.age = []
        self.amount = []
        self.snapshot_attrs = ['name', 'age', 'amount']
        # Plant-Specific Fields
        for attr in ['lifetime', 'full_amount', 'reproduce']:
            if hasattr(self.agent, attr):
                self.snapshot_attrs.append(attr)
                setattr(self, attr, getattr(self.agent, attr))
        # Plants
        if agent.agent_class == 'plants':
            self.snapshot_attrs.append('growth')
            growth_attrs = {'par_factor', 'cu_factor', 'te_factor', 'density_factor',
                            'crop_management_factor', 'growth_rate', 'grown', 'agent_step_num'}
            self.growth = {attr: [] for attr in growth_attrs if hasattr(self.agent, attr)}
        # Concrete
        if agent.agent_type == 'concrete':
            self.snapshot_attrs.append('growth')
            self.growth = dict(carbonation_rate=[], carbonation=[])
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
                self.storage[currency] = []
                if 'storage_ratios' not in self.snapshot_attrs:
                    self.snapshot_attrs.append('storage_ratios')
                    self.storage_ratios = {}
                self.storage_ratios[currency] = []
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
            # Flows
            if attr.startswith(('in', 'out')):
                if 'flows' not in self.snapshot_attrs:
                    self.snapshot_attrs.append('flows')
                    self.flows = {'in': {}, 'out': {}}
                prefix, currency = attr.split('_', 1)
                currency_desc = self.agent.model.currency_dict.get(currency)
                # Regular currencies
                if currency_desc['type'] == 'currency':
                    self.flows[prefix][currency] = {}
                    for storage in self.agent.selected_storage[prefix][currency]:
                        self.flows[prefix][currency][storage.agent_type] = []
                # Currency classes
                elif currency_desc['type'] == 'currency_class':
                    for class_currency in currency_desc['currencies']:
                        self.flows[prefix][class_currency] = {}
                    for storage in self.agent.selected_storage[prefix][currency]:
                        for class_currency in currency_desc['currencies']:
                            self.flows[prefix][class_currency][storage.agent_type] = []
                # Buffer
                cr_buffer = self.agent.attr_details[attr]['criteria_buffer']
                if cr_buffer:
                    if 'buffer' not in self.snapshot_attrs:
                        self.snapshot_attrs.append('buffer')
                        self.buffer = {}
                    self.buffer[attr] = []
                # Deprive
                deprive_value = self.agent.attr_details[attr]['deprive_value']
                if deprive_value:
                    if 'deprive' not in self.snapshot_attrs:
                        self.snapshot_attrs.append('deprive')
                        self.deprive = {}
                    self.deprive[attr] = []
            # Events
            if attr.startswith('event'):
                if 'events' not in self.snapshot_attrs:
                    self.snapshot_attrs += ['events', 'event_multipliers']
                    self.events = {}
                    self.event_multipliers = {}
                event_type = attr.split('_', 1)[1]
                self.events[event_type] = []
                self.event_multipliers[event_type] = []
        # Variation
        if 'initial_variable' in self.agent:
            self.snapshot_attrs.append('initial_variable')
            self.initial_variable = self.agent.initial_variable
        if 'step_variable' in self.agent:
            self.snapshot_attrs.append('step_variable')
            self.step_variable = []

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
                record.append(getattr(self.agent, field))
        if 'co2_scale' in self.snapshot_attrs:
            for field, record in self.co2_scale.items():
                record.append(self.agent.co2_scale[field])
        if 'flows' in self.snapshot_attrs:
            for prefix, currencies in self.flows.items():
                for currency, storages in currencies.items():
                    step_data = self.agent.step_exchange_buffer[prefix].get(currency)
                    for agent, record in storages.items():
                        value = 0 if not step_data else step_data.get(agent, 0)
                        record.append(value)
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


    def get_data(self, step_range=None, fields=None, debug=False, clear_cache=False):
        """Return all data (default) or specified range/fields."""
        if debug or fields == None:
            fields = self.snapshot_attrs
        else:
            fields = [f for f in fields if self.snapshot_attrs.includes(f)]

        def _copy_range(value, start, end):
            """Recursively segment lists"""
            if isinstance(value, (str, int, float)):
                return value
            if isinstance(value, list):
                return value[start:end]
            elif isinstance(value, dict):
                return {k: _copy_range(v, start, end) for k, v in value.items()}
        if step_range is None:
            start, end = 0, len(self.age)
        else:
            start, end = step_range
        data = {f: _copy_range(getattr(self, f), start, end) for f in fields}

        if clear_cache:
            def _clear(section):
                """Recursively clear lists while retaining and dict structures and strs"""
                if isinstance(section, list):
                    return []
                elif isinstance(section, dict):
                    return {k: _clear(v) for k, v in section.items()}
                else:
                    return section
            for field in self.snapshot_attrs:
                setattr(self, field, _clear(getattr(self, field)))
        return data
