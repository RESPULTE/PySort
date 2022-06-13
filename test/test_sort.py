from typing import List
import random
import pytest
from vizsort.lib import *
from vizsort.lib.utils import exhaust

DATASET_SIZE = 1000


@pytest.fixture(scope="session")
def arr() -> List[int]:
    dataset = list(range(0, DATASET_SIZE))
    random.shuffle(dataset)
    return dataset


@pytest.fixture(scope="session")
def sorted_arr(arr) -> List[int]:
    return sorted(arr)


@pytest.mark.parametrize(
    "sort_algo",
    [bubble_sort, insertion_sort, selection_sort, merge_sort, tim_sort, radix_sort, quick_sort, iterative_quick_sort],
)
def test_sort(sort_algo, arr, sorted_arr):
    exhaust(sort_algo(arr))
    assert arr == sorted_arr
