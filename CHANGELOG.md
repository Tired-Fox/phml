# CHANGLOG

### v0.3.0
  - Add `For` element
  - Add `For` element fallbacks similar to `if` -> `elif` -> `else`
  - Add `For` error message that is exposed to the page
  - Add `python` module import system
  - Add component hashing
  - Add scoped component style elements
  - Add dynamic compiler steps
  - Add ability to add custom steps to either setup, scoped, or post step processes
  - Add base phml compilation steps
    - conditional elements
    - embedded python
    - wrapper scope
    - `For` element
    - components
  - Add optional `Markdown` element / feature
  - Add ability to format text and files. Either phml or html
  - Add ability to compress the output
  - Add context manager for easy file IO
  
  - Remove support for XML
  
  - Components are now scoped based on hashing
  - API docs have been regenerated
  - Rewrite parsing from phml/html to phml AST
  - Rewrite compiling from phml AST to html
  - Rewrite embedded python parsing
  - Rewrite component parsing and component system
  - ... And much more, the entire library has been rewritten for optimization and overall use

