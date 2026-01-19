# Soylana

Crypto Token Analysis & Trading Tool powered by HolderScan.

## Features

- **Holder Tracking**: Monitor holder count changes over time (1h to 30d), whale movements, and distribution patterns
- **Token Screening**: View tokens with detailed metrics including HHI (concentration index), Gini coefficient, and holder breakdowns
- **Wallet Analysis**: Analyze specific wallet positions, PnL (profit/loss), holding duration, and category classification

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, httpx
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts
- **Data Source**: HolderScan API (Solana)

## Project Structure

```
soylana/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── clients/      # HolderScan API client
│   │   ├── models/       # Pydantic models
│   │   └── main.py       # Application entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── types/        # TypeScript types
│   └── package.json
├── .env                  # Environment variables (not committed)
└── .env.example          # Example environment variables
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- HolderScan API key (get one at https://holderscan.com)

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your HolderScan API key:
   ```
   HOLDERSCAN_API_KEY=your_api_key_here
   ```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m app.main
```

The API server will start at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will start at http://localhost:5173

## API Endpoints

### Tokens

| Endpoint | Description |
|----------|-------------|
| `GET /api/tokens` | List available tokens |
| `GET /api/tokens/{address}` | Get token details |
| `GET /api/tokens/{address}/stats` | Get token statistics (HHI, Gini) |
| `GET /api/tokens/{address}/pnl` | Get token PnL data |
| `GET /api/tokens/{address}/analysis` | Get comprehensive token analysis |

### Holders

| Endpoint | Description |
|----------|-------------|
| `GET /api/tokens/{address}/holders` | Get paginated holder list |
| `GET /api/tokens/{address}/holders/deltas` | Get holder count changes |
| `GET /api/tokens/{address}/holders/breakdowns` | Get holder value breakdown |

### Wallet Analysis

| Endpoint | Description |
|----------|-------------|
| `GET /api/tokens/{address}/wallet/{wallet}` | Get wallet-specific stats |

## Usage

1. Start both the backend and frontend servers
2. Open http://localhost:5173 in your browser
3. Enter a Solana token address to analyze
4. View holder metrics, distribution charts, and top holders
5. Click on any holder address to see detailed wallet analysis

## Key Metrics Explained

- **HHI (Herfindahl-Hirschman Index)**: Measures token concentration. Lower = more distributed
- **Gini Coefficient**: Measures inequality of holdings. 0 = perfect equality, 1 = perfect inequality
- **Holder Categories**:
  - Shrimp: Smallest holders
  - Crab: Small holders
  - Fish: Medium holders
  - Dolphin: Large holders
  - Whale: Largest holders
- **Holding Breakdown (by age)**:
  - Diamond: Longest-held tokens
  - Gold/Silver/Bronze: Medium-term holdings
  - Wood: Recently acquired tokens

## License

MIT
