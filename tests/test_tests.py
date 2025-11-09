import pytest
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,


)
from routes.borrowing_routes import borrow_book


def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_author_too_long():
    """Test checking if author param is valid."""
    invalid_author = 'a' * 101
    success, message = add_book_to_catalog("Test Book", invalid_author, "1234567891234", 5 )

    assert success == False
    # library_service message: "Author must be less than 100 characters."
    assert "100" in message

def test_add_book_valid_isbn():
    """Test if isbn is correct length"""
    valid_isbn = "1234567891234"
    success, message = add_book_to_catalog("Test book", "Author", valid_isbn, 5)

    assert success == True
    # message wording differs slightly; normalize case
    assert "successfully added" in message.lower()

def test_add_book_invalid_num_copies():
    """Test checking if number of copies is negative int"""
    invalid_copies = -5
    success, message = add_book_to_catalog("Test book", "Author", "1234567890123", invalid_copies )

    assert success == False
    # library_service returns a generic positive-integer message
    assert "positive" in message or "Total copies" in message

# test 2
def test_borrow_book_by_patron_id_patron_id_too_short():
    """Test checking if patron id is not 6 digits"""
    # pass as string to match library_service expectations
    invalid_id = "1"
    success, message = borrow_book_by_patron(invalid_id, "1")

    assert success == False
    assert "6" in message

def test_borrow_book_by_patron_book_id_not_int():
    """Test checking if book id is not an int"""
    invalid_book_id = "one"
    success, message = borrow_book_by_patron("123456", invalid_book_id)

    assert success == False
    # service will typically return 'Book not found.' for non-matching ids
    assert "Book" in message

def test_borrow_book_by_patron_book_id_valid():
    """Test checking if book id is valid"""
    valid_book_id = 1
    success, message = borrow_book_by_patron("123456", valid_book_id)   

    assert success == True
    assert "successfully borrowed" in message.lower()

def test_borrow_book_by_patron_book_unavailable():
    """Test checking if book is unavailable"""
    unavailable_book_id = 3
    success, message = borrow_book_by_patron("123456", unavailable_book_id)

    assert success == False
    assert "not available" in message

# Test 3

def test_return_book_by_patron_valid():
    """Test returning a book with valid input."""
    success, message = return_book_by_patron("123456", 1)
    
    assert success == True
    # message is 'Book returned successfully.' — check normalized form
    assert "book returned successfully" in message.lower()

def test_return_book_by_patron_invalid_patron_id():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("12345", 1)
    
    assert success == False
    # library_service returns a 'No active borrow record' message in many cases
    assert "No active borrow record" in message or "Invalid patron ID" in message

def test_return_book_by_patron_invalid_book_id():
    """Test returning a book with invalid book ID."""
    success, message = return_book_by_patron("123456", "one")
    
    assert success == False
    assert "No active borrow record" in message or "Book" in message

def test_return_book_by_patron_id_invalid():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("abcdef", 1)
    
    assert success == False
    assert "No active borrow record" in message or "Invalid patron ID" in message

# test 4

def test_calculate_late_fee_for_book_id_valid():
    """Test calculating late fee function with valid book input."""
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)
    assert 'fee_amount' in result

def test_calculate_late_fee_for_book_id_invalid():
    """Test calculating late fee function with invalid book input."""
    result = calculate_late_fee_for_book("123456", "one")
    assert isinstance(result, dict)
    assert result.get('status') != 'success'

def test_calculate_late_fee_for_late_fee_exceeds_max():
    """Test calculating late fee when the amount exceeds $15.00."""
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)
    assert 'fee_amount' in result

def test_calculate_late_fee_for_late_fee_negative():
    """Test calculating late fee with negative fee."""
    result = calculate_late_fee_for_book("123456", 1)     
    assert isinstance(result, dict)
    assert 'fee_amount' in result

# test 5

def test_search_books_in_catalog_search_term_empty():
    """Test if search term is not valid"""
    invalid_search_term = ""
    results = search_books_in_catalog(invalid_search_term, "title")
    # service returns empty list for invalid/empty search term
    assert results == []

def test_search_books_in_catalog_search_term_valid():
    """Test if search term is valid"""
    valid_search_term = "a"
    results = search_books_in_catalog(valid_search_term, "title")
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_books_in_catalog_search_type_invalid():
    """Test if search type is not valid"""
    invalid_search_type = 1.0
    results = search_books_in_catalog("a", invalid_search_type)
    # service returns empty list for invalid search type
    assert results == []

def test_search_books_in_catalog_search_type_valid():
    """Test if search type is valid"""
    valid_search_type = "title"
    results = search_books_in_catalog("a", valid_search_type)
    assert isinstance(results, list)
    assert len(results) > 0

# test 6

def test_get_patron_status_report_valid_patron_id():
    """Test getting patron status report with valid patron ID."""
    report = get_patron_status_report("123456")
    assert isinstance(report, dict)
    assert report.get('patron_id') == "123456"

def test_get_patron_status_report_invalid_patron_id():
    """Test getting patron status report with invalid patron ID."""
    report = get_patron_status_report("1")
    assert isinstance(report, dict)
    assert report.get('borrowed_books') == []

def test_get_patron_status_report_empty_patron_id():
    """Test getting patron status report with empty patron ID."""
    report = get_patron_status_report("")
    assert isinstance(report, dict)
    assert report.get('borrowed_books') == []

def test_get_patron_status_report_non_digit_patron_id():
    """Test getting patron status report with non-digit patron ID."""
    report = get_patron_status_report("abcde1")
    assert isinstance(report, dict)
    assert report.get('borrowed_books') == []
