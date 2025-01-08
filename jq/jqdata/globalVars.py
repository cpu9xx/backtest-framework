from .logger import log
import pickle
class GlobalVars(object):
    def get_state(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('__')}
        # dict_data = {}
        # for key, value in self.__dict__.items():
        #     try:
        #         log.test(f"Dumping pickle {key}, value: {value}")
        #         dict_data[key] = pickle.dumps(value)
        #     except Exception as e:
        #         log.error(f"Failed to dump pickle {key}: {e}")
        # return pickle.dumps(dict_data)

    def set_state(self, state):
        self.__dict__.update(state)
        # dict_data = pickle.loads(state)
        # for key, value in dict_data.items():
        #     try:
        #         self.__dict__[key] = pickle.loads(value)
        #     except Exception as e:
        #         log.error(f"Failed to load pickle {key}: {e}")
