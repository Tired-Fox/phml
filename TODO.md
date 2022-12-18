# TODO

- [x] Optimize Component styles and script tags to avoid duplication
- [x] Multiline python blocks marked with `{}`.
  * Is this work it concidering the `@for` functionality?
  * Assume that the data returned is to be parsed as nodes/components
  * Use yields
  * Will expect a string return value

- [x] Code safe escaping
  - All string values passed in are escaped
  - User can define regular escape or remove tags
  - User can mark the string as safe and stop escaping
- [x] More formats
  - Use `html` modules escaping
  - XML support
  - Seperate format classes and base class
- [x] Refine component system
- [x] Ability to use flask