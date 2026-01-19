import { useNavigate } from 'react-router-dom';
import { TokenSearch } from '../components';

export function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
          Soylana
        </h1>
        <p className="text-gray-400 text-lg">
          Crypto Token Analysis & Trading Tool
        </p>
      </div>

      <TokenSearch />

      {/* Tools Section */}
      <div className="mt-8 w-full max-w-xl">
        <button
          onClick={() => navigate('/cross-checker')}
          className="w-full p-4 bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 rounded-lg transition-all group"
        >
          <div className="flex items-center justify-center gap-3">
            <span className="text-2xl">🔗</span>
            <div className="text-left">
              <h3 className="font-bold text-lg">Wallet Cross-Checker</h3>
              <p className="text-sm text-gray-200 opacity-90">
                Find wallets that hold multiple tokens - identify smart money
              </p>
            </div>
            <span className="text-xl ml-auto group-hover:translate-x-1 transition-transform">→</span>
          </div>
        </button>
      </div>

      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl w-full">
        <FeatureCard
          title="Holder Analysis"
          description="Track holder count changes, whale movements, and distribution patterns"
          icon="📊"
        />
        <FeatureCard
          title="Token Screening"
          description="Filter tokens by metrics like HHI, Gini coefficient, and holder count"
          icon="🔍"
        />
        <FeatureCard
          title="Wallet Tracking"
          description="Analyze wallet positions, PnL, and holding duration"
          icon="💼"
        />
      </div>

      <div className="mt-12 text-center text-gray-500 text-sm">
        <p>Powered by <a href="https://holderscan.com" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:text-purple-300">HolderScan</a> & <a href="https://solscan.io" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300">Solscan</a></p>
      </div>
    </div>
  );
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 hover:border-purple-500/50 transition-colors">
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="font-semibold mb-1">{title}</h3>
      <p className="text-sm text-gray-400">{description}</p>
    </div>
  );
}
