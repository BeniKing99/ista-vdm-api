# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/BeniKing99/ista-vdm-api/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/BeniKing99/ista-vdm-api/releases/tag/v1.0.0