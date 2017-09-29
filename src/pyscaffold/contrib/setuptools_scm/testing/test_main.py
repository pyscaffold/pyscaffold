import os.path


def test_main():
    mainfile = os.path.join(
        os.path.dirname(__file__), "..", "setuptools_scm", "__main__.py")
    with open(mainfile) as f:
        code = compile(f.read(), "__main__.py", 'exec')
        exec(code)
