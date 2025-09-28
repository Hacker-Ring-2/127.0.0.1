// Test the enhanced Plotly configuration extraction (Node.js version of frontend logic)

// Sample HTML content similar to what WorldClassVisualizer generates
const sampleHtml = `
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div id="chart-div"></div>
    <script>
        var data = [
            {
                x: ['2024-01-01', '2024-01-02', '2024-01-03'],
                y: [105, 108, 118],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Close Price'
            }
        ];
        
        var layout = {
            title: 'Financial Chart',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Price' }
        };
        
        Plotly.newPlot('chart-div', data, layout, {responsive: true});
    </script>
</body>
</html>
`;

// Enhanced extraction function (similar to frontend)
function extractPlotlyConfig(htmlContent) {
    console.log('Extracting Plotly config from HTML...');
    
    // Method 1: Try to extract from variable declarations
    const dataVarMatch = htmlContent.match(/var\s+data\s*=\s*(\[[\s\S]*?\]);/);
    const layoutVarMatch = htmlContent.match(/var\s+layout\s*=\s*(\{[\s\S]*?\});/);
    
    if (dataVarMatch && layoutVarMatch) {
        console.log('✅ Found variable declarations');
        console.log('Raw data string:', dataVarMatch[1].substring(0, 200) + '...');
        console.log('Raw layout string:', layoutVarMatch[1].substring(0, 200) + '...');
        
        try {
            // Clean up the strings - remove trailing commas, handle JavaScript object notation
            let dataStr = dataVarMatch[1].trim();
            let layoutStr = layoutVarMatch[1].trim();
            
            // Convert JavaScript object notation to valid JSON
            dataStr = dataStr.replace(/(\w+):/g, '"$1":'); // Quote property names
            layoutStr = layoutStr.replace(/(\w+):/g, '"$1":'); // Quote property names
            
            console.log('Cleaned data string:', dataStr.substring(0, 200) + '...');
            console.log('Cleaned layout string:', layoutStr.substring(0, 200) + '...');
            
            return {
                data: JSON.parse(dataStr),
                layout: JSON.parse(layoutStr)
            };
        } catch (parseError) {
            console.error('❌ Variable parsing error:', parseError.message);
            
            // Alternative: Try direct evaluation (unsafe but for testing)
            try {
                console.log('Trying direct evaluation method...');
                const dataEval = eval('(' + dataVarMatch[1] + ')');
                const layoutEval = eval('(' + layoutVarMatch[1] + ')');
                return {
                    data: dataEval,
                    layout: layoutEval
                };
            } catch (evalError) {
                console.error('❌ Evaluation error:', evalError.message);
            }
        }
    }
    
    // Method 2: Try to extract from Plotly.newPlot call
    const newPlotRegex = /Plotly\.newPlot\(\s*[^,]+,\s*(\[[\s\S]*?\]),\s*(\{[\s\S]*?\})/;
    const newPlotMatch = htmlContent.match(newPlotRegex);
    
    if (newPlotMatch) {
        console.log('✅ Found Plotly.newPlot configuration');
        try {
            // These should be direct variable references, not JSON
            console.log('NewPlot data ref:', newPlotMatch[1].trim());
            console.log('NewPlot layout ref:', newPlotMatch[2].trim());
            
            // If they're variable names, we need to extract the variable values
            if (newPlotMatch[1].trim() === 'data' && newPlotMatch[2].trim() === 'layout') {
                console.log('References to variables - already handled above');
            }
        } catch (parseError) {
            console.error('❌ NewPlot parsing error:', parseError.message);
        }
    }
    
    console.log('❌ No extraction patterns worked');
    return null;
}

// Test the extraction
console.log('🧪 Testing Enhanced Plotly Configuration Extraction');
console.log('=' * 60);

const config = extractPlotlyConfig(sampleHtml);

if (config) {
    console.log('\n📊 Extraction Results:');
    console.log(`Data arrays: ${config.data.length}`);
    console.log(`Layout keys: ${Object.keys(config.layout).join(', ')}`);
    
    if (config.data.length > 0) {
        const firstTrace = config.data[0];
        console.log(`\nFirst trace:`);
        console.log(`  Type: ${firstTrace.type}`);
        console.log(`  Mode: ${firstTrace.mode}`);
        console.log(`  Data points: ${firstTrace.x ? firstTrace.x.length : 'N/A'}`);
        console.log(`  Sample X: ${firstTrace.x ? firstTrace.x.slice(0, 3).join(', ') : 'N/A'}`);
        console.log(`  Sample Y: ${firstTrace.y ? firstTrace.y.slice(0, 3).join(', ') : 'N/A'}`);
    }
    
    console.log('\n✅ Chart should render properly with extracted configuration');
} else {
    console.log('\n❌ Extraction failed - chart may need HTML injection method');
}