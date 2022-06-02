from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Tuple, List, Const, Dict, Assign


class FullSettings(BaseChecker):
    """
       Use full settings always
       https://docs.conan.io/en/latest/migrating_to_2.0/recipes.html#settings
    """

    __implements__ = IAstroidChecker

    name = "conan-full-settings"
    msgs = {
        "E9001": (
            "Missing one or more settings",
            "conan-missing-setting",
            "Use full settings always: `settings = 'arch', 'build_type', 'compiler', 'os'`"
        ),
        "E9002": (
            "Do not use settings as a dictionary",
            "conan-dict-settings",
            "Use only the default settings: `settings = 'arch', 'build_type', 'compiler', 'os'`."
            "The configuration can be restricted in `validate()`"
        ),
        "E9003": (
            "Missing settings attribute",
            "conan-missing-settings",
            "The member attribute `settings` must be declared with all values: `settings = 'arch', 'build_type', 'compiler', 'os'`"
        )
    }

    def visit_assign(self, node: nodes) -> None:
        parent = node.parent
        if hasattr(parent, 'basenames') and parent.basenames == ['ConanFile']:
            key = list(node.get_children())[0].as_string()
            value = list(node.get_children())[1]
            if key == 'settings':
                if isinstance(value, (Tuple, List, Const)):
                    # single value is str, multiple can be tuple
                    if value.pytype() == "builtins.str" or len(value.itered()) < 4:
                        self.add_message("conan-missing-setting", node=node)
                elif isinstance(value, Dict):
                    self.add_message("conan-dict-settings", node=node)

    def visit_classdef(self, node: nodes) -> None:
        if node.basenames == ['ConanFile']:
            for attr in node.body:
                if isinstance(attr, Assign) and list(attr.get_children())[0].as_string() == "settings":
                    return
            self.add_message("conan-missing-settings", node=node)
