"""
🚀 REVOLUTIONARY FINANCIAL VISUALIZATION ENGINE
World-class chart generation with beautiful, interactive plots
"""

# pylint: disable=import-error
# type: ignore
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import matplotlib.pyplot as plt  # type: ignore
import matplotlib.dates as mdates  # type: ignore
from matplotlib.patches import Rectangle  # type: ignore
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
import plotly.express as px  # type: ignore
import seaborn as sns  # type: ignore
import pandas as pd  # type: ignore  
import numpy as np  # type: ignore
from datetime import datetime
import json
import io
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

# Set beautiful styling
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class WorldClassFinancialVisualizer:
    """
    🎨 The world's most advanced financial visualization engine
    Creates stunning, interactive charts with professional aesthetics
    """
    
    def __init__(self):
        # Professional color schemes for financial data
        self.bull_color = '#00C851'  # Green for gains
        self.bear_color = '#FF4444'  # Red for losses  
        self.neutral_color = '#33B5E5'  # Blue for neutral
        
        # Extended professional color palette
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
        ]
        
        # Professional themes
        self.themes = {
            'dark': {
                'bg_color': '#1e1e1e',
                'paper_bg': '#2d2d2d', 
                'text_color': '#ffffff',
                'grid_color': '#404040'
            },
            'light': {
                'bg_color': '#ffffff',
                'paper_bg': '#f8f9fa',
                'text_color': '#333333',
                'grid_color': '#e6e6e6'
            },
            'professional': {
                'bg_color': '#f5f5f5',
                'paper_bg': '#ffffff',
                'text_color': '#2c3e50',
                'grid_color': '#bdc3c7'
            }
        }
        
    def generate_advanced_financial_charts(self, data_input: Union[pd.DataFrame, str], theme: str = 'professional') -> Dict[str, Any]:
        """
        🎯 Generate world-class financial visualizations
        Accepts either DataFrame or string data
        """
        print("🚀 WORLD-CLASS FINANCIAL VISUALIZATION ENGINE")
        print("="*60)
        
        try:
            # Handle both DataFrame and string inputs
            if isinstance(data_input, pd.DataFrame):
                df = data_input.copy()
                print(f"✅ Using provided DataFrame with {len(df)} rows, {len(df.columns)} columns")
            else:
                # Parse the data with enhanced intelligence
                df = self._parse_financial_data(data_input)
                if df is None or df.empty:
                    return self._create_error_response("Failed to parse financial data")
            
            print(f"✅ Parsed {len(df)} data points with {len(df.columns)} metrics")
            
            # Detect data patterns with AI-level intelligence  
            patterns = self._detect_advanced_patterns(df)
            print(f"🧠 Detected patterns: {patterns['chart_types']}")
            
            # Generate multiple professional visualizations
            charts = []
            
            # 1. Advanced Candlestick/OHLC Chart
            if patterns['has_ohlc']:
                candlestick_chart = self._create_professional_candlestick(df, patterns, theme)
                if candlestick_chart:
                    charts.append(candlestick_chart)
            
            # 2. Interactive Time Series with Technical Indicators
            if patterns['has_timeseries']:
                timeseries_chart = self._create_interactive_timeseries(df, patterns, theme)
                if timeseries_chart:
                    charts.append(timeseries_chart)
            
            # 3. Volume Analysis Chart
            if patterns['has_volume']:
                volume_chart = self._create_volume_analysis(df, patterns, theme) 
                if volume_chart:
                    charts.append(volume_chart)
            
            # 4. Correlation Heatmap for multi-metric analysis
            if len(patterns['numeric_cols']) > 2:
                heatmap_chart = self._create_correlation_heatmap(df, patterns, theme)
                if heatmap_chart:
                    charts.append(heatmap_chart)
            
            # 5. Distribution Analysis
            distribution_chart = self._create_distribution_analysis(df, patterns, theme)
            if distribution_chart:
                charts.append(distribution_chart)
                
            print(f"✨ Generated {len(charts)} world-class visualizations")
            
            return {
                "status": "success",
                "chart_count": len(charts),
                "charts": charts,
                "data_insights": patterns['insights'],
                "theme": theme
            }
            
        except Exception as e:
            print(f"❌ Error in visualization engine: {e}")
            return self._create_error_response(str(e))
    
    def _parse_financial_data(self, data_text: str) -> Optional[pd.DataFrame]:
        """🔍 Advanced financial data parsing with intelligence"""
        try:
            lines = [line.strip() for line in data_text.strip().split('\n') if line.strip()]
            if len(lines) < 2:
                return None
                
            # Find header and data rows
            header_idx = 0
            for i, line in enumerate(lines):
                if '|' in line and any(keyword in line.lower() for keyword in 
                    ['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'price']):
                    header_idx = i
                    break
            
            # Extract header
            header_line = lines[header_idx]
            headers = [col.strip() for col in header_line.split('|')]
            
            # Extract data rows
            data_rows = []
            for line in lines[header_idx + 1:]:
                if '|' in line and not line.startswith('='):
                    row_data = [cell.strip() for cell in line.split('|')]
                    if len(row_data) == len(headers):
                        data_rows.append(row_data)
            
            if not data_rows:
                return None
                
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            
            # Smart type conversion
            for col in df.columns:
                col_lower = col.lower()
                
                # Date parsing
                if any(keyword in col_lower for keyword in ['date', 'time', 'day']):
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # Numeric parsing for financial data
                elif any(keyword in col_lower for keyword in 
                    ['price', 'open', 'high', 'low', 'close', 'volume', 'amount', 'value']):
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                
                # Try general numeric conversion
                else:
                    numeric_series = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                    if not numeric_series.isna().all():
                        df[col] = numeric_series
            
            return df.dropna(how='all')
            
        except Exception as e:
            print(f"❌ Data parsing error: {e}")
            return None
    
    def _detect_advanced_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """🧠 AI-level pattern detection for financial data"""
        patterns = {
            'numeric_cols': [],
            'date_cols': [],
            'categorical_cols': [],
            'has_ohlc': False,
            'has_timeseries': False,
            'has_volume': False,
            'chart_types': [],
            'insights': []
        }
        
        # Analyze columns
        for col in df.columns:
            col_lower = col.lower()
            
            if df[col].dtype in ['datetime64[ns]', 'object'] and pd.api.types.is_datetime64_any_dtype(df[col]):
                patterns['date_cols'].append(col)
            elif pd.api.types.is_numeric_dtype(df[col]):
                patterns['numeric_cols'].append(col)
            else:
                patterns['categorical_cols'].append(col)
        
        # Detect OHLC pattern
        ohlc_keywords = ['open', 'high', 'low', 'close']
        ohlc_matches = sum(1 for col in df.columns for keyword in ohlc_keywords 
                          if keyword in col.lower())
        patterns['has_ohlc'] = ohlc_matches >= 4
        
        # Detect time series
        patterns['has_timeseries'] = len(patterns['date_cols']) > 0 and len(patterns['numeric_cols']) > 0
        
        # Detect volume data
        volume_keywords = ['volume', 'vol', 'quantity', 'amount']
        patterns['has_volume'] = any(keyword in col.lower() 
                                   for col in df.columns for keyword in volume_keywords)
        
        # Suggest chart types
        if patterns['has_ohlc']:
            patterns['chart_types'].extend(['candlestick', 'ohlc'])
        if patterns['has_timeseries']:
            patterns['chart_types'].append('timeseries')
        if patterns['has_volume']:
            patterns['chart_types'].append('volume')
        if len(patterns['numeric_cols']) > 2:
            patterns['chart_types'].extend(['correlation', 'heatmap'])
        
        patterns['chart_types'].append('distribution')
        
        # Generate insights
        patterns['insights'] = [
            f"Dataset contains {len(df)} data points",
            f"Identified {len(patterns['numeric_cols'])} numeric metrics",
            f"Time series data: {'✅' if patterns['has_timeseries'] else '❌'}",
            f"OHLC financial data: {'✅' if patterns['has_ohlc'] else '❌'}",
            f"Volume data: {'✅' if patterns['has_volume'] else '❌'}"
        ]
        
        return patterns
    
    def _create_professional_candlestick(self, df: pd.DataFrame, patterns: Dict, theme: str) -> Dict[str, Any]:
        """📊 Create professional candlestick chart with Plotly"""
        try:
            # Map OHLC columns
            ohlc_cols = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'open' in col_lower:
                    ohlc_cols['open'] = col
                elif 'high' in col_lower:
                    ohlc_cols['high'] = col
                elif 'low' in col_lower:
                    ohlc_cols['low'] = col
                elif 'close' in col_lower:
                    ohlc_cols['close'] = col
            
            if len(ohlc_cols) < 4:
                numeric_cols = patterns['numeric_cols'][:4]
                ohlc_mapping = ['open', 'high', 'low', 'close']
                ohlc_cols = {ohlc_mapping[i]: col for i, col in enumerate(numeric_cols)}
            
            # Create candlestick chart
            fig = go.Figure(data=go.Candlestick(
                x=df.index if not patterns['date_cols'] else df[patterns['date_cols'][0]],
                open=df[ohlc_cols['open']],
                high=df[ohlc_cols['high']],
                low=df[ohlc_cols['low']],
                close=df[ohlc_cols['close']],
                increasing_line_color=self.bull_color,
                decreasing_line_color=self.bear_color,
                name='OHLC'
            ))
            
            # Apply professional styling
            fig.update_layout(
                title={
                    'text': '📈 Professional OHLC Analysis',
                    'x': 0.5,
                    'font': {'size': 20, 'color': self.themes[theme]['text_color']}
                },
                xaxis_title='Time Period',
                yaxis_title='Price',
                template='plotly_white' if theme == 'light' else 'plotly_dark',
                plot_bgcolor=self.themes[theme]['bg_color'],
                paper_bgcolor=self.themes[theme]['paper_bg'],
                font={'color': self.themes[theme]['text_color']},
                showlegend=True,
                height=600
            )
            
            # Convert to base64 for embedding
            html_str = fig.to_html(include_plotlyjs='cdn')
            chart_b64 = base64.b64encode(html_str.encode()).decode()
            
            return {
                'type': 'candlestick',
                'title': 'Professional OHLC Analysis',
                'html_content': html_str,
                'base64_data': chart_b64,
                'insights': [
                    f"Analyzed {len(df)} trading periods",
                    f"Price range: {df[ohlc_cols['low']].min():.2f} - {df[ohlc_cols['high']].max():.2f}",
                    f"Latest close: {df[ohlc_cols['close']].iloc[-1]:.2f}"
                ]
            }
            
        except Exception as e:
            print(f"❌ Candlestick chart error: {e}")
            return None
    
    def _create_interactive_timeseries(self, df: pd.DataFrame, patterns: Dict, theme: str) -> Dict[str, Any]:
        """📈 Create interactive time series with technical indicators"""
        try:
            date_col = patterns['date_cols'][0] if patterns['date_cols'] else None
            x_data = df[date_col] if date_col else df.index
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=('Price Movement', 'Volume Analysis'),
                row_heights=[0.7, 0.3]
            )
            
            # Main price line
            main_metric = patterns['numeric_cols'][0]
            fig.add_trace(
                go.Scatter(
                    x=x_data,
                    y=df[main_metric],
                    mode='lines',
                    name=main_metric,
                    line=dict(color=self.bull_color, width=3),
                    hovertemplate='<b>%{y:.2f}</b><br>%{x}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Add moving average if enough data
            if len(df) >= 5:
                ma_5 = df[main_metric].rolling(window=min(5, len(df))).mean()
                fig.add_trace(
                    go.Scatter(
                        x=x_data,
                        y=ma_5,
                        mode='lines',
                        name='MA(5)',
                        line=dict(color=self.neutral_color, width=2, dash='dash'),
                        opacity=0.7
                    ),
                    row=1, col=1
                )
            
            # Volume chart if available
            volume_col = None
            for col in df.columns:
                if 'volume' in col.lower() or 'vol' in col.lower():
                    volume_col = col
                    break
            
            if volume_col:
                fig.add_trace(
                    go.Bar(
                        x=x_data,
                        y=df[volume_col],
                        name='Volume',
                        marker_color=self.neutral_color,
                        opacity=0.6
                    ),
                    row=2, col=1
                )
            
            # Professional styling
            fig.update_layout(
                title={
                    'text': '📊 Interactive Financial Time Series',
                    'x': 0.5,
                    'font': {'size': 20, 'color': self.themes[theme]['text_color']}
                },
                template='plotly_white' if theme == 'light' else 'plotly_dark',
                plot_bgcolor=self.themes[theme]['bg_color'],
                paper_bgcolor=self.themes[theme]['paper_bg'],
                font={'color': self.themes[theme]['text_color']},
                showlegend=True,
                height=700,
                hovermode='x unified'
            )
            
            html_str = fig.to_html(include_plotlyjs='cdn')
            chart_b64 = base64.b64encode(html_str.encode()).decode()
            
            return {
                'type': 'timeseries',
                'title': 'Interactive Financial Time Series',
                'html_content': html_str,
                'base64_data': chart_b64,
                'insights': [
                    f"Time series with {len(df)} data points",
                    f"Trend: {'📈 Upward' if df[main_metric].iloc[-1] > df[main_metric].iloc[0] else '📉 Downward'}",
                    f"Volatility: {df[main_metric].std():.2f}"
                ]
            }
            
        except Exception as e:
            print(f"❌ Time series chart error: {e}")
            return None
    
    def _create_volume_analysis(self, df: pd.DataFrame, patterns: Dict, theme: str) -> Dict[str, Any]:
        """📊 Create advanced volume analysis chart"""
        try:
            volume_col = None
            price_col = None
            
            for col in df.columns:
                if 'volume' in col.lower() or 'vol' in col.lower():
                    volume_col = col
                if 'close' in col.lower() or 'price' in col.lower():
                    price_col = col
            
            if not volume_col:
                return None
                
            if not price_col:
                price_col = patterns['numeric_cols'][0]
            
            # Create correlation analysis
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Volume Bars', 'Price vs Volume', 'Volume Distribution', 'Volume Trend'),
                specs=[[{}, {}], [{}, {}]]
            )
            
            x_data = df.index
            if patterns['date_cols']:
                x_data = df[patterns['date_cols'][0]]
            
            # 1. Volume bars
            colors = [self.bull_color if df[price_col].iloc[i] >= df[price_col].iloc[i-1] 
                     else self.bear_color for i in range(1, len(df))]
            colors.insert(0, self.neutral_color)
            
            fig.add_trace(
                go.Bar(x=x_data, y=df[volume_col], marker_color=colors, name='Volume'),
                row=1, col=1
            )
            
            # 2. Price vs Volume scatter
            fig.add_trace(
                go.Scatter(
                    x=df[volume_col], y=df[price_col], mode='markers',
                    marker=dict(size=8, color=self.bull_color, opacity=0.6),
                    name='Price vs Volume'
                ),
                row=1, col=2
            )
            
            # 3. Volume distribution
            fig.add_trace(
                go.Histogram(x=df[volume_col], nbinsx=20, marker_color=self.neutral_color, name='Distribution'),
                row=2, col=1
            )
            
            # 4. Volume moving average
            vol_ma = df[volume_col].rolling(window=min(5, len(df))).mean()
            fig.add_trace(
                go.Scatter(x=x_data, y=vol_ma, mode='lines', 
                          line=dict(color=self.bull_color, width=3), name='Volume MA'),
                row=2, col=2
            )
            
            fig.update_layout(
                title={
                    'text': '📈 Advanced Volume Analysis',
                    'x': 0.5,
                    'font': {'size': 20, 'color': self.themes[theme]['text_color']}
                },
                template='plotly_white' if theme == 'light' else 'plotly_dark',
                plot_bgcolor=self.themes[theme]['bg_color'],
                paper_bgcolor=self.themes[theme]['paper_bg'],
                font={'color': self.themes[theme]['text_color']},
                showlegend=True,
                height=800
            )
            
            html_str = fig.to_html(include_plotlyjs='cdn')
            chart_b64 = base64.b64encode(html_str.encode()).decode()
            
            return {
                'type': 'volume_analysis',
                'title': 'Advanced Volume Analysis', 
                'html_content': html_str,
                'base64_data': chart_b64,
                'insights': [
                    f"Total volume: {df[volume_col].sum():,.0f}",
                    f"Average volume: {df[volume_col].mean():,.0f}",
                    f"Volume trend: {'📈 Increasing' if vol_ma.iloc[-1] > vol_ma.iloc[0] else '📉 Decreasing'}"
                ]
            }
            
        except Exception as e:
            print(f"❌ Volume analysis error: {e}")
            return None
    
    def _create_correlation_heatmap(self, df: pd.DataFrame, patterns: Dict, theme: str) -> Dict[str, Any]:
        """🔥 Create beautiful correlation heatmap"""
        try:
            # Select numeric columns
            numeric_df = df[patterns['numeric_cols']].corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=numeric_df.values,
                x=numeric_df.columns,
                y=numeric_df.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(numeric_df.values, 2),
                texttemplate='%{text}',
                textfont={'size': 12},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title={
                    'text': '🔥 Correlation Heatmap Analysis',
                    'x': 0.5,
                    'font': {'size': 20, 'color': self.themes[theme]['text_color']}
                },
                template='plotly_white' if theme == 'light' else 'plotly_dark',
                plot_bgcolor=self.themes[theme]['bg_color'],
                paper_bgcolor=self.themes[theme]['paper_bg'],
                font={'color': self.themes[theme]['text_color']},
                height=600
            )
            
            html_str = fig.to_html(include_plotlyjs='cdn')
            chart_b64 = base64.b64encode(html_str.encode()).decode()
            
            # Find strongest correlations
            correlations = []
            for i in range(len(numeric_df.columns)):
                for j in range(i+1, len(numeric_df.columns)):
                    corr_val = numeric_df.iloc[i, j]
                    if abs(corr_val) > 0.5:
                        correlations.append(f"{numeric_df.columns[i]} ↔ {numeric_df.columns[j]}: {corr_val:.2f}")
            
            return {
                'type': 'correlation',
                'title': 'Correlation Heatmap Analysis',
                'html_content': html_str,
                'base64_data': chart_b64,
                'insights': [
                    f"Analyzed {len(patterns['numeric_cols'])} metrics",
                    "Strong correlations:" if correlations else "No strong correlations found",
                    *correlations[:3]  # Top 3 correlations
                ]
            }
            
        except Exception as e:
            print(f"❌ Correlation heatmap error: {e}")
            return None
    
    def _create_distribution_analysis(self, df: pd.DataFrame, patterns: Dict, theme: str) -> Dict[str, Any]:
        """📊 Create distribution analysis with box plots and histograms"""
        try:
            main_metric = patterns['numeric_cols'][0]
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    f'{main_metric} Distribution',
                    f'{main_metric} Box Plot', 
                    'Q-Q Plot',
                    'Descriptive Statistics'
                ),
                specs=[[{}, {}], [{}, {"type": "table"}]]
            )
            
            # 1. Histogram with KDE
            fig.add_trace(
                go.Histogram(
                    x=df[main_metric],
                    nbinsx=20,
                    marker_color=self.bull_color,
                    opacity=0.7,
                    name='Distribution'
                ),
                row=1, col=1
            )
            
            # 2. Box plot
            fig.add_trace(
                go.Box(
                    y=df[main_metric],
                    name=main_metric,
                    marker_color=self.neutral_color,
                    boxpoints='outliers'
                ),
                row=1, col=2
            )
            
            # 3. Q-Q plot approximation
            sorted_data = np.sort(df[main_metric].dropna())
            n = len(sorted_data)
            theoretical_quantiles = np.linspace(0.01, 0.99, n)
            normal_quantiles = np.percentile(sorted_data, theoretical_quantiles * 100)
            
            fig.add_trace(
                go.Scatter(
                    x=theoretical_quantiles,
                    y=normal_quantiles,
                    mode='markers',
                    marker=dict(color=self.bear_color, size=6),
                    name='Q-Q Plot'
                ),
                row=2, col=1
            )
            
            # 4. Statistics table
            stats = df[main_metric].describe()
            fig.add_trace(
                go.Table(
                    header=dict(values=['Statistic', 'Value'],
                               fill_color=self.themes[theme]['paper_bg']),
                    cells=dict(values=[
                        ['Mean', 'Std', 'Min', 'Max', 'Median', 'Skewness'],
                        [f"{stats['mean']:.2f}", f"{stats['std']:.2f}", 
                         f"{stats['min']:.2f}", f"{stats['max']:.2f}",
                         f"{stats['50%']:.2f}", f"{df[main_metric].skew():.2f}"]
                    ],
                    fill_color=self.themes[theme]['bg_color'])
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title={
                    'text': f'📊 {main_metric} Distribution Analysis',
                    'x': 0.5,
                    'font': {'size': 20, 'color': self.themes[theme]['text_color']}
                },
                template='plotly_white' if theme == 'light' else 'plotly_dark',
                plot_bgcolor=self.themes[theme]['bg_color'],
                paper_bgcolor=self.themes[theme]['paper_bg'],
                font={'color': self.themes[theme]['text_color']},
                showlegend=True,
                height=800
            )
            
            html_str = fig.to_html(include_plotlyjs='cdn')
            chart_b64 = base64.b64encode(html_str.encode()).decode()
            
            return {
                'type': 'distribution',
                'title': f'{main_metric} Distribution Analysis',
                'html_content': html_str,
                'base64_data': chart_b64,
                'insights': [
                    f"Mean: {stats['mean']:.2f}",
                    f"Standard Deviation: {stats['std']:.2f}",
                    f"Range: {stats['min']:.2f} - {stats['max']:.2f}",
                    f"Distribution: {'Right-skewed' if df[main_metric].skew() > 0.5 else 'Left-skewed' if df[main_metric].skew() < -0.5 else 'Normal'}"
                ]
            }
            
        except Exception as e:
            print(f"❌ Distribution analysis error: {e}")
            return None
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "message": error_msg,
            "chart_count": 0,
            "charts": []
        }

# Global instance for easy access
world_class_visualizer = WorldClassFinancialVisualizer()