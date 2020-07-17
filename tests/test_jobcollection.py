from pathlib import Path
import tempfile

import pytest

# pylint: disable=unused-import,wrong-import-order
from .fixtures import (
    auth_mock,
    job_mock,
    jobcollection_mock,
    auth_live,
    jobs_live,
    jobcollection_live,
)


def test_jobcollection(jobcollection_mock):
    assert len(jobcollection_mock.jobs) == 1


@pytest.mark.live
def test_job_download_result_live(jobcollection_live):
    with tempfile.TemporaryDirectory() as tempdir:
        out_files_dict = jobcollection_live.download_parallel_results(Path(tempdir))
        jobid_1, jobid_2 = jobcollection_live.jobs_id
        for _, value in out_files_dict.items():
            for p in value:
                assert Path(p).exists()
        assert jobid_1 in out_files_dict
        assert jobid_2 in out_files_dict
        assert len(out_files_dict[jobid_1]) == 2
        assert len(out_files_dict[jobid_2]) == 2
