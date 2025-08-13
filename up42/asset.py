import dataclasses
import datetime as dt
import pathlib
from typing import Iterator, List, Literal, Optional, Union, cast, Type

import pystac
import pystac_client
import tenacity as tnc

from up42 import base, host, utils

logger = utils.get_logger(__name__)

MAX_ITEM = 50
LIMIT = 50

NOT_PROVIDED = object()
_retry = tnc.retry(
    stop=tnc.stop_after_attempt(5),
    wait=tnc.wait_exponential(multiplier=1),
    reraise=True,
)


class AssetSorting:
    name = utils.SortingField("name")
    title = utils.SortingField("title")
    size = utils.SortingField("size")
    created_at = utils.SortingField("createdAt")
    updated_at = utils.SortingField("updatedAt")
    source = utils.SortingField("source")
    collection_name = utils.SortingField("collectionName")
    producer_name = utils.SortingField("producerName")


AssetSorting = cast(
    Type[AssetSorting],
    utils.deprecation(None, "3.0.0")(AssetSorting)
)


class Asset:
    session = base.Session()
    stac_client = base.StacClient()
    id: str
    account_id: str
    created_at: str
    name: Optional[str]
    size: int
    updated_at: str
    workspace_id: str
    order_id: Optional[str]
    source: Optional[Literal["ARCHIVE", "TASKING", "PROCESSING"]]
    product_id: Optional[str]
    content_type: str
    producer_name: Optional[str]
    collection_name: Optional[str]
    geospatial_metadata_extraction_status: Optional[Literal["SUCCESSFUL", "FAILED", "IN_PROGRESS", "NOT_PROCESSED"]]
    title: Optional[str]
    tags: Optional[list[str]]
    info: dict

    @property
    @utils.deprecation(None, "3.0.0")
    def asset_id(self) -> str:
        return self.info["id"]

    @staticmethod
    def _from_metadata(metadata: dict) -> "Asset":
        return Asset(
            id=metadata["id"],
            account_id=metadata["accountId"],
            created_at=metadata["createdAt"],
            name=metadata.get("name"),
            size=metadata["size"],
            updated_at=metadata["updatedAt"],
            workspace_id=metadata["workspaceId"],
            order_id=metadata.get("orderId"),
            source=metadata.get("source"),
            product_id=metadata.get("productId"),
            content_type=metadata["contentType"],
            producer_name=metadata.get("producerName"),
            collection_name=metadata.get("collectionName"),
            geospatial_metadata_extraction_status=metadata.get("geospatialMetadataExtractionStatus"),
            title=metadata.get("title"),
            tags=metadata.get("tags"),
            info=metadata,
        )

    @classmethod
    @utils.deprecation(None, "3.0.0")
    def get(cls, asset_id: str) -> "Asset":
        url = host.endpoint(f"/v2/assets/{asset_id}/metadata")
        return cls._from_metadata(cls.session.get(url=url).json())

    @classmethod
    @utils.deprecation(None, "3.0.0")
    def all(
        cls,
        created_after: Optional[Union[str, dt.datetime]] = None,
        created_before: Optional[Union[str, dt.datetime]] = None,
        workspace_id: Optional[str] = None,
        collection_names: Optional[List[str]] = None,
        producer_names: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        search: Optional[str] = None,
        sort_by: Optional[utils.SortingField] = None,
    ) -> Iterator["Asset"]:
        params = {
            "createdAfter": created_after and utils.format_time(created_after),
            "createdBefore": created_before and utils.format_time(created_before),
            "workspaceId": workspace_id,
            "collectionNames": collection_names,
            "producerNames": producer_names,
            "tags": tags,
            "sources": sources,
            "search": search,
            "sort": sort_by,
        }
        return map(cls._from_metadata, utils.paged_query(params, "/v2/assets", cls.session))

    @property
    @utils.deprecation("pystac::Client.get_items", "3.0.0")
    @_retry
    def stac_items(self) -> pystac.ItemCollection:
        """Returns the stac items from an UP42 asset STAC representation."""
        try:
            filter_by_asset_id = {
                "max_items": MAX_ITEM,
                "limit": LIMIT,
                "filter": {
                    "op": "=",
                    "args": [
                        {"property": "asset_id"},
                        self.asset_id,
                    ],
                },
            }
            stac_search = self.stac_client.search(filter=filter_by_asset_id)
            return stac_search.item_collection()
        except Exception as exc:
            raise ValueError(f"No STAC metadata information available for this asset {self.asset_id}") from exc

    @property
    @utils.deprecation(None, "3.0.0")
    @_retry
    def stac_info(self) -> Union[pystac.Collection, pystac_client.CollectionClient]:
        """
        Gets the storage STAC information for the asset as a FeatureCollection.
        One asset can contain multiple STAC items (e.g. the PAN and multispectral images).
        """
        return self.stac_client.get_collection(self.stac_items[0].collection_id)

    @utils.deprecation("pystac::Item.update", "3.0.0")
    def update_metadata(
        self,
        title: Union[Optional[str], object] = NOT_PROVIDED,
        tags: Union[Optional[List[str]], object] = NOT_PROVIDED,
    ) -> dict:
        """
        Update the metadata of the asset.

        Args:
            title: The title string to be assigned to the asset. No value will keep the existing title.
            tags: A list of tag strings to be assigned to the asset. No value will keep the existing tags.

        Returns:
            The updated asset metadata information
        """
        if title != NOT_PROVIDED:
            self.title = cast(Optional[str], title)
        if tags != NOT_PROVIDED:
            self.tags = cast(Optional[list[str]], tags)
        self._save()
        return self.info

    def _save(self):
        url = host.endpoint(f"/v2/assets/{self.asset_id}/metadata")
        payload = {"title": self.title, "tags": self.tags}
        asset = self._from_metadata(self.session.post(url=url, json=payload).json())
        for field in dataclasses.fields(asset):
            setattr(self, field.name, getattr(asset, field.name))

    def _get_download_url(self, asset_id: str) -> str:
        url = host.endpoint(f"/v2/assets/{asset_id}/download-url")
        return self.session.post(url=url).json()["url"]

    @property
    @utils.deprecation(None, "3.0.0")
    def file(self) -> utils.ImageFile:
        return utils.ImageFile(url=self._get_download_url(self.asset_id))

    @utils.deprecation("pystac::Asset.file.url", "3.0.0")
    def get_stac_asset_url(self, stac_asset: pystac.Asset):
        """
        Returns the signed URL for the STAC Asset.
        Args:
            stac_asset: pystac Asset object.

        Returns:
            Signed URL for the STAC Asset.
        """
        stac_asset_id = stac_asset.href.split("/")[-1]
        return self._get_download_url(asset_id=stac_asset_id)

    @utils.deprecation("pystac::Asset.file::download", "3.0.0")
    def download(
        self,
        output_directory: Union[str, pathlib.Path, None] = None,
        unpacking: bool = True,
    ) -> List[str]:
        """
        Downloads the asset. Unpacking the downloaded file will happen as default.

        Args:
            output_directory: The file output directory, defaults to the current working
                directory.
            unpacking: By default the download TGZ/TAR or ZIP archive file will be unpacked.

        Returns:
            List of the downloaded asset filepaths.
        """
        logger.info("Downloading asset %s", self.asset_id)

        if output_directory is None:
            output_directory = pathlib.Path.cwd() / f"asset_{self.asset_id}"
        else:
            output_directory = pathlib.Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info("Download directory: %s", output_directory)

        download_url = self._get_download_url(asset_id=self.asset_id)
        download = utils.download_archive if unpacking else utils.download_file
        return download(
            download_url=download_url,
            output_directory=output_directory,
        )

    @utils.deprecation("pystac::Asset.file::download", "3.0.0")
    def download_stac_asset(
        self,
        stac_asset: pystac.Asset,
        output_directory: Union[str, pathlib.Path, None] = None,
    ) -> pathlib.Path:
        """
        Downloads a STAC asset to a specified output directory.

        Args:
            self (object): The instance of the class calling this method.
            stac_asset (pystac.Asset): The STAC asset to be downloaded.
            output_directory (Union[str, Path, None], optional): The directory where the asset
                will be downloaded. If not provided, a default directory structure will be used.

        Returns:
            Path: The path to the downloaded asset file.

        Raises:
            requests.exceptions.HTTPError: If there is an HTTP error during the download.

        """
        logger.info("Downloading STAC asset %s", stac_asset.title)
        if output_directory is None:
            output_directory = pathlib.Path.cwd() / f"asset_{self.asset_id}/{stac_asset.title}"
        else:
            output_directory = pathlib.Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info("Download directory: %s", output_directory)
        download_url = self.get_stac_asset_url(stac_asset=stac_asset)
        return pathlib.Path(utils.download_file(download_url, output_directory)[0])


Asset = cast(
    Type[Asset],
    utils.deprecation(None, "3.0.0")(dataclasses.dataclass(Asset))
)
