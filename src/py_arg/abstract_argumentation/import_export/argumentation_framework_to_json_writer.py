import json

from py_arg.abstract_argumentation.classes.abstract_argumentation_framework \
    import AbstractArgumentationFramework
from py_arg.incomplete_aspic.import_export.writer import Writer


# class ArgumentationFrameworkToJSONWriter(Writer):
#     def __init__(self):
#         super().__init__()

#     @staticmethod
#     def to_dict(argumentation_framework: AbstractArgumentationFramework):
#         return {'name': argumentation_framework.name,
#                 'arguments':
#                     [str(argument)
#                      for argument in argumentation_framework.arguments],
#                 'defeats': [(str(defeat.from_argument),
#                              str(defeat.to_argument))
#                             for defeat in argumentation_framework.defeats]}

#     def write(self, argumentation_framework: AbstractArgumentationFramework,
#               file_name: str):
#         write_path = self.data_folder / file_name
#         result = self.to_dict(argumentation_framework)
#         with open(write_path, 'w') as write_file:
#             json.dump(result, write_file)

class ArgumentationFrameworkToJSONWriter(Writer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def to_dict(af: AbstractArgumentationFramework) -> dict:
        # 1) Name
        result = {'name': af.name}

        # 2) Arguments → list of {id, annotation, url}
        args = []
        for arg in af.arguments:
            args.append({
                'id':         getattr(arg, 'id', str(arg)),
                'annotation': getattr(arg, 'annotation', ""),
                'url':        getattr(arg, 'url', "")
            })
        result['arguments'] = args

        # 3) Defeats → list of {from, to, annotation}
        defs_ = []
        for d in af.defeats:
            attacker = d.from_argument
            target   = d.to_argument
            defs_.append({
                'from':       getattr(attacker, 'id', str(attacker)),
                'to':         getattr(target,   'id', str(target)),
                'annotation': getattr(d, 'annotation', "")
            })
        result['defeats'] = defs_

        return result

    def write(self,
              argumentation_framework: AbstractArgumentationFramework,
              file_name: str):
        write_path = self.data_folder / file_name
        result = self.to_dict(argumentation_framework)
        # pretty‑print JSON with 2‑space indent
        with open(write_path, 'w', encoding='utf-8') as write_file:
            json.dump(result, write_file, indent=2, ensure_ascii=False)
