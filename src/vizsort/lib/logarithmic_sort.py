from bisect import insort
from vizsort.lib._type_hint import CT
from vizsort.lib.utils import exhaust
from typing import List, MutableSequence, Tuple
from itertools import accumulate
from operator import lt, gt

__all__ = ["merge_sort", "tim_sort", "radix_sort", "iterative_quick_sort", "quick_sort"]


def merge_sort(arr: MutableSequence[CT], start: int = 0, end: int = None) -> None:
    """
    executes merge sort on the given array in place

    [Process]
    1. Get the length of the array and get the midpoint of it

    2. recursively split the array at the midpoint into left & right half, and continue until the array is of size 1

    3. get the minimum element of both array & write it to the original array, continue until one of the halves has been exhausted

    4. just repeat the same process for the other half that hasn't had it element written back into the original array yet

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


def tim_sort(arr: MutableSequence[CT], merge_size: int = 32) -> None:
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
    run_chunks: List[Tuple[int, int]] = []

    while index < end_index:
        comparator = lt if arr[index] < arr[index + 1] else gt

        index += 1
        run_size = 2
        while index < end_index and comparator(arr[index], arr[index + 1]):
            yield arr[index, True]
            index += 1
            run_size += 1

        if comparator is gt:
            end_section_index = prev_index + -(-(index - prev_index) // 2)

            for i in range(prev_index, end_section_index):
                arr[i], arr[end_section_index] = arr[end_section_index], arr[i]
                yield arr[end_section_index, True]
                end_section_index -= 1

        if run_size < min_runsize or 0 < end_index - index < min_runsize:
            index = min(index + min_runsize - run_size, end_index)

            for i in range(prev_index + 1, index + 1):
                while i > prev_index and arr[i - 1] > arr[i]:
                    arr[i - 1], arr[i] = arr[i], arr[i - 1]
                    yield arr[i, True]
                    i -= 1

        run_chunks.append((prev_index, index))
        index += 1
        prev_index = index

    if len(run_chunks) == 1:
        return

    while (size := len(run_chunks)) > 1:

        for m in range(size - 1, -1, -2):
            rc_2, rc_1 = run_chunks.pop(m), run_chunks.pop(m - 1)
            start, mid, end = rc_1[0], rc_1[1], rc_2[1]

            left_size = mid - start + 1
            right_size = end - mid
            mid += 1
            if left_size > right_size:
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

            insort(run_chunks, (start, end))


def radix_sort(arr: MutableSequence[CT], base: int = 10) -> None:
    max_elem = max(arr)
    arr_size = len(arr)

    # the larger the base, the larger the required space, but the lower the time complexity
    # larger base allows for lesser iterations of the array through counting sort, but it increases
    # the size of the temporary array used, base larger than the size of the array itself would result in a lot of
    # unnecessary empty-space created in the count_index array
    base = min(base, len(arr))
    digit = 1

    # keep looping until the digit of the max element has been exceeded
    while max_elem // digit > 0:

        # to keep track of the number of occurence of each number (0-9)
        count_index = [0] * base

        for i in range(0, arr_size):
            # divide the number so that the position that we're looking for is the LSD
            index = arr[i] // digit
            # modulus the number to get the LSD
            count_index[index % base] += 1
            yield arr[i, True]

        # getting the cummulative sum of the count_index array
        # basically getting the index of the element with the given LSD in the actual array
        # i.e: given an already sorted array
        # given_array = [0, 1, 1, 2, 3, 5, 6, 6, 7, 8, 9]
        # count_array = [1, 2, 1, 1, 0, 1, 2, 1, 1, 1]
        # cummulative_count_array = [1, 3, 4, 5, 5, 6, 8, 9, 10, 11]
        # given the element 7, its index would be 7, which corresponds to 9 in the cummulative_count_array,
        # minus 1 and its 8, whih is the correct index of the element in the actual array
        cummulative_count_index = list(accumulate(count_index))

        i = arr_size - 1
        output_arr = [0] * arr_size
        while i >= 0:
            elem = arr[i]
            index = (elem // digit) % base
            output_arr[cummulative_count_index[index] - 1] = elem
            cummulative_count_index[index] -= 1
            i -= 1

        # re-writing the temporary array back into the actual array
        for i in range(0, arr_size):
            arr[i] = output_arr[i]
            yield output_arr[i, True]

        digit *= base


def iterative_quick_sort(arr: MutableSequence[CT]) -> None:
    def recursive_quick_sort(start: int, end: int) -> None:
        while start < end:

            pivot = arr[end]
            i = start

            for j in range(start, end):
                if arr[j] <= pivot:
                    arr[i], arr[j] = arr[j], arr[i]
                    yield arr[j, True]
                    i += 1

            arr[i], arr[end] = arr[end], arr[i]
            yield arr[end, True]

            if i - start < end - i:
                yield from recursive_quick_sort(start, i - 1)
                start = i + 1
                continue

            yield from recursive_quick_sort(i + 1, end)
            end = i - 1

    yield from recursive_quick_sort(0, len(arr) - 1)


def quick_sort(arr: MutableSequence[CT]) -> None:
    def recursive_quick_sort(start: int, end: int) -> None:
        if start >= end:
            return

        pivot = arr[end]
        i = start

        for j in range(start, end):
            if arr[j] <= pivot:
                arr[i], arr[j] = arr[j], arr[i]
                yield arr[j, True]
                i += 1

        arr[i], arr[end] = arr[end], arr[i]
        yield arr[end]

        yield from recursive_quick_sort(start, i - 1)
        yield from recursive_quick_sort(i + 1, end)

    yield from recursive_quick_sort(0, len(arr) - 1)
