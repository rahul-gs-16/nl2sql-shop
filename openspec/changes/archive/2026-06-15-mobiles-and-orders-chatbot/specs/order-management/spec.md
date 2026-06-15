## ADDED Requirements

### Requirement: Orders Table
The system SHALL store customer orders in a SQLite database table named `orders`.

#### Scenario: Orders schema creation
- **WHEN** the `create_db.py` script is executed
- **THEN** it generates an `orders` table with columns `id`, `customer_name`, `address`, `product_id`, `quantity`, `total_amount`, and `order_date`.

### Requirement: Transactional Order Processing
The system SHALL process orders using Python application logic in a single SQLite transaction.

#### Scenario: Successful order
- **WHEN** an order is placed and sufficient stock exists
- **THEN** a new row is inserted into `orders` AND the `stock` in `products` is decremented by the order quantity.

#### Scenario: Insufficient stock
- **WHEN** an order is placed but the requested quantity exceeds the available stock
- **THEN** the system rejects the order, no records are updated, and the user is informed that stock is unavailable.
