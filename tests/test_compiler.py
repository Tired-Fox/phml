from pytest import raises

from phml.compiler import HypertextMarkupCompiler, __SETUP__, add_step, setup_step
from phml.parser import HypertextMarkupParser
from phml.components import ComponentManager
from phml.nodes import Element, AST, Literal, LiteralType

from data import *

components = ComponentManager()
components.add("tests/src/component.phml", ignore="tests/src/")
components.add("tests/src/sub/component.phml", ignore="tests/src/")
components["Component"]["hash"] = hashes["Component"]
components["Sub.Component"]["hash"] = hashes["Sub.Component"]

html_exists = False


@setup_step
def step_collect_html(node, *_):
    global html_exists
    for n in node:
        if isinstance(n, Element) and n.tag == "html":
            html_exists = True


add_step(step_collect_html, "setup")


class TestHyperTextMarkupCompiler:
    compiler = HypertextMarkupCompiler()

    def test_compile(self):
        ast = self.compiler.compile(
            phml_ast, components, message=message, _phml_path_="tests/src/"
        )

        assert ast == html_ast
        assert html_exists

    def test_render(self):
        ast = self.compiler.compile(
            phml_ast, components, message=message, _phml_path_="tests/src/"
        )
        result = self.compiler.render(ast)
        assert result == html_file

    def test_compiler_compressed(self):
        ast = self.compiler.compile(
            phml_ast, components, message=message, _phml_path_="tests/src/"
        )
        result = self.compiler.render(ast, True)
        assert result == html_file_compressed

    def test_compiler_unknown_renderable(self):
        ast = self.compiler.compile(
            phml_ast, components, message=message, _phml_path_="tests/src/"
        )
        ast.append(AST())
        with raises(TypeError, match="Unknown renderable node type .+"):
            self.compiler.render(ast)


class TestCompilerStepExceptions:
    compiler = HypertextMarkupCompiler()
    parser = HypertextMarkupParser()
    components = ComponentManager()

    def test_step_loop(self):
        no_expression = self.parser.parse(
            """\
<For each=""><p>{{i}}</p></For>\
"""
        )
        no_iterations = self.parser.parse(
            """\
<For each="i in range(0)"><p>{{i}}</p></For>
<p @elif="not blank(_loop_fail_)">Error: {{_loop_fail_}}</p>
<p>No Iterations</p>\
"""
        )
        has_exception = self.parser.parse(
            """\
<For each="i in None"><p>{{i}}</p></For>
<p @elif="not blank(_loop_fail_)">Error: {{_loop_fail_}}</p>
<p>No Iterations</p>\
"""
        )

        with raises(
            ValueError,
            match="Expected expression in 'each' attribute for <For/> to be a valid list comprehension.",
        ):
            self.compiler.compile(
                no_expression, self.components, _phml_path_="tests/src/"
            )

        assert self.compiler.compile(
            no_iterations, self.components, _phml_path_="tests/src/"
        ) == AST([Element("p", children=[Literal(LiteralType.Text, "No Iterations")])])

        ast = self.compiler.compile(has_exception, components)
        assert len(ast) == 3 and isinstance(ast[0], Element) and ast[0].tag == "p"

    def test_step_component_slot_multiple_exception(self):
        components["Sub.Component"]["elements"].append(
            Element("Slot", {"name": "extra"})
        )

        with raises(
            ValueError,
            match="Can not have more that one of the same named slot in a component",
        ):
            self.compiler.compile(phml_ast, components, _phml_path_="tests/src/")

        components["Sub.Component"]["elements"][-1] = Element("Slot")
        with raises(
            ValueError, match="Can not have more that one catch all slot in a component"
        ):
            self.compiler.compile(phml_ast, components, _phml_path_="tests/src/")

        del components["Sub.Component"]["elements"][-1]

    def test_step_conditional_exceptions(self):
        multi_conditon_on_one = self.parser.parse(
            """\
<p @if="False" @else>Something</p>\
"""
        )
        invalid_condition_order = self.parser.parse(
            """\
<p @if="False">Something</p>
<p @else>A</p>
<p @elif="True">B</p>\
"""
        )

        invalid_conditon_value = self.parser.parse(
            """\
<p @if="'invalid'">Invalid</p>
"""
        )

        with raises(
            ValueError,
            match="More that one condition attribute found at .+\\. Expected at most one condition",
        ):
            self.compiler.compile(multi_conditon_on_one, self.components)

        with raises(
            ValueError,
            match="Invalid condition element order at .+\\. Expected if -> \\(elif -> else\\) \\| else",
        ):
            self.compiler.compile(invalid_condition_order, self.components)

        with raises(
            ValueError,
            match="Expected boolean expression in condition attribute '.+' at .+",
        ):
            self.compiler.compile(invalid_conditon_value, self.components)

    def test_step_markup(self):
        # No src or invalid src
        with raises(
            ValueError,
            match="<Markdown /> element must have a 'src' or ':src' attribute that is a string",
        ):
            self.compiler.compile(
                self.parser.parse("""<Markdown :extras='["footnotes"]'>"""),
                self.components,
                _phml_path_="tests/src/",
            )

        # Invalid `:extras` value type
        with raises(
            TypeError,
            match="Expected ':extras' attribute to be a space seperated list as a str or a python list of str",
        ):
            self.compiler.compile(
                self.parser.parse("""<Markdown :extras='None'>"""),
                self.components,
                _phml_path_="tests/src/",
            )
        # Markdown file doesn't exist
        with raises(FileNotFoundError, match="No markdown file at path '.+'"):
            self.compiler.compile(
                self.parser.parse(
                    """\
<Markdown src="invalid/readme.md" />\
"""
                ),
                self.components,
                _phml_path_="tests/src/",
            )
