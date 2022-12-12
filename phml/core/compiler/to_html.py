from typing import Optional

from phml.core.nodes import AST, All_Nodes


class ToHTML:
    """Compiles an ast to a hypertest markup language."""

    def __init__(self, ast: Optional[AST] = None, offset: int = 4):
        self.ast = ast
        self.offset = offset

    def compile(self, ast: Optional[AST] = None, offset: Optional[int] = None) -> str:
        """Compile an ast to html."""

        ast = ast or self.ast
        if ast is None:
            raise Exception("Converting to html requires that an ast is provided")

        self.offset = offset or self.offset
        lines = self.__compile_children(ast.tree)
        return "\n".join(lines)

    def __one_line(self, node, indent: int = 0) -> str:
        return "".join(
            [
                " " * indent + node.start_tag(),
                node.children[0].stringify(
                    indent + self.offset if node.children[0].num_lines > 1 else 0
                ),
                node.end_tag(),
            ]
        )

    def __many_children(self, node, indent: int = 0) -> list:
        from phml.utilities import visit_children  # pylint: disable=import-outside-toplevel

        lines = []
        for child in visit_children(node):
            if child.type == "element":
                lines.extend(self.__compile_children(child, indent + self.offset))
            else:
                lines.append(child.stringify(indent + self.offset))
        return lines

    def __construct_element(self, node, indent: int = 0) -> list:
        lines = []
        if (
            len(node.children) == 1
            and node.children[0].type == "text"
            and node.children[0].num_lines == 1
        ):
            lines.append(self.__one_line(node, indent))
        else:
            lines.append(" " * indent + node.start_tag())
            lines.extend(self.__many_children(node, indent))
            lines.append(" " * indent + node.end_tag())
        return lines

    def __compile_children(self, node: All_Nodes, indent: int = 0) -> list[str]:
        from phml.utilities import visit_children  # pylint: disable=import-outside-toplevel

        lines = []
        if node.type == "element":
            if node.startend:
                lines.append(" " * indent + node.start_tag())
            else:
                lines.extend(self.__construct_element(node, indent))
        elif node.type == "root":
            for child in visit_children(node):
                lines.extend(self.__compile_children(child))
        else:
            lines.append(node.stringify(indent + self.offset))

        return lines
