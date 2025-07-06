#!/usr/bin/env python3
"""
Enhanced MCP Server for Stock Database Access + Document Analysis
Connects to MySQL database containing historical stock prices
Provides PDF document analysis for fundamental insights
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import json

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent
import mcp.types as types

# Add PDF processing capability
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stock-mcp-server")

# Load environment variables (optional)
try:
    load_dotenv()
except UnicodeDecodeError:
    logger.warning("Could not load .env file due to encoding issues. Using fallback configuration.")

class StockMCPServer:
    def __init__(self):
        self.server = Server("stock-database-server")
        self.engine = None
        
        # Use absolute path relative to this script's location
        script_dir = Path(__file__).parent
        self.documents_dir = script_dir / "data"  # Directory for PDF documents
        
        # Create documents directory if it doesn't exist
        self.documents_dir.mkdir(exist_ok=True)
        
        # Setup handlers after server is created
        self.setup_handlers()
        
        logger.info(f"StockMCPServer initialized successfully - Documents dir: {self.documents_dir}")
        
    def get_database_url(self) -> str:
        """Get database URL from environment or use fallback"""
        try:
            database_url = os.getenv('DATABASE_URL')
            
            # Fallback to hardcoded URL if env var is not available
            if not database_url:
                # Use the same format that works in your other apps
                database_url = ""
                logger.info("Using fallback database URL (DATABASE_URL environment variable not found)")
            else:
                logger.info("Using DATABASE_URL from environment")
            
            # Clean up the URL (remove quotes if present)
            database_url = database_url.strip('"\'')
            
            # Convert mysql:// to mysql+pymysql:// for SQLAlchemy compatibility
            if database_url.startswith('mysql://'):
                database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
                logger.info("Converted mysql:// to mysql+pymysql:// for SQLAlchemy")
            
            return database_url
        
        except Exception as e:
            logger.error(f"Error getting database URL: {e}")
            # Return fallback URL
            return ""
    
    async def connect_database(self):
        """Connect to the MySQL database"""
        try:
            database_url = self.get_database_url()
            logger.info(f"Connecting to database...")
            
            # Create the engine
            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False  # Set to True for SQL debugging
            )
            
            # Test the connection
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def setup_handlers(self):
        """Set up MCP protocol handlers"""
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            tools = [
                Tool(
                    name="get_stock_info",
                    description="Get basic information about a stock including company details, price ranges, and volume data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock symbol (e.g. RELIANCE, TCS)"
                            }
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="get_price_history",
                    description="Get historical price data with technical indicators (RSI) for a stock",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock symbol (e.g. RELIANCE, TCS)"
                            },
                            "period": {
                                "type": "string",
                                "enum": ["daily", "weekly"],
                                "description": "Time period for price data",
                                "default": "daily"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format (optional)"
                            },
                            "end_date": {
                                "type": "string", 
                                "description": "End date in YYYY-MM-DD format (optional)"
                            }
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="search_stocks",
                    description="Search for stocks by symbol pattern or company name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Search pattern (part of symbol or company name)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["pattern"]
                    }
                ),
                Tool(
                    name="get_advanced_metrics",
                    description="Get comprehensive technical and risk metrics for a stock (beta, volatility, Sharpe ratio, RSI, MACD, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock symbol (e.g. RELIANCE, TCS)"
                            },
                            "timeframe": {
                                "type": "string",
                                "enum": ["short", "medium", "long"],
                                "description": "Analysis timeframe",
                                "default": "medium"
                            }
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="screen_stocks_by_metrics",
                    description="Screen stocks based on advanced metrics criteria (risk, return, technical indicators)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "criteria": {
                                "type": "object",
                                "description": "Screening criteria",
                                "properties": {
                                    "sector": {"type": "string", "description": "Filter by sector"},
                                    "timeframe": {"type": "string", "enum": ["short", "medium", "long"], "default": "medium"},
                                    "min_sharpe_ratio": {"type": "number", "description": "Minimum Sharpe ratio"},
                                    "max_volatility": {"type": "number", "description": "Maximum volatility"},
                                    "min_rsi": {"type": "number", "description": "Minimum RSI (oversold threshold)"},
                                    "max_rsi": {"type": "number", "description": "Maximum RSI (overbought threshold)"},
                                    "limit": {"type": "integer", "default": 20, "description": "Maximum results"}
                                }
                            }
                        },
                        "required": ["criteria"]
                    }
                )
            ]
            
            # Add PDF tools if PyMuPDF is available
            if PDF_AVAILABLE:
                pdf_tools = [
                    Tool(
                        name="analyze_document",
                        description="Extract and analyze text content from PDF documents (earnings reports, transcripts, etc.)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "Name of the PDF file in the data directory"
                                },
                                "output_format": {
                                    "type": "string",
                                    "enum": ["text", "json", "html", "structured"],
                                    "description": "Output format for extracted content",
                                    "default": "structured"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "enum": ["summary", "financial_highlights", "full_text", "key_metrics"],
                                    "description": "Type of analysis to perform",
                                    "default": "summary"
                                }
                            },
                            "required": ["filename"]
                        }
                    ),
                    Tool(
                        name="list_documents",
                        description="List all available PDF documents in the data directory",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_company_fundamentals",
                        description="Extract fundamental analysis from company documents (combine stock data with document insights)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol to analyze"
                                },
                                "document_pattern": {
                                    "type": "string",
                                    "description": "Pattern to match relevant documents (optional)",
                                    "default": ""
                                }
                            },
                            "required": ["symbol"]
                        }
                    ),
                    Tool(
                        name="find_company_documents",
                        description="Show which documents are available for a specific stock symbol (useful for debugging document matching)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol to search documents for"
                                }
                            },
                            "required": ["symbol"]
                        }
                    )
                ]
                tools.extend(pdf_tools)
            
            return tools
            
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_stock_info":
                    return await self.get_stock_info(arguments.get("symbol"))
                elif name == "get_price_history":
                    return await self.get_price_history(
                        arguments.get("symbol"),
                        arguments.get("period", "daily"),
                        arguments.get("start_date"),
                        arguments.get("end_date")
                    )
                elif name == "search_stocks":
                    return await self.search_stocks(
                        arguments.get("pattern"),
                        arguments.get("limit", 10)
                    )
                elif name == "get_advanced_metrics":
                    return await self.get_advanced_metrics(
                        arguments.get("symbol"),
                        arguments.get("timeframe", "medium")
                    )
                elif name == "screen_stocks_by_metrics":
                    return await self.screen_stocks_by_metrics(
                        arguments.get("criteria", {})
                    )
                elif name == "analyze_document" and PDF_AVAILABLE:
                    return await self.analyze_document(
                        arguments.get("filename"),
                        arguments.get("output_format", "structured"),
                        arguments.get("analysis_type", "summary")
                    )
                elif name == "list_documents" and PDF_AVAILABLE:
                    return await self.list_documents()
                elif name == "get_company_fundamentals" and PDF_AVAILABLE:
                    return await self.get_company_fundamentals(
                        arguments.get("symbol"),
                        arguments.get("document_pattern", "")
                    )
                elif name == "find_company_documents" and PDF_AVAILABLE:
                    return await self.find_company_documents(
                        arguments.get("symbol")
                    )
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

    async def get_stock_info(self, symbol: str) -> list[TextContent]:
        """Get basic stock information"""
        try:
            with self.engine.connect() as connection:
                # Get stock info with price history summary
                query = text("""
                SELECT s.symbol, s.companyName, s.sector, s.instrumentToken,
                       COUNT(ph.id) as total_records,
                       MIN(ph.date) as earliest_date,
                       MAX(ph.date) as latest_date,
                       MAX(ph.close) as max_price,
                       MIN(ph.close) as min_price,
                       AVG(ph.volume) as avg_volume
                FROM Stock s
                LEFT JOIN PriceHistory ph ON s.id = ph.stockId
                WHERE s.symbol = :symbol
                GROUP BY s.id, s.symbol, s.companyName, s.sector, s.instrumentToken
                """)
                
                result = connection.execute(query, {"symbol": symbol.upper()}).fetchone()
                
                if result and result.total_records > 0:
                    info = f"""Stock Information for {symbol.upper()}:
