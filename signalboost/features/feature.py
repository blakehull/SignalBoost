import json
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from typing import Any, Annotated, DefaultDict, Optional, Callable

from pydantic import BaseModel, ConfigDict, field_validator, field_serializer, Field


class Record(BaseModel):
    value: Any
    timestamp: datetime | None
    user: str | None

    @field_serializer("timestamp")
    def serialize_dt(self, timestamp: datetime, _info):
        return timestamp.isoformat()

    @field_validator("*", mode="before")
    @classmethod
    def apply_default(cls, v, val_info):
        field = cls.model_fields[val_info.field_name]
        if v is None and issubclass(datetime, field.annotation):
            return datetime.now()
        return v


class Feature(ABC):

    def __init__(self, id: str, record: Record, data_type: type):
        self.id = id
        self.record: Record = record
        self.data_type: type = data_type

    @abstractmethod
    def combine(self, other):
        pass

    def __repr__(self):
        return json.dumps(
            {"type": self.__class__.__name__, "record": self.record.model_dump()}
        )


class FeatureSummary:
    def __init__(self):
        self.count = 0
        self.total_value = 0
        self.type = None
        self.oldest_record_timestamp: datetime | None = None
        self.newest_record_timestamp: datetime | None = None

    def update(self, feature: Feature):
        self.count += 1

        if not self.type:
            self.type = feature.data_type

        if isinstance(feature.record.value, (int, float)):
            self.total_value += feature.record.value

        timestamp = feature.record.timestamp
        if (
            self.oldest_record_timestamp is None
            or timestamp < self.oldest_record_timestamp
        ):
            self.oldest_record_timestamp = timestamp
        if (
            self.newest_record_timestamp is None
            or timestamp > self.newest_record_timestamp
        ):
            self.newest_record_timestamp = timestamp

    def summary(self) -> dict:
        return {
            "count": self.count,
            "total_value": self.total_value,
            "type": self.type,
            "start_time": self.oldest_record_timestamp,
            "end_time": self.newest_record_timestamp,
        }


class Features(BaseModel):
    id: str
    features: DefaultDict[str, Annotated[list[Any], Field(default_factory=list)]] = (
        Field(default_factory=lambda: defaultdict(list))
    )
    summaries: DefaultDict[
        str, Annotated[FeatureSummary, Field(default_factory=FeatureSummary)]
    ] = Field(default_factory=lambda: defaultdict(FeatureSummary))

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __add__(self, feature: Feature):
        self.features[feature.id].append(feature)
        self.summaries[feature.id].update(feature)
        return self

    def add_feature(self, feature: Feature):
        return self.__add__(feature)

    def totals(self, id: str) -> int | float:
        """
        Return the total aggregate for a given feature ID
        (if the feature is numeric).
        """
        if id in self.summaries:
            return self.summaries[id].total_value
        return 0

    def search(
        self,
        filters: Optional[dict[str, Any]] = None,
        custom_filter: Optional[Callable[[Feature], bool]] = None,
    ) -> list[Feature]:
        """
        Search for features based on arbitrary attributes.

        - filters: A dictionary where keys are attribute paths (dot-separated for nested attributes)
          and values are the values to match or a callable for complex conditions.
        - custom_filter: A callable that takes a Feature and returns True if it matches.

        Examples:
            features.search(filters={
                'record.value': 10,
                'record.timestamp': lambda ts: ts >= start_time and ts <= end_time
            })

            features.search(custom_filter=lambda f: isinstance(f, Click) and f.record.value > 5)
        """
        results = []

        if filters is None:
            filters = {}

        for feature_list in self.features.values():
            for feature in feature_list:
                match = True

                for attr_path, expected in filters.items():
                    attrs = attr_path.split(".")
                    value = feature
                    try:
                        for attr in attrs:
                            value = getattr(value, attr)
                    except AttributeError:
                        match = False
                        break

                    if callable(expected):
                        if not expected(value):
                            match = False
                            break
                    else:
                        if value != expected:
                            match = False
                            break

                if custom_filter and not custom_filter(feature):
                    match = False

                if match:
                    results.append(feature)

        return results

    def summary(self, id: str) -> dict:
        """
        Return summary statistics for a given feature ID.
        """
        if id in self.summaries:
            return self.summaries[id].summary()
        return {}
