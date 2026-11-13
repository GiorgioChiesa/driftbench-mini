# microweb

A micro web framework for internal tools: a WSGI-free `App` that turns `Request` objects into
`Response` objects, a URL router, small path helpers and a minimal `{{ var }}` template renderer.

```python
from microweb import App, Request

app = App()

@app.route("/hello/<name>")
def hello(request, name):
    return f"hello {name}"

app.handle(Request("GET", "/hello/world")).body  # 'hello world'
```

Run the tests with `python -m pytest`.
