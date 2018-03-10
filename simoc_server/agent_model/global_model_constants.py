import collections

from simoc_server.database.db_model import GlobalModelConstant
from simoc_server.util import load_db_attributes_into_dict

class GlobalModelConstantsHolder(collections.Mapping):

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._loaded = False

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __getitem__(self, key):
        if not self._loaded:
            _constants = GlobalModelConstant.query.all()
            load_db_attributes_into_dict(_constants, target=self._dict)
            self._loaded = True
        return self._dict[key]


global_model_constants = GlobalModelConstantsHolder()