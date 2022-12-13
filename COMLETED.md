# TODO
- [x] Write Tests
  - [x] Utils
    - [x] find
    - [x] misc
    - [x] transform
    - [x] travel
    - [x] validate
  - [x] AST
    - [x] Correct AST Generation (parsing)
      - [x] To json
      - [x] To phml
      - [x] To html
    - [x] Correct ast conversion (compiling)
      - [x] From phml/html
      - [x] From json
- [x] All utilities
  - [x] unist
  - [x] hast
- [x] Ensure python conditions are immediate siblings
- [x] Optimize
  - [x] Parsing files
  - [x] Compiling files
  - [x] AST linking from parser and compiler
  - [x] Nodes to dataclasses?
  - [x] Utilities
- [x] Component based system
- [x] Layout for components
  - [x] Can provide script, python, styles elements
  - [x] Parent element or single element and then script, style, python, etc?
- [x] re-write inspect to be external util function
  - [x] Pretty lines
  - [x] # children
  - [x] Positional
  - [x] Type and/or tag
  - [x] values of literals
  - [x] properties of elements
  - [x] data of entire tree
- [x] from-python: create temp python file for `python` tag and evaluate and import all *`from temp_python import *`*
- [x] evaluate-python: evaluate a string containing python
- [x] Node conversion external from nodes
- [x] Validate ast is proper format
  - [x] doctype is only in root
  - [x] if no doctype add doctype
  - [x] root nodes are at the root of the tree
- [x] Convert From Formats
  - [x] Json
  - [x] html
  - [x] phml
- [x] Convert To Formats
  - [x] Json
  - [x] phml
  - [x] html

## Utils from [`unist`](https://github.com/syntax-tree/unist#list-of-utilities) and [`hast`](https://github.com/syntax-tree/hast#list-of-utilities) to implement

### unist
- [x] position: Positional information on node
- [x] inspect: Node inspector
- [x] find: Find node by condition
- [x] find-after: Find first node after certain node
- [x] find-all-after: Find all nodes after certain node
- [x] size: Calc number of nodes in a tree
- [x] test: Check if node passes test
- [x] find-before: Find first node before certain node
- [x] find-all-before: Find all nodes before certain node
- [x] find-all-between: Find all nodes between two nodes
- [x] ancestor: Get common ancestor of one or more nodes

- [x] walk: recursively walk over nodes
- [x] visit-children: visit direct children of a parent
- [x] visit-all-after: visit all nodes after another node

- [x] filter: Create a new tree with only nodes that pass a condition
- [x] remove: Remove nodes from trees
- [x] map: Create a new tree by mapping nodes

- [x] assert: Asserts that a node is valid
- [x] generated: Check if node is generated
 
- [x] builder: Helper for creating ast's (Own module)
- [x] index: Index the tree given conditions. Helps with traversal
- [x] modify-children: modify direct children of a parent

- [ ] ? replace-all-between: replace nodes between two nodes or positions
- [ ] ? reduce: recursively reduce tree
- [ ] ? flatmap: Flat version of tree
- [ ] ? flat-filter: flat map of `filter`
- [ ] ? source: get the source of a value

## hast
- [x] class-list: Mimic browser's classList API
- [x] classnames: merge class names together
- [x] has-property: Check if element has a certain property
- [x] heading: check if node is a heading
- [x] heading-rank: get the rank(depth/level) of headings
- [x] is-css-link: check if node is a CSS link
- [x] is-css-style: check if node is a CSS style
- [x] is-element: check if node is a certain element
- [x] is-event-handler: check if property is an event handler
- [x] is-javascript: check if node is a javascript `script` [ref](https://html.spec.whatwg.org/#category-label)
- [x] shift-heading: change heading rank (depth/level)
- [x] find-and-replace: find and replace text in tree
- [x] to-string: Get textContent of element

- [x] embedded: check if a node is an embedded element
- [x] interactive: check if the node is an interactive element
- [x] phrasing: check if node is phrasing content
- [ ] ? menu-state: check the state of a menu element

- [x] select: `querySelector`, `querySelectorAll`, and `matches`
- [x] sanitize: sanitize nodes
- [ ] ? to-text: inner-text of element - Rendered text

- [ ] ? to-markdown: Converts phml ast tree to markdown
- [ ] ? from-markdown: Uses python markdown and gets ast from rendered markdown
