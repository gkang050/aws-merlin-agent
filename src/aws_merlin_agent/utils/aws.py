from __future__ import annotations

from functools import lru_cache

import boto3


@lru_cache(maxsize=None)
def client(service_name: str, region_name: str | None = None):
    """Return a cached boto3 client to avoid repeated session construction."""
    return boto3.client(service_name, region_name=region_name)


@lru_cache(maxsize=None)
def resource(service_name: str, region_name: str | None = None):
    """Return a cached boto3 resource."""
    return boto3.resource(service_name, region_name=region_name)
