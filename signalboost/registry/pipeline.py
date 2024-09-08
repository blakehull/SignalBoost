from pydantic import BaseModel

from signalboost.features.feature import Features


class Registry(BaseModel):
    features: list[Features]
    # need to implement: backends, labels, etc.
