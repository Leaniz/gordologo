from unidecode import unidecode


def compare_name(name_1, name_2):
        name_1 = unidecode(name_1).lower()
        name_2 = unidecode(name_2).lower()
        return name_1 == name_2
