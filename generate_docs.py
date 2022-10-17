import re
import sys
import warnings
from pydoc import ModuleScanner


def scan_modules():
    """taken from the source code of help('modules')

    https://github.com/python/cpython/blob/63298930fb531ba2bb4f23bc3b915dbf1e17e9e1/Lib/pydoc.py#L2178"""
    modules = {}

    def callback(path, modname, desc, modules=modules):
        if modname and modname[-9:] == ".__init__":
            modname = modname[:-9] + " (package)"
        if modname.find(".") < 0:
            modules[modname] = 1

    def onerror(modname):
        callback(None, modname, None)

    with warnings.catch_warnings():
        # ignore warnings from importing deprecated modules
        warnings.simplefilter("ignore")
        ModuleScanner().run(callback, onerror=onerror)
    return list(modules.keys())


def import_module(module_name):
    import io
    from contextlib import redirect_stdout

    # Importing modules causes ('Constant String', 2, None, 4) and
    # "Hello world!" to be printed to stdout.
    f = io.StringIO()
    with warnings.catch_warnings(), redirect_stdout(f):
        # ignore warnings caused by importing deprecated modules
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        try:
            module = __import__(module_name)
        except Exception as e:
            return e
    return module


def is_child(module, item):
    import inspect

    item_mod = inspect.getmodule(item)
    return item_mod is module


def traverse(module, names, item):
    import inspect

    has_doc = inspect.ismodule(item) or inspect.isclass(item) or inspect.isbuiltin(item)
    if has_doc and isinstance(item.__doc__, str):
        yield names, item.__doc__
    attr_names = dir(item)
    for name in attr_names:
        if name in [
            "__class__",
            "__dict__",
            "__doc__",
            "__objclass__",
            "__name__",
            "__qualname__",
            "__annotations__",
        ]:
            continue
        try:
            attr = getattr(item, name)
        except AttributeError:
            assert name == "__abstractmethods__", name
            continue

        if module is item and not is_child(module, attr):
            continue

        is_type_or_module = (type(attr) is type) or (type(attr) is type(__builtins__))
        new_names = names.copy()
        new_names.append(name)

        if item == attr:
            pass
        elif not inspect.ismodule(item) and inspect.ismodule(attr):
            pass
        elif is_type_or_module:
            yield from traverse(module, new_names, attr)
        elif (
            callable(attr)
            or not issubclass(type(attr), type)
            or type(attr).__name__ in ("getset_descriptor", "member_descriptor")
        ):
            if inspect.isbuiltin(attr):
                yield new_names, attr.__doc__
        else:
            assert False, (module, new_names, attr, type(attr).__name__)


def traverse_all(root):
    from glob import glob
    import os.path

    files = (
        glob(f"{root}/Lib/*")
        + glob(f"{root}/vm/src/stdlib/*")
        + glob(f"{root}/stdlib/src/*")
    )
    allowlist = set(
        [os.path.basename(file).lstrip("_").rsplit(".", 1)[0] for file in files]
    )
    for denied in ("this", "antigravity"):
        allowlist.remove(denied)

    for module_name in scan_modules():
        if module_name.lstrip("_") not in allowlist:
            print("skipping:", module_name, file=sys.stderr)
            continue
        module = import_module(module_name)
        if hasattr(module, "__cached__"):  # python module
            continue
        yield from traverse(module, [module_name], module)

    def f():
        pass

    builtin_types = [
        type(bytearray().__iter__()),
        type(bytes().__iter__()),
        type(dict().__iter__()),
        type(dict().values().__iter__()),
        type(dict().items().__iter__()),
        type(dict().values()),
        type(dict().items()),
        type(set().__iter__()),
        type(list().__iter__()),
        type(range(0).__iter__()),
        type(str().__iter__()),
        type(tuple().__iter__()),
        type(None),
        type(f),
    ]
    for typ in builtin_types:
        names = ["builtins", typ.__name__]
        if not isinstance(typ.__doc__, str):
            yield names, typ.__doc__
        yield from traverse(__builtins__, names, typ)


def docs(rustpython_path):
    return ((".".join(names), escape(doc)) for names, doc in traverse_all(rustpython_path))


UNICODE_ESCAPE = re.compile(r"\\u([0-9]+)")


def escape(doc):
    if doc is None:
        return None
    return re.sub(UNICODE_ESCAPE, r"\\u{\1}", doc)


def test_escape():
    input = r"It provides access to APT\u2019s idea of the"
    expected = r"It provides access to APT\u{2019}s idea of the"
    output = escape(input)
    assert output == expected


if __name__ == "__main__":
    import sys
    import json

    try:
        rustpython_path = sys.argv[1]
    except IndexError:
        print("1st argument is rustpython source code path")
        raise SystemExit

    try:
        out_path = sys.argv[2]
    except IndexError:
        out_path = "-"

    def dump(docs):
        yield "[\n"
        for name, doc in docs:
            if doc is None:
                yield f"    ({json.dumps(name)}, None),\n"
            else:
                yield f"    ({json.dumps(name)}, Some({json.dumps(doc)})),\n"
        yield "]\n"

    out_file = open(out_path, "w") if out_path != "-" else sys.stdout
    out_file.writelines(dump(docs(rustpython_path)))