- Company: {result.companyName}
- Sector: {result.sector}
- Total Price Records: {result.total_records}
- Data Range: {result.earliest_date} to {result.latest_date}
- Price Range: ${result.min_price:.2f} - ${result.max_price:.2f}
- Average Volume: {int(result.avg_volume):,}
- Instrument Token: {result.instrumentToken or 'N/A'}
"""
                elif result:
                    info = f"""Stock found but no price history:
- Company: {result.companyName}
- Sector: {result.sector}
- Symbol: {symbol.upper()}
"""
                else:
                    info = f"No data found for stock symbol: {symbol.upper()}"
                
                return [TextContent(type="text", text=info)]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_stock_info: {e}")
            return [TextContent(type="text", text=f"Database error: {str(e)}")]
    
    async def get_price_history(self, symbol: str, period: str, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None) -> list[TextContent]:
        """Get historical price data"""
        try:
            with self.engine.connect() as connection:
                
                if period == "weekly":
                    # Query weekly data with moving averages
                    query = text("""
                    SELECT wph.weekEnding as date, wph.open, wph.high, wph.low, wph.close, wph.volume,
                           wsm.sma_20, wsm.sma_50, wsm.sma_100, wsm.sma_200
                    FROM Stock s
                    JOIN WeeklyPriceHistory wph ON s.id = wph.stockId
                    LEFT JOIN WeeklyStockMetrics wsm ON s.id = wsm.stockId AND wph.weekEnding = wsm.weekEnding
                    WHERE s.symbol = :symbol
                    """)
                    params = {"symbol": symbol.upper()}
                    
                    if start_date:
                        query = text(str(query) + " AND wph.weekEnding >= :start_date")
                        params["start_date"] = start_date
                    if end_date:
                        query = text(str(query) + " AND wph.weekEnding <= :end_date")
                        params["end_date"] = end_date
                        
                    query = text(str(query) + " ORDER BY wph.weekEnding DESC LIMIT 100")
                    
                else:
                    # Query daily data with RSI indicators
                    query = text("""
                    SELECT ph.date, ph.open, ph.high, ph.low, ph.close, ph.volume, ph.rsi30, ph.rsi20
                    FROM Stock s
                    JOIN PriceHistory ph ON s.id = ph.stockId
                    WHERE s.symbol = :symbol
                    """)
                    params = {"symbol": symbol.upper()}
                    
                    if start_date:
                        query = text(str(query) + " AND ph.date >= :start_date")
                        params["start_date"] = start_date
                    if end_date:
                        query = text(str(query) + " AND ph.date <= :end_date")
                        params["end_date"] = end_date
                        
                    query = text(str(query) + " ORDER BY ph.date DESC LIMIT 100")
                
                results = connection.execute(query, params).fetchall()
                
                if results:
                    # Format the results
                    data_text = f"Price History for {symbol.upper()} ({period}):\n\n"
                    
                    if period == "daily":
                        data_text += "Date       | Open    | High    | Low     | Close   | Volume     | RSI30   | RSI20\n"
                        data_text += "-" * 85 + "\n"
                        
                        for row in results:
                            rsi30 = f"{row.rsi30:6.2f}" if row.rsi30 else "  N/A "
                            rsi20 = f"{row.rsi20:6.2f}" if row.rsi20 else "  N/A "
                            data_text += f"{row.date} | {row.open:7.2f} | {row.high:7.2f} | {row.low:7.2f} | {row.close:7.2f} | {row.volume:>10} | {rsi30} | {rsi20}\n"
                    else:
                        # Weekly data with moving averages
                        data_text += "Week Ending| Open    | High    | Low     | Close   | Volume     | SMA20   | SMA50   | SMA100  | SMA200\n"
                        data_text += "-" * 105 + "\n"
                        
                        for row in results:
                            volume = row.volume if row.volume else 0
                            sma20 = f"{row.sma_20:7.2f}" if row.sma_20 else "   N/A "
                            sma50 = f"{row.sma_50:7.2f}" if row.sma_50 else "   N/A "
                            sma100 = f"{row.sma_100:6.2f}" if row.sma_100 else "  N/A "
                            sma200 = f"{row.sma_200:6.2f}" if row.sma_200 else "  N/A "
                            data_text += f"{row.date} | {row.open:7.2f} | {row.high:7.2f} | {row.low:7.2f} | {row.close:7.2f} | {row.volume:>10} | {sma20} | {sma50} | {sma100} | {sma200}\n"
                else:
                    data_text = f"No {period} price data found for {symbol.upper()}"
                
                return [TextContent(type="text", text=data_text)]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_price_history: {e}")
            return [TextContent(type="text", text=f"Database error: {str(e)}")]
    
    async def search_stocks(self, pattern: str, limit: int) -> list[TextContent]:
        """Search for stocks by symbol pattern or company name"""
        try:
            with self.engine.connect() as connection:
                query = text("""
                SELECT symbol, companyName, sector
                FROM Stock 
                WHERE symbol LIKE :pattern OR companyName LIKE :pattern
                ORDER BY symbol
                LIMIT :limit
                """)
                
                search_pattern = f"%{pattern.upper()}%"
                results = connection.execute(query, {
                    "pattern": search_pattern, 
                    "limit": limit
                }).fetchall()
                
                if results:
                    result_text = f"Found {len(results)} stocks matching '{pattern}':\n\n"
                    result_text += "Symbol     | Company Name                           | Sector\n"
                    result_text += "-" * 75 + "\n"
                    
                    for row in results:
                        company_name = row.companyName[:35] + "..." if len(row.companyName) > 35 else row.companyName
                        result_text += f"{row.symbol:<10} | {company_name:<37} | {row.sector}\n"
                else:
                    result_text = f"No stocks found matching pattern: {pattern}"
                
                return [TextContent(type="text", text=result_text)]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in search_stocks: {e}")
            return [TextContent(type="text", text=f"Database error: {str(e)}")]

    async def get_advanced_metrics(self, symbol: str, timeframe: str) -> list[TextContent]:
        """Get advanced technical and risk metrics for a stock"""
        try:
            with self.engine.connect() as connection:
                # Get the latest metrics for the stock
                query = text(f"""
                SELECT s.symbol, s.companyName, s.sector,
                       asm.calculatedAt,
                       asm.beta_{timeframe},
                       asm.volatility_{timeframe},
                       asm.sharpe_{timeframe},
                       asm.momentum_{timeframe},
                       asm.total_return_{timeframe},
                       asm.annualized_return_{timeframe},
                       asm.max_drawdown_{timeframe},
                       asm.win_rate_{timeframe},
                       asm.sortino_ratio_{timeframe},
                       asm.rsi_14, asm.rsi_20, asm.rsi_30,
                       asm.bb_upper, asm.bb_lower, asm.bb_position,
                       asm.macd, asm.macd_signal, asm.macd_histogram,
                       asm.atr, asm.atr_percent
                FROM Stock s
                JOIN AdvancedStockMetrics asm ON s.id = asm.stockId
                WHERE s.symbol = :symbol
                ORDER BY asm.calculatedAt DESC
                LIMIT 1
                """)
                
                result = connection.execute(query, {"symbol": symbol.upper()}).fetchone()
                
                if result:
                    metrics_text = f"""Advanced Metrics for {symbol.upper()} ({timeframe} timeframe):
