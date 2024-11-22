from icecream import ic


def ic_all_attributes(obj):
    attrs = vars(obj)
    for attr, value in attrs.items():
        if not attr.startswith("_"):
            ic(attr, value)
