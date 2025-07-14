from pkgutil import iter_modules

assert __package__
_ext = [x for x in iter_modules(__path__, prefix=__package__+".")]
EXT_LIST = _ext