from pyscaffold import extensions


def make_extension(name, **kwargs):
    props = {"__doc__": f"activate {name}", **kwargs}
    return type(name, (extensions.Extension,), props)()
