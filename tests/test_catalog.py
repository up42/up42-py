from .fixtures import auth_mock, catalog_mock  # pylint: disable=unused-import
import up42  # pylint: disable=wrong-import-order


def test_catalog(catalog_mock):
    assert isinstance(catalog_mock, up42.Catalog)
