from constants import *


# IF YOU RUN TEST WITH -q , it goes on else
# IF YOU RUN TEST WITH -all, it goes on if

# TODO: Will be usable and complete after adding chain turn on/off feature

def pytest_addoption(parser):
    parser.addoption("--epoch", action="store_true", help="run all combinations")


def pytest_generate_tests(metafunc):
    if "epoch" in metafunc.fixturenames:
        if metafunc.config.getoption("epoch"):
            end = 3
        else:
            end = 7
        metafunc.parametrize("param1", range(end))


