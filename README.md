# Parking Lot System 🚗🏍️🚚

A multi-floor parking lot system with thread-safe operations, vehicle-specific spot allocation, and comprehensive test coverage.  
**Designed for evaluations** to demonstrate OOP, concurrency, and problem-solving skills.

---

## Key Features
- **Vehicle Class Hierarchy**: Polymorphic `Vehicle` classes (Car, Bike, Truck) with type-specific spot requirements.
- **Nearest Spot Allocation**: Uses min-heap for efficient O(1) spot assignment (cars/bikes) and sorted checks for trucks.
- **Thread Safety**: Per-floor locks for concurrent operations without race conditions.
- **Backward Compatibility**: Supports both `Vehicle` objects and string-based types (e.g., "Car", "Truck").
- **Test Suite**: 17+ test cases covering edge scenarios (fragmented spots, duplicates, stress tests).

---

## Installation
1. **Requirements**:  
   Ensure Python 3.6+ is installed. No external dependencies are needed.  
   Core libraries used: `heapq`, `threading`, `dataclasses`, `enum`.

2. **Clone the Repository**:  
   ```bash
   git clone https://github.com/shashvat1412/parking-lot-system.git
