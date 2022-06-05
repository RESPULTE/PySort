from typing import List
import random
import pytest
from pysort.lib.quadratic_sort import bubble_sort, insertion_sort, selection_sort
from pysort.lib.logarithmic_sort import merge_sort

DATASET_SIZE = 10_000


@pytest.fixture(scope="session")
def arr() -> List[int]:
    return [random.randint(0, DATASET_SIZE) for _ in range(DATASET_SIZE)]


@pytest.fixture(scope="session")
def sorted_arr(arr) -> List[int]:
    return sorted(arr)


@pytest.mark.parametrize("sort_algo", [bubble_sort, insertion_sort, selection_sort, merge_sort])
def test_sort(sort_algo, arr, sorted_arr):
    sort_algo(arr)
    assert arr == sorted_arr
