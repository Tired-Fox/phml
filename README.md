# pehl - Python Extended HTML Language
A python based html parser that allows for adding additional functionality and custom nodes

1. Tags are between `<` and `>`
2. Brackets `{` and `}` indicate injected python code
3. Open tags can have `py-` prefixed attributes

Follows:
1. [hast](https://github.com/syntax-tree/hast#list-of-utilities)
2. [unist](https://github.com/syntax-tree/unist#intro)
3. [Web IDL](https://webidl.spec.whatwg.org/)