from pathlib import Path

from typing import Dict, List, Union

from up42.auth import Auth
from up42.tools import Tools
from up42.utils import (
    get_logger,
    download_results_from_gcs,
    download_results_from_gcs_without_unpacking,
)

logger = get_logger(__name__)


class Asset(Tools):
    def __init__(
        self,
        auth: Auth,
        asset_id: str,
    ):
        """
        The Asset class provides access to fullfilled Orders and results of select data blocks.
        """
        self.auth = auth
        self.workspace_id = auth.workspace_id
        self.asset_id = asset_id
        self.results = None
        if self.auth.get_info:
            self._info = self.info

    def __repr__(self):
        info = self.info
        return (
            f"Asset(name: {info['name']}, asset_id: {self.asset_id}, type: {info['type']}, "
            f"source: {info['source']}, createdAt: {info['createdAt']}, "
            f"size: {info['size']})"
        )

    @property
    def info(self) -> Dict:
        """
        Gets the asset metadata information.
        """
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/assets/{self.asset_id}"
        response_json = self.auth._request(request_type="GET", url=url)
        self._info = response_json["data"]
        return response_json["data"]

    @property
    def source(self) -> Dict:
        """
        Gets the source of the Asset. One of `TASKING`, `ORDER`, `BLOCK`, `UPLOAD`.
        """
        source = self.info["source"]
        logger.info(f"Asset source is {source}")
        return source

    def _get_download_url(self) -> str:
        url = f"{self.auth._endpoint()}/workspaces/{self.workspace_id}/assets/{self.asset_id}/downloadUrl"
        response_json = self.auth._request(request_type="GET", url=url)
        download_url = response_json["data"]["url"]
        return download_url

    def download(
        self, output_directory: Union[str, Path, None] = None, unpacking: bool = True
    ) -> List[str]:
        """
        Downloads the asset. Unpacking the downloaded file will happen as default.

        Args:
            output_directory: The file output directory, defaults to the current working
                directory.
            unpacking: By default the final result which is in TAR or ZIP archive format will be unpacked.

        Returns:
            List of the downloaded asset filepaths.
        """
        logger.info(f"Downloading asset {self.asset_id}")

        if output_directory is None:
            output_directory = (
                Path.cwd() / f"project_{self.auth.project_id}/asset_{self.asset_id}"
            )
        else:
            output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download directory: {str(output_directory)}")

        download_url = self._get_download_url()
        if unpacking:
            out_filepaths = download_results_from_gcs(
                download_url=download_url,
                output_directory=output_directory,
            )
        else:
            out_filepaths = download_results_from_gcs_without_unpacking(
                download_url=download_url,
                output_directory=output_directory,
            )

        self.results = out_filepaths
        return out_filepaths
