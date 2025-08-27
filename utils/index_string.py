INDEX_STRING = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* DataFrame-like styling */
            .dash-spreadsheet-container .dash-spreadsheet-inner table {
                border-collapse: collapse;
                font-family: monospace;
            }
            
            /* Fix for edge rendering issues */
            .dash-spreadsheet-container .dash-spreadsheet-inner * {
                box-sizing: border-box;
            }
            
            /* Better table header styling */
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
                position: sticky;
                top: 0;
                z-index: 1;
                box-shadow: 0 1px 0 #555;
            }
            
            /* Animation for success message */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #1a1e26;
            }
            ::-webkit-scrollbar-thumb {
                background: #444;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            
            /* Cell hover effect */
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td:hover {
                background-color: rgba(55, 90, 127, 0.2) !important;
            }
            
            /* Ensure data cells don't wrap and show ellipsis */
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 180px;
            }
            
            /* Row index column special styling */
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td:first-child,
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th:first-child {
                font-weight: bold;
                background-color: #20242c !important;
            }
            
            /* Responsive table container */
            .dash-spreadsheet {
                width: 100% !important;
                max-width: 100% !important;
            }
            
            /* Full screen mode */
            .fullscreen-table {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                z-index: 9999 !important;
                background: #23272f !important;
                padding: 20px !important;
                overflow: auto !important;
            }
            
            .fullscreen-table .dash-spreadsheet {
                height: calc(100vh - 80px) !important;
            }
            
            /* Exit fullscreen button */
            #exit-fullscreen {
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 10000;
                background: #444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                cursor: pointer;
                display: none;
            }
            
            #exit-fullscreen:hover {
                background: #555;
            }
            
            /* Make the data table responsive */
            @media (max-width: 1200px) {
                .dash-table-container {
                    overflow-x: auto;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <button id="exit-fullscreen">Exit Fullscreen</button>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // Add fullscreen functionality
            document.addEventListener('DOMContentLoaded', function() {
                const fullscreenBtn = document.getElementById('fullscreen-btn');
                const exitBtn = document.getElementById('exit-fullscreen');
                const tableContainer = document.querySelector('.dash-table-container');
                
                if (fullscreenBtn && exitBtn && tableContainer) {
                    fullscreenBtn.addEventListener('click', function() {
                        const container = tableContainer.parentElement;
                        container.classList.add('fullscreen-table');
                        exitBtn.style.display = 'block';
                    });
                    
                    exitBtn.addEventListener('click', function() {
                        const container = tableContainer.parentElement;
                        container.classList.remove('fullscreen-table');
                        exitBtn.style.display = 'none';
                    });
                }
                
                // Add double-click to fullscreen
                if (tableContainer) {
                    tableContainer.addEventListener('dblclick', function(e) {
                        // Only trigger on header double-click
                        if (e.target.tagName === 'TH' || e.target.parentElement.tagName === 'TH') {
                            const container = tableContainer.parentElement;
                            if (!container.classList.contains('fullscreen-table')) {
                                container.classList.add('fullscreen-table');
                                exitBtn.style.display = 'block';
                            } else {
                                container.classList.remove('fullscreen-table');
                                exitBtn.style.display = 'none';
                            }
                        }
                    });
                }
            });
        </script>
    </body>
</html>
'''