Company: {result.companyName} | Sector: {result.sector}
Calculated: {result.calculatedAt}

RISK & RETURN METRICS:
- Beta: {getattr(result, f'beta_{timeframe}'):.4f} (Market correlation)
- Volatility: {getattr(result, f'volatility_{timeframe}'):.4f} ({getattr(result, f'volatility_{timeframe}')*100:.2f}%)
- Sharpe Ratio: {getattr(result, f'sharpe_{timeframe}'):.4f} (Risk-adjusted return)
- Sortino Ratio: {getattr(result, f'sortino_ratio_{timeframe}'):.4f} (Downside risk-adjusted)
- Max Drawdown: {getattr(result, f'max_drawdown_{timeframe}'):.4f} ({getattr(result, f'max_drawdown_{timeframe}')*100:.2f}%)

PERFORMANCE METRICS:
- Total Return: {getattr(result, f'total_return_{timeframe}'):.4f} ({getattr(result, f'total_return_{timeframe}')*100:.2f}%)
- Annualized Return: {getattr(result, f'annualized_return_{timeframe}'):.4f} ({getattr(result, f'annualized_return_{timeframe}')*100:.2f}%)
- Momentum: {getattr(result, f'momentum_{timeframe}'):.4f}
- Win Rate: {getattr(result, f'win_rate_{timeframe}'):.4f} ({getattr(result, f'win_rate_{timeframe}')*100:.1f}%)

