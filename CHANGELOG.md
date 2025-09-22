# Changelog

Update your installation to the latest version with the following command:

=== "pip"

    ```bash
    pip install up42-py --upgrade
    ```

=== "conda"

    ```bash
    conda update -c conda-forge up42-py
    ```

You can check your current version with the following command:

=== "pip"

    ```bash
    pip show up42-py
    ```

=== "conda"

    ```bash
    conda search up42-py
    ```

For more information, see [UP42 Python package description](https://pypi.org/project/up42-py/).

### 2.6.0a5
**September 22, 2025**
- Deprecate `DetectionChangeSpacept` data class
- Deprecate `DetectionChangePleiadesHyperverge` data class
- Deprecate `DetectionChangeSPOTHyperverge` data class

### 2.6.0a4
**September 18, 2025**
- Added missing properties to `TaskingOrderDetails` data class.

### 2.6.0a3
**September 15, 2025**
- Security: updated urllib3 to >=2.5.0.

### 2.6.0a2
**September 10, 2025**
- Removed `description` field from `ResolutionValue`.

### 2.6.0a1
**August 27, 2025**
- Added `DetectionChangeSimularity` job template.

## 2.5.0
**August 25, 2025**

### Fixed
- Fix how collection items are retrieved in `BulkDeletion`.

### Added
- Added error message `InvalidSearchRequest` to request when `Producer::search` fails.
- Added bulk deletion of items: `BulkDeletion`.
- Added default property values for `Provider` class to simplify a host creation by name.
- Exported `Provider` class to the global `up42` namespace.
- Added a new processing job template: `UpsamplingNSSentinel`.

### Changed
- Removed `rgb` and `ned` parameters from the `UpsamplingNS` job template.
- Removed `mkdocs`, its dependencies and other unused dependencies

### 2.5.0a7
**August 18, 2025**
- Drop `mkdocs`, its dependencies and other unused dependencies

### 2.5.0a6
**August 18, 2025**
- Propagate request error message with `InvalidSearchRequest` when `Producer::search` fails.

### 2.5.0a5
**August 15, 2025**
- Fix how collection items are retrieved in `BulkDeletion`.

### 2.5.0a4
**August 6, 2025**
- Added bulk deletion of items: `BulkDeletion`.

### 2.5.0a3
**Aug 4, 2025**
- Added default property values for `Provider` class to simplify a host creation by name.
- Exported `Provider` class to the global `up42` namespace.

### 2.5.0a2
**July 25, 2025**
- Added a new processing job template: `UpsamplingNSSentinel`.

### 2.5.0a1
**July 22, 2025**
- Removed `rgb` and `ned` parameters from the `UpsamplingNS` job template.

## 2.4.0
**July 21, 2025**

### Deprecated
- Deprecated the `webhooks` module and the `base::get_credits_balance` function.

### Added
- Added a warning when outdated versions are imported.
- Added `provider_properties` data field to `glossary::Scene` active record class.
- Added `FeasibilityStudy` active record class to `tasking` module.
- Exported `FeasibilityStudy` and `FeasibilityStudySorting` to `up42` namespace.

### 2.4.0a4
**July 16, 2025**
- Display warning when importing outdated versions

### 2.4.0a3
**July 15, 2025**
- Deprecated the `webhooks` module and the `base::get_credits_balance` function

### 2.4.0a2
**July 07, 2025**
- Added `provider_properties` data field to `glossary::Scene` active record class.

### 2.4.0a1
**July 04, 2025**
- Added `FeasibilityStudy` active record class to `tasking` module.
- Exported `FeasibilityStudy` and `FeasibilityStudySorting` to `up42` namespace.

## 2.3.1
**June 26, 2025**

### Fixed
- `Up42ExtensionProperty` for order id

### Security
- Updated requests dependency to 2.32.4
- Updated tornado dependency to 6.5.1

### Deprecated
- `Order.get_assets`

## 2.3.0
**June 10, 2025**

### Added
- Added `CoregistrationJobTemplate` process template to allow running coregistration-simularity

### Deprecated
- Deprecated `Asset.get`
- Deprecated `Asset.all`
- Deprecated `Asset.stac_items` in favour of `pystac::Client.get_items`
- Deprecated `Asset.stac_info`
- Deprecated `Asset.file` in favour of `pystac::Asset.file`
- Deprecated `Asset.download` in favour of `pystac::Asset.file.download`

## 2.2.0
**Apr 29, 2025**
### Added
- Validate process exists after `JobTemplate` initialisation
- Added sorting fields to `QuotationSorting`.
- Added `region` as an optional input type to `base::authenticate` with the possible values being `eu` and `sa`
- When authenticating the region gets set globally and used in `host::user_info_endpoint`, `host::token_endpoint`, `host::endpoint` accordingly
- Added `up42` property to `pystac::Item` and `pystac::Collection` to get and set UP42 STAC extensions data.
- Added `update` extension method to `pystac::Item`.
- Publish `stac_client` function to `up42` namespace.
- Added `file` property to `Asset` class to unify with `pystac::Asset` experience.
- Use unauthenticated session for signed url image file in `FileProvider` module with `FileProvider` class.
- Experiment `stac` module with `FileProvider` descriptor for `pystac::Asset`.
- Added STAC object dynamic extension on `up42` import.
- Added `Asset::save` method.
- Added model fields to `Asset` class.
- Added coverage for `Asset::all` method.
- Exported `AssetSorting` to `up42` namespace.
- Enabled access to authenticated image files via extraction session to a parameter.
- Generalized downloadable images to `ImageFile` in `utils` module.
- Added `quicklook` property to `Scene` class.
- Added `is_host` property to `Provider` class.
- Added `search` method to `Provider` class.
- Added `schema` property to `DataProduct` class.
- Added `Quotation` active record to `tasking` module.
- Exported `Quotation` and `QuotationSorting` to `up42` namespace.
- Added `order_template` module with `BatchOrderTemplate` and supporting classes.
- Add missing properties to `Order` data class and auxiliary classes.
- Introduced `Order::all` method to filter and list orders.
- Added `Order::get` class method as part of conversion to active record pattern.
- Added `Order::track` method.

### Changed

- Adjust `Provider::search` to allow `start_date` and `end_date`, combine them and add to payload as datetime
- Adjust `Order` representation to remove redundant fields.
- Adjust `BatchOrderTemplate` to exclude tags from the payload when not provided, preventing `400 Bad Request` errors from the API.
- Update `AssetSorting` with possible sorting fields
- Adjust `FileProvider::_get_` to check href url that starts with the current region base api url.
- Updated feasibility endpoint URL.
- Relax dependency constraint to allow geopandas 1.0.1.
- Switched to using stac client descriptor in `Asset` class and reduced duplication.
- Made `BatchOrderTemplate::tags` optional.
- Converted `Asset` to a data class with `get` and `all` methods.
- Simplified `Catalog::download_quicklooks` to use `ImageFile` class internally.
- Simplified `CatalogBase::estimate_order` to a static method.
- Simplified `CatalogBase::place_order` to a class method.
- Modified `Storage::get_orders` testing to eliminate dependency on order data.
- Modified `up42::initialize_order` testing to eliminate dependency on order data.
- Modified `CatalogBase::place_order` testing to eliminate dependency on order data.
- Converted `Order` to dataclass.
- Extended `Order::order_details` to cover archive orders as well.

### Deprecated
- Deprecated `Asset::download` method in favour of `Asset.file::download`.
- Deprecated `Asset::download_stac_asset` in favour of `pystac::Asset.file::download`.
- Deprecated `Asset::get_stac_asset_url` in favour of `pystac::Asset.file.url`.
- Deprecated `up42::initialize_tasking`.
- Deprecated `Tasking::get_feasibility`.
- Deprecated `Tasking::choose_feasibility`.
- Deprecated `Asset::update_metadata` in favour of `pystac::Item.update`.
- Deprecated `Asset.asset_id` in favour of `Asset.id`.
- Deprecated `up42::initialize_catalog` since all `Catalog` and `CatalogBase` methods are deprecated.
- Deprecated `Storage::get_assets` in favour of `Asset::all`.
- Deprecated `up42::initialize_asset` in favour of `Asset::get`.
- Deprecated `up42::initialize_storage`.
- Deprecated `Catalog::download_quicklooks` in favour of `Provider::search`.
- Deprecated `Catalog::construct_search_parameters` in favour of `Provider::search`.
- Deprecated `Catalog::search` in favour of `Provider::search`.
- Deprecated `Tasking::get_quotations` in favour of `Quotation::all`.
- Deprecated `Tasking::decide_quotation` in favour of `Quotation` class methods.
- Deprecated `Tasking.construct_order_parameters` in favour of `BatchOrderTemplate`.
- Deprecated `Catalog.construct_order_parameters` in favour of `BatchOrderTemplate`.
- Deprecated `CatalogBase::estimate_order` in favour of `BatchOrderTemplate.estimate`.
- Deprecated `CatalogBase::place_order` in favour of `BatchOrderTemplate::place`.
- Deprecated `Order::estimate` in favour of `BatchOrderTemplate.estimate`.
- Deprecated `Order::place` in favour of `BatchOrderTemplate::place`.
- Deprecated `CatalogBase::get_data_product_schema` in favour of `DataProduct.schema`.
- Deprecated `up42::initiliaze_order` in favour of `Order::get`.
- Deprecated `Order.order_id` in favour of `Order.id`.
- Deprecated `Order.order_details` in favour of `Order.details`.
- Deprecated `Storage::get_orders` method.
- Deprecated `Order::track_status` method.

### Removed
- Remove deprecated viz dependencies.
- Reduced test dependencies on `Asset` structure.
- Dropped eager loading of `Order::info`.
- Dropped `Order::__repr__` in favour of native dataclass implementation.

### Fixed
- Fix authenticated download in `Catalog::download_quicklooks`.
- Fixed `Order::place` method to retrieve order info via additional call and not from response.

## 2.2.0a33
**Apr 9, 2025**
- Adjust `Provider::search` to allow `start_date` and `end_date`, combine them and add to payload as `datetime`

## 2.2.0a32
**Apr 2, 2025**
- Adjust Order representation to remove redundant fields.

## 2.2.0a31
**Apr 1, 2025**
- Adjust `BatchOrderTemplate` to exclude tags from the payload when not provided, preventing 400 Bad Request errors from the API.

## 2.2.0a30
**Mar 28, 2025**
- Validate process exists after `JobTemplate` initialisation

## 2.2.0a29
**Mar 27, 2025**
- Update `AssetSorting` with possible sorting fields

## 2.2.0a28
**Mar 27, 2025**
- Drop `Asset::save` method
- Adjust deprecation message in `Asset::update_metadata` to indicate `pystac::Item.update`.

## 2.2.0a27
**Mar 24, 2025**
- Adjust `FileProvider::_get_` to check href url that starts with the current region base api url.

## 2.2.0a26
**Mar 20, 2025**
- Updated feasibility endpoint URL.

## 2.2.0a25
**Mar 19, 2025**
- Added sorting fields to `QuotationSorting`.

## 2.2.0a24

**Mar 14, 2025**
- Added `region` as an optional input type to `base::authenticate` with the possible values being `eu` & `sa`
- When authenticating the region gets set globally and used in `host::user_info_endpoint`, `host::token_endpoint`, `host::endpoint` accordingly

## 2.2.0a23
**Mar 13, 2025**
- Remove deprecated viz dependencies.

## 2.2.0a22
**Jan 17, 2025**
- Relax dependency constraint to allow geopandas 1.0.1.

## 2.2.0a21
**Jan 16, 2025**
- Added `up42` property to `pystac::Item` and `pystac::Collection` to get and set UP42 STAC extensions data.

## 2.2.0a20
**Jan 9, 2025**
- Added `update` extension method to `pystac::Item`.

## 2.2.0a19
**Dec 20, 2024**
- Switched to using stac client descriptor in `Asset` class and reduced duplication.
- Publish `stac_client` function to `up42` namespace.
- Added `file` property to `Asset` class to unify with `pystac::Asset` experience.
- Deprecated `Asset::download` method in favour of `Asset.file::download`.

## 2.2.0a18
**Dec 19, 2024**
- Use unauthenticated session for signed url image file in `FileProvider` module with `FileProvider` class.

## 2.2.0a17
**Dec 19, 2024**
- Experiment `stac` module with `FileProvider` descriptor for `pystac::Asset`.
- Added STAC object dynamic extension on `up42` import.
- Deprecated `Asset::download_stac_asset` in favour of `pystac::Asset.file::download`.
- Deprecated `Asset::get_stac_asset_url` in favour of `pystac::Asset.file.url`.

## 2.2.0a16
**Dec 19, 2024**
- Made `BatchOrderTemplate::tags` optional.
- Deprecated `up42::initialize_tasking`.
- Deprecated `Tasking::get_feasibility`.
- Deprecated `Tasking::choose_feasibility`.

## 2.2.0a15
**Dec 19, 2024**
- Added `Asset::save` method.
- Deprecated `Asset::update_metadata` in favour of `Asset::save`.

## 2.2.0a14
**Dec 19, 2024**
- Added model fields to `Asset` class.
- Deprecated `Asset.asset_id` in favour of `Asset.id`.
- Deprecated `up42::initialize_catalog` since all `Catalog` and `CatalogBase` methods are deprecated.

## 2.2.0a13
**Dec 19, 2024**
- Added coverage for `Asset::all` method.
- Exported `AssetSorting` to `up42` namespace.
- Reduced test dependencies on `Asset` structure.

## 2.2.0a12
**Dec 19, 2024**
- Converted `Asset` to a data class with `get` and `all` methods.
- Fix authenticated download in `Catalog::download_quicklooks`.
- Deprecated `Storage::get_assets` in favour of `Asset::all`.
- Deprecated `up42::initialize_asset` in favour of `Asset::get`.
- Deprecated `up42::initialize_storage`.

## 2.2.0a11
**Dec 19, 2024**
- Enabled access to authenticated image files via extraction session to a parameter.

## 2.2.0a10
**Dec 18, 2024**
- Generalized downloadable images to `ImageFile` in `utils` module.
- Added `quicklook` property to `Scene` class.
- Deprecated `Catalog::download_quicklooks` in favour of `Provider::search`.
- Simplified `Catalog::download_quicklooks` to use `ImageFile` class internally.

## 2.2.0a9
**Dec 18, 2024**
- Added `is_host` property to `Provider` class.
- Added `search` method to `Provider` class.
- Deprecated `Catalog::construct_search_parameters` in favour of `Provider::search`.
- Deprecated `Catalog::search` in favour of `Provider::search`.
- Simplified `CatalogBase::estimate_order` to a static method.
- Simplified `CatalogBase::place_order` to a class method.

## 2.2.0a8
**Dec 18, 2024**
- Added `schema` property to `DataProduct` class.
- Modified deprecation of `CatalogBase::get_data_product_schema` in favour of `DataProduct.schema`.

## 2.2.0a7
**Dec 18, 2024**
- Added `Quotation` active record to `tasking` module.
- Exported `Quotation` and `QuotationSorting` to `up42` namespace.
- Deprecated `Tasking::get_quotations` in favour of `Quotation::all`.
- Deprecated `Tasking::decide_quotation` in favour of `Quotation` class methods.

## 2.2.0a6
**Dec 18, 2024**
- Added `order_template` module with `BatchOrderTemplate` and supporting classes.
- Deprecated `Tasking.construct_order_parameters` in favour of `BatchOrderTemplate`.
- Deprecated `Catalog.construct_order_parameters` in favour of `BatchOrderTemplate`.
- Deprecated `CatalogBase::estimate_order` in favour of `BatchOrderTemplate.estimate`.
- Deprecated `CatalogBase::place_order` in favour of `BatchOrderTemplate::place`.
- Deprecated `Order::estimate` in favour of `BatchOrderTemplate.estimate`.
- Deprecated `Order::place` in favour of `BatchOrderTemplate::place`.
- Deprecated `CatalogBase::get_data_product_schema`.

## 2.2.0a5
**Dec 17, 2024**
- Deprecated `up42::initiliaze_order` in favour of `Order::get`.
- Add missing properties to `Order` data class and auxiliary classes.
- Deprecated `Order.order_id` in favour of `Order.id`.
- Deprecated `Order.order_details` in favour of `Order.details`.

## 2.2.0a4
**Dec 17, 2024**
- Modified `Storage::get_orders` testing to eliminate dependency on order data.

## 2.2.0a3
**Dec 17, 2024**
- Introduced `Order::all` method to filter and list orders.
- Deprecated `Storage::get_orders` method.

## 2.2.0a2
**Dec 17, 2024**
- Fixed `Order::place` method to retrieve order info via additional call and not from response.
- Modified `up42::initialize_order` testing to eliminate dependency on order data.
- Modified `CatalogBase::place_order` testing to eliminate dependency on order data.

## 2.2.0a1
**Dec 17, 2024**
- Converted `Order` to dataclass.
- Dropped eager loading of `Order::info`.
- Added `Order::get` class method as part of conversion to active record pattern.
- Extended `Order::order_details` to cover archive orders as well.
- Dropped `Order::__repr__` in favour of native dataclass implementation.
- Added `Order::track` method and deprecated `Order::track_status` method.

## 2.1.1
**Dec 10, 2024**

### Changed
- Restore accepting string instead of enum in `Storage::get_orders`.
- Improve coverage for `Tasking::decide_quotation`.
- Improve coverage for `Tasking::get_feasibility`.
- Improve coverage for `Tasking::choose_feasibility`.
- Updating endpoint for `base::get_credits_balance`.
- Switched workspace id retrieval from the deprecated endpoint to the user info endpoint.
- Added requesting `openid` scope when retrieving token.
- Move `tests/fixtures/fixtures_globals.py` to `tests/constants.py`.
- Move `collection_credentials` from `auth.py` to `client.py`.
- Switched to base descriptors in `Storage` class and drop the dependencies from `auth.py` module.

### Fixed
- Fixed bug with passing enum entries instead of values in `Storage::get_orders`.
- Fixed `Catalog::construct_search_parameters` `limit` description in the documentation.
- Fixed paging bug for case of empty response.
- Fixed confusing name for type `FeasibilityDecision` to `FeasibilityStatus`.
- Fixed test coverage for `Tasking::get_quotations`.
- Fixed test coverage for `Tasking::construct_order_parameters`.
- Fixed types of `Asset::asset_id` and `Asset::_get_info`.
- Unified paging between `Order`, `Tasking` and `Storage` classes.

### Removed
- Drop process template `DetectionTreesHeightsSpacept`.
- Dropped limiting false statuses in `Storage::get_orders` since the type hinting is enabled.
- Dropped failing wrong `sortby` value in `Storage::get_orders` since the type hinting is enabled.
- Dropped `Tasking::auth` property.
- Dropped legacy `auth.py`.
- Dropped legacy fixtures for storage test coverage.
- Dropped `asset_searcher.py` module.
- Dropped unused `Auth::request` and the corresponding test coverage.
- Dropped unneeded `Storage::__repr__`.
- Dissolve `auth.Auth` in `_Workspace::authenticate`.

## 2.1.1a13

**Dec 4, 2024**
- Move `tests/fixtures/fixtures_globals.py` to `tests/constants.py`.
- Move constants used in a single test module to the corresponding module.

## 2.1.1a12

**Dec 3, 2024**
- Drop process template `DetectionTreesHeightsSpacept`.

## 2.1.1a11

**Dec 2, 2024**
- Added requesting `openid` scope when retrieving token.
- Switched workspace id retrieval from the deprecated endpoint to the user info endpoint.

## 2.1.1a10

**Dec 2, 2024**
- Remove duplication of workspace mocking in tests.
- Remove duplication of setting raising session in tests.
- Move `collection_credentials` from `auth.py` to `client.py`.
- Dissolve `auth.Auth` in `_Workspace::authenticate`.
- Drop legacy `auth.py`.

## 2.1.1a9

**Nov 29, 2024**
- Restore accepting string instead of enum in `Storage::get_orders`.

## 2.1.1a8

**Nov 28, 2024**
- Dropped legacy fixtures for storage test coverage.
- Unified paging between `Order`, `Tasking` and `Storage` classes.
- Fixed paging bug for case of empty response.
- Dropped `asset_searcher.py` module.
- Switched to base descriptors in `Storage` class and drop the dependencies from `auth.py` module.
- Dropped unused `Auth::request` and the corresponding test coverage.
- Dropped unneeded `Storage::__repr__`.
- Dropped limiting false statuses in `Storage::get_orders` since the type hinting is enabled.
- Fixed bug with passing enum entries instead of values in `Storage::get_orders`.
- Dropped failing wrong `sortby` value in `Storage::get_orders` since the type hinting is enabled.

## 2.1.1a7

**Nov 28, 2024**
- Drop legacy fixtures for order testing.
- Delete unused mocking data.
- Fix confusing name for type `FeasibilityDecision` to `FeasibilityStatus`.

## 2.1.1a6

**Nov 27, 2024**
- Drop `Tasking::auth` property.
- Improve coverage for `Tasking::decide_quotation`.
- Improve coverage for `Tasking::get_feasibility`.
- Improve coverage for `Tasking::choose_feasibility`.
- Drop legacy test fixtures.

## 2.1.1a5

**Nov 25, 2024**
- Fix test coverage for `Tasking::get_quotations`.

## 2.1.1a4

**Nov 18, 2024**
- Updating endpoint for `base::get_credits_balance`.

## 2.1.1a3

**Oct 29, 2024**
- Fix `Catalog::construct_search_parameters` `limit` description in the documentation.

## 2.1.1a2

**Oct 28, 2024**
- Fix test coverage for `Tasking::construct_order_parameters`.

## 2.1.1a1

**Oct 28, 2024**
- Fix types of `Asset::asset_id` and `Asset::_get_info`.

## 2.1.0

**Oct 9, 2024**
### Added
- Moving `estimate_order` method to `CatalogBase` class.
- `Order.get_assets` now allows to get assets from orders in `BEING_FULFILLED` state.

### Fixed
- Fix test coverage for `Catalog`, `Order`, and `Asset` classes.

### Changed
- Switch to `workspace_id` descriptor in `CatalogBase`.
- Switch `Asset` and `Order` classes to use `session` descriptor.
- Remove `utils::autocomplete_order_parameters` and inline to `Catalog::construct_order_parameters` and `Tasking::construct_order_parameters`.
- Make `CatalogBase::type` mandatory.
- Drop `CatalogBase::auth` and introduce `Tasking::auth` for backwards compatibility.
- Drop `Tasking::__repr__`.
- Switch `OrderParamsV2` as output type for `_translate_construct_parameters` in order module.
- Switch `OrderParams` as input type for `CatalogBase::place` and `Catalog::estimate` from `Optional[dict]`.
- Changed `Order::status` type from `str` to `Literal`.
- Changed `Order::track_status` report_time input type to float.

## 2.1.0a12

**Oct 8, 2024**
- Make `CatalogBase::type` mandatory.
- Drop `CatalogBase::auth` and introduce `Tasking::auth` for backwards compatibility.
- Switch to `workspace_id` descriptor in `CatalogBase`.
- Drop `Tasking::__repr__`.

## 2.1.0a11

**Oct 8, 2024**
- Moving `estimate_order` method to `CatalogBase` class.

## 2.1.0a10

**Oct 8, 2024**
- Fix test coverage for `Catalog::download_quicklooks`.

## 2.1.0a9

**Oct 7, 2024**
- Fix test coverage for `Catalog::construct_order_parameters`.

## 2.1.0a8

**Sep 26, 2024**
- Fix test coverage for `Catalog::search`.

## 2.1.0a7

**Sep 25, 2024**
- Fix test coverage for `Catalog::construct_search_parameters`.

## 2.1.0a6

**Sep 25, 2024**
- Fix test coverage for `CatalogBase` class.

## 2.1.0a5

**Sep 20, 2024**
- Remove `utils::autocomplete_order_parameters` and inline to `Catalog::construct_order_parameters` and `Tasking::construct_order_parameters`.

## 2.1.0a4

**Sep 11, 2024**
- `Order.get_assets` now allows to get assets from orders in `BEING_FULFILLED` state.
- Switch `Order` class to use `session` descriptor.
- Set `OrderParams` as input type for `CatalogBase::place` and `Catalog::estimate` from `Optional[dict]`.
- Added `OrderParamsV2` as output type for `_translate_construct_parameters` in order module.
- Changed `Order::status` type from `str` to `Literal`.

## 2.1.0a3

**Sep 10, 2024**
- Switch `Asset` class to use `session` descriptor.
- Improve test coverage `Asset` class.

## 2.1.0a2

**Sep 2, 2024**
- Fix test coverage for `Order::estimate`, `Order::place`, and `Order::track_status` methods.
- Change `Order::track_status` report_time input type to float.

## 2.1.0a1

**Aug 30, 2024**
- Improve test coverage `Order` class.

## 2.0.1

**Aug 15, 2024**

- Switch `ProductGlossary::IntegrationValue` from `Enum` to `Literal`.
- Fixed `FEASIBILITY_STUDY_MAY_BE_REQUIRED` value in the `glossary.IntegrationValue` Literal.


## 2.0.1a3

**Aug 15, 2024**

- Fixed `FEASIBILITY_STUDY_MAY_BE_REQUIRED` in the `glossary.IntegrationValue` Literal.

## 2.0.1a2

**Aug 13, 2024**

- Extract `IntegrationValue` type alias.


## 2.0.1a1

**Aug 13, 2024**

- Switch `ProductGlossary::IntegrationValue` from `Enum` to `Literal`.

## 2.0.0

**Aug 8, 2024**

### Changed
- **Breaking:** Switch to the new product glossary V2 endpoint in `ProductGlossary::get_collections`.
- **Breaking:** Updated `Collection` class in `catalog.py` to match new `ProductGlossary` endpoints.
- Moved `ProductGlossary` and its dependencies to `glossary.py`.
- Published `CollectionType` in the global namespace.

### Removed
The following deprecated code was dropped (**Breaking**):

- Functions in `up42` global namespace
  - `initialize_webhook`
  - `get_webhooks`
  - `create_webhook`
  - `get_webhook_events`

  in `CatalogBase` class
  - keyword arguments in `place_order` method - used to pass arguments `scene` and `geometry`

  in `Catalog` class
  - keyword arguments in `estimate_order` method - used to pass arguments `scene` and `geometry`
  - `sortby` and `ascending` arguments in `construct_search_parameters` method
  - `acquired_after`, `acquired_before`, `geometry` and `custom_filter` arguments in `get_assets` method
  in `Webhook` class
  - `info` and `webhook_id` properties
  - `update` and `create` methods
  - `return_json` argument in `all` method.

- Dropped `ProductGlossary` classes `Producer` and `Host` in `catalog.py`.
- Dropped `processing_templates.AugmentationSpacept`.


## 2.0.0a5

**Aug 7, 2024**
- Moved `ProductGlossary` and its dependencies to `glossary.py`.
- Published `CollectionType` in the global namespace.

## 2.0.0a4

**Aug 6, 2024**
The following deprecated code was dropped:
- Functions in `up42` global namespace
  - `initialize_webhook`
  - `get_webhooks`
  - `create_webhook`
  - `get_webhook_events`
- in `CatalogBase` class
  - keyword arguments in `place_order` method - used to pass arguments `scene` and `geometry`
- in `Catalog` class
  - keyword arguments in `estimate_order` method - used to pass arguments `scene` and `geometry`
  - `sortby` and `ascending` arguments in `construct_search_parameters` method
  - `acquired_after`, `acquired_before`, `geometry` and `custom_filter` arguments in `get_assets` method
- in `Webhook` class
  - `info` and `webhook_id` properties
  - `update` and `create` methods
  - `return_json` argument in `all` method.

## 2.0.0a3

**Aug 06, 2024**
- Switch to the new product glossary V2 endpoint in `ProductGlossaty::get_collections`.
- Updated `Collection` class in `catalog.py` to match new `ProductGlossary` endpoints.
- Dropped `ProductGlossary` classes `Producer` and `Host` in `catalog.py`.

## 2.0.0a2

**Jul 31, 2024**
- Dropped `processing_templates.AugmentationSpacept`.

## 2.0.0a1

**Jul 31, 2024**
- Dropped `ProductGlossary::get_data_products` and switched to `ProductGlossary::get_collections` in dependencies.

## 1.1.1

**Jul 31, 2024**
### Changes
- Added EULA acceptance check to processing job templates.
- Added EULA related statuses to processing jobs.
- Added various failure statuses to job tracking stop list.
- Added `session` descriptor to `CatalogBase`.
- Deprecated `get_data_products` method in `CatalogBase` class.
- Extract `CollectionType` type alias.
- Extract `ProductGlossary` in `catalog.py`.
- Provide type hints for `ProductGlossary` methods.
- Switch to new token endpoint in `auth.py` and `oauth.py`.

### Fixes
- Fix type hint for `get_webhook_events`.

### Improvements
- Drop unused `return_text` parameter in `Auth::request`.
- Improve test coverage for `Catalog::search`.
- Improve `Catalog::download_quicklooks` code.
- Improve test coverage for `Catalog::download_quicklooks` type alias.
- Reduce the usage `auth::request` in `base.py`.
- Simplify the usage of `get_data_products` in `CatalogBase`.
- Simplify pagination in `Catalog::search` code.
- Use token duration information from token data instead of static configuration.
- Use expiry offset to refresh token 30s earlier.

### Dependencies:
- Bumped dependencies `certifi` from 2024.2.2 to 2024.7.4.
- Bumped dependencies `setuptools` from 69.1.1 to 70.0.0.
- Bumped dependencies `urllib` from 2.2.1 to 2.2.2.
- Bumped dependencies `zipp` from 3.17.0 to 3.19.1.

## 1.1.1a11

**Jul 30, 2024**
- Added EULA acceptance check to processing job templates.
- Added various failure statuses to job tracking stop list.
- Added EULA related statuses to processing jobs.

## 1.1.1a10

**Jul 29, 2024**
- Deprecated `get_data_products` method in `CatalogBase` class.

## 1.1.1a9

**Jul 17, 2024**
- Bumped dependencies `zipp` from 3.17.0 to 3.19.1.

## 1.1.1a8

**Jul 17, 2024**
- Bumped dependencies `setuptools` from 69.1.1 to 70.0.0.

## 1.1.1a7

**Jul 16, 2024**
- Simplify pagination in `Catalog::search` code.
- Improve test coverage for `Catalog::search`.

## 1.1.1a6

**Jul 15, 2024**
- Improve `Catalog::download_quicklooks` code.
- Improve test coverage for `Catalog::download_quicklooks` type alias.
- Drop unused `return_text` parameter in `Auth::request`.
- Add `session` descriptor to `CatalogBase`.

## 1.1.1a5

**Jul 15, 2024**
- Extract `CollectionType` type alias.

## 1.1.1a4

**Jul 15, 2024**
- Extract `ProductGlossary` in `catalog.py`.
- Provide type hints for `ProductGlossary` methods.
- Simplify the usage of `get_data_products` in `CatalogBase`.
- Fix type hint for `get_webhook_events`.
- Reduce the usage `auth::request` in `base.py`.


## 1.1.1a3

**Jul 8, 2024**
- Bumped dependencies `certifi` from 2024.2.2 to 2024.7.4.

## 1.1.1a2

**Jul 8, 2024**

- Bumped dependencies `urllib` from 2.2.1 to 2.2.2.

## 1.1.1a1

**Jun 27, 2024**

- Switch to new token endpoint in `auth.py` and `oauth.py`.
- Use token duration information from token data instead of static configuration.
- Use expiry offset to refresh token 30s earlier.

## 1.1.0

**Jun 25, 2024**

### Changes

- `Job`, `JobSorting` and `JobStatus` classes now available in `up42` namespace.
- Change default created and credits ordering as descending.
- Change default status ordering to descending.
- Rename `templates.py` to `processing_templates.py`.

### Fixes

- Fix multiple process id value query parameter to use concatenation with commas.
- Fix multiple status value query parameter to use concatenation with commas.
- Fix processing job tracking to wait until credits are captured or released.
- Fix missing process ids for processing templates.

### Improvements

- Trim off milliseconds in job metadata timestamps to avoid rounding errors.
- Trim nanoseconds in job metadata timestamps since not supported by native Python datetime.
- Update processing template names.
- Add missing `workspace_id` query param to job execution.
- Convert relative paths in processing job page links to absolute ones.

## 1.1.0a7

**Jun 20, 2024**

- Trim off milliseconds in job metadata timestamps to avoid rounding errors.
- Fix multiple process id value query parameter to use concatenation with commas.
- Change default created and credits ordering as descending.

## 1.1.0a6

**Jun 20, 2024**

- Trim nanoseconds in job metadata timestamps since not supported by native Python datetime.
- Fix processing job tracking to wait until credits are captured or released.
- Fix multiple status value query parameter to use concatenation with commas.
- Change default status ordering to descending.

## 1.1.0a5

**Jun 20, 2024**

- Update processing template names.

## 1.1.0a4

**Jun 19, 2024**

- Add missing workspace id query param to job execution.

## 1.1.0a3

**Jun 19, 2024**

- Export `JobStatus` in `up42` namespace.

## 1.1.0a2

**Jun 18, 2024**

- Convert relative paths in processing job page links to absolute ones.

## 1.1.0a1

**Jun 18, 2024**

- Export `Job` and `JobSorting` in `up42` namespace.
- Fix missing process ids for processing templates.
- Rename `templates.py` to `processing_templates.py`.

## 1.0.4

**Jun 17, 2024**

## New Features

### Processing Module:
- Introduced the `Job` class for interacting with processing jobs.
- Implemented job querying capabilities (processing.py).
- Added a collection attribute to the `Job` class.
- Introduced processing job tracking.

### Job Templates:
- Created basic single and multi-item processing job templates in templates.py.
- Enabled job template execution (templates.py).
- Added specialized templates for `SpaceptAugmentation`, `NSUpsamling`, and `Pansharpening`.
- Added cost evaluation to the JobTemplate class (number comparison).
- Implemented `SingleItemJobTemplate` and `MultiItemJobTemplate` helper classes.

## Improvements

### Base Module (formerly main):
- Renamed the `main` module to `base` for clarity.
- Added descriptors: `Session`, `WorkspaceId`, and `StacClient` to `base` module for improved access within classes.

### Webhooks:
- Refactored webhooks as active records.
- Consolidated webhook code into a dedicated module/class.
- Enhanced test coverage for webhooks.
- Deprecated legacy webhook code.

## Dependencies:
- Updated requests to 2.32.0.
- Relaxed geopandas version constraint to < 1.
- Upgraded tornado to 6.4.1.

## Bugfixes:
- Enabled deep copy in Up42Auth for compatibility.
- Fix `tenacity not Found` Error by upgrading `tenacity` dependency.
- Removed deprecated Catalog::construct_parameters method.

## 1.0.4a21

**Jun 17, 2024**

- Support deep copy in `Up42Auth` to be compliant with pystac client.
- Align processing job query parameter names.

## 1.0.4a20

**Jun 17, 2024**

- Added processing job tracking.
- Upgrade tenacity.

## 1.0.4a19

**Jun 13, 2024**

- Added errors and credits retrieval to processing jobs.

## 1.0.4a18

**Jun 13, 2024**

- Deprecate legacy webhook code.
- Drop long deprecated `Catalog::construct_parameters`.

## 1.0.4a17

**Jun 13, 2024**

- Added `collection` to job class in processing module.
- Added `StacClient` descriptor to base module.

## 1.0.4a16

**Jun 11, 2024**

- Added job querying to `processing.py`

## 1.0.4a15

**Jun 11, 2024**

- Added job template execution to `templates.py`

# 1.0.4a14

**Jun 10, 2024**

- Added class `Job` to `processing` module to access processing job features.

## 1.0.4a13

**June 10, 2024**
- Allow dependency `geopandas` from 0.13.2 to any version less than `1`.

## 1.0.4a12

**Jun 10, 2024**

- Bumped dependencies `tornado` from 6.4 to 6.4.1.

## 1.0.4a11

**Jun 10, 2024**

- Added job templates for `SpaceptAugmentation`, `NSUpsamling`, `Pansharpening` to `templates.py`

## 1.0.4a10

**Jun 7, 2024**

- Added simple single and multi item processing job templates to `templates.py`

## 1.0.4a9

**Jun 7, 2024**

- Added cost evaluation to `JobTemplate` class with number comparison support.

## 1.0.4a8

**Jun 6, 2024**

- Added module `processing.py` with base `JobTemplate` class with post-construct inputs validation.
- Added helper `SingleItemJobTemplate` and `MultiItemJobTemplate` classes as bases for future specific processing templates.

## 1.0.4a7

**May 30, 2024**

- Moved instance methods of `Webhooks` class to class methods of `Webhook` class and dropped the former.

## 1.0.4a6

**May 30, 2024**

- Remodeled webhook as active record.

## 1.0.4a5

**May 30, 2024**

- Move webhooks related code from `base.py`

## 1.0.4a4

**May 29, 2024**

- Delegated webhook repr to its info
- Improved test coverage for webhooks
- Dropped unneeded shared and global fixtures for webhook tests


## 1.0.4a3

**May 27, 2024**

- Added `Session` and `WorkspaceId` descriptors to provide access to session and workspace_id from other classes.
- Renaming `main` module to `base`.


## 1.0.4a2

**May 24, 2024**

- Added workspace singleton in `main.py`, encapsulating global state (auth, workspace id).
- Inject auth and workspace id instead of passing a containing object.


## 1.0.4a1

**May 24, 2024**
- Bumped dependencies `requests` from 2.31.0 to 2.32.0.

## 1.0.3

**May 23, 2024**
- Added tenacity as dependency.
- Added resilience on `asset::stac_info` and `asset::stac_items`
- Dropped pystac client subclassing
- Cleaned up fixtures
- Improved test coverage
- Dropped unneeded exposure of token

## 1.0.3a1

**May 23, 2024**
- Added tenacity as dependency.
- Added resilience on `asset::stac_info` and `asset::stac_items`
- Dropped pystac client subclassing
- Cleaned up fixtures
- Improved test coverage
- Dropped unneeded exposure of token


## 1.0.2

**May 15, 2024**
- Added thread safety to token retrieval.


## 1.0.2a1

**May 15, 2024**
- Added thread safety to token retrieval.


## 1.0.1

**May 13, 2024**
- Increased retries and backoff in http resilience.
- Fixed bug with temporary storage overfill when downloading archives.
- Bumped dependencies jinja2, tqdm, geojson.

## 1.0.1a4

**May 13, 2024**
- geojson dependency bumped from 3.0.1 to 3.1.0 to fix conda python 3.12 installer.


## 1.0.1a3

**May 7, 2024**
- Setting http_adapter default configuration to `retries = 5` and `backoff factor = 1`


## 1.0.1a2

**May 7, 2024**
- Renamed `download_from_gcs_unpack` to `download_archive`
- Renamed `download_gcs_not_unpack` to `download_file`
- Improved test coverage for `download_archive`
- Bug fix in `download_archive`: use output directory provided for temporary archive storage instead of default temp folder


## 1.0.1a1

**May 7, 2024**
- jinja2 dependency bumped from 3.1.3 to 3.1.4.
- tqdm dependency bumped from 4.66.2 to 4.66.3.


## 1.0.0

**Apr 17, 2024**
- Dropped deprecated functionalities: Jobs, Projects, Workflows, Viztools
- Dropped deprecated code related to blocks


## 1.0.0a7

**Apr 16, 2024**
- Dropped `get_blocks`, `get_block_details` and `get_block_coverage` from `main.py`

## 1.0.0a6

**Apr 16, 2024**
- Dropped project id and api key based authentication in `main.py`, `auth.py`, `http/oauth.py` and `http/client.py`
- Adapted tests and fixtures
- Dropped viztools.py

## 1.0.0a5

**Apr 16, 2024**

- Dropped deprecated Workflow functions - info, workflow_tasks, get_workflow_tasks, get_parameters_info,
 _get_default_parameters (internal function), _construct_full_workflow_tasks_dict (internal function),
 get_jobs, delete
- Dropped Workflow tests and fixtures

## 1.0.0a4

**Apr 15, 2024**

- Dropped deprecated Jobtask functions - info, get_results_json, download_results, download_quicklooks
- Dropped Jobtask tests and fixtures

## 1.0.0a3

**Apr 15, 2024**

- Dropped deprecated Job functions - info, status, is_succeeded, download_quicklooks, get_results_json, download_results,
get_logs, upload_results_to_bucket, get_jobtasks, get_jobtasks_results_json, get_credits
- Dropped Job tests and fixtures

## 1.0.0a2

**Apr 15, 2024**

- Dropped deprecated JobCollection functions - info, status, apply, download_results
- Dropped deprecated Project functions - info, get_workflows, get_project_settings, get_jobs
- Dropped Project's fixtures and tests
- Dropped JobCollection's fixtures and tests
- Dropped Workflow's get_jobs function

## 1.0.0a1

**Apr 15, 2024**

- Dropped deprecated viztools functions: folium_base_map(), plot_quicklooks(), plot_coverage(), draw_aoi(), _map_images() (internal function), map_quicklooks(), plot_coverage(), plot_results(), requires_viz() (internal function), map_results(), render() (internal function)

## 0.37.2

**Apr 8, 2024**

Dependabot security updates:
 - Bump black from 22.12.0 to 24.3.0
 - Bump pillow from 10.2.0 to 10.3.0

## 0.37.1

**Apr 5, 2024**

- Removed upper bound for Python 3.12.
- Dropped support for Python 3.8.
- New authentication token are retrieved upon expiration instead of every request.
- Dropped tenacity, requests-oauthlib and types-oauthlib as dependencies.
- Updated the deprecation date for `Jobs`, `Workflow`, and `Projects` related features.
- Multiple refactoring improvements.

## 0.37.1a11

**Apr 4, 2024**

- Added standard headers to `http/session.py`
- Added session provisioning to `auth.py` and `http/client.py`
- Dropped undocumented `authenticate` flag in `auth.py`
- Dropped undocumented kwargs in `auth.py` and `main.py`

## 0.37.1a10

**Apr 3, 2024**

- Updating the deprecation date for `Jobs`, `Workflow`, and `Projects` related features.

## 0.37.1a9

**Apr 2, 2024**

- Dropped legacy `estimation.py`, `test_estimation.py` and `fixtures_estimation.py`

## 0.37.1a8

**March 28, 2024**

- Dependency injection and test coverage improvement in `auth.py`

## 0.37.1a7

**March 27, 2024**

- Raise typed error if token retrieval fails due to wrong credentials.

## 0.37.1a6

**March 26, 2024**

- Switched to using `http.client.Client` in `auth.py` for authentication and token management
- Dropped unneeded resiliency code
- Dropped tenacity, requests-oauthlib and types-oauthlib as unneeded dependencies


## 0.37.1a5

**March 21, 2024**

- Run test pipeline on Python versions 3.9 to 3.12
- Removed upper bound for Python 3.12
- Dropped support for Python 3.8


## 0.37.1a4

**March 21, 2024**

- New http stack client to provide resilient token and requests compliant authentication.


## 0.37.1a3

**March 20, 2024**

- Detection of token retriever based on supplied settings.


## 0.37.1a2

**March 19, 2024**

- Detection of credentials settings based on supplied credentials.


## 0.37.1a1

**March 19, 2024**

- Dropped all the live tests.


## 0.37.0

**March 15, 2024**

- Fixed inadvertent title and tags removals during asset metadata updates.
- Dropped unneeded `auth::env` property and the corresponding tests.
- Generalized new authentication stack to cover account authentication case.
- Added new components within the HTTP layer to facilitate future enhancements in authentication and request processes.
- Adjusted most of the code in accordance with pylint checks.


## 0.37.0a14

**March 15, 2024**

- Fixed inadvertent titles and tags removals during asset metadata updates.

## 0.37.0a13

**March 15, 2024**

- Dropped unneeded `auth::env` property and the corresponding tests.


## 0.37.0a12

**March 14, 2024**

- Adjusted `initialization.py`, `test_initialization.py`, `main.py` and `test_main.py` in accordance with Pylint checks.


## 0.37.0a11

**March 14, 2024**

- Adjusted `asset.py`, `asset_searcher.py`, `test_asset.py` and `fixtures_asset.py` in accordance with Pylint checks.
- Adjusted `test_http_adapter.py` in accordance with Pylint checks.
- Dropped `test_e2e_catalog.py` since it is covered by SDK tests.
- Fixed a flaky test in `test_session.py`


## 0.37.0a10

**March 13, 2024**

- Adjusted `webhooks.py`, `test_webhooks.py` and `fixtures_webhook.py` in accordance with Pylint checks.
- Dropped `test_e2e_30sec.py` since it covers functionality dropped earlier.

## 0.37.0a9

**March 13, 2024**

- Adjusted `macros.py`, `utils.py`, and `test_utils.py` in accordance with Pylint checks.


## 0.37.0a8

**March 13, 2024**

- Adjusted `estimation.py`, `test_estimation.py` and `fixtures_estimation.py` in accordance with Pylint checks.


## 0.37.0a7

**March 13, 2024**

- Adjusted `order.py`, `test_order.py` and `fixtures_order.py` in accordance with Pylint checks.


## 0.37.0a6

**March 13, 2024**

- Adjusted `host.py`, `tools.py`, `test_tools.py`, `storage.py`, `test_storage.py` and `fixtures_storage.py` in accordance with Pylint checks.

## 0.37.0a5

**March 11, 2024**

- Adjusted `auth.py` and `oauth.py` with their coverage and fixtures in accordance with Pylint checks.
- Adjusted `conftest.py` in accordance with Pylint checks.


## 0.37.0a4

**March 07, 2024**

- Generalized new authentication stack to cover account authentication case.

## 0.37.0a3

**March 07, 2024**

- Adjusted `tasking.py`, `test_tasking.py`, and `fixtures_tasking.py` in accordance with Pylint checks.

## 0.37.0a2

**March 06, 2024**

- Adjusted `catalog.py` and `test_catalog.py` in accordance with Pylint checks.
- Conducted minor refactoring in other classes due to changes in function names within the authentication module.


## 0.37.0a1

**March 06, 2024**

- Added a new component within the HTTP layer to facilitate future enhancements in authentication and request processes: ported a resilient and authenticated cached session.


## 0.37.0a0

**March 04, 2024**

Added new components within the HTTP layer to facilitate future enhancements in authentication and request processes:

- Ported the HTTP adapter, providing configurable resilience.
- Ported resilient project authentication, managing token expiration.

## 0.36.0

**February 20, 2024**

- Updated the `place_order()` and `estimate_order()` functions of the CatalogBase class to the latest version of the API.

## 0.35.0

**January 25, 2024**

- Discontinued support for the following edit and create functions:

    - up42:
        - `validate_manifest()`

    - Project:
        - `max_concurrent_jobs`
        - `update_project_settings()`
        - `create_workflow()`

    - Workflow:
        - `max_concurrent_jobs`
        - `update_name()`
        - `add_workflow_tasks()`
        - `get_compatible_blocks()`
        - `get_parameters_info()`
        - `construct_parameters()`
        - `construct_parameters_parallel()`
        - `estimate_job()`
        - `test_job()`
        - `test_jobs_parallel()`
        - `run_job()`
        - `run_jobs_parallel()`

    - Job:
        - `track_status()`
        - `cancel_job()`

- Marked the following visualization functions as deprecated:

    - up42:
        - `viztools.folium_base_map()`

    - Catalog:
        - `plot_coverage()`
        - `map_quicklooks()`
        - `plot_quicklooks()`

    - Job:
        - `map_results()`
        - `plot_results()`

    - JobCollection:
        - `map_results()`
        - `plot_results()`

    - JobTask:
        - `map_results()`
        - `plot_results()`
        - `plot_quicklooks()`

    They will be discontinued after March 31, 2024.


## 0.34.1

**December 15, 2023**

- Restored the `order.get_assets` function.

## 0.34.0

**December 13, 2023**

- Updated the `storage.get_orders` function to the latest version of the API.
- Set Poetry as the only dependency manager.
- Discontinued support for the `order.get_assets` function.

## 0.33.1

**November 23, 2023**

Marked the following parameters of `storage.get_assets` as deprecated to enforce the use of the PySTAC client search.

- `geometry`
- `acquired_before`
- `acquired_after`
- `custom_filter`

## 0.33.0

**November 14, 2023**

- Updated authentication by changing it from project-based to account-based.
- Added a new function to the Asset class: `get_stac_asset_url` generates a signed URL that allows to download a STAC asset from storage without authentication.

## 0.32.0

**September 7, 2023**

A new function added to the Asset class:

- `download_stac_asset` allows you to download STAC assets from storage.

## 0.31.0

**August 9, 2023**

- Supported STAC assets in `asset.stac_items`.
- Added substatuses to `order.track_status`.
- Limited `catalog.search(sort_by)` to `acquisition_date` only.
- Removed `get_credits_history` from the main class.
- `asset.stac_info` now returns the `pystac.Collection` object.
- Python 3.7 is no longer supported.

## 0.30.1

**July 14, 2023**

Fixed the failing construct_order_parameters function and updated tests.

## 0.30.0

**July 3, 2023**

Added a new `tags` argument to the following functions:

- `construct_order_parameters`, to assign tags to new tasking and catalog orders.
- `get_order`, to filter orders by tags.
- `get_assets`, to filter assets by tags.

## 0.29.0

**June 20, 2023**

Integrated new functions into the Tasking class:

- `get_feasibility` — Returns a list of feasibility studies for tasking orders.
- `choose_feasibility` — Allows accepting one of the proposed feasibility study options.
- `get_quotations` — Returns a list of all quotations for tasking orders.
- `decide_quotation` — Allows accepting or rejecting a quotation for a tasking order.

## 0.28.1

**April 6, 2023**

- Updating test to latest version

## 0.28.0

**February 17, 2023**

- Added STAC search functionality to storage.get_assets.
  Now you can filter assets by new parameters: `geometry`, `acquired_after`, `acquired_before`,
  `collection_names`, `producer_names`, `tags`, `search`, `sources`.
- Added storage.pystac_client.
  Use it to authenticate PySTAC client to access your UP42 storage assets using its library.
- Added asset.stac_info.
  Use it to access STAC metadata, such as acquisition, sensor, and collection information.

## 0.27.1

**January 26, 2023**

- Improve error communication of functions using API v2 endpoints.
- add `up42.__version__` attribute to access the package version with Python.
- Adapt asset class attributes (`created` to `createdAt`) to UP42 API.

## 0.27.0

**December 12, 2022**

- Add `asset.update_metadata()` for adjusting title & tags of an asset.
- `storage.get_assets()` has new parameters `created_after`, `created_before`, `workspace_id`  to better filter the
  desired assets. It now queries the assets of all accessible workspaces by default.
- Adopt new UP42 API 2.0 endpoints for user storage & assets.

## 0.26.0

**November 2, 2022**

- Remove Python version upper bound, this will enable immediate but untested installation with any new Python version.
- Changes to `workflow.construct_parameters`:
  - Deprecates the `assets` parameter (list of asset objects), instead use `asset_ids` (list of asset_ids).
  - Removes limitation of using only assets originating from blocks, now also supports assets from catalog &
    tasking.
  - In addition to required parameters, now adds all optional parameters that have default values.
- `tasking.construct_order_parameters` now accepts a Point feature (e.g. use with Blacksky).
- Fix: `get_data_products` with `basic=False` now correctly returns only tasking OR catalog products.
- The up42 object now correctly does not give access to third party imports anymore (restructured init module).

## 0.25.0

**October 25, 2022**

- Add dedicated tasking class for improved handling of satellite tasking orders.
- `construct_order_parameters` now also adds the parameters specific to the selected data-product, and suggests
  possible values based on the data-product schema.

## 0.24.0

**October 20, 2022**

- Add `catalog.get_data_product_schema()` for details on the order parameters
- Switches parameter `sensor` to `collection` in `catalog.download_quicklooks`.
- Various small improvements e.g. quicklooks automatic band selection, Reduced use of default parameters in
  constructor methods, error message display, optimized API call handling for parameter validation etc.
- Internal: Separation of Catalog and CatalogBase to prepare addition of Tasking class, reorganize test fixtures.

## 0.23.1

**October 5, 2022**

- Fixes issue with filename of downloaded assets containing two suffix `.` e.g. `./output..zip`.
  Resolves [#350](https://github.com/up42/up42-py/issues/350)

## 0.23.0

**September 20, 2022**

- Integrates the UP42 data productsm e.g. the selection "Display" and "Reflectance" configuration in the ordering process. The new ordering process requires the selection of a specific data product.
- The `order_parameters` argument for `catalog.estimate_order` and `catalog.place_order` now has a different structure.
  **The previous option to just specify the collection name will soon be deactivated in the UP42 API!**
- New function `catalog.get_data_products`
- New function `catalog.construct_order_parameters`
- `catalog.construct_search_parameters` replaces `catalog.construct_parameters` which is deprecated and will be
  removed in v0.25.0

## 0.22.2

**July 21, 2022**

- Fix unpacking of order assets if no output topfolder inherent in archive

## 0.22.1

**July 19, 2022**

- Fix conda release (include requirements-viz file)

## 0.22.0

**July 5, 2022**

- Adds webhooks functionality to the SDK, see new webhooks docs chapter.
- Introduces optional installation option for the visualization functionalities. The required dependencies are now
  not installed by default.
- Removes `order.metadata` property, as removed from UP42 API.
- Fix: Using a MultiPolygon geometry in construct_parameters will now correctly raise an error as not accepted.
- Documentation overhaul & various improvements

## 0.21.0

**May 12, 2022**

- Adding `up42.get_balance` and `up42.get_credits_history` features for allowing account information retrieval.
- Adding `up42.get_block_coverage` features for retrieval of the catalog blocks' coverage as GeoJSON.
- `project.get_jobs` now has sorting criteria, sorting order and limit parameters.
- Catalog search now enables search for Pleiades Neo etc. (uses host specific API endpoints)
- Fix: `project.get_jobs` now correctly queries the full number of jobs.

## 0.20.2

**April 10, 2022**

- Update documentation
- Non functional changes to enable conda release
- Update requirements and removing overlapping subdependencies

## 0.20.1

**April 5, 2022**

- Update documentation for latest changes on the user console.
- Remove outdated examples.
- Add required files on the dist version for allowing creation of conda meta files.

## 0.20.0

**February 15, 2022**

- Enables getting credits consumed by a job via `job.get_credits`.

## 0.19.0

**January 28, 2022**

- Add support for UP42 data collections via `catalog.get_collections`.
- Switch `catalog.construct_parameters` to use `collection` instead of `sensor` for
  the collection selection.
- Refactor retry mechanism. Resolves issue of unintended token renewals & further limits
  retries.

## 0.18.1

**December 20, 2021**

- Allow installation with Python 3.9

## 0.18.0

**November 10, 2021**

- Add sorting criteria, sorting order and results limit parameters to `storage.get_orders`
  and `storage.get_assets`. Now also uses results pagination which avoids timeout issues
  when querying large asset/order collections.
- Significant speed improvement for:
    -`.get_jobs`, `.get_workflows`, `.get_assets`, `.get_orders` calls.
    - `workflow.create_workflow` when used with `existing=True`.
    - Printing objects representations, which now does not trigger additional object info API calls.
- Removal: Removes deprecated handling of multiple features as input geometry in `.construct_parameters`
  Instead, using multiple features or a MultiPolygon will now raise an error.
  This aligns the Python SDK with the regular UP42 platform behaviour.
- Removal: Remove the Python SDK Command Line Interface.
- Fix: JobTask.info and the printout now uses the correct jobtask information.

## 0.17.0

**September 10, 2021**

- Adds `usage_type` parameter for selection of "DATA" and "ANALYTICS" data in catalog search.
- Adds automatic handling of catalog search results pagination when requesting more
  than 500 results.
- Adds support for datetime objects and all iso-format compatible time strings to
  `construct_parameters`.
- Fix: `get_compatible_blocks` with an empty workflow now returns all data blocks.
- Start deprecation for `handle_multiple_features` parameter in `construct_parameters` to
  guarantee parity with UP42 platform. In the future, the UP42 SDK will only handle
  single geometries.
- Uses Oauth for access token handling.

## 0.16.0

**June 30, 2021**

- Limit memory usage for large file downloads (#237)
- Remove deprecated job.get_status() (Replace by job.status) (#224)
- Remove deprecated jobcollection.get_job_info() and jobcollection.get_status() (Replaced by jobcollection.info and jobcollection.status)
- Remove order-id functionality (#228)
- Limit installation to Python <=3.9.4
- Internal code improvements (e.g. project settings, retry)

## 0.15.2

**April 7, 2021**

- Enables plotting of jobcollection with `.map_results()`.
- Fixes `.cancel_job()` functionality.

## 0.15.1

**March 12, 2021**

- Fixes breaking API change in catalog search.
- Catalog search result now contains a `sceneId` property instead of `scene_id`.

## 0.15.0

**January 27, 2021**

- Add `Storage`, `Order` and `Asset` objects.
- Add possibility to create orders from `Catalog` with `Catalog.place_order`.
- Add possibility to use assets in job parameters with `Workflow.construct_paramaters`.
- Update job estimation endpoint.
- Multiple documentation fixes.

## 0.14.0

**December 7, 2020**

- Add `workflow.estimate_job()` function for estimation of credit costs & job duration before running a job.
- Add `bands=[3,2,1]` parameter in `.plot_results()` and `.map_results()` for band & band order selection.
- `.plot_results()` now accepts kwargs of [rasterio.plot.show](https://rasterio.readthedocs.io/en/latest/api/rasterio.plot.html#rasterio.plot.show) and matplotlib.
- Add `up42.initialize_jobcollection()`
- Add `get_estimation=False` parameter to `workflow.test_job`.
- Add ship-identification example.
- Overhaul "Getting started" examples.

## 0.13.1

**November 18, 2020**

- Handle request rate limits via retry mechanism.
- Limit `map_quicklooks()` to 100 quicklooks.
- Add aircraft detection example & documentation improvements.

## 0.13.0

**October 30, 2020**

- New consistent use & documentation of the basic functionality:
    - All [basic functions](up42-reference.md) (e.g. `up42.get_blocks`) are accessible
        from the `up42` import object. Now consistently documented in the `up42`
        [object code reference](up42-reference.md).
    - The option to use this basic functionality from any lower level object will soon be
        removed (e.g. `project.get_blocks`, `workflow.get_blocks`). Now triggers a deprecation warning.
- The plotting functionality of each object is now documented directly in that [object's code reference](job-reference.md).
- Fix: Repair catalog search for sobloo.
- *Various improvements to docs & code reference.*
- *Overhaul & simplify test fixtures.*
- *Split off viztools module from tools module.*

## 0.12.0

**October 14, 2020**

- Simplify object representation, also simplifies logger messages.
- Add `.info` property to all objects to get the detailed object information, deprecation process for `.get_info`.
- Add `.status` property to job, jobtask and jobcollection objects. Deprecation process for `.get_status`.
- Add selection of job mode for `.get_jobs`.
- Add description of initialization of each object to code reference.
- Fix: Use correct cutoff time 23:59:59 in default datetimes.
- Fix: Download jobtasks to respective jobtask subfolders instead of the job folder.
- Unpin geopandas version in requirements.
- Move sdk documentation to custom subdomain "sdk.up42.com".
- *Simplify mock tests & test fixtures*

## 0.11.0

**August 13, 2020**

- Fix: Remove buffer 0 for fixing invalid geometry.
- Add `.map_quicklooks` method for visualising quicklooks interactively.
- Add an example notebook for mapping quicklooks using `.map_quicklooks` method.

## 0.10.1

**August 13, 2020**

- Hotfix: Fixes usage of multiple features as the input geometry.

## 0.10.0

**August 7, 2020**

- Add parallel jobs feature. Allows running jobs for multiple geometries, scene_ids or
 timeperiods in parallel. Adds `workflow.construct_parameters_parallel`,
 `workflow.test_job_parallel`, `workflow.run_job_parallel` and the new `JobCollection` object.
- Adjusts `workflow.get_jobs` and `project.get_jobs` to return JobCollections.
- Adjusts airports-parallel example notebook to use the parallel jobs feature.
- Adjusts flood mapping example notebook to use OSM block.
- Adds option to not unpack results in `job.download_results`.
- Now allows passing only scene_ids to `workflow.construct_parameters`.
- Improves layout of image results plots for multiple results.
- Added binder links.
- Now truncates log messages > 2k characters.
- *Various small improvements & code refactorings.*

## 0.9.3

**July 15, 2020**

- Add support for secondary GeoJSON file to `job.map_results`

## 0.9.2

**July 4, 2020**

- Fix inconsistency with `job.map_results` selecting the JSON instead of the image

## 0.9.1

**June 25, 2020**

- Fixes typo in catalog search parameters

## 0.9.0

**May 7, 2020**

- Enable block_name and block_display_name for `workflow.add_workflow_tasks`
- Replace requirement to specify provider by sensor for `catalog.download_quicklooks`
- Add option to disable logging in `up42.settings`
- Add `project.get_jobs` and limit `workflow.get_jobs` to jobs in the workflow.
- Fix download of all output files
- Job name selectabable in `workflow.test_job` and `workflow.run_job` (with added suffix _py)
- Fix CRS issues in make `job.map_results`, make plotting functionalities more robust

## 0.8.3

**April 30, 2020**

- Pin geopandas to 0.7.0, package requires new CRS convention

## 0.8.2

**April 24, 2020**

- Removed `job.create_and_run_job`, now split into `job.test_job` and `job.run_job`
