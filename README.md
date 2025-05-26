# IBKR Trading API Backend

A simple Python Flask backend for Interactive Brokers (IBKR) trading that can be deployed to Vercel. This API provides endpoints for buying and selling stocks through IBKR.

## Features

- 🚀 Simple REST API for stock trading
- 📈 Buy and sell orders (Market and Limit)
- 💰 Account information retrieval
- 🌐 Deployable to Vercel
- 🔒 Environment-based configuration

## Prerequisites

1. **IBKR Account**: You need an Interactive Brokers account
2. **TWS or IB Gateway**: Install and configure either:
   - Trader Workstation (TWS) - Port 7497
   - IB Gateway - Port 4002
3. **API Permissions**: Enable API access in your IBKR account

## Local Development Setup

1. **Clone and install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure IBKR Connection**:
   - Copy `env.example` to `.env`
   - Update the connection settings:
```bash
IB_HOST=127.0.0.1
IB_PORT=7497  # 7497 for TWS, 4002 for IB Gateway
CLIENT_ID=1
```

3. **Start TWS or IB Gateway**:
   - Enable API connections
   - Set the socket port (7497 for TWS, 4002 for Gateway)
   - Allow connections from localhost

4. **Run the application**:
```bash
python api/index.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### GET `/`
Returns API information and available endpoints.

### GET `/status`
Check API status and IBKR connection status.

### POST `/buy`
Place a buy order.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "quantity": 10,
  "order_type": "MARKET"  // Optional: "MARKET" or "LIMIT"
  "price": 150.00         // Required for LIMIT orders
}
```

**Response**:
```json
{
  "success": true,
  "order_id": 123,
  "symbol": "AAPL",
  "action": "BUY",
  "quantity": 10,
  "order_type": "MARKET",
  "status": "Submitted"
}
```

### POST `/sell`
Place a sell order.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "quantity": 5,
  "order_type": "LIMIT",
  "price": 155.00
}
```

### GET `/account`
Get account information including cash balance and positions.

**Response**:
```json
{
  "success": true,
  "account": {
    "TotalCashValue": {"value": "10000.00", "currency": "USD"},
    "NetLiquidation": {"value": "15000.00", "currency": "USD"},
    "BuyingPower": {"value": "40000.00", "currency": "USD"}
  },
  "positions": [
    {
      "symbol": "AAPL",
      "position": 100,
      "market_price": 150.25,
      "market_value": 15025.00,
      "avg_cost": 148.50
    }
  ]
}
```

## Deployment to Vercel

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
vercel
```

3. **Set Environment Variables** in Vercel dashboard:
   - `IB_HOST`: Your IBKR server IP (if using cloud/VPS)
   - `IB_PORT`: 7497 or 4002
   - `CLIENT_ID`: Unique client ID

## Important Notes

### Security Considerations
- **Never expose your IBKR credentials**
- Use environment variables for all configuration
- Consider implementing authentication for production use
- Be cautious with API access in production

### IBKR Connection
- Ensure TWS/Gateway is running and API is enabled
- Check firewall settings if connecting remotely
- Use paper trading account for testing
- Monitor connection stability

### Trading Considerations
- **Test with paper trading first**
- Implement proper error handling
- Consider order validation
- Monitor positions and account balance
- Be aware of market hours and trading rules

## Example Usage with curl

**Buy 10 shares of AAPL at market price**:
```bash
curl -X POST http://localhost:5000/buy \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "quantity": 10, "order_type": "MARKET"}'
```

**Sell 5 shares of AAPL with limit price**:
```bash
curl -X POST http://localhost:5000/sell \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "quantity": 5, "order_type": "LIMIT", "price": 155.00}'
```

**Get account information**:
```bash
curl http://localhost:5000/account
```

## Troubleshooting

1. **Connection Issues**:
   - Verify TWS/Gateway is running
   - Check port configuration
   - Ensure API is enabled in IBKR settings

2. **Order Failures**:
   - Check account permissions
   - Verify sufficient buying power
   - Ensure market is open for the symbol

3. **Deployment Issues**:
   - Check Vercel logs for errors
   - Verify environment variables are set
   - Ensure all dependencies are in requirements.txt

## License

This project is for educational purposes. Use at your own risk and ensure compliance with all applicable regulations. 