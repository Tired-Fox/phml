# Utils from [`unist`](https://github.com/syntax-tree/unist#list-of-utilities) and [`hast`](https://github.com/syntax-tree/hast#list-of-utilities) to implement

## unist
- [x] position: Positional information on node
- [x] inspect: Node inspector
- [x] find: Find node by condition
- [ ] find-all: Find all nodes with condition
- [x] find-after: Find first node after certain node
- [x] find-all-after: Find all nodes after certain node
- [ ] find-before: Find first node before certain node
- [ ] find-all-before: Find all nodes before certain node
- [ ] find-all-between: Find all nodes between two nodes
- [ ] index: Index the tree given conditions. Helps with traversal
- [x] test: Check if node passes test
- [x] size: Calc number of nodes in a tree
- [ ] select: Select nodes with css-like selectors

- [x] walk: recursively walk over nodes
- [x] visit-children: visit direct children of a parent
- [x] visit-all-after: visit all nodes after another node
- [ ] filter: Create a new tree with only nodes that pass a condition

- [ ] remove: Remove nodes from trees
- [ ] replace-all-between: replace nodes between two nodes or positions
- [ ] ancestor: Get common ancestor of one or more nodes
- [ ] reduce: recursively reduce tree
- [ ] modify-children: modify direct children of a parent
 
- [ ] flat-flilter: flat map of `filter`
- [ ] flatmap: Flat version of tree
- [ ] map: Create a new tree by mapping nodes

- [ ] builder: Helper for creating ast's (Own module)
 
- [ ] assert: Asserts that a node is valid
- [ ] generated: Check if node is generated
- [ ] source: get the source of a value
- [ ] stringify-position: strimgify a node, position, or position

## hast
- [ ] class-list: Mimic browser's classList API
- [ ] classnames: merge class names together
- [ ] has-property: Check if element has a certain property
- [ ] heading: check if node is a heading
- [ ] heading-rank: get the rank(depth/level) of headings
- [ ] is-css-link: check if node is a CSS link
- [ ] is-css-style: check if node is a CSS style
- [ ] is-element: check if node is a certain element
- [ ] is-event-handler: check if property is an event handler
- [ ] is-javascript: check if node is a javascript `script` [ref](https://html.spec.whatwg.org/#category-label)
- [ ] sanitize: sanitize nodes
- [ ] select: `querySelector`, `querySelectorAll`, and `matches`
- [ ] shift-heading: change heading rank (depth/level)

*Extensions?*
- [ ] embedded: check if a node is an embedded element
- [ ] find-and-replace: find and replace text in tree
- [ ] from-markdown: Uses python markdown and gets ast from rendered markdown
- [ ] to-markdown: Converts phml ast tree to markdown
- [ ] interactive: check if the node is an interactive element
- [ ] menu-state: check the state of a menu element
- [ ] phrasing: check if node is phrasing content
- [ ] reading-time: estimate the reading time

# Custom
- [ ] from-python: create temp python file for `python` tag and evaluate and import all *`from temp_python import *`*
- [ ] evaluate-python: evaluate a string containing python
