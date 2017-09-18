from collections import OrderedDict

from envswitch.yaml_ordered_dict import safe_load_ordered


def test_safe_load_ordered():
    import textwrap

    sample = """
        one:
            two: fish
            red: fish
            blue: fish
        two:
            a: yes
            b: no
            c: null
        """

    data = safe_load_ordered(textwrap.dedent(sample))

    assert type(data) is OrderedDict
    print(data)