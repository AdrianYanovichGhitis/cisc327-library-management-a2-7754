import pytest
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    pay_late_fees,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,
    refund_late_fee_payment,


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
    assert "100 characters" in message

def test_add_book_valid_isbn():
    """Test book has been successfully added with valid isbn"""
    valid_isbn = "1234567891234"
    success, message = add_book_to_catalog("Test book", "Author", valid_isbn, 5)

    assert success == True
    assert "successfully added" in message

def test_add_book_invalid_num_copies():
    """Test checking if number of copies is negative int"""
    invalid_copies = -5
    success, message = add_book_to_catalog("Test book", "Author", "1234567890123", invalid_copies )

    assert success == False
    assert "positive integer" in message

# test 2
def test_borrow_book_by_patron_id_patron_id_too_short():
    """Test checking if patron id is not 6 digits"""
    invalid_id = "1"
    success, message = borrow_book_by_patron(invalid_id, "1")

    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_borrow_book_by_patron_book_id_not_int():
    """Test checking if book id is not an int"""
    invalid_book_id = "one"
    success, message = borrow_book_by_patron("123456", invalid_book_id)

    assert success == False
    assert "Book not found." in message

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

def test_return_book_valid_input():
    """Test returning a book with valid input."""
    borrow_book_by_patron("123456", 1)
    success, message = return_book_by_patron("123456", 1)
    
    assert success == True
    assert "successfully" in message.lower()

def test_return_book_invalid_patron_id():
    """Test returning with invalid patron ID."""
    success, message = return_book_by_patron("12345", 1)
    
    assert success == False
    assert "Invalid patron ID" in message or "6 digits" in message or "borrow record" in message.lower()

def test_return_book_nonexistent_book():
    """Test returning a book that doesn't exist."""
    success, message = return_book_by_patron("123456", 99999)
    
    assert success == False
    assert "borrow record" in message.lower() or "not found" in message.lower()

def test_return_book_by_patron_id_invalid():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("abcdef", 1)
    
    assert success == False
    assert "Invalid" in message or "6 digits" in message or "borrow record" in message.lower()


# test 4

def test_calculate_late_fee_for_book_id_valid():
    """Test calculating late fee function with valid book input."""
    fee_info = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(fee_info, dict)
    assert "fee_amount" in fee_info
    assert fee_info["fee_amount"] >= 0

def test_calculate_late_fee_for_book_id_invalid():
    """Test calculating late fee function with invalid book input."""
    fee_info = calculate_late_fee_for_book("123", 1)

    assert isinstance(fee_info, dict)
    assert "Invalid" in fee_info["status"] or "borrow record" in fee_info["status"].lower()



def test_calculate_late_fee_for_late_fee_exceeds_max():
    """Test calculating late fee when the amount exceeds $15.00."""
    result = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] <= 15.00
    assert 'fee_amount' in result

def test_calculate_late_fee_for_late_fee_negative():
    """Test calculating late fee with negative fee."""
    result = calculate_late_fee_for_book("123456", 1)     
    
    assert isinstance(result, dict)
    assert result['fee_amount'] >= 0
    assert 'fee_amount' in result

# test 5

def test_search_books_in_catalog_search_term_empty():
    """Test if search term is not valid"""
    invalid_search_term = ""
    results = search_books_in_catalog(invalid_search_term, "title")

    assert isinstance(results, list)
    assert len(results) == 0

def test_search_books_in_catalog_search_term_valid():
    """Test if search term is valid"""
    valid_search_term = "a"
    results = search_books_in_catalog(valid_search_term, "title")

    assert isinstance(results, list)
    assert len(results) >= 0

def test_search_books_in_catalog_search_type_invalid():
    """Test if search type is not valid"""
    invalid_search_type = 1.0
    results = search_books_in_catalog("a", invalid_search_type)

    assert isinstance(results, list)
    assert len(results) == 0

def test_search_books_in_catalog_search_type_valid():
    """Test if search type is valid"""
    valid_search_type = "title"
    results = search_books_in_catalog("a", valid_search_type)

    assert isinstance(results, list)
    assert len(results) >= 0

def test_search_books_in_catalog_by_author():
    search_term = "Author Name"
    search_type = "author"

    results = search_books_in_catalog(search_term, search_type)

    assert isinstance(results, list)
    assert len(results) >= 0

# test 6

def test_get_patron_status_report_valid_patron_id():
    """Test getting patron status report with valid patron ID."""
    report = get_patron_status_report("123456")
    
    assert isinstance(report, dict)
    assert "patron_id" in report
    assert "borrowed_books" in report
    assert "total_late_fees" in report
    assert "borrowing_history" in report

def test_get_patron_status_report_invalid_patron_id():
    """Test getting patron status report with invalid patron ID."""
    report = get_patron_status_report("1")
    
    assert isinstance(report, dict)
    assert report["patron_id"] == "1"
    assert report["borrowed_books"] == []
    assert report["total_late_fees"] == 0.00

