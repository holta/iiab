class FQR:
    @classmethod
    def check_bbox_error(cls, bbox):
        """
        Check if `bbox` meets our standard format, including the basic structure.
        It should be ready to save to meta.json or pass to the pmtiles tool.
        """

        if not isinstance(bbox, list):
            return "bbox is not an array"
        if len(bbox) != 4:
            return "bbox has unexpected length"
        for coord in bbox:
            if not isinstance(coord, (int, float)):
                return "coordinate is not a number"

        min_lon, min_lat, max_lon, max_lat = bbox

        if min_lon == max_lon:
            return "longitudes are equal"
        for lon in [min_lon, max_lon]:
            if lon > 180:
                return "longitude > 180"
            if lon <= -180:
                return "longitude <= -180"

        if min_lat >= max_lat:
            return "latitudes are equal or out of order"
        for lat in [min_lat, max_lat]:
            if lat > 90:
                return "latitude > 90"
            if lat < -90:
                return "latitude < -90"

    @classmethod
    def parse_bbox(cls, extract_box_str):
        """
        This function parses and validates the bbox string that comes from the UI tool
        """
        try:
            # `float` is important here even if just as a parsing check.
            min_lon, min_lat, max_lon, max_lat = [float(n) for n in extract_box_str.split(",")]
        except Exception as e:
            raise ValueError(f"Extract box ({extract_box_str}) is malformed: {e}")

        bbox = [min_lon, min_lat, max_lon, max_lat]
        error = cls.check_bbox_error(bbox)
        if error:
            raise ValueError(f"Extract box ({extract_box_str}) is invalid: {error}")
        return bbox

    @classmethod
    def _split_antimeridian_bbox(cls, bbox):
        return (
            [bbox[0], bbox[1], 180, bbox[3]],
            [-180, bbox[1], bbox[2], bbox[3]],
        )

    @classmethod
    def _has_overlap(cls, bbox_1, bbox_2):
        if bbox_1[0] > bbox_1[2]:
            bbox_1_east, bbox_1_west = cls._split_antimeridian_bbox(bbox_1)
            return (
                cls._has_overlap(bbox_1_east, bbox_2) or
                cls._has_overlap(bbox_1_west, bbox_2)
            )
        if bbox_2[0] > bbox_2[2]:
            bbox_2_east, bbox_2_west = cls._split_antimeridian_bbox(bbox_2)
            return (
                cls._has_overlap(bbox_1, bbox_2_east) or
                cls._has_overlap(bbox_1, bbox_2_west)
            )

        # Two normal squares
        return (
            bbox_1[0] < bbox_2[2] and
            bbox_2[0] < bbox_1[2] and
            bbox_1[1] < bbox_2[3] and
            bbox_2[1] < bbox_1[3]
        )
