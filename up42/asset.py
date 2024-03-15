import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

import pystac
import pystac_client

from up42 import auth as up42_auth
from up42 import host, stac_client, utils

logger = utils.get_logger(__name__)

MAX_ITEM = 50
LIMIT = 50

NOT_PROVIDED = object()


class Asset:
    """
    The Asset class enables access to the UP42 assets in the storage. Assets are results
    of orders or results of jobs with download blocks.

    Use an existing asset:
    ```python
    asset = up42.initialize_asset(asset_id="8c2dfb4d-bd35-435f-8667-48aea0dce2da")
    ```
    """

    def __init__(
        self,
        auth: up42_auth.Auth,
        asset_id: Optional[str] = None,
        asset_info: Optional[dict] = None,
    ):
        if asset_id is not None and asset_info is not None:
            raise ValueError("asset_id and asset_info cannot be provided simultaneously.")
        if asset_id is None and asset_info is None:
            raise ValueError("Either asset_id or asset_info should be provided in the constructor.")

        self.auth = auth
        self.info = self._get_info(asset_id) if asset_id is not None else asset_info
        self.results: Union[List[str], None] = None

    def __repr__(self):
        return self.info.__repr__()

    @property
    def asset_id(self) -> dict:
        return self.info.get("id")

    def _get_info(self, asset_id: str):
        url = host.endpoint(f"/v2/assets/{asset_id}/metadata")
        return self.auth.request(request_type="GET", url=url)

    @property
    def _stac_search(self) -> Tuple[pystac_client.Client, pystac_client.ItemSearch]:
        url = host.endpoint("/v2/assets/stac")
        pystac_client_aux = stac_client.PySTACAuthClient(auth=self.auth).open(url=url)
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
            self.info = self.auth.request(request_type="POST", url=url, data=payload)
        return self.info

    def _get_download_url(self, stac_asset_id: Optional[str] = None, request_type: str = "POST") -> str:
        if stac_asset_id is None:
            url = host.endpoint(f"/v2/assets/{self.asset_id}/download-url")
        else:
            url = host.endpoint(f"/v2/assets/{stac_asset_id}/download-url")
        response_json = self.auth.request(request_type=request_type, url=url)
        return response_json["url"]

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
        if unpacking:
            out_filepaths = utils.download_from_gcs_unpack(
                download_url=download_url,
                output_directory=output_directory,
            )
        else:
            out_filepaths = utils.download_gcs_not_unpack(
                download_url=download_url,
                output_directory=output_directory,
            )

        self.results = out_filepaths
        return out_filepaths

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
        file_name = utils.get_filename(download_url, default_filename="stac_asset")
        out_file_path = output_directory / file_name
        utils.download_gcs_not_unpack(download_url, output_directory)
        return out_file_path
