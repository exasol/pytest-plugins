import os
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
import json
import pytest

from exasol.pytest_backend.parallel_task import paralleltask


@paralleltask
def brewery_factory(name: str, logos: list[str]):
    # Long-running task setting up the brewery
    # Here we will just create a flyer and write it into a file
    brewery_info = {'name': name, 'logos': logos}
    with NamedTemporaryFile('w') as temp_file:
        json.dump(brewery_info, temp_file)
        temp_file.flush()
        yield temp_file.name


@contextmanager
def my_brewery_async():
    with brewery_factory('Cambridge Brewery', ['Cambridge Beaver', 'Cam Droplets']) as brewery:
        yield brewery


def test_my_brewery():
    with my_brewery_async() as brewery:
        flyer_file = brewery.get_output()
        with open(flyer_file, 'r') as f:
            brewery_info = json.load(f)
        assert brewery_info['name'] == 'Cambridge Brewery'
        assert brewery_info['logos'] == ['Cambridge Beaver', 'Cam Droplets']
    # Now the flyer should be deleted
    assert not os.path.exists(flyer_file)


@paralleltask
def my_div(num: int, den: int):
    yield num // den


def test_div_by_zero():
    with pytest.raises(RuntimeError) as ex_info:
        with my_div(10, 0) as my_div_async:
            my_div_async.get_output()
    assert isinstance(ex_info.value.__cause__, ZeroDivisionError)
