import contextvars

current_test = contextvars.ContextVar("current_test", default="N/A")
