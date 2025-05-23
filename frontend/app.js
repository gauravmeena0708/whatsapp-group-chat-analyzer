(function() {
    'use strict';

    // Define the WhatsApp Analyzer application module
    var app = angular.module('whatsAppAnalyzerApp', []);

    // Define the MainController
    app.controller('MainController', ['$scope', '$http', function($scope, $http) {
        var vm = this; // Using 'vm' (ViewModel) as alias for 'this'

        // --- Initialize scope variables ---
        vm.chatFile = null;
        vm.analysisResults = null;
        vm.isLoading = false;
        vm.error = null;

        // --- Selected Analyses ---
        vm.selectedAnalyses = {
            wordcloud: true,
            chat_data_csv: true,
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
                return;
            }
            var file = fileInput.files[0];

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
            formData.append('chatfile', file);
            formData.append('analyses', analysesString);

            vm.isLoading = true;
            vm.analysisResults = null;
            vm.error = null;

            $http.post('http://localhost:3000/api/analyze', formData, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            }).then(function(response) {
                if (response.data && response.data.analysis) {
                    vm.analysisResults = response.data.analysis;
                    console.log('Analysis results received:', vm.analysisResults);
                } else {
                    vm.error = "Received unexpected data format from server.";
                    console.error('Unexpected response data:', response.data);
                }
                vm.isLoading = false;
            }, function(errorResponse) {
                var errorMessage = "An error occurred during analysis.";
                if (errorResponse.data && errorResponse.data.error) {
                    errorMessage = errorResponse.data.error;
                    if (errorResponse.data.details) {
                        errorMessage += " Details: " + errorResponse.data.details;
                    }
                } else if (errorResponse.statusText) {
                    errorMessage = "Error: " + errorResponse.statusText;
                }
                vm.error = errorMessage;

                if(errorResponse.data && errorResponse.data.rawOutput) {
                    console.error("Raw backend output on error: ", errorResponse.data.rawOutput);
                }
                console.error('Upload error response:', errorResponse);
                vm.isLoading = false;
            });
        };

        vm.getResultFileUrl = function(relativePath) {
            if (!relativePath || typeof relativePath !== 'string') {
                return null; 
            }
            var path = relativePath;
            // Path adjustment was previously here, but the Python script now seems to return paths like 'api/analysis_results/...'
            // If it's already a full path segment for the API, we can use it.
            // The crucial part is that `relativePath` from `analysisResult[key]` must correctly form a URL
            // when prepended by `http://localhost:3000/`.
            // Example from python: `transformedAnalysisResult[key] = api/analysis_results/${relativePathToAnalysisDir}/${filename}`;
            // So, the paths are already relative to the server root for the API.

            if (path.startsWith('api/analysis_results/') && (path.endsWith('.png') || path.endsWith('.csv'))) {
                 return 'http://localhost:3000/' + path; // Path is already relative to base URL for API
            }
            // If the path doesn't start with 'api/analysis_results' but seems like a file from older logic
            if (path.includes('/') && (path.endsWith('.png') || path.endsWith('.csv'))) {
                // This is a fallback, assuming the path might be relative to 'backend' or similar.
                // This part might need adjustment based on exact output of python script if it varies.
                // For now, relying on the python script outputting `api/analysis_results/...`
                 if (path.startsWith('backend/')) { //
                     path = path.substring('backend/'.length);
                 }
                 // If it's now `analysis_results/...`, prepend `api/`
                 if (path.startsWith('analysis_results/')) {
                     return 'http://localhost:3000/api/' + path;
                 }
            }
            return null;
        };
        
        vm.isResultAPath = function(resultValue) {
            if (resultValue && typeof resultValue === 'string') {
                const isLikelyPath = (resultValue.includes('/') && (resultValue.endsWith('.png') || resultValue.endsWith('.csv')));
                // Python script now returns "Skipped: kaleido not installed..." or similar error strings.
                const isErrorMessage = resultValue.toLowerCase().startsWith('skipped:') || resultValue.toLowerCase().startsWith('error generating') || resultValue.toLowerCase().includes('cannot generate');
                return isLikelyPath && !isErrorMessage;
            }
            return false;
        };

        // --- ADD THIS FUNCTION FOR PRINTING ---
        vm.printResults = function() {
            window.print();
        };
        // --- END OF ADDED FUNCTION ---

    }]);

})();