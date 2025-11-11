import pytest
from services.library_service import (
    pay_late_fees,
    refund_late_fee_payment,
)
from services.payment_service import PaymentGateway
import unittest.mock as mock

def test_pay_late_fees_success(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 5.0, "status": "success"})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "To kill a Mockingbird"})

    mock_gateway = mocker.Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")

    success, message, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success
    assert message == "Payment successful! Success"
    assert txn == "txn_123"

    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=5.0,
        description="Late fees for 'To kill a Mockingbird'"
    )


def test_pay_late_fee_payment_failure(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={})
    mocker.patch("services.library_service.get_book_by_id", 
                 return_value={"id":1, "title":"1984"})

    mock_gateway = mocker.Mock(spec=PaymentGateway)

    success , message, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert message == "Unable to calculate late fees."
    assert txn is None



def test_pay_late_fees_payment_gateway_declined(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 10.0, "status": "success"})
    mocker.patch("services.library_service.get_book_by_id", 
                 return_value={"id":2, "title":"Brave New World"})
    
    mock_gateway = mocker.Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, None, "Card declined")

    success, message, txn = pay_late_fees("123456", 2, mock_gateway)

    assert success is False
    assert message == "Payment failed: Card declined"
    assert txn is None

    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=10.0,
        description="Late fees for 'Brave New World'"
    )

def test_pay_late_fees_invalid_patron_id(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 5.0, "status": "success"})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "Lebron James Biography"})

    mock_gateway = mocker.Mock(spec=PaymentGateway)

    success, message, txn = pay_late_fees("123", 1, payment_gateway=mock_gateway)

    assert success is False
    assert message == "Invalid patron ID. Must be exactly 6 digits."
    assert txn is None

    mock_gateway.process_payment.assert_not_called()

def test_late_fee_payment_zero_late_fee(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0, "status": "success"}
                 )
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "Big Data for Dummies"})
    
    mock_gateway = mocker.Mock(spec=PaymentGateway)

    success, message, txn = pay_late_fees("123456", 1, payment_gateway=mock_gateway)

    assert success is False
    assert message == "No late fees to pay for this book."
    assert txn is None

    mock_gateway.process_payment.assert_not_called()

def test_late_fee_payment_network_error(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                    return_value={"fee_amount": 7.5, "status": "success"})
    mocker.patch("services.library_service.get_book_by_id",
                    return_value={"id": 1, "title": "Network Programming 101"})
    
    mock_gateway = mocker.Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network error")

    success, message, txn = pay_late_fees("123456", 1, payment_gateway=mock_gateway)

    assert success is False
    assert message == "Payment processing error: Network error"
    assert txn is None

    mock_gateway.process_payment.assert_called_once()
   
def test_refund_late_fee_payment_success(mocker):
    mock_gateway = mocker.Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund successful")

    success, message = refund_late_fee_payment("txn_123", 5.0, payment_gateway=mock_gateway)

    assert success is True
    assert message == "Refund successful"

    mock_gateway.refund_payment.assert_called_once_with(
        "txn_123",
        5.0
    )

    


def test_refund_late_fee_payment_invalid_transaction_id(mocker):
    mock_gateway = mocker.Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment("", 5.0, payment_gateway=mock_gateway)

    assert success is False
    assert message == "Invalid transaction ID."

    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_invalid_refund_amount_negative(mocker):
    mock_gateway = mocker.Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment("txn_123", -10.0, payment_gateway=mock_gateway)

    assert success is False
    assert message == "Refund amount must be greater than 0."

    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_invalid_refund_amount_zero(mocker):
    mock_gateway = mocker.Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment("txn_123", 0.0, payment_gateway=mock_gateway)

    assert success is False
    assert message == "Refund amount must be greater than 0."

    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_invalid_refund_amount_exceeds_maximum(mocker):
    mock_gateway = mocker.Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment("txn_123", 67.0, payment_gateway=mock_gateway)

    assert success is False
    assert message == "Refund amount exceeds maximum late fee."

    mock_gateway.refund_payment.assert_not_called()

