from __future__ import annotations

import threading
import time
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter implementation.
    
    This class implements a token bucket algorithm that allows bursts of requests
    up to a certain capacity while maintaining an average rate over time.
    
    The algorithm works by:
    - Starting with a bucket full of tokens (capacity)
    - Adding tokens at a fixed rate (rate) per second
    - Allowing requests only if tokens are available
    - Removing one token per allowed request
    
    Args:
        rate: Number of tokens to add per second (average rate)
        capacity: Maximum number of tokens the bucket can hold (burst capacity)
        initial_tokens: Initial number of tokens in the bucket (default: capacity)
    """
    
    def __init__(self, rate: float, capacity: int, initial_tokens: Optional[int] = None):
        if rate <= 0:
            raise ValueError("Rate must be positive")
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if initial_tokens is not None and initial_tokens < 0:
            raise ValueError("Initial tokens must be non-negative")
        if initial_tokens is not None and initial_tokens > capacity:
            raise ValueError("Initial tokens cannot exceed capacity")
        
        self.rate = rate
        self.capacity = capacity
        self.tokens = initial_tokens if initial_tokens is not None else capacity
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def _add_tokens(self) -> None:
        """Add tokens to the bucket based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        
        # Calculate tokens to add based on elapsed time
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
    
    def allow_request(self, tokens: int = 1) -> bool:
        """
        Check if a request is allowed and consume tokens if it is.
        
        Args:
            tokens: Number of tokens to consume (default: 1)
            
        Returns:
            True if the request is allowed, False otherwise
        """
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        if tokens > self.capacity:
            raise ValueError(f"Request tokens ({tokens}) exceeds bucket capacity ({self.capacity})")
        
        with self.lock:
            self._add_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_for_tokens(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Wait until the requested number of tokens are available.
        
        Args:
            tokens: Number of tokens to consume (default: 1)
            timeout: Maximum time to wait in seconds (None for infinite wait)
            
        Returns:
            True if tokens were acquired, False if timeout occurred
        """
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        if tokens > self.capacity:
            raise ValueError(f"Request tokens ({tokens}) exceeds bucket capacity ({self.capacity})")
        
        start_time = time.time()
        
        while True:
            with self.lock:
                self._add_tokens()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
                
                # Calculate how long to wait for the next token
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                
                # Check if we should wait or timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    remaining_timeout = timeout - elapsed
                    
                    if remaining_timeout <= 0:
                        return False
                    
                    wait_time = min(wait_time, remaining_timeout)
            
            # Sleep outside the lock to allow other threads to proceed
            time.sleep(wait_time)
    
    def get_current_tokens(self) -> float:
        """Get the current number of tokens in the bucket."""
        with self.lock:
            self._add_tokens()
            return self.tokens
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get the estimated wait time in seconds for the requested tokens.
        
        Args:
            tokens: Number of tokens requested
            
        Returns:
            Estimated wait time in seconds (0 if tokens are available now)
        """
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        if tokens > self.capacity:
            raise ValueError(f"Request tokens ({tokens}) exceeds bucket capacity ({self.capacity})")
        
        with self.lock:
            self._add_tokens()
            
            if self.tokens >= tokens:
                return 0.0
            
            tokens_needed = tokens - self.tokens
            return tokens_needed / self.rate
    
    def reset(self) -> None:
        """Reset the bucket to its initial state."""
        with self.lock:
            self.tokens = self.capacity
            self.last_update = time.time()


class AsyncRateLimiter(RateLimiter):
    """
    Async version of the token bucket rate limiter.
    
    This class provides async methods for use in async/await code.
    """
    
    async def allow_request_async(self, tokens: int = 1) -> bool:
        """Async version of allow_request."""
        return self.allow_request(tokens)
    
    async def wait_for_tokens_async(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Async version of wait_for_tokens.
        
        This method will asynchronously wait until the requested tokens are available.
        """
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        if tokens > self.capacity:
            raise ValueError(f"Request tokens ({tokens}) exceeds bucket capacity ({self.capacity})")
        
        import asyncio
        start_time = time.time()
        
        while True:
            with self.lock:
                self._add_tokens()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
                
                # Calculate how long to wait for the next token
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                
                # Check if we should wait or timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    remaining_timeout = timeout - elapsed
                    
                    if remaining_timeout <= 0:
                        return False
                    
                    wait_time = min(wait_time, remaining_timeout)
            
            # Async sleep outside the lock
            await asyncio.sleep(wait_time)