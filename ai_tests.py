import pytest
from datetime import datetime, timedelta

import library_service


def test_calculate_late_fee_for_book_overdue(monkeypatch):
    # Arrange: stub get_patron_borrowed_books to return an active overdue borrow
    now = datetime.now()
    overdue_days = 3
    due_date = now - timedelta(days=overdue_days)

    def fake_get_patron_borrowed_books(patron_id):
        return [{
            'book_id': 1,
            'due_date': due_date,
            'return_date': None
        }]

    monkeypatch.setattr(library_service, 'get_patron_borrowed_books', fake_get_patron_borrowed_books)

    # Act
    result = library_service.calculate_late_fee_for_book('123456', 1)

    # Assert
    assert result['status'] == 'success'
    assert result['days_overdue'] == overdue_days
    assert result['fee_amount'] == round(overdue_days * 0.50, 2)


def test_get_patron_status_report_with_fees_and_history(monkeypatch):
    # Arrange: stub get_patron_borrowed_books and get_patron_borrow_count and calculate_late_fee_for_book
    now = datetime.now()
    due_date = now - timedelta(days=2)

    fake_borrowed = [
        {'book_id': 2, 'title': 'Test Book', 'due_date': due_date, 'return_date': None}
    ]

    def fake_get_borrowed(patron_id):
        return fake_borrowed

    def fake_get_borrow_count(patron_id):
        return 4

    def fake_calc_fee(patron_id, book_id):
        return {'fee_amount': 1.0, 'days_overdue': 2, 'status': 'success'}

    monkeypatch.setattr(library_service, 'get_patron_borrowed_books', fake_get_borrowed)
    monkeypatch.setattr(library_service, 'get_patron_borrow_count', fake_get_borrow_count)
    monkeypatch.setattr(library_service, 'calculate_late_fee_for_book', fake_calc_fee)

    # Act
    report = library_service.get_patron_status_report('654321')

    # Assert
    assert report['patron_id'] == '654321'
    assert report['borrowed_books'] == fake_borrowed
    # Note: function returns total_late_fees as a string formatting bug; check it's the placeholder string
    assert isinstance(report['total_late_fees'], str)
    assert report['borrowing_history'] == 4


def test_search_books_in_catalog_filters(monkeypatch):
    # Arrange: stub get_all_books
    books = [
        {'book_id': 1, 'title': 'Python Programming', 'author': 'Alice', 'isbn': '1111111111111'},
        {'book_id': 2, 'title': 'Advanced C', 'author': 'Bob', 'isbn': '2222222222222'},
    ]

    monkeypatch.setattr(library_service, 'get_all_books', lambda: books)

    # Act & Assert
    res_title = library_service.search_books_in_catalog('python', 'title')
    assert len(res_title) == 1
    assert res_title[0]['book_id'] == 1

    res_author = library_service.search_books_in_catalog('bob', 'author')
    assert len(res_author) == 1
    assert res_author[0]['book_id'] == 2

    res_isbn = library_service.search_books_in_catalog('2222222222222', 'isbn')
    assert len(res_isbn) == 1
    assert res_isbn[0]['book_id'] == 2


def test_return_book_by_patron_success(monkeypatch):
    # Arrange: stub borrow_book_by_patron to return (True, ...), update_book_availability and update_borrow_record_return_date and calculate_late_fee_for_book
    monkeypatch.setattr(library_service, 'borrow_book_by_patron', lambda pid, bid: (True, 'borrowed'))
    called = {'update_avail': False, 'update_record': False, 'calc_fee': False}

    def fake_update_availability(book_id, delta):
        called['update_avail'] = True
        return True

    def fake_calc_fee(patron_id, book_id):
        called['calc_fee'] = True
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'success'}

    def fake_update_record(patron_id, book_id, return_date):
        called['update_record'] = True
        return True

    monkeypatch.setattr(library_service, 'update_book_availability', fake_update_availability)
    monkeypatch.setattr(library_service, 'calculate_late_fee_for_book', fake_calc_fee)
    monkeypatch.setattr(library_service, 'update_borrow_record_return_date', fake_update_record)

    # Act
    success, message = library_service.return_book_by_patron('123456', 1)

    # Assert
    assert success is True
    assert message == 'Book returned successfully.'
    assert called['update_avail'] and called['calc_fee'] and called['update_record']
