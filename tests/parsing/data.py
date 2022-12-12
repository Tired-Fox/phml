from phml import AST
from phml.builder import p

asts = {
    "phml": AST(
        p(
            p("doctype"),
            p(
                "html",
                {"lang": "en"},
                p(
                    "head",
                    p("meta", {"charset": "UTF-8"}),
                    p(
                        "meta",
                        {
                            "http-equiv": "X-UA-Compatible",
                            "content": "IE=edge",
                        },
                    ),
                    p(
                        "meta",
                        {
                            "name": "viewport",
                            "content": "width=device-width, initial-scale=1.0",
                        },
                    ),
                    p("title", '{title or ""}'),
                ),
                p(
                    "python",
                    """\
        date = "11/15/2022"
        data = {
            "name": "Zachary",
            "age": "22",
            "type": "checkbox"
        }\
""",
                ),
                p(
                    "body",
                    p("<!-- Text Comment -->"),
                    p("h1", "Hello World!"),
                    p(
                        "input",
                        {
                            "py-type": "data['type']",
                            "checked": "{date == '11/15/2022'}",
                        },
                    ),
                    p("p", {"py-if": "date == '11/15/2022'"}, "{date}"),
                    p("p", {"py-elif": "data['name'] == 'Zachary'"}, '{date["name"]}'),
                    p("p", {"py-else": True}, "Wonderful day today!"),
                    p(
                        "ul",
                        {"id": "python-loop"},
                        p(
                            "li",
                            {"py-for": "key, value in data.items()"},
                            p("span", "{key}: "),
                            p("span", "{value}"),
                        ),
                    ),
                    p("h4", "The end"),
                    p(
                        "python",
                        """\
            from pprint import pprint

            def print_data(data):
                pprint(data)\
""",
                    ),
                ),
            ),
        )
    ),
    "html": AST(
        p(
            p("doctype"),
            p(
                "html",
                {"lang": "en"},
                p(
                    "head",
                    p("meta", {"charset": "UTF-8"}),
                    p(
                        "meta",
                        {
                            "http-equiv": "X-UA-Compatible",
                            "content": "IE=edge",
                        },
                    ),
                    p(
                        "meta",
                        {
                            "name": "viewport",
                            "content": "width=device-width, initial-scale=1.0",
                        },
                    ),
                    p("title", 'sample title'),
                ),
                p(
                    "body",
                    p("<!-- Text Comment -->"),
                    p("h1", "Hello World!"),
                    p(
                        "input",
                        {
                            "type": "checkbox",
                            "checked": True,
                        },
                    ),
                    p("p", "11/15/2022"),
                    p(
                        "ul",
                        {"id": "python-loop"},
                        p(
                            "li",
                            p("span", "name: "),
                            p("span", "Zachary"),
                        ),
                        p(
                            "li",
                            p("span", "age: "),
                            p("span", "22"),
                        ),
                        p(
                            "li",
                            p("span", "type: "),
                            p("span", "checkbox"),
                        ),
                    ),
                    p("h4", "The end"),
                ),
            ),
        )
    ),
}

