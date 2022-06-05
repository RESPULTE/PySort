from collections import namedtuple
from pysort.lib._type_hint import CT
from pysort.lib.quadratic_sort import insertion_sort
from typing import List, MutableSequence, Tuple
from bisect import bisect_left
from operator import lt, gt


def merge_sort(arr: MutableSequence[CT], start: int = 0, end: int = None) -> MutableSequence[CT]:
    """
    executes merge sort on the given array in place

    [Process]
    1. Get the length of the array and get the midpoint of it

    2. recursively split the array at the midpoint into left & right half,
       and continue until the array is of size 1

    3. get the minimum element of both array & write it to the original array,
       continue until one of the halves has been exhausted

    4. just repeat the same process for the other half that
       hasn't had it element written back into the original array yet

    """

    arr_size = len(arr)
    if arr_size == 1:
        return

    # recursively splitting the array into left & right halves
    split_index = arr_size // 2
    left_arr, right_arr = arr[:split_index], arr[split_index:]
    yield from merge_sort(left_arr)
    yield from merge_sort(right_arr)

    # copying the elements of splitted-array back into the original array in order
    l = r = k = 0
    left_size, right_size = len(left_arr), len(right_arr)
    while l < left_size and r < right_size:
        right_elem = right_arr[r]
        left_elem = left_arr[l]
        if left_elem < right_elem:
            arr[k] = left_elem
            l += 1
        else:
            arr[k] = right_elem
            r += 1
        yield
        k += 1

    # exahust the any remaining elements that maybe in the left or right half of the array
    if l < left_size:
        arr[k : k + (left_size - l)] = left_arr[l:]
    elif r < right_size:
        arr[k : k + (right_size - r)] = right_arr[r:]


def tim_sort(arr: MutableSequence[CT], merge_size: int = 32) -> MutableSequence[CT]:
    remainder = 0
    arr_size = n = len(arr)
    while n >= merge_size:
        # will either be 1 or 0 depending on whether n is an odd or even number
        remainder |= n & 1
        n >>= 1
    min_runsize = n + remainder

    # perform insertion sort on subarrays with the length of the minimum run size
    index = 0
    prev_index = 0
    end_index = arr_size - 1
    RunChunk = namedtuple("RunChunk", ["start_index", "end_index"])
    run_chunks: List[RunChunk] = []
    while index < end_index:
        comparator = lt if arr[index] < arr[index + 1] else gt

        index += 1
        run_size = 2
        while index < end_index and comparator(arr[index], arr[index + 1]):
            index += 1
            run_size += 1

        if run_size < min_runsize:
            index = min(index + min_runsize - run_size, end_index)
            insertion_sort(arr, prev_index, index)

        run_chunks.append(RunChunk(prev_index, index))
        prev_index = index
        index += 1

    if len(run_chunks) == 1:
        return


def radix_sort(arr: MutableSequence[CT]) -> MutableSequence[CT]:
    ...


if __name__ == "__main__":
    import timeit

    # print(timeit.timeit("tim_sort(list(range(0, 10_000_000)))", "from __main__ import tim_sort", number=1))
    # print(timeit.timeit("sorted(list(range(10_000_000)))", number=1))
    tim_sort(list(range(100_000)))
