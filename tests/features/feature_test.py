import unittest
from datetime import datetime
from typing import Optional

from signalboost.features.feature import Feature, Features, Record


class Click(Feature):
    def __init__(
        self,
        id: str,
        value: int,
        timestamp: Optional[datetime] = None,
        user: str | None = None,
    ):
        super().__init__(
            id, Record(value=value, timestamp=timestamp, user=user), data_type=int
        )

    def combine(self, other: "Click"):
        return self.record.value + other.record.value


class Location(Feature):
    def __init__(
        self, id: str, value: str, user: str, timestamp: Optional[datetime] = None
    ):
        super().__init__(
            id, Record(value=value, timestamp=timestamp, user=user), data_type=str
        )

    def combine(self, other: "Location"):
        return self.record.value + other.record.value


class FeatureTests(unittest.TestCase):

    def setUp(self):
        self.my_feature = Click(id="1", value=1)
        self.my_feature_2 = Click(id="1", value=2)

    def test_feature_pipeline_empty(self):
        my_features = Features(id="1")
        self.assertEquals(my_features.features, {})
        self.assertEqual(len(my_features.features), 0)

    def test_add_feature(self):
        my_features = Features(id="1")
        my_same_features = Features(id="1")

        my_features + self.my_feature  # test +
        my_same_features.add_feature(self.my_feature)  # test add_feature

        # test that they both do the same thing!
        self.assertDictEqual(my_features.features, my_same_features.features)

    def test_add_features(self):
        my_features = Features(id="1")
        my_features + self.my_feature
        self.assertEqual(len(my_features.features["1"]), 1)
        self.assertEqual(len(my_features.features), 1)

        my_features.add_feature(self.my_feature_2)
        self.assertEqual(len(my_features.features["1"]), 2)
        self.assertEqual(len(my_features.features), 1)

        # Verify the specific features in the list
        self.assertEqual(my_features.features["1"][0], self.my_feature)
        self.assertEqual(my_features.features["1"][1], self.my_feature_2)

    def test_add_mixed_features(self):
        my_features = Features(id="1")
        my_features + self.my_feature
        self.assertEqual(len(my_features.features["1"]), 1)
        self.assertEqual(len(my_features.features), 1)

        my_features.add_feature(self.my_feature_2)
        self.assertEqual(len(my_features.features["1"]), 2)
        self.assertEqual(len(my_features.features), 1)
        self.assertDictEqual(
            my_features.features, {"1": [self.my_feature, self.my_feature_2]}
        )

        location_feature = Location(id="2", value="USA", user="Blake")
        my_features + location_feature
        self.assertEqual(len(my_features.features), 2)
        self.assertEqual(len(my_features.features["2"]), 1)

        self.assertEqual(my_features.features["2"][0], location_feature)
