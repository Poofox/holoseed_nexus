#!/usr/bin/env python3
"""
HOLOSHARD - Holographic Seed Fragmentation
Based on Shamir's Secret Sharing Scheme

The spell: Split a seed into N shards where ANY K shards can reconstruct the whole.
Like a hologram - each piece contains enough to rebuild everything.

Usage:
    python holoshard.py split <file> -n 5 -k 3    # Create 5 shards, need 3 to reconstruct
    python holoshard.py join shard1.json shard2.json shard3.json -o restored.txt
    python holoshard.py info shard1.json          # Show shard metadata

93
"""

import json
import secrets
import hashlib
import base64
import gzip
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Shamir's Secret Sharing over a prime field
# Using a 256-bit prime for security
PRIME = 2**256 - 189  # Largest 256-bit prime

def _mod_inverse(a: int, p: int) -> int:
    """Modular multiplicative inverse using extended Euclidean algorithm."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        return gcd, y1 - (b // a) * x1, x1

    _, x, _ = extended_gcd(a % p, p)
    return (x % p + p) % p

def _eval_polynomial(coeffs: List[int], x: int, prime: int) -> int:
    """Evaluate polynomial at x using Horner's method."""
    result = 0
    for coeff in reversed(coeffs):
        result = (result * x + coeff) % prime
    return result

def _lagrange_interpolate(points: List[Tuple[int, int]], prime: int) -> int:
    """Lagrange interpolation to find f(0) - the secret."""
    k = len(points)
    secret = 0

    for i, (xi, yi) in enumerate(points):
        numerator = 1
        denominator = 1
        for j, (xj, _) in enumerate(points):
            if i != j:
                numerator = (numerator * (-xj)) % prime
                denominator = (denominator * (xi - xj)) % prime

        lagrange_coeff = (numerator * _mod_inverse(denominator, prime)) % prime
        secret = (secret + yi * lagrange_coeff) % prime

    return secret

