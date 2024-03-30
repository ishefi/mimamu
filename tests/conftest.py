from pytest import FixtureRequest
from pytest import fixture

from mocks import do_reset_global_mocks


@fixture(scope="function", autouse=True)
def reset_global_mocks(request: FixtureRequest) -> None:
    do_reset_global_mocks(request)
