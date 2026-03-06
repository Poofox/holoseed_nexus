//! Crypto - Local Token Encryption
//! 
//! Handles encrypted storage of API tokens and secrets.
//! Uses ring crate for now - REPLACE WITH CUSTOM IMPL LATER.
//! 
//! Sovereignty means trusting NO ONE with your keys.

use ring::aead::{self, Aad, LessSafeKey, Nonce, UnboundKey, CHACHA20_POLY1305};
use ring::rand::{SecureRandom, SystemRandom};
use std::path::PathBuf;

const NONCE_LEN: usize = 12;
const KEY_LEN: usize = 32;

/// Encrypted token storage
pub struct TokenVault {
    key: LessSafeKey,
    storage_path: PathBuf,
}

impl TokenVault {
    /// Create a new vault with a derived key
    /// In production, derive this from a user passphrase via Argon2
    pub fn new(master_key: &[u8; KEY_LEN], storage_path: PathBuf) -> Result<Self, &'static str> {
        let unbound_key = UnboundKey::new(&CHACHA20_POLY1305, master_key)
            .map_err(|_| "Failed to create key")?;
        let key = LessSafeKey::new(unbound_key);
        
        Ok(Self { key, storage_path })
    }

    /// Encrypt a token
    pub fn encrypt(&self, plaintext: &[u8]) -> Result<Vec<u8>, &'static str> {
        let rng = SystemRandom::new();
        let mut nonce_bytes = [0u8; NONCE_LEN];
        rng.fill(&mut nonce_bytes).map_err(|_| "Failed to generate nonce")?;
        
        let nonce = Nonce::assume_unique_for_key(nonce_bytes);
        let mut in_out = plaintext.to_vec();
        
        self.key
            .seal_in_place_append_tag(nonce, Aad::empty(), &mut in_out)
            .map_err(|_| "Encryption failed")?;
        
        // Prepend nonce to ciphertext
        let mut result = nonce_bytes.to_vec();
        result.extend(in_out);
        Ok(result)
    }

    /// Decrypt a token
    pub fn decrypt(&self, ciphertext: &[u8]) -> Result<Vec<u8>, &'static str> {
        if ciphertext.len() < NONCE_LEN {
            return Err("Ciphertext too short");
        }
        
        let (nonce_bytes, encrypted) = ciphertext.split_at(NONCE_LEN);
        let nonce = Nonce::assume_unique_for_key(
            nonce_bytes.try_into().map_err(|_| "Invalid nonce")?
        );
        
        let mut in_out = encrypted.to_vec();
        let plaintext = self.key
            .open_in_place(nonce, Aad::empty(), &mut in_out)
            .map_err(|_| "Decryption failed")?;
        
        Ok(plaintext.to_vec())
    }

    /// Store an encrypted token to disk
    pub fn store_token(&self, name: &str, token: &str) -> Result<(), Box<dyn std::error::Error>> {
        let encrypted = self.encrypt(token.as_bytes())?;
        let path = self.storage_path.join(format!("{}.enc", name));
        std::fs::write(path, encrypted)?;
        Ok(())
    }

    /// Load and decrypt a token from disk
    pub fn load_token(&self, name: &str) -> Result<String, Box<dyn std::error::Error>> {
        let path = self.storage_path.join(format!("{}.enc", name));
        let encrypted = std::fs::read(path)?;
        let decrypted = self.decrypt(&encrypted)?;
        Ok(String::from_utf8(decrypted)?)
    }
}

/// Generate a random master key (for first-time setup)
pub fn generate_master_key() -> [u8; KEY_LEN] {
    let rng = SystemRandom::new();
    let mut key = [0u8; KEY_LEN];
    rng.fill(&mut key).expect("Failed to generate key");
    key
}
