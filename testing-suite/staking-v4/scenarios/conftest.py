import pytest

from config import chain_simulator_path
from core.chain_simulator import ChainSimulator


@pytest.fixture(scope="function")
def blockchain():
    chain_simulator = ChainSimulator(chain_simulator_path)
    chain_simulator.start()
    yield chain_simulator
    chain_simulator.stop()

@pytest.fixture
def epoch(request):
    return request.param
