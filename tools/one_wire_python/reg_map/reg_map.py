def register_map_structure_check(register_map):
    assert isinstance(register_map, tuple)
    assert len(register_map) == 2
    i = 0
    for e in register_map:
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
