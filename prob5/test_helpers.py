import pytest
from prob5.helpers import range_intersect

@pytest.mark.parametrize(
    "a,b,expected",
    [(range(0,0), range(0,0), None),
     (range(0,5), range(10,15), None),
     (range(10,15), range(20,25), None),
     (range(8,12), range(10,15), range(10,12)),
     (range(10,15), range(12,18), range(12,15)),
     (range(12,14), range(10,15), range(12,14)),
])
def test_range_intersect(a, b, expected):
    assert range_intersect(a, b) == expected