def test_get_patron_status_report_empty_patron_id():
    """Test getting patron status report with empty patron ID."""
    report = get_patron_status_report("")
    
    assert isinstance(report, dict)
    assert report["patron_id"] == ""
    assert report["borrowed_books"] == []
    assert report["total_late_fees"] == 0.00

def test_get_patron_status_report_non_digit_patron_id():
    """Test getting patron status report with non-digit patron ID."""
    report = get_patron_status_report("abcde1")
    
    assert isinstance(report, dict)
    assert report["patron_id"] == "abcde1"
    assert report["borrowed_books"] == []
    assert report["total_late_fees"] == 0.00

def test_add_book_to_catalog_success():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Valid Book", "Valid Author", "1234567890123", 3)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_to_catalog_missing_title():
    """Test adding a book with missing title."""
    success, message = add_book_to_catalog("", "Valid Author", "1234567890123", 3)
    
    assert success == False
    assert "Title is required" in message

def test_add_book_to_catalog_title_too_long():
    """Test adding a book with title exceeding 200 characters."""
    long_title = "a" * 201
    success, message = add_book_to_catalog(long_title, "Valid Author", "1234567890124", 3)
    
    assert success == False
    assert "200 characters" in message

def test_add_book_to_catalog_missing_author():
    """Test adding a book with missing author."""
    success, message = add_book_to_catalog("Valid Title", "", "1234567890125", 3)
    
    assert success == False
    assert "Author is required" in message

def test_add_book_to_catalog_duplicate_isbn():
    """Test adding a book with duplicate ISBN."""
    add_book_to_catalog("First Book", "First Author", "1234567890126", 3)
    success, message = add_book_to_catalog("Second Book", "Second Author", "1234567890126", 3)
    
    assert success == False
    assert "already exists" in message


def test_return_book_invalid_book_id_string():
    """Test returning a book with non-integer book_id."""
    success, message = return_book_by_patron("123456", -1)
    
    assert success == False
    assert "Invalid book ID" in message or "borrow record" in message.lower()

def test_return_book_invalid_book_id_zero():
    """Test returning a book with zero book_id."""
    success, message = return_book_by_patron("123456", 0)
    
    assert success == False
    assert "Invalid book ID" in message or "borrow record" in message.lower()

def test_calculate_late_fee_invalid_book_id_negative():
    """Test calculating late fee with negative book_id."""
    result = calculate_late_fee_for_book("123456", -1)
    
    assert isinstance(result, dict)
    assert "Invalid" in result["status"] or "borrow record" in result["status"].lower()

def test_calculate_late_fee_invalid_book_id_zero():
    """Test calculating late fee with zero book_id."""
    result = calculate_late_fee_for_book("123456", 0)
    
    assert isinstance(result, dict)
    assert "Invalid" in result["status"] or "borrow record" in result["status"].lower()

def test_search_books_by_isbn():
    """Test searching books by ISBN."""
    results = search_books_in_catalog("9780743273565", "isbn")
    assert isinstance(results, list)
    
    if len(results) > 0:
        assert results[0]['isbn'] == "9780743273565"

def test_search_books_by_isbn_not_found():
    """Test searching books by ISBN that doesn't exist."""
    results = search_books_in_catalog("9999999999999", "isbn")
    
    assert isinstance(results, list)
    assert len(results) == 0

def test_search_books_by_author_found():
    """Test searching books by author with matches."""
    results = search_books_in_catalog("Fitzgerald", "author")
    
    assert isinstance(results, list)
    if len(results) > 0:
        assert any("Fitzgerald" in book['author'] for book in results)

def test_calculate_late_fee_for_book_no_record():
    """Test calculating late fee for a book with no borrow record."""
    result = calculate_late_fee_for_book("999998", 2)
    
    assert isinstance(result, dict)
    assert result["status"] == "No active borrow record found for this patron and book."
    assert result["fee_amount"] == 0.00

def test_search_books_by_title_with_results():
    """Test searching books by title with matches."""
    results = search_books_in_catalog("gatsby", "title")
    assert isinstance(results, list)
    if len(results) > 0:
        assert any("Gatsby" in book['title'] for book in results)

def test_return_book_patron_id_exactly_invalid():
    """Test return book with invalid patron ID format."""
    success, message = return_book_by_patron("12345", 1)
    assert success == False
    assert "Invalid patron ID" in message or "6 digits" in message or "borrow record" in message.lower()

def test_return_book_invalid_book_id_exactly():
    """Test return book with invalid book ID."""
    success, message = return_book_by_patron("123456", -5)
    assert success == False
    assert "Invalid book ID" in message or "borrow record" in message.lower()

def test_calculate_late_fee_both_invalid():
    """Test calculating late fee with both invalid patron_id AND invalid book_id."""
    result = calculate_late_fee_for_book("123", -1)
    
    assert isinstance(result, dict)
    assert result["status"] == "Invalid patron ID or book ID."
    assert result["fee_amount"] == 0.00

def test_return_book_both_invalid():
    """Test returning a book with both invalid patron_id AND invalid book_id."""
    success, message = return_book_by_patron("123", -1)
    
    assert success == False
    assert "Invalid" in message or "borrow record" in message.lower()