class FQR:
    """
    A valid FQR that should be ready to save to meta.json or pass to the
    pmtiles tool.
    """

    # Convert from

    def __init__(self, bbox):
        self.init_from_bbox(bbox)

    def init_from_bbox(self, bbox):
        """
        Initialize values from `bbox` (i.e, a list of 4 numbers). Check if `bbox`
        meets our standard format, including the basic structure.
        """

        if not isinstance(bbox, list):
            raise ValueError("bbox is not an array")
        if len(bbox) != 4:
            raise ValueError("bbox has unexpected length")
        for coord in bbox:
            if not isinstance(coord, (int, float)):
                raise ValueError("coordinate is not a number")

        self.min_lon, self.min_lat, self.max_lon, self.max_lat = bbox

        if self.min_lon == self.max_lon:
            raise ValueError("longitudes are equal")
        for lon in [self.min_lon, self.max_lon]:
            if lon > 180:
                raise ValueError("longitude > 180")
            if lon <= -180:
                raise ValueError("longitude <= -180")

        if self.min_lat >= self.max_lat:
            raise ValueError("latitudes are equal or out of order")
        for lat in [self.min_lat, self.max_lat]:
            if lat > 90:
                raise ValueError("latitude > 90")
            if lat < -90:
                raise ValueError("latitude < -90")

    @classmethod
    def from_bbox_str(cls, extract_box_str):
        """
        This function parses and validates the bbox string that comes from the
        UI tool (the same format that gets passed into pmtiles), and
        initializes an FQR from it.

        An example string in this format is `"0,10,50.5,60.5"`
        """
        try:
            # `float` is important here even if just as a parsing check.
            min_lon, min_lat, max_lon, max_lat = [float(n) for n in extract_box_str.split(",")]
        except Exception as e:
            raise ValueError(f"bbox ({extract_box_str}) is malformed: {e}")

        try:
            return cls([min_lon, min_lat, max_lon, max_lat])
        except Exception as e:
            raise ValueError(f"bbox ({[min_lon, min_lat, max_lon, max_lat]}) is invalid: {e}")


    # Convert to

    def to_bbox(self):
        return [self.min_lon, self.min_lat, self.max_lon, self.max_lat]

    def to_bbox_str(self):
        return ",".join(map(repr, self.to_bbox()))


    # Check for overlaps

    def _split_antimeridian_bbox(self):
        """
        Assumes `self` crosses the antimeridian
        """
        # Remember: the western edge of the -180/180 logical map is the eastern
        # portion of the region that crosses that 180/-180 edge.
        # NOTE - This -179.99999999 is an awkward situation and creates various problems.
        # This will be fixed in an upcoming commit.
        east = FQR([-179.99999999, self.min_lat, self.max_lon, self.max_lat])
        west = FQR([self.min_lon, self.min_lat, 180, self.max_lat])
        return (east, west)

    def overlaps(self, other):
        # self crosses antimeridian, so let's split it in two and recursively try this test on both
        if self.min_lon > self.max_lon:
            self_east, self_west = self._split_antimeridian_bbox()
            return (
                self_east.overlaps(other) or
                self_west.overlaps(other)
            )

        # other crosses antimeridian, so let's split it in two and recursively try this test on both
        if other.min_lon > other.max_lon:
            other_east, other_west = other._split_antimeridian_bbox()
            return (
                other_east.overlaps(self) or
                other_west.overlaps(self)
            )

        # self and other do not cross the antimeridian so we can test them simply
        return (
            self.min_lon < other.max_lon and
            other.min_lon < self.max_lon and
            self.min_lat < other.max_lat and
            other.min_lat < self.max_lat
        )
