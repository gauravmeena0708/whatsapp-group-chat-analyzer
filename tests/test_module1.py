import unittest
import os
import shutil
import tempfile
from whatsapptools.groupanalyzer import GroupAnalyzer

class TestSimple(unittest.TestCase):

    def test_add(self):
        self.assertEqual(1, 1)

class TestGroupAnalyzer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for output plots
        self.test_output_dir = tempfile.mkdtemp(prefix="whatsapptools_test_")
        self.dummy_chat_file = os.path.join(os.path.dirname(__file__), "dummy_chat.txt")

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_output_dir)

    def test_most_active_users_plot_generation(self):
        # Instantiate GroupAnalyzer with the dummy chat file and temp output directory
        analyzer = GroupAnalyzer(
            chat_file=self.dummy_chat_file,
            output_dir=self.test_output_dir,
            output_prefix="test_plot_",
            analyses_to_run=['most_active_users_plot'],
            debug=False,
            config_file=None  # Assuming no special config for this test
        )

        # 1. Parse the chat data
        parsing_success = analyzer.parse_chat_data()
        self.assertTrue(parsing_success, "Chat data parsing failed")

        # 2. Clean the DataFrame
        analyzer.df_basic_cleanup()
        self.assertFalse(analyzer.df.empty, "DataFrame is empty after cleanup")

        # 3. Run the plot generation (analyze method)
        results = analyzer.analyze()

        # Check the result for 'most_active_users_plot'
        plot_result = results.get('most_active_users_plot')

        # Assertion 3: Result is a string
        self.assertIsInstance(plot_result, str, "Plot result is not a string")

        # Assertion 4: String ends with '.png'
        self.assertTrue(plot_result.endswith(".png"), f"Plot result '{plot_result}' does not end with .png")

        # Assertion 5: String does not start with "Skipped:" or "Error generating"
        self.assertFalse(plot_result.startswith("Skipped:"), f"Plot generation was skipped: {plot_result}")
        self.assertFalse(plot_result.startswith("Error generating"), f"Plot generation failed: {plot_result}")

        # Assertion 6: Check if the plot file was actually created
        expected_plot_filename = os.path.join(self.test_output_dir, plot_result)
        self.assertTrue(os.path.exists(expected_plot_filename), f"Plot file '{expected_plot_filename}' was not created")
        self.assertTrue(os.path.getsize(expected_plot_filename) > 0, f"Plot file '{expected_plot_filename}' is empty")

if __name__ == '__main__':
    unittest.main()
