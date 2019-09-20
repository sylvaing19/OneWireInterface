from os.path import dirname, abspath, join, isfile, basename
from os import listdir
from importlib.util import spec_from_file_location, module_from_spec

"""
Structure typing:
OneWireRegisterMap: (str, [OneWireRegisterEntry, ...], [OneWireRegisterEntry, ...])
OneWireRegisterEntry: (int, int, str, bool, int, int, str)

Structure meaning:
OneWireRegisterMap: (name, [EEPROM_register, ...], [RAM_register, ...])
OneWireRegisterEntry: (address, size, name, writable, min, max, docstring)
"""

def register_map_structure_check(register_map):
    assert isinstance(register_map, tuple)
    assert len(register_map) == 3
    assert isinstance(register_map[0], str)
    i = 0
    for e in register_map[1:]:
        j = 0
        try:
            assert isinstance(e, list)
            for f in e:
                assert isinstance(f, tuple)
                assert len(f) == 7
                assert isinstance(f[0], int)
                assert isinstance(f[1], int)
                assert isinstance(f[2], str)
                assert isinstance(f[3], bool)
                assert isinstance(f[4], int)
                assert isinstance(f[5], int)
                assert isinstance(f[6], str)
                j += 1
        except AssertionError:
            print("Error at i=" + str(i), "j=" + str(j))
            raise
        i += 1


def get_register_map_list():
    this_file = abspath(__file__)
    reg_dir = dirname(this_file)
    other_files = []
    for f in listdir(reg_dir):
        file = join(reg_dir, f)
        if isfile(file) and file != this_file and file.lower().endswith('.py'):
            other_files.append(file)
    reg_map_list = []
    for f in other_files:
        # noinspection PyBroadException
        try:
            spec = spec_from_file_location(basename(f), f)
            reg_module = module_from_spec(spec)
            spec.loader.exec_module(reg_module)
            reg_map = reg_module.OneWireRegisterMap
            register_map_structure_check(reg_map)
            reg_map_list.append(reg_map)
        except Exception:
            pass
    return reg_map_list
