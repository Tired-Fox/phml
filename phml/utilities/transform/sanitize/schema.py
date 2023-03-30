"""Defines the schema on how to sanitize the phml ast."""
from dataclasses import dataclass, field


@dataclass
class Schema:
    """Dataclass of information on how to sanatize a phml tree.

    `strip (list[str])`: The elements to strip from the tree.
    `protocols (dict[str, list])`: Collection of element name and allowed protocal value list
    `tag_names (list[str])`: List of allowed tag names.
    `attributes (dict[str, list[str | list[str]]])`: Collection of element name and allowed property
    names.
    `required (dict[str, str | list[str]])`: Collection of element names and their required
    properties and required property values.
    """

    strip: list[str] = field(default_factory=lambda: ['script'])
    ancestors: dict[str, list] = field(
        default_factory=lambda: {
            "tbody": ['table'],
            "tfoot": ['table'],
            "thead": ['table'],
            "td": ['table'],
            "th": ['table'],
            "tr": ['table'],
        }
    )
    protocols: dict[str, list] = field(
        default_factory=lambda: {
            "href": ['http', 'https', 'mailto', 'xmpp', 'irc', 'ircs'],
            "cite": ['http', 'https'],
            "src": ['http', 'https'],
            "longDesc": ['http', 'https'],
        }
    )
    tag_names: list[str] = field(
        default_factory=lambda: [
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'br',
            'b',
            'i',
            'strong',
            'em',
            'a',
            'pre',
            'code',
            'img',
            'tt',
            'div',
            'ins',
            'del',
            'sup',
            'sub',
            'p',
            'ol',
            'ul',
            'table',
            'thead',
            'tbody',
            'tfoot',
            'blockquote',
            'dl',
            'dt',
            'dd',
            'kbd',
            'q',
            'samp',
            'var',
            'hr',
            'ruby',
            'rt',
            'rp',
            'li',
            'tr',
            'td',
            'th',
            's',
            'strike',
            'summary',
            'details',
            'caption',
            'figure',
            'figcaption',
            'abbr',
            'bdo',
            'cite',
            'dfn',
            'mark',
            'small',
            'span',
            'time',
            'wbr',
            'input',
        ]
    )
    attributes: dict[str, list[str | list[str]]] = field(
        default_factory=lambda: {
            "a": ['href'],
            "img": ['src', 'longDesc'],
            "input": [['type', 'checkbox'], ['disabled', True]],
            "li": [['class', 'task-list-item']],
            "div": ['itemScope', 'itemType'],
            "blockquote": ['cite'],
            "del": ['cite'],
            "ins": ['cite'],
            "q": ['cite'],
            '*': [
                'abbr',
                'accept',
                'acceptCharset',
                'accessKey',
                'action',
                'align',
                'alt',
                'ariaDescribedBy',
                'ariaHidden',
                'ariaLabel',
                'ariaLabelledBy',
                'axis',
                'border',
                'cellPadding',
                'cellSpacing',
                'char',
                'charOff',
                'charSet',
                'checked',
                'clear',
                'cols',
                'colSpan',
                'color',
                'compact',
                'coords',
                'dateTime',
                'dir',
                'disabled',
                'encType',
                'htmlFor',
                'frame',
                'headers',
                'height',
                'hrefLang',
                'hSpace',
                'isMap',
                'id',
                'label',
                'lang',
                'maxLength',
                'media',
                'method',
                'multiple',
                'name',
                'noHref',
                'noShade',
                'noWrap',
                'open',
                'prompt',
                'readOnly',
                'rel',
                'rev',
                'rows',
                'rowSpan',
                'rules',
                'scope',
                'selected',
                'shape',
                'size',
                'span',
                'start',
                'summary',
                'tabIndex',
                'target',
                'title',
                'type',
                'useMap',
                'vAlign',
                'value',
                'vSpace',
                'width',
                'itemProp',
            ],
        }
    )
    required: dict[str, dict[str, str|bool]] = field(
        default_factory=lambda: {
            "input": {
                "type": 'checkbox',
                "disabled": True,
            }
        }
    )
