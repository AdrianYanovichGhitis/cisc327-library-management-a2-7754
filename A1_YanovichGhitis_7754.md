add_book_to_catalog: Implemented : N\A

borrow_book_by_patron: Implemented : N\A

return_book_by_patron: Not Implemented : 
- Does not check for if patron id or book id are valid
- Does not verify if book was taken by the patron
- Does not update records, available copies, or return dates
- Does not call late fees function or check for late fees

calculate_late_fee_for_book: Not Implemented :
- No API endpoint
- Does not calculate late fees (per the rules in requirements)
- Does not return anything

search_books_in_catalog: Not Implemented : 
- Search functionality is completely missing
- No partial matching
- No exact matching

get_patron_status_report: Not Implemented :
- No collection of currently borrowed books from specific patrons
- No call to database to get info of patron
- No late fees calculator

Book Catalog Display: Implemented : N\A
                            
Summary of the test scripts:

Test Scripts test the functionality of all the functions inside of library_service.py. 

add_book_to_catalog: I tested for valid and invalid isbn number, author length, number of book copies.
All tests ran as expected, failed when invalid isbn number, author length, number of copies were passed into
function. Passed when valid isbn, author, title, and number of copies passed through.

borrow_book_by_patron: Tested for valid/invalid patron id, and valid/invalid book id.
All tests ran as expected. When parameter was invalid, test returned false. When parameters were valid,
test returned true.

return_book_by_patron: Tested for valid input, invalid patron id, invalid book id, invalid patron id type
All tests ran as expected. All invalid inputs failed, while valid passed.

calculate_late_fee_for_book: Tested for valid book id, late fees exceed max, negative late fee
All tests ran as expected. Both late fee tests returned invalid book id returned false, while valid input
returned true

search_books_in_catalog: Tested for if search term is empty or valid, and if search type is of correct type and valid input. Tests ran as expected, empty and wrong type tests returned false, while valid inputs returned true.

get_patron_status_report: Tested for invalid, empty, valid, wrong type, patron id. All tests ran as expected, invalid ones returned false, while valid input returned true.



