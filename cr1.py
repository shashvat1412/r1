"""
Parking Lot System with Vehicle Class Hierarchy and Nearest Spot Allocation

This system implements a multi-floor parking lot with:
- Vehicle type-specific parking requirements
- Thread-safe operations
- Nearest spot allocation strategy
- Backward compatibility with string-based vehicle types
- Comprehensive test suite
"""

import heapq
import threading
from dataclasses import dataclass
from enum import Enum
from typing import List, Union

# region Vehicle Class Hierarchy
class Vehicle:
    """Abstract base class representing a vehicle type"""
    def spots_needed(self) -> int:
        """Return the number of consecutive parking spots required"""
        raise NotImplementedError("Subclasses must implement spots_needed")

class Car(Vehicle):
    """Represents a car vehicle type requiring 1 parking spot"""
    def spots_needed(self) -> int:
        return 1

class Bike(Vehicle):
    """Represents a bike vehicle type requiring 1 parking spot"""
    def spots_needed(self) -> int:
        return 1

class Truck(Vehicle):
    """Represents a truck vehicle type requiring 2 consecutive parking spots"""
    def spots_needed(self) -> int:
        return 2
# endregion

# region Backward Compatibility Layer
class VehicleType(Enum):
    """
    Enum for backward compatibility with string-based vehicle type specification
    Maps string identifiers to Vehicle instances
    """
    BIKE = Bike()
    CAR = Car()
    TRUCK = Truck()
# endregion

# region Core System Components
@dataclass
class SpotAssignment:
    """
    Data class representing a parking spot assignment
    Attributes:
        floor (int): Floor number of the parking spot
        spot (int): Spot number within the floor
    """
    floor: int
    spot: int

class Floor:
    """
    Represents a single floor in the parking lot with spot management
    
    Attributes:
        floor_number (int): Identifier for this floor
        available_spots (list): Min-heap of available spot numbers
        available_set (set): Set version of available spots for O(1) lookups
        lock (threading.Lock): Floor-specific lock for thread safety
    """
    
    def __init__(self, floor_number: int, spots_per_floor: int):
        """
        Initialize a parking floor with sequential spots
        
        Args:
            floor_number: Numerical identifier for this floor
            spots_per_floor: Total number of spots on this floor
        """
        self.floor_number = floor_number
        # Use min-heap to track available spots for O(1) nearest spot access
        self.available_spots = list(range(spots_per_floor))
        # Set version for efficient membership checks and updates
        self.available_set = set(self.available_spots)
        heapq.heapify(self.available_spots)  # Transform list into min-heap
        self.lock = threading.Lock()

    def _occupy_spots(self, num_spots: int) -> int:
        """
        Attempt to allocate parking spots on this floor
        
        Args:
            num_spots: Number of consecutive spots needed (1 or 2)
            
        Returns:
            int: Starting spot number if successful, -1 otherwise
        """
        with self.lock:  # Ensure thread-safe operations
            if num_spots == 1:
                # Fast path for single spot allocation using min-heap
                if not self.available_spots:
                    return -1
                spot = heapq.heappop(self.available_spots)
                self.available_set.remove(spot)
                return spot
            
            # Find first consecutive pair (slower path for trucks)
            sorted_spots = sorted(self.available_set)
            for i in range(len(sorted_spots)-1):
                if sorted_spots[i]+1 == sorted_spots[i+1]:
                    start = sorted_spots[i]
                    # Update both data structures
                    self.available_set -= {start, start+1}
                    self.available_spots = sorted(self.available_set)
                    heapq.heapify(self.available_spots)
                    return start
            return -1

    def free_spots(self, start: int, num_spots: int):
        """
        Release previously occupied spots back to available pool
        
        Args:
            start: Starting spot number to free
            num_spots: Number of consecutive spots to free
        """
        with self.lock:  # Thread-safe modification
            # Generate range of spots to free
            new_spots = set(range(start, start + num_spots))
            # Update both data structures
            self.available_set.update(new_spots)
            self.available_spots = sorted(self.available_set)
            heapq.heapify(self.available_spots)

