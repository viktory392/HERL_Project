import pytest
import math
from Calculator import Calculator

@pytest.fixture
def calc():
    """Fixture to initialize the Calculator instance."""
    return Calculator(items=None)

def test_quaternion_norm(calc):
    """Verify that the norm function returns a unit vector."""
    raw_q = [1.0, 1.0, 1.0, 1.0]
    normed_q = calc.QuaternionNorm(raw_q)
    
    # The magnitude of [0.5, 0.5, 0.5, 0.5] is 1.0
    magnitude = math.sqrt(sum(val**2 for val in normed_q))
    assert pytest.approx(magnitude) == 1.0
    assert normed_q == [0.5, 0.5, 0.5, 0.5]

def test_euler_to_quaternion_identity(calc):
    """Test that zero rotation returns an identity quaternion."""
    euler = [0, 0, 0]
    q = calc.EulerXYZ2Quaternion(euler)
    # Expected identity quaternion is [0, 0, 0, 1]
    assert q == [0.0, 0.0, 0.0, 1.0]

def test_round_trip_conversion(calc):
    """Verify that converting Euler -> Quaternion -> Euler returns original values."""
    original_euler = [math.pi/4, math.pi/6, math.pi/3] # 45, 30, 60 degrees
    
    q = calc.EulerXYZ2Quaternion(original_euler)
    converted_euler = calc.Quaternion2EulerXYZ(q)
    
    assert pytest.approx(converted_euler) == original_euler

def test_degree_radian_conversion(calc):
    """Test the utility functions for unit conversion."""
    degrees = [0, 90, 180]
    radians = [0, math.pi/2, math.pi]
    
    assert pytest.approx(calc.to_rad(degrees)) == radians
    assert pytest.approx(calc.to_deg(radians)) == degrees

def test_quaternion_normalization_within_euler(calc):
    """Verify that Quaternion2EulerXYZ handles non-normalized input internally."""
    # A non-normalized version of the identity quaternion
    raw_q = [0, 0, 0, 5.0] 
    euler = calc.Quaternion2EulerXYZ(raw_q)
    
    assert euler == [0.0, 0.0, 0.0]
