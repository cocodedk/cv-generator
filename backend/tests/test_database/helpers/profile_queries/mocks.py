"""Mock setup helpers for profile query tests."""
from unittest.mock import Mock


def setup_mock_session_for_read_write(mock_session, mock_tx_read, mock_tx_write):
    """Setup mock session to handle both read and write transactions."""

    def execute_read(work_func):
        return work_func(mock_tx_read)

    def execute_write(work_func):
        return work_func(mock_tx_write)

    mock_session.read_transaction.side_effect = execute_read
    mock_session.write_transaction.side_effect = execute_write
    mock_session.execute_read.side_effect = execute_read
    mock_session.execute_write.side_effect = execute_write


def setup_mock_session_for_write(mock_session, mock_tx):
    """Setup mock session for write-only transactions."""

    def execute_work(work_func):
        return work_func(mock_tx)

    mock_session.write_transaction.side_effect = execute_work
    mock_session.execute_write.side_effect = execute_work


def setup_mock_session_for_read(mock_session, mock_tx):
    """Setup mock session for read-only transactions."""

    def execute_work(work_func):
        return work_func(mock_tx)

    mock_session.read_transaction.side_effect = execute_work
    mock_session.execute_read.side_effect = execute_work


def create_mock_tx_with_result(result_value):
    """Create a mock transaction that returns the specified result."""
    mock_tx = Mock()
    mock_result = Mock()
    mock_result.single.return_value = result_value
    mock_tx.run.return_value = mock_result
    return mock_tx, mock_result


def create_mock_tx_with_multiple_results(result_values):
    """Create a mock transaction that returns different results for multiple calls.

    Args:
        result_values: List of result values to return in order for each tx.run() call
    """
    mock_tx = Mock()
    mock_results = []
    for result_value in result_values:
        mock_result = Mock()
        mock_result.single.return_value = result_value
        mock_result.consume.return_value = None
        mock_results.append(mock_result)
    mock_tx.run.side_effect = mock_results
    return mock_tx, mock_results
