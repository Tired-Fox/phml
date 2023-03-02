"""."""
import re
from pathlib import Path

from typing import Any, Literal


self_closing = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
    "command",
    "keygen",
    "menuitem",
]

REGEX = {
    "element": re.compile(
        r"<!--(?P<comment>[\w\W]*)-->|<(?P<name>[\w]+(?:[\w.:]+)*)(?P<attrs>(?:\s*([\w:.]+=\"[^\"]*\"|[\w:.]+='[^']*'|[\w:.]+=[^ />]+|[\w:.]+))*)\s*(?P<closing>\/)?>|<(?!!--)(?=\s*/?>)"
    ),
    "end_tag": "</\\s*{}\\s*>",
    "attr": re.compile(r"((?P<n1>[\w:.]+)='(?P<v1>[^']*)'|(?P<n2>[\w:.]+)=\"(?P<v2>[^\"]*)\"|(?P<n3>[\w:.]+)=(?P<v3>[^>\s]+)|(?P<n4>[\w:.]+))"),
}

RElem = dict[Literal["name", "attrs", "comment", "closing"], str|None]

Element = dict[Literal["_type", "tag", "attrs", "children"], Any]
Comment = dict[Literal["_type", "name", "data"], str]

def parse_attr_value(attrs: str, stop_chars: str|None=None):
    stop_pattern = (
            re.compile(f"^[{stop_chars}]$")
            if stop_chars is not None
            else re.compile(r"^[>\s]$")
    )
    i = 0
    while i < len(attrs) and stop_pattern.match(attrs[i]) is None:
        input("attr value: " + attrs[i])
        i += 1
        print(stop_pattern.match(attrs[i]), attrs[i]) if i < len(attrs) else print("OOB")

    if stop_chars is not None and attrs[i] not in stop_chars:
        raise ValueError("Attribute not closed. Expected <{', '.join(repr(c) for c in stop_chars)}>")

    return attrs[:i], i

def parse_attrs(attrs: str) -> dict | None:
    attrs = attrs.strip()
    i = 0
    result = {}
    attr_name = ""
    while i < len(attrs): 
        input(attrs[i])
        if attrs[i] == "=":
            input(attrs[i+1])
            i += 1
            if attrs[i] in ['"', "'"]:
                i+=1
                value, x = parse_attr_value(attrs[i:], attrs[i-1])
                i += x
                result[attr_name] = value
                attr_name = ""
            elif attrs[i] not in [" ", "\n", "\t"]:
                value, x = parse_attr_value(attrs[i:])
                i += x
                result[attr_name] = value
                attr_name = ""
            else:
                raise ValueError("Expected attribute value after '='")
        elif attrs[i] in [" ", "\n", "\t"]:
            if attr_name != "":
                result[attr_name] = True
                attr_name = ""
            i += 1
            while attrs[i] in [" ", "\n", "\t"]:
                i += 1
            continue
        else:
            attr_name += attrs[i]
        i+=1

    if attr_name != "":
        result[attr_name] = attrs[i:] if i < len(attrs) else True
    input(result)
    return None

def parse_tags(data: str, context: Element):
    while REGEX["element"].search(data) is not None:
        tag = REGEX["element"].search(data)
        tag_info = tag.groupdict()

        start = tag.start()
        if start > 0:
            context["children"].append({"_type": "literal", "name": "text", "data": data[:start]})
        data = data[start + len(tag.group(0)):]
        if tag_info["comment"] is None:
            end = re.compile(REGEX["end_tag"].format(tag_info["name"]))
            end_tag = end.search(data)
            if end_tag is None or tag_info["closing"] is not None:
                if tag_info["name"] not in self_closing and tag_info["closing"] is None:
                    raise ValueError(f"<{tag_info['name']}> tag was not closed")
                else:
                    context["children"].append({
                        "_type": "element",
                        "tag": tag_info["name"],
                        "attrs": parse_attrs(tag_info["attrs"]),
                        "children": None
                    })
            else:
                context["children"].append({
                    "_type": "element",
                    "tag": tag_info["name"] or "",
                    "attrs": parse_attrs(tag_info["attrs"]),
                    "children": [] 
                })
                parse_tags(data[:end_tag.start()], context["children"][-1])
                data = data[end_tag.start() + len(end_tag.group(0)):]
        elif tag_info["comment"] is not None:
            context["children"].append({
                "_type": "literal",
                "name": "comment",
                "data": tag_info["comment"]
            })
    
    if len(data) > 0:
        context["children"].append({"_type": "literal", "name": "text", "data": data})

if __name__ == "__main__":
    from saimll import pprint

    with Path("sandbox/sample.phml").open("r", encoding="utf-8") as file:
        data = file.read()
    
    root: Element = {"_type": "root", "children": []}
    parse_tags(data, root)
    # print(root)
    pprint(root, depth=-1)

