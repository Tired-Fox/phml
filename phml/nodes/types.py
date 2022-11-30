"""Here is a collection of type annotations
"""

from typing import Any

__all__ = ["Properties"]

Data = dict

PropertyName = str
"""Property names are keys on Properties objects and reflect HTML, SVG, ARIA, XML, XMLNS,
or XLink attribute names. Often, they have the same value as the corresponding attribute
(for example, id is a property name reflecting the id attribute name), but there are some
notable differences.

    These rules aren't simple. Use hastscript (or property-information directly) to help.

The following rules are used to transform HTML attribute names to property names. These
rules are based on how ARIA is reflected in the DOM ([ARIA]), and differs from how some
(older) HTML attributes are reflected in the DOM.

Any name referencing a combinations of multiple words (such as “stroke miter limit”) becomes
a camelcased property name capitalizing each word boundary. This includes combinations
that are sometimes written as several words. For example, `stroke-miterlimit` becomes
`strokeMiterLimit`, `autocorrect` becomes `autoCorrect`, and `allowfullscreen` becomes
`allowFullScreen`.

Any name that can be hyphenated, becomes a camelcased property name capitalizing each boundary.
For example, “read-only” becomes `readOnly`.

Compound words that are not used with spaces or hyphens are treated as a normal word and the
previous rules apply. For example, “placeholder”, “strikethrough”, and “playback” stay the same.

Acronyms in names are treated as a normal word and the previous rules apply. For example,
`itemid` become `itemId` and `bgcolor` becomes `bgColor`.
"""

PropertyValue = Any
"""Property values should reflect the data type determined by their property name.
For example, the HTML `<div hidden></div>` has a `hidden` attribute, which is reflected
as a `hidden` property name set to the property value `true`, and `<input minlength="5">`,
which has a `minlength` attribute, is reflected as a `minLength` property name set to the
property value `5`.

    In JSON, the value `null` must be treated as if the property was not included.
    In JavaScript, both `null` and `undefined` must be similarly ignored.

The DOM has strict rules on how it coerces HTML to expected values,
whereas hast is more lenient in how it reflects the source. Where the DOM treats
`<div hidden="no"></div>` as having a value of `true` and `<img width="yes">`
as having a value of `0`, these should be reflected as `'no'` and `'yes'`, respectively, in hast.

    The reason for this is to allow plugins and utilities to inspect these non-standard values.

The DOM also specifies comma separated and space separated lists attribute values.
In hast, these should be treated as ordered lists. For example, `<div class="alpha bravo"></div>`
is represented as `['alpha', 'bravo']`.

    There's no special format for the property value of the `style` property name.
"""

Properties = dict[PropertyName, PropertyValue]
"""Properties represents information associated with an element.

Every field must be a PropertyName and every value a PropertyValue.
"""
