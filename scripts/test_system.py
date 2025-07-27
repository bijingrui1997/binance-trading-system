"""币安历史数据系统测试"""
import os
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

from historical_data_manager import HistoricalDataManager
from data_downloader import BinanceDataDownloader
from data_reader import BinanceDataReader
from config import DEFAULT_CONFIG, KLINE_INTERVALS


class TestBinanceDataSystem(unittest.TestCase):
    """币安数据系统测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.manager = HistoricalDataManager(self.test_dir)
        self.downloader = BinanceDataDownloader(self.test_dir)
        self.reader = BinanceDataReader(self.test_dir)
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效参数
        self.manager._validate_parameters("spot", "klines", "1h")
        
        # 测试无效市场类型
        with self.assertRaises(ValueError):
            self.manager._validate_parameters("invalid", "klines", "1h")
        
        # 测试无效数据类型
        with self.assertRaises(ValueError):
            self.manager._validate_parameters("spot", "invalid", "1h")
        
        # 测试无效K线间隔
        with self.assertRaises(ValueError):
            self.manager._validate_parameters("spot", "klines", "invalid")
    
    def test_file_path_generation(self):
        """测试文件路径生成"""
        # 测试月度K线文件URL
        url = self.downloader._get_file_url(
            "spot", "klines", "BTCUSDT", "1h", 2024, 1, is_daily=False
        )
        expected = "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-01.zip"
        self.assertEqual(url, expected)
        
        # 测试日度交易文件URL
        url = self.downloader._get_file_url(
            "spot", "trades", "ETHUSDT", date="2024-01-01", is_daily=True
        )
        expected = "https://data.binance.vision/data/spot/daily/trades/ETHUSDT/ETHUSDT-trades-2024-01-01.zip"
        self.assertEqual(url, expected)
        
        # 测试本地文件路径
        local_path = self.downloader._get_local_file_path(
            "spot", "klines", "BTCUSDT", "1h", 2024, 1, is_daily=False
        )
        expected_end = "spot/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2024-01.zip"
        self.assertTrue(local_path.endswith(expected_end))
    
    @patch('requests.Session.get')
    def test_download_file_success(self, mock_get):
        """测试文件下载成功"""
        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'test data']
        mock_get.return_value = mock_response
        
        # 测试下载
        test_file = os.path.join(self.test_dir, "test.zip")
        result = self.downloader._download_file("http://test.com/file.zip", test_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
    
    @patch('requests.Session.get')
    def test_download_file_failure(self, mock_get):
        """测试文件下载失败"""
        # 模拟失败的HTTP响应
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        # 测试下载
        test_file = os.path.join(self.test_dir, "test.zip")
        result = self.downloader._download_file("http://test.com/file.zip", test_file)
        
        self.assertFalse(result)
        self.assertFalse(os.path.exists(test_file))
    
    def test_data_directory_creation(self):
        """测试数据目录创建"""
        # 测试目录是否被创建
        self.assertTrue(os.path.exists(self.test_dir))
        
        # 测试子目录创建
        local_path = self.downloader._get_local_file_path(
            "spot", "klines", "BTCUSDT", "1h", 2024, 1, is_daily=False
        )
        # 目录应该被创建
        self.assertTrue(os.path.exists(os.path.dirname(local_path)))
    
    def test_available_symbols(self):
        """测试可用交易对列表"""
        symbols = self.downloader.list_available_symbols("spot")
        self.assertIsInstance(symbols, list)
        self.assertGreater(len(symbols), 0)
        self.assertIn("BTCUSDT", symbols)
    
    def test_data_info_empty(self):
        """测试空数据信息"""
        info = self.reader.get_data_info("BTCUSDT", "spot", "klines", "1h")
        
        self.assertEqual(info["symbol"], "BTCUSDT")
        self.assertEqual(info["files_count"], 0)
        self.assertIsNone(info["date_range"])
    
    def test_storage_stats_empty(self):
        """测试空存储统计"""
        stats = self.manager.get_storage_stats()
        
        self.assertEqual(stats["total_size_mb"], 0)
        self.assertEqual(stats["total_files"], 0)
        self.assertEqual(stats["data_directory"], self.test_dir)
    
    def test_local_symbols_empty(self):
        """测试空本地交易对列表"""
        symbols = self.manager.get_local_symbols("spot", "klines")
        self.assertEqual(symbols, [])
    
    def test_read_data_empty(self):
        """测试读取空数据"""
        df = self.reader.read_data("BTCUSDT", "spot", "klines", "1h")
        self.assertTrue(df.empty)
    
    def create_test_zip_file(self, file_path: str, data_type: str = "klines"):
        """创建测试用的ZIP文件"""
        import zipfile
        import io
        
        # 创建测试数据
        if data_type == "klines":
            test_data = [
                "1640995200000,50000.00,51000.00,49000.00,50500.00,100.5,1640998799999,5050000.00,1000,50.25,2525000.00,0",
                "1640998800000,50500.00,51500.00,49500.00,51000.00,120.3,1641002399999,6141500.00,1200,60.15,3070750.00,0"
            ]
        elif data_type == "trades":
            test_data = [
                "1,50000.00,0.1,5000.00,1640995200000,false,true",
                "2,50100.00,0.2,10020.00,1640995260000,true,true"
            ]
        else:  # aggTrades
            test_data = [
                "1,50000.00,0.1,1,1,1640995200000,false,true",
                "2,50100.00,0.2,2,2,1640995260000,true,true"
            ]
        
        # 创建目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 创建ZIP文件
        with zipfile.ZipFile(file_path, 'w') as zf:
            csv_content = '\n'.join(test_data)
            zf.writestr('data.csv', csv_content)
    
    def test_read_zip_file(self):
        """测试ZIP文件读取"""
        # 创建测试ZIP文件
        test_file = os.path.join(self.test_dir, "test.zip")
        self.create_test_zip_file(test_file, "klines")
        
        # 读取文件
        df = self.reader._read_zip_file(test_file, "klines")
        
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertEqual(len(df.columns), 12)  # K线数据有12列
    
    def test_data_processing(self):
        """测试数据处理"""
        # 创建测试数据
        test_data = {
            'open_time': [1640995200000, 1640998800000],
            'open': ['50000.00', '50500.00'],
            'high': ['51000.00', '51500.00'],
            'low': ['49000.00', '49500.00'],
            'close': ['50500.00', '51000.00'],
            'volume': ['100.5', '120.3'],
            'close_time': [1640998799999, 1641002399999],
            'quote_asset_volume': ['5050000.00', '6141500.00'],
            'number_of_trades': [1000, 1200],
            'taker_buy_base_asset_volume': ['50.25', '60.15'],
            'taker_buy_quote_asset_volume': ['2525000.00', '3070750.00'],
            'ignore': [0, 0]
        }
        
        df = pd.DataFrame(test_data)
        processed_df = self.reader._process_dataframe(df, "klines")
        
        # 检查时间戳转换
        self.assertEqual(processed_df['open_time'].dtype, 'datetime64[ns]')
        self.assertEqual(processed_df['close_time'].dtype, 'datetime64[ns]')
        
        # 检查数值转换
        self.assertTrue(pd.api.types.is_numeric_dtype(processed_df['open']))
        self.assertTrue(pd.api.types.is_numeric_dtype(processed_df['volume']))
    
    def test_manager_integration(self):
        """测试管理器集成功能"""
        # 测试参数验证
        with self.assertRaises(ValueError):
            self.manager.download_data(["BTCUSDT"], market_type="invalid")
        
        # 测试字符串转列表
        with patch.object(self.manager.downloader, 'download_data') as mock_download:
            mock_download.return_value = []
            self.manager.download_data("BTCUSDT")  # 传入字符串而不是列表
            mock_download.assert_called_once()
            args = mock_download.call_args[1]
            self.assertEqual(args['symbols'], ["BTCUSDT"])


class TestSystemIntegration(unittest.TestCase):
    """系统集成测试"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manager = HistoricalDataManager(self.test_dir)
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_full_workflow_simulation(self):
        """测试完整工作流程模拟"""
        # 创建模拟数据文件
        symbol = "BTCUSDT"
        market_type = "spot"
        data_type = "klines"
        interval = "1h"
        
        # 创建月度文件
        monthly_file = os.path.join(
            self.test_dir, market_type, "monthly", data_type, 
            symbol, interval, f"{symbol}-{interval}-2024-01.zip"
        )
        
        test_case = TestBinanceDataSystem()
        test_case.test_dir = self.test_dir
        test_case.reader = self.manager.reader
        test_case.create_test_zip_file(monthly_file, data_type)
        
        # 测试数据信息获取
        info = self.manager.get_data_info(symbol, market_type, data_type, interval)
        self.assertEqual(info["files_count"], 1)
        self.assertIsNotNone(info["date_range"])
        
        # 测试数据读取
        df = self.manager.read_data(symbol, market_type, data_type, interval)
        self.assertFalse(df.empty)
        
        # 测试存储统计
        stats = self.manager.get_storage_stats()
        self.assertGreater(stats["total_files"], 0)
        
        # 测试本地交易对列表
        local_symbols = self.manager.get_local_symbols(market_type, data_type)
        self.assertIn(symbol, local_symbols)


def run_tests():
    """运行所有测试"""
    print("开始运行币安历史数据系统测试...")
    print("=" * 50)
    
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_suite.addTest(loader.loadTestsFromTestCase(TestBinanceDataSystem))
    test_suite.addTest(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出结果
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("所有测试通过！")
    else:
        print(f"测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)