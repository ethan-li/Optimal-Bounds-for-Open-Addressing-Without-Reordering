"""
Tests for the OpenAddressHashTable implementation.
"""

import unittest
import random
from src.hash_table import OpenAddressHashTable, SubArray, LastSubArray

class TestSubArray(unittest.TestCase):
    """Test cases for SubArray."""
    
    def setUp(self):
        """Set up test cases."""
        self.subarray = SubArray(16)
        
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.subarray._size, 16)
        self.assertEqual(len(self.subarray._table), 16)
        self.assertEqual(self.subarray._count, 0)
        
    def test_insert_and_search(self):
        """Test insertion and search operations."""
        # Test successful insertion
        self.assertTrue(self.subarray.insert("key1", "value1", 5))
        self.assertEqual(self.subarray.search("key1"), "value1")
        
        # Test insertion with collision
        self.assertTrue(self.subarray.insert("key2", "value2", 5))
        self.assertEqual(self.subarray.search("key2"), "value2")
        
        # Test search for non-existent key
        self.assertIsNone(self.subarray.search("key3"))
        
    def test_load_factor(self):
        """Test load factor calculation."""
        self.assertEqual(self.subarray.load_factor, 0.0)
        
        self.subarray.insert("key1", "value1", 5)
        self.assertEqual(self.subarray.load_factor, 1/16)
        
        self.subarray.insert("key2", "value2", 5)
        self.assertEqual(self.subarray.load_factor, 2/16)

class TestLastSubArray(unittest.TestCase):
    """Test cases for LastSubArray."""
    
    def setUp(self):
        """Set up test cases."""
        self.last_array = LastSubArray(32)
        
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.last_array._size, 32)
        self.assertEqual(self.last_array._b_size, 16)
        self.assertEqual(self.last_array._count, 0)
        
    def test_insert_and_search_b(self):
        """Test insertion and search in part B."""
        # Test successful insertion in B
        self.assertTrue(self.last_array.insert("key1", "value1"))
        self.assertEqual(self.last_array.search("key1"), "value1")
        
    def test_insert_and_search_c(self):
        """Test insertion and search in part C."""
        # Fill part B to force insertion into C
        keys = []
        for i in range(self.last_array._b_size + 1):
            key = f"key{i}"
            keys.append(key)
            self.assertTrue(self.last_array.insert(key, f"value{i}"))
            
        # Verify all values can be found
        for i, key in enumerate(keys):
            self.assertEqual(self.last_array.search(key), f"value{i}")
            
    def test_load_factor(self):
        """Test load factor calculation."""
        self.assertEqual(self.last_array.load_factor, 0.0)
        
        self.last_array.insert("key1", "value1")
        self.assertEqual(self.last_array.load_factor, 1/32)

class TestOpenAddressHashTable(unittest.TestCase):
    """Test cases for OpenAddressHashTable."""
    
    def setUp(self):
        """Set up test cases."""
        self.hash_table = OpenAddressHashTable(initial_size=64, delta=0.1)
        
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.hash_table._size, 64)
        self.assertEqual(self.hash_table._delta, 0.1)
        self.assertEqual(self.hash_table._count, 0)
        self.assertGreater(len(self.hash_table._subarrays), 0)
        
    def test_insert_and_search(self):
        """Test basic insertion and search operations."""
        # Test single insertion
        self.assertTrue(self.hash_table.insert("key1", "value1"))
        self.assertEqual(self.hash_table.search("key1"), "value1")
        
        # Test multiple insertions
        test_data = {f"key{i}": f"value{i}" for i in range(2, 11)}
        for key, value in test_data.items():
            self.assertTrue(self.hash_table.insert(key, value))
            
        # Verify all values can be found
        for key, value in test_data.items():
            self.assertEqual(self.hash_table.search(key), value)
            
        # Test search for non-existent key
        self.assertIsNone(self.hash_table.search("nonexistent"))
        
    def test_high_load_factor(self):
        """Test behavior with high load factor."""
        # Insert items until we reach close to (1-delta) load factor
        n = int(self.hash_table._size * 0.85)  # 0.85 < (1-0.1)
        test_data = {f"key{i}": f"value{i}" for i in range(n)}
        
        # Insert all items
        success_count = 0
        for key, value in test_data.items():
            if self.hash_table.insert(key, value):
                success_count += 1
                
        # Verify load factor is below 1-delta
        self.assertLess(self.hash_table.load_factor, 1 - self.hash_table._delta)
        
        # Verify we could insert most items
        self.assertGreater(success_count / n, 0.95)
        
    def test_random_operations(self):
        """Test random mix of insertions and searches."""
        random.seed(42)  # For reproducibility
        
        # Generate random test data
        test_data = {}
        operations = []
        for i in range(1000):
            if random.random() < 0.7:  # 70% insertions
                key = f"key{random.randint(0, 999)}"
                value = f"value{random.randint(0, 999)}"
                test_data[key] = value
                operations.append(("insert", key, value))
            else:  # 30% searches
                if test_data:
                    key = random.choice(list(test_data.keys()))
                    operations.append(("search", key, test_data[key]))
                    
        # Execute operations
        successful_inserts = set()  # Track successfully inserted keys
        for i, (op, key, value) in enumerate(operations):
            if op == "insert":
                success = self.hash_table.insert(key, value)
                print(f"Operation {i}: Insert {key}={value}, success={success}")
                if success:
                    successful_inserts.add(key)
                    test_data[key] = value  # Update the value if insertion succeeded
            else:  # search
                if key in successful_inserts:  # Only check keys that were successfully inserted
                    result = self.hash_table.search(key)
                    print(f"Operation {i}: Search {key}, expected={test_data[key]}, got={result}")
                    self.assertEqual(result, test_data[key])
                else:
                    print(f"Operation {i}: Search {key} skipped (not successfully inserted)")
                
    def test_load_factor(self):
        """Test load factor calculation."""
        self.assertEqual(self.hash_table.load_factor, 0.0)
        
        # Insert some items
        n = 10
        for i in range(n):
            self.hash_table.insert(f"key{i}", f"value{i}")
            self.assertEqual(self.hash_table.load_factor, (i + 1) / self.hash_table._size)

if __name__ == '__main__':
    unittest.main() 