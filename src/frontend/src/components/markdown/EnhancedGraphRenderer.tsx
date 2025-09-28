'use client';
import { useMemo } from 'react';
import { PlotlyChart } from './PlotilyChart';
import StockVisualizationEnhancer from './StockVisualizationEnhancer';
import { getUUID } from '@/utils/utility';
import { getSupportedChartTypes, COLOR_PALETTE } from '@/utils/plotly';

const EnhancedGraphRenderer = ({ codeContent }: { codeContent: string }) => {
  // Parse the JSON content safely
  const parsedData = useMemo(() => {
    try {
      return JSON.parse(codeContent);
    } catch (error) {
      console.error('Failed to parse graph data:', error);
      return null;
    }
  }, [codeContent]);

  // Convert Chart.js format to our expected format
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const convertChartJsToPlotly = (chartJsData: any) => {
    const { type, data, options } = chartJsData;
    
    // Convert Chart.js type to our internal type
    const typeMapping: { [key: string]: string } = {
      'line': 'lines',
      'bar': 'bar',
      'pie': 'pie'
    };
    
    const chart_type = typeMapping[type] || 'lines';
    const chart_title = options?.title?.text || 'Chart';
    const x_label = options?.scales?.x?.title?.text || 'X Axis';
    const y_label = options?.scales?.y?.title?.text || 'Y Axis';
    
    // Convert datasets to our format
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const convertedData = data.datasets.map((dataset: any, index: number) => {
      const colors = ['#1537ba', '#00a9f4', '#051c2c', '#82a6c9', '#99e6ff', '#14b8ab', '#9c217d'];
      return {
        legend_label: dataset.label || `Series ${index + 1}`,
        x_axis_data: data.labels || [],
        y_axis_data: dataset.data || [],
        color: colors[index % colors.length]
      };
    });

    return {
      chart_type,
      chart_title,
      x_label,
      y_label,
      data: convertedData
    };
  };

  // Convert backend format to frontend format
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const convertBackendToFrontend = (backendChart: any) => {
    console.log('🔄 Converting backend format to frontend format:', backendChart);
    
    // Check if data is in backend format (key-value pairs)
    if (backendChart.data && !Array.isArray(backendChart.data)) {
      const dataKeys = Object.keys(backendChart.data);
      console.log('📊 Detected backend format with keys:', dataKeys);
      
      if (dataKeys.length >= 2) {
        // Assume first key is x-axis, others are y-axis series
        const xKey = dataKeys[0];
        const xData = backendChart.data[xKey];
        
        // Convert each y-axis key to a data series
        const convertedData = dataKeys.slice(1).map((yKey) => ({
          legend_label: yKey,
          x_axis_data: xData,
          y_axis_data: backendChart.data[yKey],
          color: COLOR_PALETTE[dataKeys.indexOf(yKey) % COLOR_PALETTE.length]
        }));
        
        console.log('✅ Converted to frontend format:', convertedData);
        
        return {
          ...backendChart,
          data: convertedData
        };
      }
    }
    
    // If already in frontend format, return as-is
    console.log('📋 Data already in frontend format or unrecognized format');
    return backendChart;
  };

  // Create datasets object
  const updatedChartData = useMemo(() => {
    if (!parsedData) return [];

    // Check if it's Chart.js format (has type, data, options)
    if (parsedData.type && parsedData.data) {
      console.log('Detected Chart.js format, converting...');
      const converted = convertChartJsToPlotly(parsedData);
      const supportedTypes = getSupportedChartTypes(converted);
      
      return [{
        id: getUUID(),
        supportedTypes: supportedTypes,
        data: converted,
      }];
    }

    // Check if it's our expected format (has chart_collection)
    if (parsedData.chart_collection && Array.isArray(parsedData.chart_collection)) {
      console.log('🎯 Detected chart_collection format, processing...');
      
      // Convert each chart from backend to frontend format
      const convertedCharts = parsedData.chart_collection.map(convertBackendToFrontend);
      
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const supportedChartTypes = convertedCharts.map((chartData: any) => {
        if (chartData.chart_type === 'pie') {
          const response = getSupportedChartTypes(chartData);
          response.push('pie');
          return response;
        }
        return getSupportedChartTypes(chartData);
      });

      if (
        supportedChartTypes.length > 0 &&
        convertedCharts.length > 0 &&
        supportedChartTypes.length === convertedCharts.length
      ) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        return convertedCharts.map((chart: any, index: number) => ({
          id: getUUID(),
          supportedTypes: supportedChartTypes[index],
          data: chart,
        }));
      }
    }

    // Check if it's a direct chart object (has chart_type, chart_title, etc.)
    if (parsedData.chart_type && parsedData.chart_title) {
      console.log('Detected direct chart object format');
      const supportedTypes = getSupportedChartTypes(parsedData);
      
      return [{
        id: getUUID(),
        supportedTypes: supportedTypes,
        data: parsedData,
      }];
    }

    console.warn('Unknown chart format:', parsedData);
    return [];
  }, [parsedData]);

  // If parsing failed, show error
  if (!parsedData) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 my-4">
        <p className="text-red-700 text-sm">
          Failed to parse graph data. Please ensure the JSON format is correct.
        </p>
        <details className="mt-2">
          <summary className="text-red-600 cursor-pointer">Raw content</summary>
          <pre className="text-xs bg-red-100 p-2 mt-1 rounded overflow-auto max-h-32">
            {codeContent}
          </pre>
        </details>
      </div>
    );
  }

  // If no charts were processed, show info
  if (!updatedChartData || updatedChartData.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 my-4">
        <p className="text-yellow-700 text-sm">
          No charts could be generated from the provided data.
        </p>
        <details className="mt-2">
          <summary className="text-yellow-600 cursor-pointer">Debug info</summary>
          <pre className="text-xs bg-yellow-100 p-2 mt-1 rounded overflow-auto max-h-32">
            {JSON.stringify(parsedData, null, 2)}
          </pre>
        </details>
      </div>
    );
  }

  return (
    <div className="my-6 rounded-lg">
      <div className="mb-6">
        <div className="space-y-10">
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {updatedChartData.map((chartData: any) => (
            <div key={chartData.id}>
              <StockVisualizationEnhancer
                chartTitle={chartData.data?.chart_title || 'Chart'}
                chartData={chartData.data}
              >
                <div className="bg-white overflow-hidden rounded-lg shadow-sm border border-gray-100">
                  <PlotlyChart
                    chartData={chartData.data}
                    chartType={chartData.data.chart_type}
                    showTitle={true}
                    className="transition-all duration-300"
                  />
                </div>
              </StockVisualizationEnhancer>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EnhancedGraphRenderer;