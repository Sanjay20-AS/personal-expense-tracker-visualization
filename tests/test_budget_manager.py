import pytest
from src.budget_manager import set_budget, budgets_for_month, remove_budget

def test_reject_nonpositive_budget(tmp_path):
 with pytest.raises(ValueError): set_budget(2026,1,'Food',0,str(tmp_path/'x.db'))

def test_set_and_remove(tmp_path):
 db=str(tmp_path/'x.db');set_budget(2026,1,'Food',1200,db);assert len(budgets_for_month(2026,1,db))==1;remove_budget(2026,1,'Food',db);assert budgets_for_month(2026,1,db).empty
