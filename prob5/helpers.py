def range_intersect(range_a, range_b):
    if range_a.step != range_b.step:
        raise RuntimeError(f"intersecting ranges must have same step")
    int_start = max(range_a.start, range_b.start)
    int_stop = min(range_a.stop, range_b.stop)
    if int_stop <= int_start:
        return None
    return range(int_start, int_stop, range_a.step)


