# main.py
from flask import Flask, jsonify
import os
import hvac
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def health_check():
    return jsonify({"status": "running"}), 200

@app.route("/secret")
def fetch_secret():
    vault_url = os.getenv("VAULT_ADDR")
    vault_token = os.getenv("VAULT_TOKEN")
    vault_namespace = os.getenv("VAULT_NAMESPACE", "admin")
    
    # Log configuration (without sensitive data)
    logger.info(f"Vault URL: {vault_url}")
    logger.info(f"Namespace: {vault_namespace}")
    
    try:
        # Initialize Vault client
        client = hvac.Client(
            url=vault_url,
            token=vault_token,
            namespace=vault_namespace
        )
        
        # Verify authentication
        if not client.is_authenticated():
            raise Exception("Failed to authenticate with Vault")
            
        # Fetch secret - using the correct path format
        secret = client.secrets.kv.v2.read_secret_version(
            path='agent',           # Just the secret name without v1/secret/data/
            mount_point='secret'    # The mount point for the KV store
        )
        
        logger.info("Successfully retrieved secret")
        return jsonify({"secret": secret["data"]["data"]}), 200
        
    except Exception as e:
        logger.error(f"Error accessing vault: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/debug")
def debug():
    """Endpoint to verify environment variables"""
    return jsonify({
        "vault_url": os.getenv("VAULT_ADDR"),
        "namespace": os.getenv("VAULT_NAMESPACE"),
        "authenticated": True
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)