import pytest


@pytest.fixture
def mock_writer(mocker):
    """Mock writer.

    Returns a mock writer object with info, success, notice, warning, and error
    methods.
    """
    writer = mocker.Mock()
    writer.info = mocker.Mock()
    writer.success = mocker.Mock()
    writer.notice = mocker.Mock()
    writer.warning = mocker.Mock()
    writer.error = mocker.Mock()
    return writer
