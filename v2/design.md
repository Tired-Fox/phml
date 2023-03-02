# v2 Design

**sample**
```html
<!DOCTYPE>
<html>
  <head>
    <title>Sample</title>
  </head>

  <body>
    <h1>Sample HTML</h1> 
  </body>
</html>
```

- tag start: `<(?P<name>[\w]+(?:[\w.:]+)*)|<(?!!--)(?=\s*/?>)|(?P<comment><!--)`
