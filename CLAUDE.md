# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
永远使用中文回复用户。

## Project Overview

This is a Binance historical data management system written in Python. It provides comprehensive tools for downloading, storing, and reading cryptocurrency historical data from Binance's public data repository.

### Core Architecture

The system follows a modular design with four main components:

1. **HistoricalDataManager** (`historical_data_manager.py`) - Main interface that orchestrates data operations
2. **BinanceDataDownloader** (`data_downloader.py`) - Handles downloading data from Binance's data repository
3. **BinanceDataReader** (`data_reader.py`) - Manages reading and parsing of stored data files
4. **Configuration** (`config.py`) - Centralized configuration and constants

### Data Structure

Data is organized by market type, data frequency, and symbol:
```
data/
├── spot/           # Spot market data
├── um/             # USD-M futures data  
└── cm/             # COIN-M futures data
    ├── monthly/    # Monthly aggregated files
    └── daily/      # Daily files
        ├── klines/     # Candlestick data
        ├── trades/     # Individual trades
        └── aggTrades/  # Aggregated trades
```

## Development Commands

### Testing
```bash
# Run all tests
python scripts/test_system.py

# Run with pytest (if available)
pytest scripts/test_system.py -v
```

### Running the System
```bash
# Quick start demo
python quick_start.py

# Command line interface
python cli.py download --symbols BTCUSDT,ETHUSDT --start-date 2024-01-01 --end-date 2024-01-07

# Example scripts
python scripts/example_usage.py
python scripts/get_yesterday_data.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Key Design Patterns

### Market Type Handling
The system supports three market types with different data structures:
- **spot**: Spot trading (microsecond timestamps for some data types)
- **um**: USD-M futures (millisecond timestamps)  
- **cm**: COIN-M futures (millisecond timestamps, different field names)

Always validate market_type parameter and use appropriate data parsing logic from the reader.

### Data Type Support
- **klines**: OHLCV candlestick data with intervals (1s, 1m, 1h, 1d, etc.)
- **trades**: Individual trade records
- **aggTrades**: Aggregated trade data

### Error Handling Strategy
The system implements robust error handling:
- Network timeouts with retry logic in downloader
- File corruption detection and skipping
- Missing data graceful handling
- Parameter validation with clear error messages

### Memory Management
For large datasets, the system supports:
- Chunked reading via generators (`chunk_size` parameter)
- Lazy loading of data files
- Automatic cleanup of old data files

## Common Development Patterns

### Adding New Data Sources
When extending to new data sources, follow the existing pattern:
1. Add new market type to `MARKET_TYPES` in config.py
2. Update `get_market_path_prefix()` function
3. Add URL template patterns to `FILE_PATH_TEMPLATE`
4. Update data parsing logic in `BinanceDataReader`

### Date Range Processing
The system uses string dates in "YYYY-MM-DD" format consistently. When processing date ranges:
- Validate dates using `datetime.strptime()`
- Handle timezone considerations (data is in UTC)
- Support both monthly and daily file granularity

### Data Validation
Always validate parameters in this order:
1. Market type (spot, um, cm)
2. Data type (klines, trades, aggTrades)  
3. Interval (only for klines data)
4. Date ranges and symbol format

## Important Implementation Notes

### File Download Logic
- Monthly files are preferred over daily files when available
- Automatic fallback to daily files if monthly data is missing
- ZIP file extraction and validation built into download process
- Progress bars for long-running operations

### Data Reading Optimization
- Files are read in chronological order automatically
- Support for reading across multiple months/days seamlessly
- Pandas DataFrame output with proper column naming
- Automatic data type inference and parsing

### Configuration Management
Default configuration in `config.py` can be overridden at runtime. When adding new configuration options, update both `DEFAULT_CONFIG` and parameter validation logic.

### CLI Interface
The `cli.py` provides a command-line interface with subcommands for download, read, and info operations. Follow the existing argument parsing pattern when adding new commands.