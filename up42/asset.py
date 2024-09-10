import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import pystac
import pystac_client
import requests
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


class Asset:
    """
    The Asset class enables access to the UP42 assets in the storage. Assets are results
    of orders or results of jobs with download blocks.

    Use an existing asset:
    ```python
    asset = up42.initialize_asset(asset_id="8c2dfb4d-bd35-435f-8667-48aea0dce2da")
    ```
    """

    session = base.Session()

    def __init__(
        self,
        asset_id: Optional[str] = None,
        asset_info: Optional[dict] = None,
    ):
        if asset_id is not None and asset_info is not None:
            raise ValueError("asset_id and asset_info cannot be provided simultaneously.")
        if asset_id is None and asset_info is None:
            raise ValueError("Either asset_id or asset_info should be provided in the constructor.")

        self.info = self._get_info(asset_id) if asset_id is not None else asset_info

    def __repr__(self):
        return self.info.__repr__()

    @property
    def asset_id(self) -> dict:
        return self.info.get("id")

    def _get_info(self, asset_id: str):
        url = host.endpoint(f"/v2/assets/{asset_id}/metadata")
        return self.session.get(url=url).json()

    def _stac_search(self) -> Tuple[pystac_client.Client, pystac_client.ItemSearch]:
        stac_client = utils.stac_client(cast(requests.auth.AuthBase, self.session.auth))
        stac_search_parameters = {
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
        return stac_client, stac_client.search(filter=stac_search_parameters)

    @property
    @_retry
    def stac_info(self) -> Union[pystac.Collection, pystac_client.CollectionClient]:
        """
        Gets the storage STAC information for the asset as a FeatureCollection.
        One asset can contain multiple STAC items (e.g. the PAN and multispectral images).
        """
        stac_client, stac_search = self._stac_search()
        items = stac_search.item_collection()
        if not items:
            raise ValueError(f"No STAC metadata information available for this asset {self.asset_id}")
        return stac_client.get_collection(items[0].collection_id)

    @property
    @_retry
    def stac_items(self) -> pystac.ItemCollection:
        """Returns the stac items from an UP42 asset STAC representation."""
        try:
            _, stac_search = self._stac_search()
            return stac_search.item_collection()
        except Exception as exc:
            raise ValueError(f"No STAC metadata information available for this asset {self.asset_id}") from exc

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
        url = host.endpoint(f"/v2/assets/{self.asset_id}/metadata")
        payload: Dict[str, Any] = {}
        if title != NOT_PROVIDED:
            payload.update(title=title)
        if tags != NOT_PROVIDED:
            payload.update(tags=tags)
        if payload:
            self.info = self.session.post(url=url, json=payload).json()
        return self.info

    def _get_download_url(self, stac_asset_id: Optional[str] = None) -> str:
        if stac_asset_id is None:
            url = host.endpoint(f"/v2/assets/{self.asset_id}/download-url")
        else:
            url = host.endpoint(f"/v2/assets/{stac_asset_id}/download-url")
        return self.session.post(url=url).json()["url"]

    def get_stac_asset_url(self, stac_asset: pystac.Asset):
        """
        Returns the signed URL for the STAC Asset.
        Args:
            stac_asset: pystac Asset object.

        Returns:
            Signed URL for the STAC Asset.
        """
        stac_asset_id = stac_asset.href.split("/")[-1]
        return self._get_download_url(stac_asset_id=stac_asset_id)

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

        download_url = self._get_download_url()
        download = utils.download_archive if unpacking else utils.download_file
        return download(
            download_url=download_url,
            output_directory=output_directory,
        )

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
