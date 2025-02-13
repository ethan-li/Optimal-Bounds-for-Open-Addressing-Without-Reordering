"""
Implementation of the optimal open addressing hash table without reordering.
"""

from typing import Optional, Any, List, Tuple
import math
import random

class SubArray:
    """A subarray in the hash table."""
    
    def __init__(self, size: int):
        """
        Initialize the subarray.
        
        Args:
            size: Size of the subarray.
        """
        self._size = size
        self._table = [None] * size
        self._count = 0
        
    def _hash(self, key: Any, attempt: int = 0) -> int:
        """
        Calculate the hash value for a key.
        
        Args:
            key: The key to hash.
            attempt: The probe attempt number.
            
        Returns:
            The hash value.
        """
        # Use double hashing
        h1 = hash(key) % self._size
        h2 = 1 + (hash(str(key)) % (self._size - 1))
        return (h1 + attempt * h2) % self._size
        
    def insert(self, key: Any, value: Any, max_probes: int) -> bool:
        """
        Try to insert a key-value pair into the subarray.
        
        Args:
            key: The key to insert.
            value: The value to insert.
            max_probes: Maximum number of probes to try.
            
        Returns:
            True if insertion was successful, False otherwise.
        """
        # First check if the key already exists
        for i in range(max_probes):
            pos = self._hash(key, i)
            if self._table[pos] is None:
                break
            if self._table[pos][0] == key:
                self._table[pos] = (key, value)  # Update value
                return True
                
        # Try to find an empty slot
        for i in range(max_probes):
            pos = self._hash(key, i)
            if self._table[pos] is None:
                self._table[pos] = (key, value)
                self._count += 1
                return True
        return False
        
    def search(self, key: Any) -> Optional[Any]:
        """
        Search for a key in the subarray.
        
        Args:
            key: The key to search for.
            
        Returns:
            The value associated with the key, or None if not found.
        """
        max_probes = self._size  # Try all possible positions
        for i in range(max_probes):
            pos = self._hash(key, i)
            if self._table[pos] is None:
                return None
            if self._table[pos][0] == key:
                return self._table[pos][1]
        return None
        
    @property
    def load_factor(self) -> float:
        """
        Calculate the current load factor of the subarray.
        
        Returns:
            The load factor (number of items / table size).
        """
        return self._count / self._size