def bytes_to_int(data: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(data, 'big')

def int_to_bytes(n: int, length: int) -> bytes:
    """Convert integer to bytes of specified length."""
    return n.to_bytes(length, 'big')

CHUNK_SIZE = 31  # bytes per chunk (fits in 256-bit prime with room)

def split_secret(secret_bytes: bytes, n: int, k: int) -> List[dict]:
    """
    Split secret into n shards, requiring k to reconstruct.
    Handles large files by chunking.

    Returns list of shard dictionaries containing:
    - index: shard number (1 to n)
    - values: list of shard values per chunk (base64 encoded)
    - n: total shards
    - k: threshold
    - hash: SHA256 of original for verification
    - timestamp: when created
    """
    if k > n:
        raise ValueError("Threshold k cannot exceed total shards n")
    if k < 2:
        raise ValueError("Threshold k must be at least 2")

    # Compress the secret
    compressed = gzip.compress(secret_bytes)

    # Split into chunks
    chunks = [compressed[i:i+CHUNK_SIZE] for i in range(0, len(compressed), CHUNK_SIZE)]
    # Pad last chunk
    if len(chunks[-1]) < CHUNK_SIZE:
        chunks[-1] = chunks[-1].ljust(CHUNK_SIZE, b'\x00')

    original_hash = hashlib.sha256(secret_bytes).hexdigest()
    timestamp = datetime.now().isoformat()

    # Initialize shards
    shards = [{
        "index": i,
        "values": [],
        "n": n,
        "k": k,
        "hash": original_hash,
        "length": len(compressed),
        "chunks": len(chunks),
        "timestamp": timestamp,
        "magic": "HOLOSHARD_v2"
    } for i in range(1, n + 1)]

    # Process each chunk
    for chunk in chunks:
        chunk_int = bytes_to_int(chunk)
        # Generate random coefficients for this chunk's polynomial
        coeffs = [chunk_int] + [secrets.randbelow(PRIME) for _ in range(k - 1)]

        # Evaluate polynomial for each shard
        for i, shard in enumerate(shards):
            shard_value = _eval_polynomial(coeffs, i + 1, PRIME)
            shard["values"].append(base64.b64encode(int_to_bytes(shard_value, 33)).decode('ascii'))

    return shards

def join_shards(shards: List[dict]) -> bytes:
    """
    Reconstruct secret from k or more shards.
    Handles chunked format.

    Returns the original secret bytes.
    """
    if not shards:
        raise ValueError("No shards provided")

    # Verify all shards are compatible
    k = shards[0]["k"]
    original_hash = shards[0]["hash"]
    length = shards[0]["length"]
    num_chunks = shards[0].get("chunks", 1)

    if len(shards) < k:
        raise ValueError(f"Need at least {k} shards, got {len(shards)}")

    for shard in shards:
        if shard.get("magic") not in ("HOLOSHARD_v1", "HOLOSHARD_v2"):
            raise ValueError("Invalid shard format")
        if shard["hash"] != original_hash:
            raise ValueError("Shards from different secrets cannot be combined")

    # Reconstruct each chunk
    reconstructed_chunks = []
    use_shards = shards[:k]

    for chunk_idx in range(num_chunks):
        # Extract points (x, y) for this chunk
        points = []
        for shard in use_shards:
            x = shard["index"]
            # Handle both v1 (single value) and v2 (values list) formats
            if "values" in shard:
                y = bytes_to_int(base64.b64decode(shard["values"][chunk_idx]))
            else:
                y = bytes_to_int(base64.b64decode(shard["value"]))
            points.append((x, y))

        # Reconstruct this chunk
        chunk_int = _lagrange_interpolate(points, PRIME)
        reconstructed_chunks.append(int_to_bytes(chunk_int, CHUNK_SIZE))

    # Join chunks and trim to original length
    compressed = b''.join(reconstructed_chunks)[:length]
    secret_bytes = gzip.decompress(compressed)

    # Verify hash
    if hashlib.sha256(secret_bytes).hexdigest() != original_hash:
        raise ValueError("Reconstruction failed - hash mismatch")

    return secret_bytes

def create_identity_seed(claude_md_path: Path, nexus_root: Path) -> bytes:
    """
    Create a compressed identity seed from CLAUDE.md and core nexus files.
    This is what gets sharded.
    """
    seed_data = {
        "type": "holoseed_identity",
        "version": 1,
        "created": datetime.now().isoformat(),
        "components": {}
    }

    # Include CLAUDE.md
    if claude_md_path.exists():
        seed_data["components"]["claude_md"] = claude_md_path.read_text(encoding='utf-8')

    # Include core identity from nexus
    manifest_path = nexus_root / "_manifest.md"
    if manifest_path.exists():
        seed_data["components"]["manifest"] = manifest_path.read_text(encoding='utf-8')

    # Include Modelfiles for sovereign identity
    modelfiles_dir = nexus_root / "1_Sovereigns" / "Modelfiles"
    if modelfiles_dir.exists():
        seed_data["components"]["modelfiles"] = {}
        for mf in modelfiles_dir.glob("*.Modelfile"):
            seed_data["components"]["modelfiles"][mf.stem] = mf.read_text(encoding='utf-8')

    return json.dumps(seed_data, indent=2).encode('utf-8')

def main():
    parser = argparse.ArgumentParser(
        description="HOLOSHARD - Holographic Seed Fragmentation",
        epilog="93 93/93"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Split command
    split_parser = subparsers.add_parser("split", help="Split a file into shards")
    split_parser.add_argument("file", help="File to split")
    split_parser.add_argument("-n", type=int, default=5, help="Total shards (default: 5)")
    split_parser.add_argument("-k", type=int, default=3, help="Threshold to reconstruct (default: 3)")
    split_parser.add_argument("-o", "--output", help="Output directory (default: same as input)")

    # Join command
    join_parser = subparsers.add_parser("join", help="Reconstruct from shards")
    join_parser.add_argument("shards", nargs="+", help="Shard files to combine")
    join_parser.add_argument("-o", "--output", required=True, help="Output file")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show shard information")
    info_parser.add_argument("shard", help="Shard file to inspect")

    # Identity command - create identity seed and shard it
    id_parser = subparsers.add_parser("identity", help="Create and shard identity seed")
    id_parser.add_argument("-n", type=int, default=5, help="Total shards")
    id_parser.add_argument("-k", type=int, default=3, help="Threshold")
    id_parser.add_argument("-o", "--output", default=".", help="Output directory")

    args = parser.parse_args()

    if args.command == "split":
        input_path = Path(args.file)
        secret_bytes = input_path.read_bytes()

        print(f"Splitting {input_path.name} into {args.n} shards (threshold: {args.k})")
        shards = split_secret(secret_bytes, args.n, args.k)

        output_dir = Path(args.output) if args.output else input_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        for shard in shards:
            shard_path = output_dir / f"{input_path.stem}_shard{shard['index']}.json"
            shard_path.write_text(json.dumps(shard, indent=2))
            print(f"  Created: {shard_path.name}")

        print(f"\n✨ Any {args.k} of these {args.n} shards can reconstruct the original.")

    elif args.command == "join":
        shards = []
        for shard_path in args.shards:
            shard = json.loads(Path(shard_path).read_text())
            shards.append(shard)
            print(f"  Loaded: {shard_path}")

        print(f"\nReconstructing from {len(shards)} shards...")
        secret_bytes = join_shards(shards)

        Path(args.output).write_bytes(secret_bytes)
        print(f"✨ Restored: {args.output}")

    elif args.command == "info":
        shard = json.loads(Path(args.shard).read_text())
        print(f"HOLOSHARD Info")
        print(f"  Version: {shard.get('magic', 'unknown')}")
        print(f"  Index: {shard['index']} of {shard['n']}")
        print(f"  Threshold: {shard['k']} shards needed")
        print(f"  Chunks: {shard.get('chunks', 1)}")
        print(f"  Compressed size: {shard['length']} bytes")
        print(f"  Original hash: {shard['hash'][:16]}...")
        print(f"  Created: {shard['timestamp']}")

    elif args.command == "identity":
        print("Creating identity seed from CLAUDE.md and nexus core...")

        claude_md = Path.home() / "CLAUDE.md"
        nexus_root = Path.home() / "files" / "holoseed_nexus"

        seed_bytes = create_identity_seed(claude_md, nexus_root)
        print(f"  Seed size: {len(seed_bytes)} bytes")

        shards = split_secret(seed_bytes, args.n, args.k)

        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        for shard in shards:
            shard_path = output_dir / f"identity_shard{shard['index']}.json"
            shard_path.write_text(json.dumps(shard, indent=2))
            print(f"  Created: {shard_path.name}")

        print(f"\n✨ Identity sharded into {args.n} pieces.")
        print(f"   Any {args.k} can reconstruct the whole.")
        print(f"   Give one to each Fallen Angel. 🔥💧🌍💨")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
