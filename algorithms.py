import random


def bubble_sort(numbers):
    length = len(numbers)
    for i in range(length):
        for j in range(length - i - 1):
            if numbers[j] > numbers[j + 1]:
                temp = numbers[j]
                numbers[j] = numbers[j + 1]
                numbers[j + 1] = temp
            yield (j, j + 1)


def quick_sort(numbers, start=0, end=None):
    if end is None:
        end = len(numbers) - 1
    if start >= end:
        return

    # pick a random pivot and move it to the end
    pivot_index = random.randint(start, end)
    temp = numbers[pivot_index]
    numbers[pivot_index] = numbers[end]
    numbers[end] = temp
    pivot_value = numbers[end]

    # everything before small_end will be smaller than the pivot
    small_end = start
    for current in range(start, end):
        yield (current, end)
        if numbers[current] < pivot_value:
            temp = numbers[small_end]
            numbers[small_end] = numbers[current]
            numbers[current] = temp
            small_end += 1
            yield (small_end, current)

    # put the pivot into its final position
    temp = numbers[small_end]
    numbers[small_end] = numbers[end]
    numbers[end] = temp
    yield (small_end, end)

    # sort the left side and the right side of the pivot
    yield from quick_sort(numbers, start, small_end - 1)
    yield from quick_sort(numbers, small_end + 1, end)


def merge_sort(numbers, start=0, end=None):
    if end is None:
        end = len(numbers)
    if end - start <= 1:
        return

    middle = (start + end) // 2
    yield from merge_sort(numbers, start, middle)
    yield from merge_sort(numbers, middle, end)

    # copy the two sorted halves so we can write back into the main list
    left_half = numbers[start:middle]
    right_half = numbers[middle:end]
    left_pos = 0
    right_pos = 0
    write_pos = start

    # take the smaller front item from either half
    while left_pos < len(left_half) and right_pos < len(right_half):
        if left_half[left_pos] <= right_half[right_pos]:
            numbers[write_pos] = left_half[left_pos]
            left_pos += 1
        else:
            numbers[write_pos] = right_half[right_pos]
            right_pos += 1
        yield (write_pos,)
        write_pos += 1

    # one half ran out, copy whatever is left of the other
    while left_pos < len(left_half):
        numbers[write_pos] = left_half[left_pos]
        left_pos += 1
        yield (write_pos,)
        write_pos += 1

    while right_pos < len(right_half):
        numbers[write_pos] = right_half[right_pos]
        right_pos += 1
        yield (write_pos,)
        write_pos += 1
