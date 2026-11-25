import pytest
from src.categorizer import categorize
@pytest.mark.parametrize('description,expected', [('Swiggy dinner','Food'),('Zomato lunch','Food'),('grocery store','Food'),('Uber ride','Transportation'),('bus ticket','Transportation'),('fuel','Transportation'),('Amazon purchase','Shopping'),('clothes shopping','Shopping'),('electricity bill','Bills'),('internet bill','Bills'),('course fee','Education'),('book purchase','Education'),('Apollo pharmacy','Health'),('doctor visit','Health'),('movie ticket','Entertainment'),('Netflix','Entertainment'),('monthly rent','Housing'),('haircut','Personal Care'),('unrecognized thing','Other')])
def test_keyword_categories(description,expected): assert categorize(description)==expected

def test_empty_description_other(): assert categorize('')=='Other'
