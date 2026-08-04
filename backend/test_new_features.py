import sys
import json
import unittest
from services import assets_service
from agent import tools
from services.groq_service import GroqService

# Ensure utf-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class TestNewFeaturesAndBugFixes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.groq = GroqService()

    def test_01_bug_fix_nonetype_and_kwargs(self):
        """Test Bug Fix: Never allow NoneType ** unpacking and allow unexpected kwargs without TypeError."""
        # Calling tool with unexpected kwargs should not fail
        res = tools.get_asset_count(**{"unexpected_param": "test", "another": None})
        self.assertTrue(res["success"])
        self.assertIn("count", res)

        # Calling get_assets with unexpected kwargs
        res2 = tools.get_assets(**{"filter": "None"})
        self.assertTrue(res2["success"])

    def test_02_total_asset_summary(self):
        """Test New Feature 1: get_asset_summary() returns required structured counts from DB directly."""
        summary_res = tools.get_asset_summary()
        self.assertTrue(summary_res["success"])
        summary = summary_res["summary"]
        for key in ["total_assets", "available", "assigned", "repair", "returned", "categories"]:
            self.assertIn(key, summary)
        self.assertIsInstance(summary["categories"], dict)

    def test_03_asset_dashboard_markdown_format(self):
        """Test New Feature 2: Dashboard formatting returns beautiful structured Markdown table."""
        summary_res = tools.get_asset_summary()
        formatted = self.groq._format_tool_result_for_user(summary_res)
        self.assertIn("# 📊 Asset Dashboard", formatted)
        self.assertIn("| Metric | Count |", formatted)
        self.assertIn("📦 Total Assets", formatted)
        self.assertIn("✅ Available", formatted)
        self.assertIn("## Category Distribution", formatted)

    def test_04_show_all_assets_markdown_table(self):
        """Test New Feature 3: Show All Assets returns clean Markdown table with emojis and — for empty Assigned To."""
        all_res = tools.get_all_assets()
        formatted = self.groq._format_tool_result_for_user(all_res)
        self.assertIn("# 📋 Asset List", formatted)
        self.assertIn("| Asset Name | Category | Asset ID | Status | Assigned To |", formatted)
        # Check that empty assignments show dash
        self.assertIn("—", formatted)

    def test_05_available_assets_table_and_count(self):
        """Test New Feature 4: Available assets returns # ✅ Available Assets table and Total Available Assets: X."""
        avail_res = tools.filter_assets(status="Available")
        formatted = self.groq._format_tool_result_for_user(avail_res)
        self.assertIn("# ✅ Available Assets", formatted)
        self.assertIn("| Asset | Category | Asset ID |", formatted)
        self.assertIn("Total Available Assets:", formatted)

    def test_06_filters_support(self):
        """Test New Feature 5: Support filtering by status, brand, category, employee, unassigned, and recently added."""
        # Brand filter
        dell = tools.filter_assets(brand="Dell")
        self.assertTrue(dell["success"])
        for a in dell["assets"]:
            self.assertIn("dell", a["brand"].lower())

        # Unassigned filter
        unassigned = tools.filter_assets(unassigned=True)
        self.assertTrue(unassigned["success"])
        for a in unassigned["assets"]:
            self.assertEqual((a.get("assigned_to") or "").strip(), "")

        # Recently added filter
        recent = tools.filter_assets(recent=True)
        self.assertTrue(recent["success"])
        self.assertLessEqual(len(recent["assets"]), 5)

    def test_07_sorting_support(self):
        """Test New Feature 6: Support sorting by asset_name, category, status, asset_id in asc and desc."""
        assets_asc = tools.get_all_assets(sort_by="asset_name", sort_order="asc")["assets"]
        assets_desc = tools.get_all_assets(sort_by="asset_name", sort_order="desc")["assets"]
        if len(assets_asc) > 1:
            names_asc = [str(a.get("asset_name") or "").lower() for a in assets_asc]
            self.assertEqual(names_asc, sorted(names_asc))
            names_desc = [str(a.get("asset_name") or "").lower() for a in assets_desc]
            self.assertEqual(names_desc, sorted(names_desc, reverse=True))

    def test_08_smart_analytics(self):
        """Test New Feature 7: Smart analytics returns percentages and most assigned category."""
        analytics_res = tools.get_asset_analytics()
        self.assertTrue(analytics_res["success"])
        an = analytics_res["analytics"]
        self.assertIn("repair_percentage", an)
        self.assertIn("assignment_percentage", an)
        self.assertIn("most_assigned_category", an)
        self.assertIn("category_distribution", an)

        formatted = self.groq._format_tool_result_for_user(analytics_res)
        self.assertIn("# 📈 Smart Analytics", formatted)
        self.assertIn("Most Assigned Category:", formatted)

    def test_09_agentic_ai_backward_compatibility(self):
        """Test New Feature 9: Verify all 17 agent tools are registered and backward compatible."""
        tool_names = [t["function"]["name"] for t in self.groq.tools]
        required_tools = [
            "get_assets", "create_asset", "get_asset_by_id", "update_asset",
            "delete_asset", "assign_asset", "return_asset", "mark_clearance",
            "search_assets", "get_assets_by_status", "get_assets_by_employee",
            "get_asset_count", "get_dashboard_stats", "get_audit_logs",
            "get_asset_summary", "get_asset_analytics", "filter_assets"
        ]
        for t in required_tools:
            self.assertIn(t, tool_names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
