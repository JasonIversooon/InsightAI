INDEX_STRING = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Optimized styles - removed duplicates */
            .dash-spreadsheet-container .dash-spreadsheet-inner table {
                border-collapse: collapse;
                font-family: monospace;
            }
            
            .dash-spreadsheet-container .dash-spreadsheet-inner * {
                box-sizing: border-box;
            }
            
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
                position: sticky;
                top: 0;
                z-index: 1;
                box-shadow: 0 1px 0 #555;
            }
            
            /* Custom scrollbar */
            ::-webkit-scrollbar { width: 8px; height: 8px; }
            ::-webkit-scrollbar-track { background: #1a1e26; }
            ::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }
            ::-webkit-scrollbar-thumb:hover { background: #555; }
            
            /* Cell styling */
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td:hover {
                background-color: rgba(55, 90, 127, 0.2) !important;
            }
            
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 180px;
            }
            
            /* Row index styling */
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td:first-child,
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th:first-child {
                font-weight: bold;
                background-color: #20242c !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''