TECHNICAL INDICATORS:
- RSI (14): {result.rsi_14:.2f} | RSI (20): {result.rsi_20:.2f} | RSI (30): {result.rsi_30:.2f}
- Bollinger Position: {result.bb_position:.4f} (0=lower band, 1=upper band)
- MACD: {result.macd:.4f} | Signal: {result.macd_signal:.4f} | Histogram: {result.macd_histogram:.4f}
- ATR: {result.atr:.4f} | ATR%: {result.atr_percent:.4f} ({result.atr_percent*100:.2f}%)
"""
                else:
                    metrics_text = f"No advanced metrics found for {symbol.upper()}"
                
                return [TextContent(type="text", text=metrics_text)]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_advanced_metrics: {e}")
            return [TextContent(type="text", text=f"Database error: {str(e)}")]

    async def screen_stocks_by_metrics(self, criteria: Dict[str, Any]) -> list[TextContent]:
        """Screen stocks based on advanced metrics criteria"""
        try:
            with self.engine.connect() as connection:
                timeframe = criteria.get("timeframe", "medium")
                
                # Build dynamic query based on criteria
                base_query = f"""
                SELECT s.symbol, s.companyName, s.sector,
                       asm.sharpe_{timeframe} as sharpe_ratio,
                       asm.volatility_{timeframe} as volatility,
                       asm.total_return_{timeframe} as total_return,
                       asm.rsi_14, asm.beta_{timeframe} as beta,
                       asm.max_drawdown_{timeframe} as max_drawdown
                FROM Stock s
                JOIN AdvancedStockMetrics asm ON s.id = asm.stockId
                WHERE 1=1
                """
                
                params = {}
                conditions = []
                
                # Add filters based on criteria
                if criteria.get("sector"):
                    conditions.append(" AND s.sector = :sector")
                    params["sector"] = criteria["sector"]
                
                if criteria.get("min_sharpe_ratio") is not None:
                    conditions.append(f" AND asm.sharpe_{timeframe} >= :min_sharpe")
                    params["min_sharpe"] = criteria["min_sharpe_ratio"]
                
                if criteria.get("max_volatility") is not None:
                    conditions.append(f" AND asm.volatility_{timeframe} <= :max_vol")
                    params["max_vol"] = criteria["max_volatility"]
                
                if criteria.get("min_rsi") is not None:
                    conditions.append(" AND asm.rsi_14 >= :min_rsi")
                    params["min_rsi"] = criteria["min_rsi"]
                
                if criteria.get("max_rsi") is not None:
                    conditions.append(" AND asm.rsi_14 <= :max_rsi")
                    params["max_rsi"] = criteria["max_rsi"]
                
                # Build final query
                query_str = base_query + "".join(conditions)
                query_str += f" ORDER BY asm.sharpe_{timeframe} DESC"
                query_str += f" LIMIT {criteria.get('limit', 20)}"
                
                query = text(query_str)
                results = connection.execute(query, params).fetchall()
                
                if results:
                    screen_text = f"Stock Screening Results ({timeframe} timeframe):\n"
                    screen_text += f"Found {len(results)} stocks matching criteria\n\n"
                    screen_text += "Symbol     | Company                    | Sector      | Sharpe | Vol%   | Return% | RSI | Beta\n"
                    screen_text += "-" * 95 + "\n"
                    
                    for row in results:
                        company = row.companyName[:25] + "..." if len(row.companyName) > 25 else row.companyName
                        sector = row.sector[:10] + "..." if len(row.sector) > 10 else row.sector
                        
                        screen_text += f"{row.symbol:<10} | {company:<25} | {sector:<10} | {row.sharpe_ratio:6.2f} | {row.volatility*100:5.1f} | {row.total_return*100:6.1f} | {row.rsi_14:4.0f} | {row.beta:4.2f}\n"
                else:
                    screen_text = "No stocks found matching the specified criteria"
                
                return [TextContent(type="text", text=screen_text)]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in screen_stocks_by_metrics: {e}")
            return [TextContent(type="text", text=f"Database error: {str(e)}")]

    async def analyze_document(self, filename: str, output_format: str, analysis_type: str) -> list[TextContent]:
        """Extract and analyze text content from a PDF document"""
        try:
            if not PDF_AVAILABLE:
                return [TextContent(type="text", text="PDF processing not available. Please install PyMuPDF: pip install pymupdf")]
            
            # Build file path
            file_path = self.documents_dir / filename
            if not file_path.exists():
                return [TextContent(type="text", text=f"File not found: {filename}")]
            
            # Open and extract content from PDF
            doc = fitz.open(str(file_path))
            
            if analysis_type == "full_text":
                # Extract all text
                all_text = ""
                for page_num, page in enumerate(doc):
                    all_text += f"\n--- Page {page_num + 1} ---\n"
                    all_text += page.get_text()
                
                doc.close()
                return [TextContent(type="text", text=all_text)]
            
            elif analysis_type == "summary":
                # Extract first few pages for summary
                summary_text = f"Document Analysis Summary for {filename}\n"
                summary_text += f"Total Pages: {len(doc)}\n\n"
                
                # Extract first 3 pages
                for page_num in range(min(3, len(doc))):
                    page = doc[page_num]
                    page_text = page.get_text()
                    if page_text.strip():
                        summary_text += f"Page {page_num + 1} Summary:\n"
                        # Take first 500 characters as summary
                        summary_text += page_text[:500] + "...\n\n"
                
                doc.close()
                return [TextContent(type="text", text=summary_text)]
            
            elif analysis_type == "financial_highlights":
                # Look for financial keywords and extract relevant sections
                financial_keywords = [
                    "revenue", "profit", "earnings", "ebitda", "margin", "growth",
                    "cash flow", "debt", "equity", "roi", "roe", "eps", "dividend",
                    "net income", "gross profit", "operating profit", "balance sheet",
                    "financial", "quarter", "fy", "guidance", "outlook"
                ]
                
                highlights = f"Financial Highlights from {filename}\n"
                highlights += "=" * 50 + "\n\n"
                
                for page_num, page in enumerate(doc):
                    page_text = page.get_text().lower()
                    
                    # Find paragraphs containing financial keywords
                    paragraphs = page_text.split('\n\n')
                    for para in paragraphs:
                        if any(keyword in para for keyword in financial_keywords):
                            if len(para.strip()) > 50:  # Only meaningful paragraphs
                                highlights += f"[Page {page_num + 1}] {para.strip()[:300]}...\n\n"
                
                doc.close()
                return [TextContent(type="text", text=highlights)]
            
            elif analysis_type == "key_metrics":
                # Extract structured data if available (tables, numbers)
                metrics_text = f"Key Metrics from {filename}\n"
                metrics_text += "=" * 40 + "\n\n"
                
                for page_num, page in enumerate(doc):
                    # Try to extract tables
                    tables = page.find_tables()
                    if tables:
                        metrics_text += f"Page {page_num + 1} - Tables Found:\n"
                        for table_num, table in enumerate(tables):
                            table_data = table.extract()
                            metrics_text += f"Table {table_num + 1}:\n"
                            for row in table_data[:5]:  # First 5 rows
                                metrics_text += " | ".join(str(cell) for cell in row if cell) + "\n"
                            metrics_text += "\n"
                    
                    # Extract text with numbers/percentages
                    page_text = page.get_text()
                    import re
                    number_patterns = re.findall(r'[\d,]+\.?\d*%?(?:\s*(?:cr|crore|million|billion|lakh))?', page_text)
                    if number_patterns:
                        metrics_text += f"Page {page_num + 1} - Key Numbers: {', '.join(number_patterns[:10])}\n\n"
                
                doc.close()
                return [TextContent(type="text", text=metrics_text)]
            
            else:
                # Default structured extraction
                structured_content = {
                    "filename": filename,
                    "total_pages": len(doc),
                    "metadata": doc.metadata,
                    "content_preview": ""
                }
                
                # Get first page content as preview
                if len(doc) > 0:
                    structured_content["content_preview"] = doc[0].get_text()[:1000]
                
                doc.close()
                
                if output_format == "json":
                    return [TextContent(type="text", text=json.dumps(structured_content, indent=2))]
                else:
                    formatted_text = f"Document: {filename}\n"
                    formatted_text += f"Pages: {structured_content['total_pages']}\n"
                    formatted_text += f"Metadata: {structured_content['metadata']}\n\n"
                    formatted_text += f"Content Preview:\n{structured_content['content_preview']}"
                    return [TextContent(type="text", text=formatted_text)]
            
        except Exception as e:
            logger.error(f"Error analyzing document {filename}: {e}")
            return [TextContent(type="text", text=f"Error analyzing document: {str(e)}")]

    async def list_documents(self) -> list[TextContent]:
        """List all available PDF documents in the data directory"""
        try:
            # Get all PDF files
            pdf_files = list(self.documents_dir.glob("*.pdf"))
            
            if pdf_files:
                result_text = f"Available Documents in {self.documents_dir}:\n"
                result_text += "=" * 50 + "\n\n"
                
                for pdf_file in sorted(pdf_files):
                    file_size = pdf_file.stat().st_size
                    file_size_mb = file_size / (1024 * 1024)
                    modified_time = datetime.fromtimestamp(pdf_file.stat().st_mtime)
                    
                    result_text += f"📄 {pdf_file.name}\n"
                    result_text += f"   Size: {file_size_mb:.2f} MB\n"
                    result_text += f"   Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    
                    # Try to get basic PDF info if PyMuPDF is available
                    if PDF_AVAILABLE:
                        try:
                            doc = fitz.open(str(pdf_file))
                            result_text += f"   Pages: {len(doc)}\n"
                            if doc.metadata.get('title'):
                                result_text += f"   Title: {doc.metadata['title']}\n"
                            doc.close()
                        except:
                            result_text += f"   Pages: Unable to read\n"
                    
                    result_text += "\n"
                
                result_text += f"\nTotal: {len(pdf_files)} documents"
            else:
                result_text = f"No PDF documents found in {self.documents_dir}\n\n"
                result_text += "To add documents:\n"
                result_text += "1. Place PDF files in the 'data' directory\n"
                result_text += "2. Use the analyze_document tool to process them"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return [TextContent(type="text", text=f"Error listing documents: {str(e)}")]

    def find_relevant_documents(self, symbol: str, document_pattern: str = "") -> List[Path]:
        """Smart document matching based on stock symbol"""
        matching_docs = []
        all_pdfs = list(self.documents_dir.glob("*.pdf"))
        
        if not all_pdfs:
            return []
        
        symbol_upper = symbol.upper()
        
        # Priority 1: Exact symbol match in filename
        exact_matches = [doc for doc in all_pdfs if symbol_upper in doc.name.upper()]
        
        # Priority 2: If document_pattern provided, use it
        if document_pattern:
            pattern_matches = [doc for doc in all_pdfs if document_pattern.upper() in doc.name.upper()]
            exact_matches.extend(pattern_matches)
        
        # Priority 3: Try common variations and company name lookup
        if not exact_matches:
            # Get company name from database to match against document names
            try:
                with self.engine.connect() as connection:
                    query = text("SELECT companyName FROM Stock WHERE symbol = :symbol")
                    result = connection.execute(query, {"symbol": symbol_upper}).fetchone()
                    
                    if result:
                        company_name = result.companyName
                        # Try to match company name words
                        company_words = company_name.upper().split()
                        for doc in all_pdfs:
                            doc_name_upper = doc.name.upper()
                            # If any significant word from company name is in document name
                            if any(word in doc_name_upper for word in company_words if len(word) > 3):
                                exact_matches.append(doc)
            except Exception as e:
                logger.warning(f"Could not fetch company name for {symbol}: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        matching_docs = []
        for doc in exact_matches:
            if doc not in seen:
                matching_docs.append(doc)
                seen.add(doc)
        
        # If still no matches, return all PDFs (fallback)
        if not matching_docs:
            matching_docs = all_pdfs
        
        # Sort by relevance: exact symbol match first, then by modification date (newest first)
        def relevance_score(doc):
            score = 0
            doc_name_upper = doc.name.upper()
            
            # Exact symbol match gets highest score
            if symbol_upper in doc_name_upper:
                score += 100
                
            # Transcript files are very valuable
            if 'TRANSCRIPT' in doc_name_upper or 'CALL' in doc_name_upper:
                score += 50
                
            # Annual reports are valuable
            if 'ANNUAL' in doc_name_upper or 'REPORT' in doc_name_upper:
                score += 30
                
            # Earnings-related documents
            if 'EARNINGS' in doc_name_upper or 'RESULT' in doc_name_upper:
                score += 40
                
            # Simple SYMBOL.pdf files (main company documents) get a small boost
            if doc.name.upper() == f"{symbol_upper}.PDF":
                score += 10
                
            # Newer files are more relevant (add modification time as tiebreaker)
            try:
                score += doc.stat().st_mtime / 1000000  # Small contribution from modification time
            except:
                pass
                
            return score
        
        matching_docs.sort(key=relevance_score, reverse=True)
        
        return matching_docs[:5]  # Return top 5 most relevant documents
    
    async def find_company_documents(self, symbol: str) -> list[TextContent]:
        """Show document matching logic for debugging purposes"""
        try:
            if not PDF_AVAILABLE:
                return [TextContent(type="text", text="PDF processing not available. Please install PyMuPDF: pip install pymupdf")]
            
            result_text = f"🔍 Document Search Results for {symbol.upper()}\n"
            result_text += "=" * 50 + "\n\n"
            
            # Get all PDFs
            all_pdfs = list(self.documents_dir.glob("*.pdf"))
            
            if not all_pdfs:
                result_text += "No PDF documents found in the data directory.\n"
                result_text += f"Add documents with filenames containing '{symbol.upper()}' for automatic matching."
                return [TextContent(type="text", text=result_text)]
            
            result_text += f"📁 All available documents ({len(all_pdfs)}):\n"
            for i, doc in enumerate(all_pdfs, 1):
                result_text += f"   {i}. {doc.name}\n"
            
            # Show matching logic
            matching_docs = self.find_relevant_documents(symbol)
            
            result_text += f"\n🎯 Documents matched for {symbol.upper()} ({len(matching_docs)}):\n"
            
            if matching_docs:
                for i, doc in enumerate(matching_docs, 1):
                    result_text += f"   {i}. {doc.name}"
                    
                    # Explain why this document was matched
                    doc_name_upper = doc.name.upper()
                    symbol_upper = symbol.upper()
                    reasons = []
                    
                    if symbol_upper in doc_name_upper:
                        reasons.append("exact symbol match")
                    
                    # Check for document type keywords
                    if 'TRANSCRIPT' in doc_name_upper:
                        reasons.append("earnings transcript")
                    if 'ANNUAL' in doc_name_upper:
                        reasons.append("annual report")
                    if 'EARNINGS' in doc_name_upper:
                        reasons.append("earnings related")
                    if 'RESULT' in doc_name_upper:
                        reasons.append("results document")
                    if 'CALL' in doc_name_upper:
                        reasons.append("earnings call")
                    
                    # Special recognition for simple SYMBOL.pdf files
                    if doc.name.upper() == f"{symbol_upper}.PDF":
                        reasons.append("main company document")
                    
                    if reasons:
                        result_text += f" → {', '.join(reasons)}"
                    result_text += "\n"
            else:
                result_text += "   No documents matched the symbol.\n"
            
            # Get company name for additional context
            try:
                with self.engine.connect() as connection:
                    query = text("SELECT companyName FROM Stock WHERE symbol = :symbol")
                    result = connection.execute(query, {"symbol": symbol.upper()}).fetchone()
                    
                    if result:
                        company_name = result.companyName
                        result_text += f"\n📊 Company Info:\n"
                        result_text += f"   Symbol: {symbol.upper()}\n"
                        result_text += f"   Name: {company_name}\n"
                        
                        # Check if any documents might match company name
                        company_words = [word for word in company_name.upper().split() if len(word) > 3]
                        if company_words:
                            result_text += f"\n💡 Document Naming Suggestions:\n"
                            result_text += f"   Best: {symbol.upper()}_Transcript.pdf, {symbol.upper()}_Annual_Report.pdf\n"
                            result_text += f"   Also works: {company_words[0]}_Earnings.pdf, {symbol.upper()}_Results.pdf\n"
            except Exception as e:
                result_text += f"\n⚠️ Could not fetch company info: {e}\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error finding documents for {symbol}: {e}")
            return [TextContent(type="text", text=f"Error finding documents: {str(e)}")]
    
    async def get_company_fundamentals(self, symbol: str, document_pattern: str) -> list[TextContent]:
        """Extract fundamental analysis from company documents and combine with technical data"""
        try:
            if not PDF_AVAILABLE:
                return [TextContent(type="text", text="PDF processing not available. Please install PyMuPDF: pip install pymupdf")]
            
            # First, get technical data for the stock
            technical_data = await self.get_advanced_metrics(symbol, "medium")
            
            # Smart document matching
            matching_docs = self.find_relevant_documents(symbol, document_pattern)
            
            if not matching_docs:
                result_text = f"Fundamental Analysis for {symbol.upper()}\n"
                result_text += "=" * 50 + "\n\n"
                result_text += "📊 TECHNICAL ANALYSIS:\n"
                result_text += technical_data[0].text if technical_data else "No technical data available"
                result_text += "\n\n📄 FUNDAMENTAL ANALYSIS:\n"
                result_text += "No PDF documents found in the data directory.\n"
                result_text += "Please add company reports, transcripts, or annual reports to the data directory.\n"
                result_text += f"Example filenames: {symbol.upper()}_Transcript.pdf, {symbol.upper()}_Annual_Report.pdf"
                
                return [TextContent(type="text", text=result_text)]
            
            # Show which documents were found and analyzed
            fundamental_insights = f"📂 Found {len(matching_docs)} relevant document(s) for {symbol.upper()}:\n"
            for i, doc in enumerate(matching_docs, 1):
                fundamental_insights += f"   {i}. {doc.name}\n"
            fundamental_insights += "\n"
            
            # Analyze relevant documents
            
            for doc_file in matching_docs[:3]:  # Analyze up to 3 most relevant documents
                try:
                    doc = fitz.open(str(doc_file))
                    
                    fundamental_insights += f"\n📄 Document: {doc_file.name}\n"
                    fundamental_insights += "-" * 40 + "\n"
                    
                    # Extract financial highlights
                    financial_keywords = [
                        "revenue", "profit", "earnings", "ebitda", "margin", "growth",
                        "cash flow", "debt", "equity", "roi", "roe", "eps", "dividend",
                        "net income", "gross profit", "operating profit", "guidance",
                        "outlook", "performance", "financial", "quarter", "fy"
                    ]
                    
                    key_sections = []
                    
                    for page_num, page in enumerate(doc):
                        page_text = page.get_text()
                        
                        # Split into paragraphs and find relevant ones
                        paragraphs = page_text.split('\n\n')
                        for para in paragraphs:
                            para_lower = para.lower()
                            if any(keyword in para_lower for keyword in financial_keywords):
                                if len(para.strip()) > 100:  # Meaningful content
                                    key_sections.append(f"[Page {page_num + 1}] {para.strip()[:400]}...")
                    
                    # Show top 5 most relevant sections
                    if key_sections:
                        fundamental_insights += "\nKey Financial Insights:\n"
                        for section in key_sections[:5]:
                            fundamental_insights += f"• {section}\n\n"
                    
                    # Try to extract tables (financial data)
                    table_count = 0
                    for page_num, page in enumerate(doc):
                        tables = page.find_tables()
                        for table in tables:
                            if table_count < 2:  # Show max 2 tables
                                table_data = table.extract()
                                if table_data and len(table_data) > 1:
                                    fundamental_insights += f"\nTable from Page {page_num + 1}:\n"
                                    for row in table_data[:4]:  # First 4 rows
                                        if any(cell for cell in row if cell):
                                            fundamental_insights += " | ".join(str(cell or "") for cell in row) + "\n"
                                    fundamental_insights += "\n"
                                    table_count += 1
                    
                    doc.close()
                    
                except Exception as e:
                    fundamental_insights += f"Error processing {doc_file.name}: {str(e)}\n"
            
            # Combine technical and fundamental analysis
            result_text = f"🔍 COMPREHENSIVE ANALYSIS FOR {symbol.upper()}\n"
            result_text += "=" * 60 + "\n\n"
            
            result_text += "📊 TECHNICAL ANALYSIS:\n"
            result_text += "-" * 25 + "\n"
            result_text += technical_data[0].text if technical_data else "No technical data available"
            
            result_text += "\n\n📄 FUNDAMENTAL ANALYSIS:\n"
            result_text += "-" * 30 + "\n"
            result_text += fundamental_insights
            
            result_text += "\n\n💡 INVESTMENT PERSPECTIVE:\n"
            result_text += "-" * 25 + "\n"
            result_text += "This analysis combines real-time technical metrics from the database "
            result_text += "with latest fundamental insights from company documents. "
            result_text += "Use this comprehensive view for informed investment decisions.\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error extracting company fundamentals for {symbol}: {e}")
            return [TextContent(type="text", text=f"Error extracting company fundamentals: {str(e)}")]

async def main():
    """Main server function"""
    logger.info("=== Starting MCP Server Application ===")
    
    try:
        # Create and initialize the server
        logger.info("Creating StockMCPServer instance...")
        stock_server = StockMCPServer()
        logger.info("StockMCPServer instance created successfully")
        
        # Connect to database
        logger.info("Attempting database connection...")
        await stock_server.connect_database()
        logger.info("Database connection successful")
        
        # Run the server
        logger.info("Starting Stock MCP Server stdio interface...")
        
        # Use the correct MCP server stdio transport
        import sys
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as streams:
            logger.info("MCP Server is running and ready for connections")
            await stock_server.server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="stock-database-server",
                    server_version="1.0.0",
                    capabilities=stock_server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise
    finally:
        # Clean up database connection
        logger.info("Cleaning up...")
        if 'stock_server' in locals() and stock_server.engine:
            stock_server.engine.dispose()
            logger.info("Database connection closed")
        logger.info("=== MCP Server Application Ended ===")

if __name__ == "__main__":
    asyncio.run(main())