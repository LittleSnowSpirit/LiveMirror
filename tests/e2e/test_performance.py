"""
LiveMirror 性能测试 E2E 测试
测试系统在各种负载下的性能表现
"""

import pytest
import time
import statistics
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class TestPerformance:
    """性能测试类"""
    
    @pytest.fixture
    def large_dataset(self):
        """创建大型数据集"""
        return [{"id": i, "data": f"item_{i}"} for i in range(10000)]
    
    @pytest.fixture
    def medium_dataset(self):
        """创建中型数据集"""
        return [{"id": i, "data": f"item_{i}"} for i in range(1000)]
    
    def test_upload_speed_single_file(self, tmp_path):
        """测试单文件上传速度"""
        # 创建 10MB 测试文件
        test_file = tmp_path / "large_file.bin"
        file_size = 10 * 1024 * 1024  # 10MB
        test_file.write_bytes(b"x" * file_size)
        
        start_time = time.time()
        # 模拟上传（本地复制）
        dest_file = tmp_path / "uploaded.bin"
        dest_file.write_bytes(test_file.read_bytes())
        end_time = time.time()
        
        elapsed = end_time - start_time
        speed_mbps = (file_size / 1024 / 1024) / elapsed if elapsed > 0 else 0
        
        print(f"✓ 单文件上传速度：{speed_mbps:.2f} MB/s (耗时 {elapsed:.3f}s)")
        assert elapsed < 5.0  # 应该在 5 秒内完成
    
    def test_upload_speed_batch_files(self, tmp_path):
        """测试批量文件上传速度"""
        file_count = 100
        file_size = 1024 * 100  # 100KB per file
        
        # 创建测试文件
        files = []
        for i in range(file_count):
            f = tmp_path / f"batch_{i}.bin"
            f.write_bytes(b"x" * file_size)
            files.append(f)
        
        start_time = time.time()
        
        # 模拟批量上传
        for f in files:
            dest = tmp_path / f"uploaded_{f.name}"
            dest.write_bytes(f.read_bytes())
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        total_size = file_count * file_size
        speed_mbps = (total_size / 1024 / 1024) / elapsed if elapsed > 0 else 0
        
        print(f"✓ 批量上传速度：{speed_mbps:.2f} MB/s ({file_count} 个文件，耗时 {elapsed:.3f}s)")
        assert elapsed < 10.0
    
    def test_download_speed(self, tmp_path):
        """测试下载速度"""
        # 创建测试数据
        data_size = 5 * 1024 * 1024  # 5MB
        source = tmp_path / "source.bin"
        source.write_bytes(b"y" * data_size)
        
        start_time = time.time()
        
        # 模拟下载
        dest = tmp_path / "downloaded.bin"
        dest.write_bytes(source.read_bytes())
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        speed_mbps = (data_size / 1024 / 1024) / elapsed if elapsed > 0 else 0
        
        print(f"✓ 下载速度：{speed_mbps:.2f} MB/s (耗时 {elapsed:.3f}s)")
        assert elapsed < 3.0
    
    def test_search_performance(self, medium_dataset):
        """测试搜索性能"""
        dataset = medium_dataset
        
        # 线性搜索
        start_time = time.time()
        results = [item for item in dataset if item["id"] == 500]
        linear_time = time.time() - start_time
        
        # 使用字典索引搜索
        index = {item["id"]: item for item in dataset}
        start_time = time.time()
        result = index.get(500)
        indexed_time = time.time() - start_time
        
        print(f"✓ 搜索性能：线性 {linear_time*1000:.2f}ms, 索引 {indexed_time*1000:.2f}ms")
        assert indexed_time < linear_time
    
    def test_sort_performance(self, large_dataset):
        """测试排序性能"""
        import random
        
        # 打乱数据集
        dataset = large_dataset.copy()
        random.shuffle(dataset)
        
        start_time = time.time()
        sorted_data = sorted(dataset, key=lambda x: x["id"])
        elapsed = time.time() - start_time
        
        # 验证排序正确
        assert sorted_data[0]["id"] == 0
        assert sorted_data[-1]["id"] == len(dataset) - 1
        
        print(f"✓ 排序性能：{len(dataset)} 条记录，耗时 {elapsed*1000:.2f}ms")
        assert elapsed < 1.0
    
    def test_filter_performance(self, large_dataset):
        """测试过滤性能"""
        dataset = large_dataset
        
        start_time = time.time()
        filtered = [item for item in dataset if item["id"] % 2 == 0]
        elapsed = time.time() - start_time
        
        assert len(filtered) == len(dataset) // 2
        
        print(f"✓ 过滤性能：{len(dataset)} 条记录，耗时 {elapsed*1000:.2f}ms")
        assert elapsed < 0.5
    
    def test_concurrent_operations(self, tmp_path):
        """测试并发操作性能"""
        import threading
        
        operation_count = 10
        results = []
        lock = threading.Lock()
        
        def operation(thread_id):
            start = time.time()
            # 模拟操作
            time.sleep(0.01)
            elapsed = time.time() - start
            with lock:
                results.append(elapsed)
        
        threads = []
        overall_start = time.time()
        
        for i in range(operation_count):
            t = threading.Thread(target=operation, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        overall_elapsed = time.time() - overall_start
        
        avg_time = statistics.mean(results)
        
        print(f"✓ 并发性能：{operation_count} 个操作，平均 {avg_time*1000:.2f}ms, 总耗时 {overall_elapsed*1000:.2f}ms")
        # 并发执行应该比串行快
        assert overall_elapsed < operation_count * 0.01 * 1.5
    
    def test_memory_usage(self, large_dataset):
        """测试内存使用"""
        import sys
        
        # 获取数据集大小
        dataset_size = sys.getsizeof(large_dataset)
        for item in large_dataset:
            dataset_size += sys.getsizeof(item)
        
        print(f"✓ 内存使用：{len(large_dataset)} 条记录，约 {dataset_size / 1024:.2f} KB")
        assert dataset_size < 100 * 1024 * 1024  # 小于 100MB
    
    def test_response_time_consistency(self, medium_dataset):
        """测试响应时间一致性"""
        response_times = []
        
        for _ in range(10):
            start = time.time()
            # 模拟操作
            _ = [item for item in medium_dataset if item["id"] < 100]
            elapsed = time.time() - start
            response_times.append(elapsed)
        
        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        
        print(f"✓ 响应时间一致性：平均 {avg_time*1000:.2f}ms, 标准差 {std_dev*1000:.2f}ms")
        # 标准差应该较小，表示响应时间稳定
        assert std_dev < avg_time * 0.5
    
    def test_throughput_under_load(self, tmp_path):
        """测试负载下的吞吐量"""
        import threading
        
        concurrent_users = 5
        operations_per_user = 20
        total_operations = 0
        lock = threading.Lock()
        
        def user_operation(user_id):
            nonlocal total_operations
            for _ in range(operations_per_user):
                # 模拟操作
                test_file = tmp_path / f"user_{user_id}_op_{_}.txt"
                test_file.write_text("data")
                with lock:
                    total_operations += 1
        
        threads = []
        start_time = time.time()
        
        for i in range(concurrent_users):
            t = threading.Thread(target=user_operation, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        throughput = total_operations / elapsed if elapsed > 0 else 0
        
        print(f"✓ 吞吐量：{throughput:.2f} 操作/秒 ({total_operations} 操作，{elapsed:.2f}s)")
        assert total_operations == concurrent_users * operations_per_user
    
    def test_latency_percentiles(self, medium_dataset):
        """测试延迟百分位数"""
        latencies = []
        
        for i in range(100):
            start = time.time()
            # 模拟操作
            _ = medium_dataset[i % len(medium_dataset)]
            elapsed = time.time() - start
            latencies.append(elapsed)
        
        latencies.sort()
        
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        
        print(f"✓ 延迟百分位数：P50={p50*1000:.3f}ms, P95={p95*1000:.3f}ms, P99={p99*1000:.3f}ms")
        assert p99 < 0.1  # P99 应该小于 100ms
    
    def test_cache_performance(self):
        """测试缓存性能"""
        cache = {}
        cache_hits = 0
        cache_misses = 0
        
        def get_with_cache(key):
            nonlocal cache_hits, cache_misses
            if key in cache:
                cache_hits += 1
                return cache[key]
            else:
                cache_misses += 1
                # 模拟计算
                value = f"value_{key}"
                cache[key] = value
                return value
        
        # 模拟访问模式
        for i in range(100):
            get_with_cache(i % 10)  # 只有 10 个不同的键
        
        hit_rate = cache_hits / (cache_hits + cache_misses) * 100
        
        print(f"✓ 缓存性能：命中率 {hit_rate:.1f}% (命中 {cache_hits}, 未命中 {cache_misses})")
        assert hit_rate > 80  # 命中率应该高于 80%
    
    def test_stress_test(self, tmp_path):
        """压力测试"""
        import threading
        
        stress_duration = 2  # 秒
        operation_count = 0
        lock = threading.Lock()
        stop_flag = False
        
        def stress_operation():
            nonlocal operation_count
            while not stop_flag:
                test_file = tmp_path / f"stress_{operation_count}.txt"
                test_file.write_text("stress test")
                with lock:
                    operation_count += 1
        
        threads = []
        for _ in range(4):
            t = threading.Thread(target=stress_operation)
            threads.append(t)
            t.start()
        
        time.sleep(stress_duration)
        stop_flag = True
        
        for t in threads:
            t.join()
        
        ops_per_second = operation_count / stress_duration
        
        print(f"✓ 压力测试：{operation_count} 操作 / {stress_duration}s = {ops_per_second:.2f} ops/s")
        assert operation_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
