# pylint: disable=import-error
# type: ignore
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import json
import re
import pandas as pd  # type: ignore
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import numpy as np  # type: ignore

class SmartChartGenerator:
    """
    Intelligent chart generator that analyzes data patterns and creates appropriate charts
    without relying on LLM APIs. This eliminates quota limitations and API dependencies.
    """
    
    def __init__(self):
        self.color_palette = [
            "#1537ba", "#00a9f4", "#051c2c", "#82a6c9", 
            "#99e6ff", "#14b8ab", "#9c217d"
        ]
        
    def parse_markdown_table(self, md_content: str) -> Optional[pd.DataFrame]:
        """Parse markdown table into pandas DataFrame"""
        try:
            lines = md_content.strip().split('\n')
            
            # Find table lines (contain |)
            table_lines = [line.strip() for line in lines if '|' in line and line.strip()]
            
            if len(table_lines) < 2:
                return None
                
            # Extract header
            header_line = table_lines[0]
            headers = [col.strip() for col in header_line.split('|') if col.strip()]
            
            # Skip separator line if exists
            data_start_idx = 1
            if len(table_lines) > 1:
                second_line = table_lines[1]
                if all(c in '|-: ' for c in second_line.replace('|', '')):
                    data_start_idx = 2
            
            # Extract data rows
            data_rows = []
            for line in table_lines[data_start_idx:]:
                row_data = [col.strip() for col in line.split('|') if col.strip()]
                if len(row_data) >= len(headers):
                    data_rows.append(row_data[:len(headers)])
            
            if not data_rows:
                return None
                
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            
            # Smart data type conversion
            for col in df.columns:
                df[col] = self._smart_convert_column(df[col])
                
            return df
            
        except Exception as e:
            print(f"Error parsing table: {e}")
            return None
    
    def _smart_convert_column(self, series: pd.Series) -> pd.Series:
        """Intelligently convert column data types"""
        # Try numeric conversion first
        try:
            # Remove common non-numeric characters
            cleaned = series.astype(str).str.replace('[,$%]', '', regex=True)
            numeric_series = pd.to_numeric(cleaned, errors='coerce')
            
            # If most values are numeric, use numeric
            if numeric_series.notna().sum() > len(series) * 0.7:
                return numeric_series
        except:
            pass
            
        # Try date conversion
        try:
            date_series = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            if date_series.notna().sum() > len(series) * 0.7:
                return date_series
        except:
            pass
            
        # Return as string if nothing else works
        return series.astype(str)
    
    def detect_data_pattern(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect data patterns and suggest chart types"""
        pattern_info = {
            'row_count': len(df),
            'col_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': {},
            'has_dates': False,
            'has_numeric': False,
            'financial_keywords': [],
            'suggested_charts': []
        }
        
        # Analyze columns
        numeric_cols = []
        date_cols = []
        categorical_cols = []
        
        for col in df.columns:
            col_data = df[col]
            col_lower = col.lower()
            
            # Determine data type
            if pd.api.types.is_numeric_dtype(col_data):
                pattern_info['data_types'][col] = 'numeric'
                numeric_cols.append(col)
                pattern_info['has_numeric'] = True
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                pattern_info['data_types'][col] = 'date'
                date_cols.append(col)
                pattern_info['has_dates'] = True
            else:
                pattern_info['data_types'][col] = 'categorical'
                categorical_cols.append(col)
        
        # Check for financial keywords
        financial_keywords = [
            'price', 'open', 'high', 'low', 'close', 'volume', 'stock', 
            'ohlc', 'market', 'trading', 'shares', 'revenue', 'profit',
            'sales', 'earnings', 'dividend', 'yield'
        ]
        
        all_text = ' '.join(df.columns).lower() + ' '.join(df.astype(str).values.flatten()).lower()
        found_keywords = [kw for kw in financial_keywords if kw in all_text]
        pattern_info['financial_keywords'] = found_keywords
        
        # Suggest chart types based on patterns
        pattern_info['suggested_charts'] = self._suggest_chart_types(
            numeric_cols, date_cols, categorical_cols, found_keywords, df
        )
        
        return pattern_info
    
    def _suggest_chart_types(self, numeric_cols: List[str], date_cols: List[str], 
                           categorical_cols: List[str], financial_keywords: List[str],
                           df: pd.DataFrame) -> List[str]:
        """Suggest appropriate chart types based on data structure"""
        suggestions = []
        
        # Financial data patterns
        if financial_keywords:
            if any(kw in financial_keywords for kw in ['open', 'high', 'low', 'close']):
                suggestions.append('candlestick')
                suggestions.append('ohlc')
            
            if 'volume' in [col.lower() for col in df.columns]:
                suggestions.append('volume_bar')
                
            if date_cols and numeric_cols:
                suggestions.append('line_time_series')
                
            if len(numeric_cols) >= 2:
                suggestions.append('comparison_bar')
        
        # Time series patterns
        elif date_cols and numeric_cols:
            suggestions.append('line_time_series')
            if len(numeric_cols) > 1:
                suggestions.append('multi_line_series')
        
        # Comparison patterns
        elif categorical_cols and numeric_cols:
            suggestions.append('bar_chart')
            if len(numeric_cols) > 1:
                suggestions.append('grouped_bar')
        
        # Multiple numeric columns
        elif len(numeric_cols) >= 2:
            suggestions.append('comparison_bar')
            suggestions.append('correlation_scatter')
        
        # Default fallback
        if not suggestions:
            if numeric_cols:
                suggestions.append('bar_chart')
            else:
                suggestions.append('table_summary')
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def generate_charts(self, md_content: str) -> str:
        """
        Main method to generate charts from markdown table data
        Returns JSON string with chart configurations
        """
        print("🔍 SMART CHART GENERATION (API-FREE)")
        print("="*60)
        
        # Parse the data
        df = self.parse_markdown_table(md_content)
        if df is None or df.empty:
            print("❌ Could not parse table data")
            return "NO_CHART_GENERATED"
        
        print(f"✅ Parsed table: {len(df)} rows × {len(df.columns)} columns")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Analyze data patterns
        pattern_info = self.detect_data_pattern(df)
        print(f"🎯 Detected patterns: {pattern_info['suggested_charts']}")
        print(f"💰 Financial keywords: {pattern_info['financial_keywords']}")
        
        # Generate chart configurations
        charts = []
        for i, chart_type in enumerate(pattern_info['suggested_charts']):
            if i >= 3:  # Limit to 3 charts
                break
                
            chart_config = self._create_chart_config(df, chart_type, pattern_info, i)
            if chart_config:
                charts.append(chart_config)
        
        if not charts:
            print("❌ No valid charts could be generated")
            return "NO_CHART_GENERATED"
        
        result = {
            "chart_collection": charts
        }
        
        print(f"✅ Generated {len(charts)} charts successfully")
        print("="*60)
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def _create_chart_config(self, df: pd.DataFrame, chart_type: str, 
                           pattern_info: Dict, chart_index: int) -> Optional[Dict[str, Any]]:
        """Create specific chart configuration based on type and data"""
        try:
            numeric_cols = [col for col, dtype in pattern_info['data_types'].items() if dtype == 'numeric']
            date_cols = [col for col, dtype in pattern_info['data_types'].items() if dtype == 'date']
            categorical_cols = [col for col, dtype in pattern_info['data_types'].items() if dtype == 'categorical']
            
            if chart_type == 'candlestick' and len(numeric_cols) >= 4:
                return self._create_candlestick_chart(df, numeric_cols, date_cols, chart_index)
            elif chart_type == 'line_time_series' and date_cols and numeric_cols:
                return self._create_time_series_chart(df, date_cols[0], numeric_cols[0], chart_index)
            elif chart_type == 'comparison_bar' and len(numeric_cols) >= 2:
                return self._create_comparison_chart(df, numeric_cols, chart_index)
            elif chart_type == 'bar_chart':
                return self._create_simple_bar_chart(df, categorical_cols, numeric_cols, chart_index)
            else:
                # Fallback: create a simple line chart
                return self._create_fallback_chart(df, chart_index)
                
        except Exception as e:
            print(f"Error creating chart {chart_type}: {e}")
            return None
    
    def _create_candlestick_chart(self, df: pd.DataFrame, numeric_cols: List[str], 
                                date_cols: List[str], index: int) -> Dict[str, Any]:
        """Create OHLC/Candlestick chart configuration"""
        # Map columns to OHLC
        ohlc_mapping = {}
        for col in numeric_cols[:4]:
            col_lower = col.lower()
            if 'open' in col_lower:
                ohlc_mapping['open'] = col
            elif 'high' in col_lower:
                ohlc_mapping['high'] = col
            elif 'low' in col_lower:
                ohlc_mapping['low'] = col
            elif 'close' in col_lower:
                ohlc_mapping['close'] = col
        
        # If mapping incomplete, use first 4 numeric columns
        if len(ohlc_mapping) < 4:
            ohlc_keys = ['open', 'high', 'low', 'close']
            for i, col in enumerate(numeric_cols[:4]):
                ohlc_mapping[ohlc_keys[i]] = col
        
        x_data = []
        y_data_series = {key: [] for key in ohlc_mapping.keys()}
        
        # Use date column if available, otherwise use index
        if date_cols:
            x_col = date_cols[0]
            x_data = [str(val) for val in df[x_col].astype(str)]
        else:
            x_data = [str(i) for i in range(len(df))]
        
        # Extract OHLC data
        for key, col in ohlc_mapping.items():
            y_data_series[key] = [float(val) if pd.notna(val) else 0.0 for val in df[col]]
        
        return {
            "chart_type": "candlestick",
            "chart_title": f"OHLC Price Chart",
            "x_label": "Date" if date_cols else "Period",
            "y_label": "Price",
            "data": [
                {
                    "x_axis_data": x_data,
                    "y_axis_data": y_data_series['open'],
                    "legend_label": "Open",
                    "color": self.color_palette[0]
                },
                {
                    "x_axis_data": x_data,
                    "y_axis_data": y_data_series['high'],
                    "legend_label": "High",
                    "color": self.color_palette[1]
                },
                {
                    "x_axis_data": x_data,
                    "y_axis_data": y_data_series['low'],
                    "legend_label": "Low",
                    "color": self.color_palette[2]
                },
                {
                    "x_axis_data": x_data,
                    "y_axis_data": y_data_series['close'],
                    "legend_label": "Close",
                    "color": self.color_palette[3]
                }
            ]
        }
    
    def _create_time_series_chart(self, df: pd.DataFrame, date_col: str, 
                                numeric_col: str, index: int) -> Dict[str, Any]:
        """Create time series line chart"""
        x_data = [str(val) for val in df[date_col].astype(str)]
        y_data = [float(val) if pd.notna(val) else 0.0 for val in df[numeric_col]]
        
        return {
            "chart_type": "line",
            "chart_title": f"{numeric_col} Over Time",
            "x_label": "Date",
            "y_label": numeric_col,
            "data": [{
                "x_axis_data": x_data,
                "y_axis_data": y_data,
                "legend_label": numeric_col,
                "color": self.color_palette[index % len(self.color_palette)]
            }]
        }
    
    def _create_comparison_chart(self, df: pd.DataFrame, numeric_cols: List[str], index: int) -> Dict[str, Any]:
        """Create comparison chart with multiple metrics"""
        # Use first column as x-axis or create index
        x_data = [str(i) for i in range(len(df))]
        
        data_series = []
        for i, col in enumerate(numeric_cols[:3]):  # Limit to 3 series
            y_data = [float(val) if pd.notna(val) else 0.0 for val in df[col]]
            data_series.append({
                "x_axis_data": x_data,
                "y_axis_data": y_data,
                "legend_label": col,
                "color": self.color_palette[i % len(self.color_palette)]
            })
        
        return {
            "chart_type": "bar",
            "chart_title": "Comparison Chart",
            "x_label": "Data Points",
            "y_label": "Value",
            "data": data_series
        }
    
    def _create_simple_bar_chart(self, df: pd.DataFrame, categorical_cols: List[str], 
                                numeric_cols: List[str], index: int) -> Dict[str, Any]:
        """Create simple bar chart"""
        if categorical_cols and numeric_cols:
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
        else:
            # Fallback to first two columns
            x_col = df.columns[0]
            y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        x_data = [str(val) for val in df[x_col]]
        y_data = [float(val) if pd.notna(val) and str(val).replace('.','').replace('-','').isdigit() else 0.0 for val in df[y_col]]
        
        return {
            "chart_type": "bar",
            "chart_title": f"{y_col} by {x_col}",
            "x_label": x_col,
            "y_label": y_col,
            "data": [{
                "x_axis_data": x_data,
                "y_axis_data": y_data,
                "legend_label": y_col,
                "color": self.color_palette[index % len(self.color_palette)]
            }]
        }
    
    def _create_fallback_chart(self, df: pd.DataFrame, index: int) -> Dict[str, Any]:
        """Create fallback chart when specific patterns don't match"""
        # Use first two columns
        x_col = df.columns[0]
        y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        x_data = [str(val) for val in df[x_col]]
        
        # Try to extract numeric data from y column
        y_data = []
        for val in df[y_col]:
            try:
                # Extract numbers from string
                num_str = str(val).replace(',', '').replace('$', '').replace('%', '')
                if num_str.replace('.', '').replace('-', '').isdigit():
                    y_data.append(float(num_str))
                else:
                    y_data.append(0.0)
            except:
                y_data.append(0.0)
        
        return {
            "chart_type": "line",
            "chart_title": f"Data Visualization: {y_col}",
            "x_label": x_col,
            "y_label": y_col,
            "data": [{
                "x_axis_data": x_data,
                "y_axis_data": y_data,
                "legend_label": y_col,
                "color": self.color_palette[0]
            }]
        }

# Create global instance
smart_chart_generator = SmartChartGenerator()