from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import asyncio
from ib_insync import IB, Stock, MarketOrder
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# IBKR connection settings for paper trading
IB_HOST = os.getenv('IB_HOST', '127.0.0.1')
IB_PORT = int(os.getenv('IB_PORT', 7497))  # 7497 for TWS paper trading
CLIENT_ID = int(os.getenv('CLIENT_ID', 1))

class IBKRTrader:
    def __init__(self):
        self.ib = IB()
        self.connected = False
    
    async def connect(self):
        """Connect to IBKR for paper trading"""
        try:
            # Check if already connected
            if self.ib.isConnected():
                self.connected = True
                return True
                
            await self.ib.connectAsync(IB_HOST, IB_PORT, clientId=CLIENT_ID)
            
            # Verify connection is actually established
            if self.ib.isConnected():
                self.connected = True
                return True
            else:
                self.connected = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to IBKR: {str(e)}")
            self.connected = False
            return False
    
    async def test_connection(self):
        """Test connection to IBKR and return detailed status"""
        try:
            if not self.connected:
                await self.ib.connectAsync(IB_HOST, IB_PORT, clientId=CLIENT_ID)
                self.connected = True
            
            # Test if we can get account summary
            accounts = self.ib.managedAccounts()
            
            return {
                "success": True,
                "connected": True,
                "accounts": accounts,
                "host": IB_HOST,
                "port": IB_PORT,
                "client_id": CLIENT_ID
            }
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            self.connected = False
            return {
                "success": False
            }
    
    async def disconnect(self):
        """Disconnect from IBKR"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
    
    async def place_market_order(self, symbol, action, quantity):
        """Place a market order (BUY or SELL)"""
        try:
            # Always check if connection is actually working, not just the flag
            if not self.ib.isConnected():
                self.connected = False
                if not await self.connect():
                    return {"error": "Failed to connect to IBKR"}
            
            # Double-check connection is still valid
            if not self.ib.isConnected():
                return {"error": "No active connection to IBKR"}
            
            # Create stock contract
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Qualify the contract
            qualified_contracts = await self.ib.qualifyContractsAsync(contract)
            if not qualified_contracts:
                return {"error": f"Could not qualify contract for symbol {symbol}"}
            
            contract = qualified_contracts[0]
            
            # Create market order
            order = MarketOrder(action.upper(), quantity)
            
            # Place the order
            trade = self.ib.placeOrder(contract, order)
            
            # Wait a moment for order to be processed
            await asyncio.sleep(0.1)
            
            return {
                "success": True,
                "order_id": trade.order.orderId,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "order_type": "MARKET",
                "status": trade.orderStatus.status
            }
            
        except Exception as e:
            logger.error(f"Error placing market order: {str(e)}")
            # Reset connection flag on error
            self.connected = False
            return {"error": str(e)}

# Initialize trader
trader = IBKRTrader()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Simple IBKR Paper Trading API",
        "endpoints": {
            "/buy": "POST - Place market buy order",
            "/sell": "POST - Place market sell order", 
            "/status": "GET - Check connection status",
            "/test-connection": "GET - Test connection with detailed info"
        }
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "connected_to_ibkr": trader.connected,
        "trading_mode": "paper",
        "config": {
            "host": IB_HOST,
            "port": IB_PORT,
            "client_id": CLIENT_ID
        }
    })

@app.route('/test-connection', methods=['GET'])
def test_connection():
    """Test connection endpoint with detailed troubleshooting info"""
    try:
        result = asyncio.run(trader.test_connection())
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in test-connection endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/buy', methods=['POST'])
def buy_stock():
    """Buy stock with market order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'symbol' not in data or 'quantity' not in data:
            return jsonify({"error": "Missing required fields: symbol and quantity"}), 400
        
        symbol = data['symbol'].upper()
        quantity = int(data['quantity'])
        
        # Place market buy order
        result = asyncio.run(trader.place_market_order(symbol, 'BUY', quantity))
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in buy endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/sell', methods=['POST'])
def sell_stock():
    """Sell stock with market order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'symbol' not in data or 'quantity' not in data:
            return jsonify({"error": "Missing required fields: symbol and quantity"}), 400
        
        symbol = data['symbol'].upper()
        quantity = int(data['quantity'])
        
        # Place market sell order
        result = asyncio.run(trader.place_market_order(symbol, 'SELL', quantity))
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in sell endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 