class ParkingLot:
    """
    Main parking lot system managing multiple floors and vehicle tracking
    
    Attributes:
        floors (List[Floor]): List of Floor objects in the parking lot
        vehicle_map (dict): Mapping of license plates to their spot assignments
        lock (threading.Lock): Global lock for vehicle map operations
    """
    
    def __init__(self, num_floors: int, spots_per_floor: int):
        """
        Initialize parking lot with specified configuration
        
        Args:
            num_floors: Number of floors in the parking lot
            spots_per_floor: Number of spots per floor
        """
        self.floors = [Floor(i, spots_per_floor) for i in range(num_floors)]
        self.vehicle_map = {}
        self.lock = threading.Lock()

    def park_vehicle(self, license_plate: str, vehicle_type: Union[str, Vehicle]) -> bool:
        """
        Attempt to park a vehicle in the parking lot
        
        Args:
            license_plate: Unique vehicle identifier
            vehicle_type: Either Vehicle instance or string name
            
        Returns:
            bool: True if parking succeeded, False otherwise
        """
        # Backward compatibility layer for string-based vehicle types
        if isinstance(vehicle_type, str):
            try:
                vehicle = VehicleType[vehicle_type.upper()].value
            except KeyError:
                return False
        else:
            vehicle = vehicle_type

        with self.lock:  # Protect vehicle map operations
            if license_plate in self.vehicle_map:
                return False  # Prevent duplicate parking

            # Try each floor in order (implements nearest-floor-first strategy)
            for floor in self.floors:
                start = floor._occupy_spots(vehicle.spots_needed())
                if start != -1:
                    # Create spot assignments for tracking
                    spots = [
                        SpotAssignment(floor.floor_number, start + i)
                        for i in range(vehicle.spots_needed())
                    ]
                    self.vehicle_map[license_plate] = spots
                    return True
            return False  # No available spots found

    def leave_vehicle(self, license_plate: str) -> bool:
        """
        Remove a vehicle from the parking lot and free its spots
        
        Args:
            license_plate: License plate of vehicle to remove
            
        Returns:
            bool: True if vehicle was found and removed, False otherwise
        """
        with self.lock:  # Protect vehicle map operations
            spots = self.vehicle_map.pop(license_plate, None)
            if not spots:
                return False  # Vehicle not found

            # Free the occupied spots
            start = spots[0].spot
            floor_num = spots[0].floor
            self.floors[floor_num].free_spots(start, len(spots))
            return True

    def get_available_spots_per_floor(self, floor_number: int) -> int:
        """
        Get number of available spots on a specific floor
        
        Args:
            floor_number: Target floor number
            
        Returns:
            int: Number of available spots, or -1 for invalid floor
        """
        if 0 <= floor_number < len(self.floors):
            return len(self.floors[floor_number].available_spots)
        return -1

    def is_full(self) -> bool:
        """Check if all floors have no available spots"""
        return all(not floor.available_spots for floor in self.floors)

    def get_vehicle_location(self, license_plate: str) -> List[SpotAssignment]:
        """
        Retrieve parking location for a vehicle
        
        Args:
            license_plate: Vehicle to locate
            
        Returns:
            List[SpotAssignment]: Spot assignments or empty list if not found
        """
        return self.vehicle_map.get(license_plate, [])
# endregion

# region Test Cases
def test_park_single_car():
    """Test parking a single car on an empty floor"""
    pl = ParkingLot(1, 5)
    assert pl.park_vehicle("CAR1", "Car")
    assert pl.get_available_spots_per_floor(0) == 4
    loc = pl.get_vehicle_location("CAR1")
    assert len(loc) == 1
    assert loc[0].floor == 0 and loc[0].spot == 0  # Verify nearest spot

def test_park_truck():
    """Test parking a truck requiring consecutive spots"""
    pl = ParkingLot(1, 3)
    assert pl.park_vehicle("TRUCK1", "Truck")
    assert pl.get_available_spots_per_floor(0) == 1
    loc = pl.get_vehicle_location("TRUCK1")
    assert len(loc) == 2
    assert loc[0].spot + 1 == loc[1].spot  # Verify consecutive spots

def test_truck_fragmented_spots():
    """Test truck parking fails when only fragmented spots available"""
    pl = ParkingLot(1, 4)
    assert pl.park_vehicle("C1", "Car")
    assert pl.park_vehicle("C2", "Car")
    assert pl.park_vehicle("C3", "Car")
    pl.leave_vehicle("C2")
    assert not pl.park_vehicle("TRUCK1", "Truck")

def test_leave_invalid_vehicle():
    """Test removing non-existent vehicle returns false"""
    pl = ParkingLot(1, 10)
    assert not pl.leave_vehicle("GHOST")

def test_is_full():
    """Test full parking lot detection"""
    pl = ParkingLot(1, 1)
    pl.park_vehicle("C1", "Car")
    assert pl.is_full()

def test_free_spots():
    """Test spot freeing after vehicle departure"""
    pl = ParkingLot(1, 2)
    pl.park_vehicle("TRUCK1", "Truck")
    pl.leave_vehicle("TRUCK1")
    assert pl.get_available_spots_per_floor(0) == 2

