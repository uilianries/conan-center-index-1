from packaging.version import Version, parse


if __name__ == "__main__":
    assert isinstance(parse("1.0"), Version)
