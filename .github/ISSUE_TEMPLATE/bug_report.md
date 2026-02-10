---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Import library with `from ista_vdm_api import IstaVdmAPI`
2. Call method `...`
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Code Example**
```python
import asyncio
from ista_vdm_api import IstaVdmAPI

async def reproduce():
    api = IstaVdmAPI("email", "password")
    await api.authenticate()
    # ...

asyncio.run(reproduce())
```

**Error Message**
```
Paste the full error traceback here
```

**Environment (please complete the following information):**
 - OS: [e.g. Ubuntu 22.04, Windows 11, macOS 13]
 - Python Version: [e.g. 3.11, 3.12]
 - Library Version: [e.g. 1.0.0]
 - Installation method: [e.g. pip, poetry]

**Additional context**
Add any other context about the problem here.