def test_multiple_floors():
    """Test parking across multiple floors"""
    pl = ParkingLot(2, 2)
    pl.park_vehicle("C1", "Car")
    pl.park_vehicle("C2", "Car")
    pl.park_vehicle("C3", "Car")
    assert pl.get_available_spots_per_floor(0) == 0
    assert pl.get_available_spots_per_floor(1) == 1

def test_duplicate_parking():
    """Test preventing duplicate vehicle parking"""
    pl = ParkingLot(1, 2)
    assert pl.park_vehicle("C1", "Car")
    assert not pl.park_vehicle("C1", "Car")

def test_invalid_vehicle_type():
    """Test handling invalid vehicle type strings"""
    pl = ParkingLot(1, 2)
    assert not pl.park_vehicle("INVALID", "Bus")

def test_no_available_spots():
    """Test parking fails when no spots available"""
    pl = ParkingLot(1, 1)
    assert pl.park_vehicle("C1", "Car")
    assert not pl.park_vehicle("C2", "Car")

def test_zero_floors():
    """Test parking fails in lot with zero floors"""
    pl = ParkingLot(0, 5)
    assert not pl.park_vehicle("C1", "Car")

def test_zero_spots_per_floor():
    """Test parking fails in lot with zero spots per floor"""
    pl = ParkingLot(3, 0)
    assert not pl.park_vehicle("C1", "Car")

def test_mixed_case_vehicle_type():
    """Test case-insensitive vehicle type handling"""
    pl = ParkingLot(1, 3)
    assert pl.park_vehicle("CAR1", "cAr")
    assert pl.park_vehicle("TRUCK1", "tRUCK")
    assert pl.get_available_spots_per_floor(0) == 0

def test_duplicate_across_floors():
    """Test vehicle can't park twice across different floors"""
    pl = ParkingLot(2, 5)
    assert pl.park_vehicle("C1", "Car")
    assert not pl.park_vehicle("C1", "Car")

def test_truck_scattered_spots():
    """Test truck parking fails with non-consecutive spots"""
    pl = ParkingLot(1, 5)
    assert pl.park_vehicle("C1", "Car")  # Spot 0
    assert pl.park_vehicle("C2", "Car")  # Spot 1
    assert pl.park_vehicle("C3", "Car")  # Spot 2
    assert pl.park_vehicle("C4", "Car")  # Spot 3
    pl.leave_vehicle("C3")  # Free spot 2
    assert not pl.park_vehicle("TRUCK1", "Truck")

def test_spot_deallocation():
    """Test spot deallocation returns correct available spots"""
    pl = ParkingLot(1, 3)
    initial_spots = pl.get_available_spots_per_floor(0)
    assert pl.park_vehicle("C1", "Car")
    pl.leave_vehicle("C1")
    assert pl.get_available_spots_per_floor(0) == initial_spots

def stress_test():
    """Test system under high load with 900 vehicles"""
    pl = ParkingLot(10, 100)
    for i in range(900):
        assert pl.park_vehicle(f"C{i}", "Car")
    total_available = sum(pl.get_available_spots_per_floor(f) for f in range(10))
    assert total_available == 100
    for i in range(900):
        assert pl.leave_vehicle(f"C{i}")
    assert sum(pl.get_available_spots_per_floor(f) for f in range(10)) == 1000
# endregion

if __name__ == "__main__":
    # Configure test execution
    tests = [
        test_park_single_car,
        test_park_truck,
        test_truck_fragmented_spots,
        test_leave_invalid_vehicle,
        test_is_full,
        test_free_spots,
        test_multiple_floors,
        test_duplicate_parking,
        test_invalid_vehicle_type,
        test_no_available_spots,
        test_zero_floors,
        test_zero_spots_per_floor,
        test_mixed_case_vehicle_type,
        test_duplicate_across_floors,
        test_truck_scattered_spots,
        test_spot_deallocation,
        stress_test
    ]
    
    passed = 0
    failed = 0
    print("=== Parking Lot System Test Suite ===")
    
    # Execute all tests with verbose reporting
    for test_num, test in enumerate(tests, 1):
        try:
            test()
            print(f"Test {test_num:02d}: {test.__name__} - PASSED")
            passed += 1
        except AssertionError as e:
            print(f"Test {test_num:02d}: {test.__name__} - FAILED ({str(e)})")
            failed += 1
        except Exception as e:
            print(f"Test {test_num:02d}: {test.__name__} - CRASHED ({str(e)})")
            failed += 1
    
    # Final results summary
    print("\n=== Test Summary ===")
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("===================")