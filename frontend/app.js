(function() {
    'use strict';

    // Define the WhatsApp Analyzer application module
    var app = angular.module('whatsAppAnalyzerApp', []);

    // Define the MainController
    app.controller('MainController', ['$scope', '$http', function($scope, $http) {
        var vm = this; // Using 'vm' (ViewModel) as alias for 'this'

        // --- Initialize scope variables ---
        vm.chatFile = null; // To store the selected file object (optional, as we get it directly in uploadFile)
        vm.analysisResults = null; // To store results from the backend
        vm.isLoading = false; // For loading indicators
        vm.error = null; // To store error messages

        // --- Selected Analyses ---
        vm.selectedAnalyses = {
            wordcloud: true, // Default analysis
            chat_data_csv: true, // Default analysis
            basic_stats: false,
            most_active_users_plot: false,
            most_active_day_plot: false,
            top_emojis_global_csv: false
        };

        // --- File Upload Function ---
        vm.uploadFile = function() {
            var fileInput = document.getElementById('chatFile');
            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                alert("Please select a file first!");
                vm.error = "Please select a file first.";
                // $scope.$apply(); // Not strictly needed here due to alert, but good if no alert
                return;
            }
            var file = fileInput.files[0];

            // Construct the analyses string
            var selectedKeys = [];
            for (var key in vm.selectedAnalyses) {
                if (vm.selectedAnalyses.hasOwnProperty(key) && vm.selectedAnalyses[key]) {
                    selectedKeys.push(key);
                }
            }
            var analysesString = selectedKeys.join(',');
            if (!analysesString) {
                alert("Please select at least one analysis type!");
                vm.error = "Please select at least one analysis type.";
                return;
            }

            var formData = new FormData();
            formData.append('chatfile', file); // Key 'chatfile' must match backend (multer field name)
            formData.append('analyses', analysesString); // Add selected analyses

            vm.isLoading = true;
            vm.analysisResults = null; // Clear previous results
            vm.error = null; // Clear previous errors

            $http.post('http://localhost:3000/api/analyze', formData, {
                transformRequest: angular.identity, // Let browser handle FormData
                headers: {'Content-Type': undefined} // Let browser set Content-Type with boundary
            }).then(function(response) {
                // Assuming backend returns: { message: "...", analysis: { ...results... } }
                if (response.data && response.data.analysis) {
                    vm.analysisResults = response.data.analysis; // Store the 'analysis' object
                    console.log('Analysis results received:', vm.analysisResults);
                } else {
                    vm.error = "Received unexpected data format from server.";
                    console.error('Unexpected response data:', response.data);
                }
                vm.isLoading = false;
            }, function(errorResponse) {
                var errorMessage = "An error occurred during analysis."; // Default message
                if (errorResponse.data && errorResponse.data.error) {
                    errorMessage = errorResponse.data.error; // Main error message from backend
                    if (errorResponse.data.details) {
                        errorMessage += " Details: " + errorResponse.data.details; // Add details if present
                    }
                } else if (errorResponse.statusText) {
                    errorMessage = "Error: " + errorResponse.statusText; // Fallback to status text
                }
                vm.error = errorMessage; // Set the refined error message

                // Log more details to the console for debugging
                if(errorResponse.data && errorResponse.data.rawOutput) {
                    console.error("Raw backend output on error: ", errorResponse.data.rawOutput);
                }
                console.error('Upload error response:', errorResponse);
                vm.isLoading = false;
            });
        };

        // --- Helper function to construct full URLs for backend-served files ---
        vm.getResultFileUrl = function(relativePath) {
            if (!relativePath || typeof relativePath !== 'string') { // Check if it's a string
                // Check if it's an error message string from Python (e.g. "Skipped: kaleido not installed")
                // In this case, we don't want to form a URL.
                // The HTML template should handle displaying such strings directly.
                return null; 
            }
            // Remove 'backend/' prefix if present
            var path = relativePath;
            if (path.startsWith('backend/')) {
                path = path.substring('backend/'.length);
            }
            // Ensure it looks like a path before prepending the base URL
            // This is a simple check; more robust validation might be needed
            if (path.includes('/') && (path.endsWith('.png') || path.endsWith('.csv'))) {
                 return 'http://localhost:3000/api/' + path;
            }
            return null; // Return null if it's not a recognized file path
        };
        
        // Helper to check if a result is a valid URL (path) or an error/skip message string
        vm.isResultAPath = function(resultValue) {
            if (resultValue && typeof resultValue === 'string') {
                // Simple check: if it contains typical file extensions and path separators,
                // and is not one of the known "Skipped" or "Error" messages.
                const isLikelyPath = (resultValue.includes('/') && (resultValue.endsWith('.png') || resultValue.endsWith('.csv')));
                const isErrorMessage = resultValue.toLowerCase().startsWith('skipped:') || resultValue.toLowerCase().startsWith('error generating');
                return isLikelyPath && !isErrorMessage;
            }
            return false;
        };


        // --- (Optional) Placeholder for fetching status from backend (example) ---
        // vm.getBackendStatus = function() {
        //     $http.get('http://localhost:3000/api/status').then(function(response) {
        //         console.log('Backend status:', response.data);
        //         alert('Backend status: ' + response.data.status);
        //     }).catch(function(err) {
        //         console.error('Error fetching backend status:', err);
        //         alert('Error fetching backend status. Check console.');
        //     });
        // };

    }]);

})();
