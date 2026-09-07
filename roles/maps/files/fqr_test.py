import unittest
from fqr import FQR

class TestOverlap(unittest.TestCase):
    def test_simple_fqr(self):
        """
        Test that there's no problem creating a basic FQR
        """
        FQR([0, 10, 50, 60])

    def test_to_bbox(self):
        bbox = [0, 10, 50, 60]
        self.assertEqual(FQR(bbox).to_bbox(), bbox)

    def test_to_bbox_str(self):
        bbox = [0, 10, 50.5, 60.5]
        self.assertEqual(FQR(bbox).to_bbox_str(), "0,10,50.5,60.5")

    def test_split_antimeridian_bbox(self):
        fqr = FQR([170, 80, -170, 90])
        east, west = fqr._split_antimeridian_bbox()
        self.assertEqual(east.to_bbox(), [-179.99999999, 80, -170, 90])
        self.assertEqual(west.to_bbox(), [170, 80, 180, 90])

    def test_overlap_neither_antimeridian_cross(self):
        """
        Test overlaps and non-overlaps between two regions, neither of which cross the antimeridian
        """

        self.assertTrue(FQR([0, 0, 20, 20]).overlaps(FQR([10, 10, 30, 30])), "expected: regions overlap")

        self.assertFalse(FQR([0, 0, 20, 20]).overlaps(FQR([30, 30, 40, 40])), "expected: no overlap - disjoint lat and lon")
        self.assertFalse(FQR([0, 0, 20, 20]).overlaps(FQR([10, 30, 30, 40])), "expected: no overlap - disjoint only lat")
        self.assertFalse(FQR([0, 0, 20, 20]).overlaps(FQR([30, 10, 40, 30])), "expected: no overlap - disjoint only lon")

        self.assertFalse(FQR([0, 0, 20, 20]).overlaps(FQR([20, 0, 40, 20])), "expected: no overlap - borders on lon")
        self.assertFalse(FQR([0, 0, 20, 20]).overlaps(FQR([0, 20, 20, 40])), "expected: no overlap - borders on lat")

    def test_overlap_one_antimeridian_cross(self):
        """
        Test overlaps and non-overlaps between two regions, one of which crosses the antimeridian
        """

        self.assertTrue(FQR([160, 0, -160, 20]).overlaps(FQR([-170, 0, -150, 20])), "expected: overlap - east of antimeridian (-170 to -160)")
        self.assertTrue(FQR([160, 0, -160, 20]).overlaps(FQR([150, 0, 170, 20])), "expected: overlap - west of antimeridian (160 to 170)")

        self.assertFalse(FQR([160, 0, -160, 20]).overlaps(FQR([-150, 0, -140, 20])), "expected: no overlap - east of antimeridian")
        self.assertFalse(FQR([160, 0, -160, 20]).overlaps(FQR([140, 0, 150, 20])), "expected: no overlap - west of antimeridian")

    def test_overlap_both_antimeridian_cross(self):
        """
        Test overlaps and non-overlaps between two antimeridian-crossing regions
        """

        self.assertTrue(FQR([160, 0, -160, 20]).overlaps(FQR([170, 0, -150, 20])), "expected: overlap - first region starts and ends more east than second region does")
        self.assertTrue(FQR([160, 0, -160, 20]).overlaps(FQR([150, 0, -170, 20])), "expected: overlap - first region starts and ends more west than second region does")
        self.assertTrue(FQR([160, 0, -160, 20]).overlaps(FQR([170, 0, -170, 20])), "expected: overlap - first region fully contains second region")
        self.assertTrue(FQR([170, 0, -170, 20]).overlaps(FQR([160, 0, -160, 20])), "expected: overlap - second region fully contains first region")

if __name__ == "__main__":
    unittest.main()
