from cd2_matrix_studio.i18n import STRINGS


def test_languages_have_the_same_keys():
    assert set(STRINGS["en"]) == set(STRINGS["ru"])