dicts = {
    "type": "root",
    "position": None,
    "children": [
        {"type": "doctype", "position": None, "lang": "html"},
        {
            "type": "element",
            "position": None,
            "properties": {"lang": "en"},
            "tag": "html",
            "startend": False,
            "locals": {},
            "children": [
                {
                    "type": "element",
                    "position": None,
                    "properties": {},
                    "tag": "head",
                    "startend": False,
                    "locals": {},
                    "children": [
                        {
                            "type": "element",
                            "position": None,
                            "properties": {"charset": "UTF-8"},
                            "tag": "meta",
                            "startend": True,
                            "locals": {},
                            "children": [],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
                            "tag": "meta",
                            "startend": True,
                            "locals": {},
                            "children": [],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {
                                "name": "viewport",
                                "content": "width=device-width, initial-scale=1.0",
                            },
                            "tag": "meta",
                            "startend": True,
                            "locals": {},
                            "children": [],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {},
                            "tag": "title",
                            "startend": False,
                            "locals": {},
                            "children": [
                                {
                                    "type": "text",
                                    "position": None,
                                    "value": "{title or \"\"}",
                                    "num_lines": 1,
                                }
                            ],
                        },
                    ],
                },
                {
                    "type": "element",
                    "position": None,
                    "properties": {},
                    "tag": "python",
                    "startend": False,
                    "locals": {},
                    "children": [
                        {
                            "type": "text",
                            "position": None,
                            "value": "        date = \"11/15/2022\"\n        data = {\n            \"name\": \"Zachary\",\n            \"age\": \"22\",\n            \"type\": \"checkbox\"\n        }",
                            "num_lines": 6,
                        }
                    ],
                },
                {
                    "type": "element",
                    "position": None,
                    "properties": {},
                    "tag": "body",
                    "startend": False,
                    "locals": {},
                    "children": [
                        {"type": "comment", "position": None, "value": " Text Comment "},
                        {
                            "type": "element",
                            "position": None,
                            "properties": {},
                            "tag": "h1",
                            "startend": False,
                            "locals": {},
                            "children": [
                                {
                                    "type": "text",
                                    "position": None,
                                    "value": "Hello World!",
                                    "num_lines": 1,
                                }
                            ],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {
                                "py-type": "data['type']",
                                "checked": "{date == '11/15/2022'}",
                            },
                            "tag": "input",
                            "startend": True,
                            "locals": {},
                            "children": [],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {"py-if": "date == '11/15/2022'"},
                            "tag": "p",
                            "startend": False,
                            "locals": {},
                            "children": [
                                {
                                    "type": "text",
                                    "position": None,
                                    "value": "{date}",
                                    "num_lines": 1,
                                }
                            ],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {"py-elif": "data['name'] == 'Zachary'"},
                            "tag": "p",
                            "startend": False,
                            "locals": {},
                            "children": [
                                {
                                    "type": "text",
                                    "position": None,
                                    "value": "{date[\"name\"]}",
                                    "num_lines": 1,
                                }
                            ],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {"py-else": True},
                            "tag": "p",
                            "startend": False,
                            "locals": {},
                            "children": [
                                {
                                    "type": "text",
                                    "position": None,
                                    "value": "Wonderful day today!",
                                    "num_lines": 1,
                                }
                            ],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {"id": "python-loop"},
                            "tag": "ul",
                            "startend": False,
                            "locals": {},
                            "children": [
                                {
                                    "type": "element",
                                    "position": None,
                                    "properties": {"py-for": "key, value in data.items()"},
                                    "tag": "li",
                                    "startend": False,
                                    "locals": {},
                                    "children": [
                                        {
                                            "type": "element",
                                            "position": None,
                                            "properties": {},
                                            "tag": "span",
                                            "startend": False,
                                            "locals": {},
                                            "children": [
                                                {
                                                    "type": "text",
                                                    "position": None,
                                                    "value": "{key}: ",
                                                    "num_lines": 1,
                                                }
                                            ],
                                        },
                                        {
                                            "type": "element",
                                            "position": None,
                                            "properties": {},
                                            "tag": "span",
                                            "startend": False,
                                            "locals": {},
                                            "children": [
                                                {
                                                    "type": "text",
                                                    "position": None,
                                                    "value": "{value}",
                                                    "num_lines": 1,
                                                }
                                            ],
                                        },
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {},
                            "tag": "h4",
                            "startend": False,
                            "locals": {},
                            "children": [
                                {
                                    "type": "text",
                                    "position": None,
                                    "value": "The end",
                                    "num_lines": 1,
                                }
                            ],
                        },
                        {
                            "type": "element",
                            "position": None,
                            "properties": {},
                            "tag": "python",
                            "startend": False,
                            "locals": {},
                            "children": [
                                {
                                    "type": "text",
                                    "position": None,
                                    "value": "            from pprint import pprint\n\n            def print_data(data):\n                pprint(data)",
                                    "num_lines": 3,
                                }
                            ],
                        },
                    ],
                },
            ],
        },
    ],
}

strings = {
    "phml": '''\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{title or ""}</title>
    </head>
    <python>
        date = "11/15/2022"
        data = {
            "name": "Zachary",
            "age": "22",
            "type": "checkbox"
        }
    </python>
    <body>
        <!-- Text Comment -->
        <h1>Hello World!</h1>
        <input py-type="data['type']" checked="{date == '11/15/2022'}" />
        <p py-if="date == '11/15/2022'">{date}</p>
        <p py-elif="data['name'] == 'Zachary'">{date["name"]}</p>
        <p py-else>Wonderful day today!</p>
        <ul id="python-loop">
            <li py-for="key, value in data.items()">
                <span>{key}: </span>
                <span>{value}</span>
            </li>
        </ul>
        <h4>The end</h4>
        <python>
            from pprint import pprint

            def print_data(data):
                pprint(data)
        </python>
    </body>
</html>
''',
    "html": """\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>sample title</title>
    </head>
    <body>
        <!-- Text Comment -->
        <h1>Hello World!</h1>
        <input type="checkbox" checked />
        <p>11/15/2022</p>
        <ul id="python-loop">
            <li>
                <span>name: </span>
                <span>Zachary</span>
            </li>
            <li>
                <span>age: </span>
                <span>22</span>
            </li>
            <li>
                <span>type: </span>
                <span>checkbox</span>
            </li>
        </ul>
        <h4>The end</h4>
    </body>
</html>\
""",
}

if __name__ == "__main__":
    from phml import PHML
    from phml.core.valid_file_types import Formats

    phml = PHML()
    phml.ast = asts["phml"]

    # write to expected files
    (
        phml.write(dest="../sample.html", title="sample title")
        .write(dest="../sample.phml", file_type=Formats.PHML, title="sample title")
        .write("../sample.json", file_type=Formats.JSON, title="sample title")
    )
