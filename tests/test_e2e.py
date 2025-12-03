
import pytest
from playwright.sync_api import Page, expect


class TestLibraryE2E:
    
    def test_add_book_and_check_if_book_is_in_catalog(self, page: Page):
        
        page.goto("http://localhost:5000/catalog")
        
        expect(page.locator("h2")).to_contain_text("Book Catalog")
        
        
        page.click("text=Add New Book")
        
        expect(page.locator("h2")).to_contain_text("Add New Book")
        
        test_isbn = "9781234567890"
        page.fill("#title", "Lebron James Autobiography")
        page.fill("#author", "Lebron James")
        page.fill("#isbn", test_isbn)
        page.fill("#total_copies", "67")
        
        page.click("button[type='submit']")
        
        expect(page).to_have_url("http://localhost:5000/catalog")
        
        page.wait_for_selector(".alert, .flash, [class*='success']", timeout=5000)
        
        expect(page.locator("body")).to_contain_text("Lebron James Autobiography")
        expect(page.locator("body")).to_contain_text("Lebron James")
        expect(page.locator("body")).to_contain_text(test_isbn)
        
        expect(page.locator("body")).to_contain_text("67/67 Available")
    
    def test_borrow_book_and_check_if_book_is_borrowed(self, page: Page):
        page.goto("http://localhost:5000/catalog")
        
        page.wait_for_selector("table", timeout=5000)
        
        available_row = page.locator("tr:has(input[name='patron_id'])").first
        
        patron_input = available_row.locator("input[name='patron_id']")
        patron_input.fill("123456")
        
        borrow_button = available_row.locator("button:has-text('Borrow')")
        borrow_button.click()
        
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url("http://localhost:5000/catalog")
        
        page.wait_for_selector(".alert, .flash, [class*='success']", timeout=5000)
        body_text = page.locator("body").inner_text()
        assert "successfully" in body_text.lower() or "borrowed" in body_text.lower(), \
            "Success message should appear after borrowing"
    
    