class LastSubArray:
    """Special implementation for the last subarray (Aα+1)."""
    
    def __init__(self, size: int):
        """
        Initialize the last subarray with two parts: B and C.
        
        Args:
            size: Total size of the subarray.
        """
        self._size = size
        self._b_size = size // 2
        self._c_size = size - self._b_size
        self._bucket_size = 2 * int(math.log2(math.log2(size + 1) + 1))
        self._b = [None] * self._b_size  # Uniform probing
        self._c = [[None] * self._bucket_size for _ in range((self._c_size + self._bucket_size - 1) // self._bucket_size)]  # Two-choice with buckets
        self._count = 0
        
    def _hash_b(self, key: Any, attempt: int = 0) -> int:
        """Hash function for part B."""
        h1 = hash(key) % self._b_size
        h2 = 1 + (hash(str(key)) % (self._b_size - 1))
        return (h1 + attempt * h2) % self._b_size
        
    def _hash_c(self, key: Any) -> Tuple[int, int]:
        """Hash function for part C, returns two bucket indices."""
        num_buckets = len(self._c)
        h1 = hash(key) % num_buckets
        h2 = (h1 + 1 + hash(str(key)) % (num_buckets - 1)) % num_buckets
        return h1, h2
        
    def insert(self, key: Any, value: Any) -> bool:
        """
        Insert a key-value pair into the last subarray.
        
        Args:
            key: The key to insert.
            value: The value to insert.
            
        Returns:
            True if insertion was successful, False otherwise.
        """
        # First check if the key exists in part B
        max_attempts = int(math.log2(math.log2(self._size + 1) + 1))
        for i in range(max_attempts):
            pos = self._hash_b(key, i)
            if self._b[pos] is not None and self._b[pos][0] == key:
                self._b[pos] = (key, value)  # Update value
                return True
                
        # Then check if the key exists in part C
        b1, b2 = self._hash_c(key)
        for bucket in [self._c[b1], self._c[b2]]:
            for i, item in enumerate(bucket):
                if item is not None and item[0] == key:
                    bucket[i] = (key, value)  # Update value
                    return True
                    
        # Try to insert into part B
        for i in range(max_attempts):
            pos = self._hash_b(key, i)
            if self._b[pos] is None:
                self._b[pos] = (key, value)
                self._count += 1
                return True
                
        # If B fails, try part C
        b1, b2 = self._hash_c(key)
        bucket1 = self._c[b1]
        bucket2 = self._c[b2]
        
        # Count empty slots in each bucket
        empty1 = sum(1 for x in bucket1 if x is None)
        empty2 = sum(1 for x in bucket2 if x is None)
        
        # Choose the bucket with more empty slots
        target_bucket = bucket1 if empty1 >= empty2 else bucket2
        
        # Try to insert into the chosen bucket
        for i in range(self._bucket_size):
            if target_bucket[i] is None:
                target_bucket[i] = (key, value)
                self._count += 1
                return True
                
        return False
        
    def search(self, key: Any) -> Optional[Any]:
        """
        Search for a key in the last subarray.
        
        Args:
            key: The key to search for.
            
        Returns:
            The value associated with the key, or None if not found.
        """
        # Search in part B
        max_attempts = int(math.log2(math.log2(self._size + 1) + 1))
        for i in range(max_attempts):
            pos = self._hash_b(key, i)
            if self._b[pos] is None:
                break
            if self._b[pos][0] == key:
                return self._b[pos][1]
                
        # Search in part C
        b1, b2 = self._hash_c(key)
        for bucket in [self._c[b1], self._c[b2]]:
            for item in bucket:
                if item is not None and item[0] == key:
                    return item[1]
                    
        return None
        
    @property
    def load_factor(self) -> float:
        """
        Calculate the current load factor of the last subarray.
        
        Returns:
            The load factor (number of items / table size).
        """
        return self._count / self._size

class OpenAddressHashTable:
    """
    A hash table implementation using open addressing without reordering.
    """
    
    def __init__(self, initial_size: int = 16, delta: float = 0.1):
        """
        Initialize the hash table.
        
        Args:
            initial_size: Initial size of the hash table.
            delta: The target empty space ratio (between 0 and 1).
        """
        self._size = initial_size
        self._delta = delta
        self._count = 0
        
        # Calculate number of subarrays
        self._alpha = int(math.log2(1/delta) / 3)
        
        # Initialize subarrays with geometrically decreasing sizes
        self._subarrays: List[SubArray] = []
        current_size = initial_size // 2
        for i in range(self._alpha):
            size = current_size // (2 ** i)
            if size < 1:
                break
            self._subarrays.append(SubArray(size))
            
        # Initialize the last subarray
        last_size = initial_size - sum(arr._size for arr in self._subarrays)
        if last_size > 0:
            self._last_array = LastSubArray(last_size)
        else:
            self._last_array = None
            
    def insert(self, key: Any, value: Any) -> bool:
        """
        Insert a key-value pair into the hash table.
        
        Args:
            key: The key to insert.
            value: The value to insert.
            
        Returns:
            True if insertion was successful, False otherwise.
        """
        # First try to find if the key already exists
        for subarray in self._subarrays:
            max_probes = int(math.log2(1/self._delta))
            if subarray.search(key) is not None:
                return subarray.insert(key, value, max_probes)
                
        if self._last_array is not None and self._last_array.search(key) is not None:
            return self._last_array.insert(key, value)
            
        # Key doesn't exist, try to insert it
        # Calculate current load factor
        current_load = self.load_factor
        if current_load >= 0.9:  # If load factor is too high, don't insert
            return False
            
        # Try each subarray in order
        for subarray in self._subarrays:
            max_probes = int(math.log2(1/self._delta))
            if subarray.insert(key, value, max_probes):
                self._count += 1
                return True
                
        # If all subarrays fail, try the last array
        if self._last_array is not None and self._last_array.insert(key, value):
            self._count += 1
            return True
            
        return False
        
    def search(self, key: Any) -> Optional[Any]:
        """
        Search for a key in the hash table.
        
        Args:
            key: The key to search for.
            
        Returns:
            The value associated with the key, or None if not found.
        """
        # Search in each subarray
        for subarray in self._subarrays:
            result = subarray.search(key)
            if result is not None:
                return result
                
        # Search in the last array
        if self._last_array is not None:
            return self._last_array.search(key)
            
        return None
        
    @property
    def load_factor(self) -> float:
        """
        Calculate the current load factor of the hash table.
        
        Returns:
            The load factor (number of items / table size).
        """
        return self._count / self._size 