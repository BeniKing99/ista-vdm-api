# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-11-24

### Added

- Support for accounts with multiple flats: `get_flats()`, the `flat_ids`
  property and an optional `flat_id` argument for `get_flat_info()` and
  `get_consumption_data()` (defaults to the first flat, as before)
- Cold water consumption (`Kaltwasser` section of the export) in the new
  `ConsumptionData.cold_water_consumption` field
- Unit tests for CSV parsing and flat discovery

### Fixed

- Rows of sections other than heating and hot water (such as cold water) were
  parsed as heating values and overwrote the real heating consumption

### Changed

- The `id` returned by `get_flat_info()` is now always a string

## [1.0.2] - 2026-02-23

### Fixed

- January data was not parsed when the export used the Austrian month name `Jänner`
- A 401 response while loading flat info or consumption data now raises
  `IstaVdmAuthError`, so password changes are detected

## [1.0.0] - 2025-02-10

### Added

- Initial release
- OAuth2 authentication with ista VDM portal
- Consumption data retrieval (heating and hot water)
- Flat information access (address, square meters, etc.)
- CSV parsing for consumption reports
- Async/await support throughout
- Full type hints and mypy compliance
- Comprehensive test suite
- Documentation and examples

### Features

- **Authentication**: Secure login via Keycloak OAuth2
- **Consumption Data**: Retrieve monthly heating and hot water usage
- **Flat Info**: Access property details and address information
- **Session Management**: Automatic token refresh
- **Error Handling**: Custom exceptions for auth and API errors
- **Type Safety**: Fully typed with mypy support

[Unreleased]: https://github.com/BeniKing99/ista-vdm-api/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/BeniKing99/ista-vdm-api/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/BeniKing99/ista-vdm-api/compare/v1.0.1...v1.0.2
[1.0.0]: https://github.com/BeniKing99/ista-vdm-api/releases/tag/v1.0.0