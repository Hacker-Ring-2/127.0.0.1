// Test regex pattern for graph detection
const testContent = `Here is some HP Inc. stock data:

graph {"chart_collection": [{"chart_type": "lines", "chart_title": "Test Chart", "x_label": "Date", "y_label": "Price", "data": [{"date": "2025-01-01", "Close Price (USD)": 100}]}]} <END_OF_GRAPH>

More content here.`;

console.log('Original content:');
console.log(testContent);
console.log('\n---\n');

const graphPattern = /graph\s*(\{"chart_collection":.+?<END_OF_GRAPH>)/gs;
const matches = [...testContent.matchAll(graphPattern)];

console.log('Test Results:');
console.log('Found matches:', matches.length);
if (matches[0]) {
  console.log('First match:', matches[0][0].substring(0, 100) + '...');
}

const processed = testContent.replace(
  graphPattern,
  '\n\n```graph\n$1\n```\n\n'
);

console.log('\nProcessed result:');
console.log(processed);