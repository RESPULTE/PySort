from collections import deque, namedtuple
from pysort.lib._type_hint import CT
from pysort.lib.quadratic_sort import insertion_sort
from typing import List, MutableSequence, Tuple
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

    def recursive_merge_sort(start: int, end: int) -> None:
        if end == start:
            return

        # recursively splitting the array into left & right halves
        mid = start + (end - start) // 2
        yield from recursive_merge_sort(start, mid)
        yield from recursive_merge_sort(mid + 1, end)

        # choosing the left/right array to become the temporary array
        # +1 for the left array's size to avoid it being a 0 when the array is the size of 2, i.e (0, 0, 1) -> (start, mid, end)
        left_size = mid - start + 1
        right_size = end - mid

        # +1 for mid beacuse everything brekas without doing this
        mid += 1
        if left_size > right_size:
            # i.e (0, 1, 2) -> (start, mid, end)
            # since left size is bigger left arr must be [0, 1] & right arr must be only 2
            # but this is not possible with index slicing unless the end & mid is incremented by 1
            # so the slicing notations ends up being arr[0:2], arr[2:3]
            # ? there's most definitely a better way to go about this, but i'm too tired to care
            temp_arr = arr[mid : end + 1]
            arr[start + right_size : mid + right_size] = arr[start:mid]

            temp_size = right_size

            i = start + right_size
            end_index = left_size + i

        else:
            temp_arr = arr[start:mid]
            temp_size = left_size

            i = mid
            end_index = right_size + i

        # copying the elements of splitted-array back into the original array in order
        t, k = 0, start
        while t < temp_size and i < end_index:
            temp_elem = temp_arr[t]
            orig_elem = arr[i]

            if temp_elem < orig_elem:
                arr[k] = temp_elem
                yield temp_elem
                t += 1
            else:
                arr[k] = orig_elem
                yield orig_elem
                i += 1
            k += 1

        while i < end_index:
            arr[k] = arr[i]
            k += 1
            i += 1

        while t < temp_size:
            arr[k] = temp_arr[t]
            k += 1
            t += 1

    yield from recursive_merge_sort(0, len(arr) - 1)


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

    for rc in run_chunks:
        ...


def radix_sort(arr: MutableSequence[CT]) -> MutableSequence[CT]:
    ...


if __name__ == "__main__":
    import timeit

    # print(timeit.timeit("tim_sort(list(range(0, 10_000_000)))", "from __main__ import tim_sort", number=1))
    # print(timeit.timeit("sorted(list(range(10_000_000)))", number=1))
