from vizsort.lib._type_hint import CT
from typing import Iterable, MutableSequence

__all__ = ["bubble_sort", "insertion_sort", "selection_sort"]


def bubble_sort(arr: MutableSequence[CT], start: int = 0, end: int = None) -> Iterable[CT]:
    """excecutes bubble sort on the given array in-place
    [Process]
    1. for every element in the array, compare its value to the value of the next element
    2. if the value is bigger than the said element swap their position in the array
    3. repeat until the end-index (initially the end of the array)
    4. decrement the end-index by 1 and continue looping

    [Time Complexity]: N^2

    """
    if end is None:
        end = len(arr) - 1

    # note: the 'sorted group' will reside at the end of the array
    for i in range(start, end + 1):

        # for every element up-till the last 'i' element
        for j in range(end - i):

            # compare the element's value with its predecessor's value
            k = j + 1
            if arr[j] > arr[k]:
                arr[j], arr[k] = arr[k], arr[j]
                yield arr[k]


def insertion_sort(arr: MutableSequence[CT], start: int = 0, end: int = None) -> Iterable[CT]:
    """excecutes insertion sort on the given array in-place

    [Process]
    1. for every element in the array, check its direct ancestor's (the first element to the left of it) value
    2. if its is greater than the element's value, the shifting begins:

        i. while the ancestor element is greater than the element, move its position in the array up by 1
        ii. keep doing this until either the start of the array is reached or
            the ancestor's value is no longer greater than the element

        [basically shifting the array in reverse from left-to-right by 1 index until the right position is found for the element]

    5. continue for the next element in the array

    [Time Complexity]: N^2

    """
    # note: the 'sorted group' will reside at the start of the array
    if end is None:
        end = len(arr) - 1

    for i in range(start + 1, end + 1):
        while i > start and arr[i - 1] > arr[i]:
            arr[i - 1], arr[i] = arr[i], arr[i - 1]
            yield arr[i]
            i -= 1


def selection_sort(arr: MutableSequence[CT], start: int = 0, end: int = None) -> MutableSequence[CT]:
    """excecutes selection sort on the given array in-place

    [Process]
    1. set the 'minimum_value' as the first element in the array, at index 0
    2. loop through the entire array and pick out the element that's smaller than the 'minimum_value'
    3. swap that element with the 'minimum_value'
    4. increment the index by 1 and continue

    [Time Complexity]: N^2

    """
    if end is None:
        end = len(arr) - 1
    # note: the 'sorted group' will reside at the start of the array
    for i in range(start, end + 1):
        elem = arr[i]

        # looping through to find a smaller value
        min_elem_index = i
        for j in range(i, end + 1):
            _elem = arr[j]

            if _elem < elem:
                min_elem_index = j
                elem = _elem
                yield _elem

        # swap if a new minimum value has been found
        if min_elem_index != i:
            arr[i], arr[min_elem_index] = arr[min_elem_index], arr[i]

    return arr
