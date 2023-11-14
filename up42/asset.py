from pathlib import Path
from typing import List, Optional, Tuple, Union

import pystac
from pystac_client import Client, ItemSearch

from up42.auth import Auth
from up42.stac_client import PySTACAuthClient
from up42.utils import download_from_gcs_unpack, download_gcs_not_unpack, get_filename, get_logger

logger = get_logger(__name__)

MAX_ITEM = 50
LIMIT = 50


class Asset:
    """
    The Asset class enables access to the UP42 assets in the storage. Assets are results
    of orders or results of jobs with download blocks.

    Use an existing asset:
    ```python
    asset = up42.initialize_asset(asset_id="8c2dfb4d-bd35-435f-8667-48aea0dce2da")
    ```
    """

    def __init__(self, auth: Auth, asset_id: str, asset_info: Optional[dict] = None):
        self.auth = auth
        self.asset_id = asset_id
        self.results: Union[List[str], None] = None
        if asset_info is not None:
            self._info = asset_info
        else:
            self._info = self.info

    def __repr__(self):
        representation = (
            f"Asset(name: {self._info['name']}, asset_id: {self.asset_id}, createdAt: {self._info['createdAt']}, "
            f"size: {self._info['size']})"
        )
        if "source" in self._info:
            representation += f", source: {self._info['source']}"
        if "contentType" in self._info:
            representation += f", contentType: {self._info['contentType']}"
        return representation

    @property
    def info(self) -> dict:
        """
        Gets and updates the asset metadata information.
        """
        url = f"{self.auth._endpoint()}/v2/assets/{self.asset_id}/metadata"
        response_json = self.auth._request(request_type="GET", url=url)
        self._info = response_json
        return self._info

    @property
    def _stac_search(self) -> Tuple[Client, ItemSearch]:
        url = f"{self.auth._endpoint()}/v2/assets/stac"
        pystac_client_aux = PySTACAuthClient(auth=self.auth).open(url=url)
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
        pystac_asset_search = pystac_client_aux.search(filter=stac_search_parameters)
        return (pystac_client_aux, pystac_asset_search)

    @property
    def stac_info(self) -> Optional[pystac.Collection]:
        """
        Gets the storage STAC information for the asset as a FeatureCollection.
        One asset can contain multiple STAC items (e.g. the PAN and multispectral images).
        """
        pystac_client_aux, pystac_asset_search = self._stac_search
        resulting_item = pystac_asset_search.item_collection()
        if resulting_item is None:
            raise ValueError(f"No STAC metadata information available for this asset {self.asset_id}")
        collection_id = resulting_item[0].collection_id
        return pystac_client_aux.get_collection(collection_id)

    @property
    def stac_items(self) -> pystac.ItemCollection:
        """Returns the stac items from an UP42 asset STAC representation."""
        try:
            _, pystac_asset_search = self._stac_search
            resulting_items = pystac_asset_search.item_collection()
            return resulting_items
        except Exception as exc:
            raise ValueError(f"No STAC metadata information available for this asset {self.asset_id}") from exc

    def update_metadata(self, title: str = None, tags: List[str] = None, **kwargs) -> dict:
        """
        Update the metadata of the asset.

        Args:
            title: The title string to be assigned to the asset.
            tags: A list of tag strings to be assigned to the asset.

        Returns:
            The updated asset metadata information
        """
        url = f"{self.auth._endpoint()}/v2/assets/{self.asset_id}/metadata"
        body_update = {"title": title, "tags": tags, **kwargs}
        response_json = self.auth._request(request_type="POST", url=url, data=body_update)
        self._info = response_json
        return self._info

    def _get_download_url(self, stac_asset_id: Optional[str] = None, request_type: str = "POST") -> str:
        if stac_asset_id is None:
            url = f"{self.auth._endpoint()}/v2/assets/{self.asset_id}/download-url"
        else:
            url = f"{self.auth._endpoint()}/v2/assets/{stac_asset_id}/download-url"
        response_json = self.auth._request(request_type=request_type, url=url)
        download_url = response_json["url"]
        return download_url

    def get_stac_asset_url(self, stac_asset: pystac.Asset):
        """
        Returns the signed URL for the STAC Asset.
        Args:
            stac_asset: pystac Asset object.

        Returns:
            Signed URL for the STAC Asset.
        """
        stac_asset_id = stac_asset.href.split("/")[-1]
        # so we can utilize all functionalities of Auth class
        return self._get_download_url(stac_asset_id=stac_asset_id)

    def download(
        self,
        output_directory: Union[str, Path, None] = None,
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
        logger.info(f"Downloading asset {self.asset_id}")

        if output_directory is None:
            output_directory = Path.cwd() / f"asset_{self.asset_id}"
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download directory: {str(output_directory)}")

        download_url = self._get_download_url()
        if unpacking:
            out_filepaths = download_from_gcs_unpack(
                download_url=download_url,
                output_directory=output_directory,
            )
        else:
            out_filepaths = download_gcs_not_unpack(
                download_url=download_url,
                output_directory=output_directory,
            )

        self.results = out_filepaths
        return out_filepaths

    def download_stac_asset(
        self,
        stac_asset: pystac.Asset,
        output_directory: Union[str, Path, None] = None,
    ) -> Path:
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
        logger.info(f"Downloading STAC asset {stac_asset.title}")
        if output_directory is None:
            output_directory = Path.cwd() / f"asset_{self.asset_id}/{stac_asset.title}"
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download directory: {str(output_directory)}")
        download_url = self.get_stac_asset_url(stac_asset=stac_asset)
        file_name = get_filename(download_url, default_filename="stac_asset")
        out_file_path = output_directory / file_name
        download_gcs_not_unpack(download_url, output_directory)
        return out_file_path
