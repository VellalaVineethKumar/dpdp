"""Token storage and validation for the Compliance Assessment Tool.

This module handles:
- Secure token generation and storage
- Token validation and expiry
- Access control management
"""

import os
import csv
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from config import BASE_DIR

# Setup logging
logger = logging.getLogger(__name__)

# Constants
TOKEN_LENGTH = 32
TOKEN_EXPIRY_DAYS = 30
SECURE_DIR = os.path.join(BASE_DIR, "secure")
TOKENS_FILE = os.path.join(SECURE_DIR, "tokens.csv")

# Also expose TOKEN_PATH for backwards compatibility
TOKEN_PATH = TOKENS_FILE

# Ensure secure directory exists
os.makedirs(SECURE_DIR, exist_ok=True)

# Define standard column order as a constant
TOKEN_CSV_COLUMNS = ['token', 'created_at', 'expires_at', 'organization_name', 'generated_by']

def ensure_token_storage():
    """Ensure token storage directory and file exist"""
    try:
        os.makedirs(SECURE_DIR, exist_ok=True)
        if not os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(TOKEN_CSV_COLUMNS)
            logger.info(f"Created new token storage file at {TOKENS_FILE}")
        else:
            # Check existing columns to ensure compatibility
            with open(TOKENS_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                try:
                    header = next(reader, None)
                    if header and set(header) != set(TOKEN_CSV_COLUMNS):
                        logger.warning(f"Token file has inconsistent columns: {header}")
                        # Consider migrating the file structure here
                except Exception as e:
                    logger.error(f"Error reading token file headers: {e}")
        
        # Verify the file is writable
        if not os.access(TOKENS_FILE, os.W_OK):
            logger.warning(f"Token file exists but may not be writable: {TOKENS_FILE}")
            try:
                # Try to make it writable
                os.chmod(TOKENS_FILE, 0o666)
                logger.info(f"Updated permissions on token file")
            except Exception as perm_e:
                logger.error(f"Could not update permissions: {perm_e}")
        
        return True
    except Exception as e:
        logger.error(f"Error ensuring token storage: {e}")
        return False

def generate_token(organization: str, generated_by: str = "Admin") -> Optional[str]:
    """Generate a new access token for an organization"""
    try:
        ensure_token_storage()
        
        # Generate token with DATAINFA_ prefix followed by organization name
        # Replace spaces with underscores and make uppercase
        org_part = organization.strip().replace(' ', '_').upper()
        token = f"DATAINFA_{org_part}"
        
        # Add a random suffix for uniqueness
        random_suffix = secrets.token_hex(8)  # 8 bytes = 16 hex chars
        token = f"{token}_{random_suffix}"
        
        created_at = datetime.now()
        expires_at = created_at + timedelta(days=TOKEN_EXPIRY_DAYS)
        
        # Save token - match the exact column order of the CSV
        with open(TOKENS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                token,
                created_at.isoformat(),
                expires_at.isoformat(),
                organization,
                generated_by
            ])
        
        logger.info(f"Generated token for {organization} by {generated_by}: {token}")
        logger.info(f"Token will expire on {expires_at.isoformat()}")
        
        return token
        
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return None

def validate_token(token: str) -> bool:
    """Validate an access token"""
    # Admin token special case
    if token == 'dpdp2025':
        logger.info("Admin token validated")
        return True
        
    try:
        if not os.path.exists(TOKENS_FILE):
            logger.error(f"Token file not found at {TOKENS_FILE}")
            return False
        
        with open(TOKENS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            # Check if all required columns exist
            fieldnames = reader.fieldnames
            if not fieldnames:
                logger.error("Token file has no headers")
                return False
                
            if 'token' not in fieldnames:
                logger.error(f"Token file missing 'token' column. Found: {fieldnames}")
                return False
            
            for row in reader:
                if row.get('token') == token:
                    logger.info(f"Found matching token: {token[:8]}...")
                    
                    # Check expiration if available
                    if 'expires_at' in row and row['expires_at']:
                        try:
                            # Handle different date formats
                            expires_str = row['expires_at']
                            if 'T' in expires_str:
                                # ISO format with T separator
                                expires_at = datetime.fromisoformat(expires_str)
                            else:
                                # Try various common formats
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
                                    try:
                                        expires_at = datetime.strptime(expires_str, fmt)
                                        break
                                    except ValueError:
                                        continue
                                else:
                                    # If no format worked, assume it's valid
                                    logger.warning(f"Could not parse expiry date: {expires_str}, assuming valid")
                                    return True
                                
                            if datetime.now() > expires_at:
                                logger.warning(f"Token expired on {expires_at}")
                                return False
                        except Exception as e:
                            logger.error(f"Error checking token expiry: {e}, assuming valid")
                            # If we can't parse the date, assume token is valid
                            return True
                    
                    return True
            
            logger.warning(f"No matching token found: {token[:8]}...")
            return False
        
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        return False

def get_organization_for_token(token: str) -> Optional[str]:
    """Get the organization associated with a token"""
    try:
        if not os.path.exists(TOKENS_FILE):
            return None
            
        with open(TOKENS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['token'] == token:
                    return row['organization']
                    
        return None
            
    except Exception as e:
        logger.error(f"Error getting organization for token: {e}")
        return None

def revoke_token(token: str) -> bool:
    """Revoke an access token"""
    try:
        if not os.path.exists(TOKENS_FILE):
            return False
            
        rows = []
        token_found = False
        
        with open(TOKENS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            rows.append(next(reader))  # Header row
            for row in reader:
                if row['token'] != token:
                    rows.append(row)
                else:
                    token_found = True
        
        if token_found:
            with open(TOKENS_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            logger.info(f"Revoked token: {token}")
            return True
        else:
            return False
        
    except Exception as e:
        logger.error(f"Error revoking token: {e}")
        return False

def cleanup_expired_tokens() -> int:
    """Remove expired tokens from storage"""
    try:
        if not os.path.exists(TOKENS_FILE):
            return 0
        
        current_time = datetime.now()
        rows = []
        expired_count = 0
        
        with open(TOKENS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            rows.append(next(reader))  # Header row
            for row in reader:
                expires_at = datetime.fromisoformat(row['expires_at'])
                if current_time <= expires_at:
                    rows.append(row)
                else:
                    expired_count += 1
        
        if expired_count > 0:
            with open(TOKENS_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            logger.info(f"Removed {expired_count} expired tokens")
        
        return expired_count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}")
        return 0