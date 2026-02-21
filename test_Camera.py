import pytest
from unittest.mock import MagicMock, patch
from Camera import Camera

@pytest.fixture
def camera_obj():
    return Camera()

@patch('cv2.VideoCapture')
@patch('cv2.imshow')
@patch('cv2.imwrite')
@patch('cv2.waitKey')
@patch('cv2.destroyWindow')
def test_get_image_success(
    mock_destroy, mock_wait, mock_imwrite, mock_imshow, mock_VideoCapture, camera_obj):
    """Test successful image capture logic."""
    # Setup mock camera behavior
    mock_cam = MagicMock()
    mock_VideoCapture.return_value = mock_cam
    
    # Simulate a successful frame read (True, image_data)
    mock_cam.read.return_value = (True, "fake_image_data")
    
    result_filename = camera_obj.get_image()
    
    # Assertions
    assert result_filename == "image.png"
    mock_cam.read.assert_called_once()
    mock_imwrite.assert_called_once_with("image.png", "fake_image_data")
    mock_cam.release.assert_called_once()

@patch('cv2.VideoCapture')
def test_get_image_failure(mock_VideoCapture, camera_obj, capsys):
    """Test behavior when no image is detected."""
    mock_cam = MagicMock()
    mock_VideoCapture.return_value = mock_cam
    
    # Simulate a failed frame read (False, None)
    mock_cam.read.return_value = (False, None)
    
    result_filename = camera_obj.get_image()
    
    # Check that it still returns the filename but prints an error
    captured = capsys.readouterr()
    assert "No image detected" in captured.out
    assert result_filename == "image.png"
    mock_cam.release.assert_called_once()

@patch('cv2.imshow') # Add this patch to prevent OpenCV from validating the image
@patch('cv2.VideoCapture')
def test_camera_port_selection(mock_VideoCapture, mock_imshow, camera_obj):
    """Verify the code attempts to open the correct camera port (0)."""
    mock_cam = MagicMock()
    # Return a dummy value that satisfies unpacking but doesn't need to be a real array
    mock_cam.read.return_value = (True, "dummy_frame")
    mock_VideoCapture.return_value = mock_cam
    
    # We also need to mock other cv2 calls that might crash on strings
    with patch('cv2.imwrite'), patch('cv2.waitKey'), patch('cv2.destroyWindow'):
        camera_obj.get_image()
    
    mock_VideoCapture.assert_called_with(0)
