import json

from py_arg.abstract_argumentation.classes.argument import Argument
from py_arg.abstract_argumentation.classes.defeat import Defeat
from py_arg.abstract_argumentation.classes.abstract_argumentation_framework \
    import AbstractArgumentationFramework


# class ArgumentationFrameworkFromJsonReader:
#     def __init__(self):
#         pass

#     @staticmethod
#     def from_json(json_object) -> AbstractArgumentationFramework:
#         if json_object['name']:
#             name = json_object['name']
#         else:
#             name = ''
#         arguments = [Argument(argument_name)
#                      for argument_name in json_object['arguments']]
#         defeats = [Defeat(Argument(from_argument), Argument(to_argument)) for
#                    from_argument, to_argument in json_object['defeats']]
#         return AbstractArgumentationFramework(name, arguments, defeats)

#     def read_from_json(self, file_path: str) -> AbstractArgumentationFramework:
#         with open(file_path, 'r') as reader:
#             argumentation_framework_json = json.load(reader)
#         return self.from_json(argumentation_framework_json)


class ArgumentationFrameworkFromJsonReader:
    def __init__(self):
        pass

    @staticmethod
    def from_json(json_object) -> AbstractArgumentationFramework:
        # -- 1) Name
        name = json_object.get('name', '')

        # -- 2) Build Argument instances (and keep them in a dict for lookup)
        arg_map = {}
        for a in json_object.get('arguments', []):
            arg_id = a['id']
            arg_obj = Argument(arg_id)
            # attach your extra fields
            # arg_obj.annotation = a['annotation']
            # arg_obj.url        = a['url']
            arg_map[arg_id] = arg_obj

        # -- 3) Build Defeat instances
        defeats = []
        for d in json_object.get('defeats', []):
            attacker = arg_map[d['from']]
            target   = arg_map[d['to']]
            defeat = Defeat(attacker, target)
            # attach the defeat’s annotation string
            # defeat.annotation = d['annotation']
            defeats.append(defeat)

        # -- 4) Return the framework
        return AbstractArgumentationFramework(name,
                                              list(arg_map.values()),
                                              defeats)

    def read_from_json(self, file_path: str) -> AbstractArgumentationFramework:
        with open(file_path, 'r') as reader:
            af_json = json.load(reader)
        return self.from_json(af_json)
