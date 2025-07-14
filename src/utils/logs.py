import traceback, datetime

def write_traceback(exc: Exception):
    etype = type(exc)
    trace = exc.__traceback__
    lines = traceback.format_exception(etype, exc, trace)
    traceback_text = ''.join(lines)
    code = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {etype.__name__} \n{traceback_text}"

    with open("error.log", "a") as file:
        file.write(code)