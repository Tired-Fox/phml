- **tokenize**
- **parse**
- **return AST**

```html
<!DOCTYPE html>
<html>
    <head>
        <meta content="">
        <title>Some title</title>
    </head>
    <body>
        <input
            type="number"
            max="100"
            min="2"
            placeholder="10"
            hidden
        >
    </body>
</html>
```

### Open Tag
- Open tag is `<` maybe followed by `!` then a name like `html` with no spaces.
- After the first space the attributes are a list of tokens of format `<name> = "<value>"` or `<name> = '<value>'` or `<name> = <value>` or `<name>`. Key symbol is `=` an then what is the next non whitespace char. `"`, `'` are quoted blocks, otherwise it is any non whitespace characters. If a space is present and no `=` then just the name exists.
- The open tag ends with a `>`.
- There can be any amount of whitespace. Whitespace only matters for starting the attributes and for attribute values not wrapped in quotes.
- Open tags can end with `/` or can be automatically self closing
- Name can be only whitespace or empty. This tag can not have attributes

### Close Tag
- Closes the current opened scope.
- Starts with `/` and the name of the tag it is closing. Must match current scope and no whitespace.
- No attributes

### General
- pre tags make all children retain whitespace
- each token contains a position range of where it is in the string regardless of if it is in a file or not

