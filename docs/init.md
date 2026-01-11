# The Package Marker: `aws_lib/__init__.py`

## Role
This small file turns the `aws_lib` folder into a **Package**.

## What it does
In Python, a folder is just a folder. But if you put an `__init__.py` file inside it, Python treats it as a library (package) that you can import from.

## Why it is useful
It acts as a shortcut.

Without this file, to use our tools, you would have to type:
```python
from aws_lib.core import SessionManager
```

With this file, we can "expose" the important tools so you can just type:
```python
from aws_lib import SessionManager
```

It keeps the `import` statements in other files clean and readable.
