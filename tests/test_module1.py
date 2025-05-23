import unittest
import os
import shutil
import tempfile
from whatsapptools.groupanalyzer import GroupAnalyzer
import pandas as pd # Required for DataFrame checks

class TestSimple(unittest.TestCase):

    def test_add(self):
        self.assertEqual(1, 1)

class TestGroupAnalyzer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for output plots
        self.test_output_dir = tempfile.mkdtemp(prefix="whatsapptools_test_")
        # Assume dummy_chat.txt is in the same directory as the test file
        self.dummy_chat_file = os.path.join(os.path.dirname(__file__), "dummy_chat.txt")
        # Ensure dummy_chat.txt exists (it should have been created in a previous step)
        if not os.path.exists(self.dummy_chat_file):
            with open(self.dummy_chat_file, "w") as f:
                f.write("01/01/23, 10:00 AM - User1: Hello\n")
                f.write("01/01/23, 10:01 AM - User2: Hi there!\n")
                f.write("01/01/23, 10:02 AM - User1: This is a test message for plotting.\n")


    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_output_dir)

    def test_most_active_users_plot_generation(self):
        # 1. Instantiate GroupAnalyzer
        analyzer = GroupAnalyzer(self.dummy_chat_file)

        # 2. Parse the chat data
        df_raw = analyzer.parse_chat_data()
        self.assertIsNotNone(df_raw, "Chat data parsing returned None (failed)")
        self.assertIsInstance(df_raw, pd.DataFrame, "Parsed data is not a Pandas DataFrame")

        # 3. Clean the DataFrame
        df_cleaned = analyzer.df_basic_cleanup(df_raw.copy())
        self.assertFalse(df_cleaned.empty, "DataFrame is empty after cleanup")
        self.assertIn('name', df_cleaned.columns, "Column 'name' not found in cleaned DataFrame")
        self.assertIn('message', df_cleaned.columns, "Column 'message' not found in cleaned DataFrame")

        # 4. Create Plotly figure
        try:
            fig = analyzer.create_plotly_fig(
                df_cleaned,
                x='name',
                y='message',
                sortby='message',
                asc=False,
                count=True
            )
            fig.update_layout(title_text="Most Active Users by Message Count")

            # 5. Define output path and save image
            plot_filename = "test_most_active_users.png"
            plot_output_path = os.path.join(self.test_output_dir, plot_filename)
            fig.write_image(plot_output_path)
            
            plot_result = plot_output_path # This is what we'll assert against

        except ImportError:
            self.fail("Test failed due to ImportError, likely kaleido is not installed or not found.")
        except Exception as e:
            self.fail(f"Test failed during plot generation or saving: {str(e)}")

        # Assertions on the plot_result (which is the output path)
        self.assertIsInstance(plot_result, str, "Plot result (path) is not a string")
        self.assertTrue(plot_result.endswith(".png"), f"Plot result path '{plot_result}' does not end with .png")
        
        # Assertions on the file itself
        self.assertTrue(os.path.exists(plot_result), f"Plot file '{plot_result}' was not created")
        self.assertTrue(os.path.getsize(plot_result) > 0, f"Plot file '{plot_result}' is empty")

if __name__ == '__main__':
    unittest.main()
