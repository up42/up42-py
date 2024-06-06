import dataclasses
from typing import List

import pystac

from up42 import processing


def _create_single_item_template(name: str, process_id: str):
    template_class = dataclasses.make_dataclass(
        name=name,
        fields=[("title", str), ("item", pystac.Item)],
        bases=(processing.SingleItemJobTemplate),
    )
    template_class.process_id = process_id
    return template_class


@dataclasses.dataclass
class SpaceptBuildingsDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-buildings-spacept"


@dataclasses.dataclass
class SpaceptTreesDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-trees-spacept"


@dataclasses.dataclass
class SpaceptTreeHeightsDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-trees-heights-spacept"


@dataclasses.dataclass
class SpaceptShadowsDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-shadows-spacept"


@dataclasses.dataclass
class AirbusShipsDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-ships-airbus"


@dataclasses.dataclass
class AirbusWindTurbinesDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-wind-turbines-airbus"


@dataclasses.dataclass
class AirbusStorageTanksDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-storage-tanks-airbus"


@dataclasses.dataclass
class OrbitalInsightTrucksDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id: str = "detection-trucks-oi"


@dataclasses.dataclass
class OrbitalInsightCarsDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-cars-oi"


@dataclasses.dataclass
class OrbitalInsightAircraftDetection(processing.SingleItemJobTemplate):
    title: str
    item: pystac.Item
    process_id = "detection-aircraft-oi"


@dataclasses.dataclass
class SpaceptChangeDetection(processing.MultiItemJobTemplate):
    title: str
    items: List[pystac.Item]
    process_id = "detection-change-spacept"


@dataclasses.dataclass
class HypervergePleiadesChangeDetection(processing.MultiItemJobTemplate):
    title: str
    items: List[pystac.Item]
    process_id = "detection-change-pleiades-hyperverge"


@dataclasses.dataclass
class HypervergeSpotChangeDetection(processing.MultiItemJobTemplate):
    title: str
    items: List[pystac.Item]
    process_id = "detection-change-spot-hyperverge"
