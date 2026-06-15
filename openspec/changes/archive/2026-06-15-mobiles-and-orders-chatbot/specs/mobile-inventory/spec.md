## ADDED Requirements

### Requirement: Store Apple Mobile Devices
The system SHALL store Apple iPhone inventory data in a SQLite database table named `products`.

#### Scenario: Database schema creation
- **WHEN** the `create_db.py` script is executed
- **THEN** it generates a `products` table with columns: `id`, `model`, `variant`, `color`, `storage`, `stock`, `price`.

### Requirement: Predefined Options
The system SHALL restrict inventory seeding to specific pre-defined options.

#### Scenario: Color options
- **WHEN** seeding the database
- **THEN** only 'Black', 'White', 'Blue', and 'Pink' are used as colors.

#### Scenario: Storage options
- **WHEN** seeding the database
- **THEN** Standard models use 128GB, 256GB, or 512GB, and Pro/Pro Max models use 256GB, 512GB, or 1TB.

### Requirement: Approximate Pricing
The system SHALL use approximate real-world pricing for seeded products.

#### Scenario: Price assignment
- **WHEN** seeding the database
- **THEN** realistic prices (e.g., ~$799 for base models) are applied.
