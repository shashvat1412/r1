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

## Usage 

# Initialize a parking lot with 3 floors and 10 spots per floor
parking_lot = ParkingLot(num_floors=3, spots_per_floor=10)

# Park a car
parking_lot.park_vehicle("KA-01-1234", "Car")

# Park a truck (requires 2 consecutive spots)
parking_lot.park_vehicle("MH-02-5678", "Truck")

# Check available spots on floor 0
print(parking_lot.get_available_spots_per_floor(0))

# Remove a vehicle
parking_lot.leave_vehicle("KA-01-1234")

# Check if the parking lot is full
print(parking_lot.is_full())

Design Highlights

    OOP Principles:

        Vehicle class hierarchy for extensibility.

        Floor class encapsulates spot management (heap + set for efficiency).

    Concurrency:

        Per-floor locks allow parallel operations across floors.

        Global lock protects the vehicle_map for thread-safe lookups.

    Efficiency:

        Min-heap ensures nearest-spot-first allocation.

        Set operations for O(1) membership checks.

Testing

Run all test cases (included in cr1.py):
bash
Copy

python cr1.py

Sample Tests:

    test_park_truck(): Validates consecutive spot allocation.

    test_truck_fragmented_spots(): Ensures trucks reject non-consecutive spots.

    stress_test(): Simulates 900 vehicles to validate scalability.

Contribution

Contributions are welcome! Open an issue or PR for:

    Adding new vehicle types (e.g., ElectricCar).

    Implementing a CLI/API interface.
