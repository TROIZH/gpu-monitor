/* @ds-bundle: {"format":3,"namespace":"BuidlpadDesignSystem_1e72c1","components":[],"sourceHashes":{"ui_kits/earn/EarnApp.jsx":"6951c600e759","ui_kits/earn/EarnNavbar.jsx":"966e5ed91be3","ui_kits/earn/HodlPoolCard.jsx":"b46c073910be","ui_kits/earn/StakeDialog.jsx":"156c5ff626ef","ui_kits/invest/App.jsx":"aae7e017d55a","ui_kits/invest/LoginDialog.jsx":"7afe3f75daf8","ui_kits/invest/Navbar.jsx":"d7a995c16c10","ui_kits/invest/ProjectCard.jsx":"992bfd76f954","ui_kits/invest/ProjectDetails.jsx":"69d2d0b9af38"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.BuidlpadDesignSystem_1e72c1 = window.BuidlpadDesignSystem_1e72c1 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// ui_kits/earn/EarnApp.jsx
try { (() => {
const {
  useState
} = React;
const POOLS = [{
  id: 'momentum',
  name: 'Momentum',
  ticker: 'MOMO',
  tvl: '577.5M',
  apy: '18.4%',
  lockDays: 60,
  booster: 1.8,
  status: 'active',
  featured: true,
  phase: 'pre-tge'
}, {
  id: 'falcon',
  name: 'Falcon',
  ticker: 'FLC',
  tvl: '412.1M',
  apy: '24.5%',
  lockDays: 90,
  booster: 2.2,
  status: 'active',
  featured: false,
  phase: 'post-tge'
}, {
  id: 'lombard',
  name: 'Lombard',
  ticker: 'LMB',
  tvl: '189.4M',
  apy: '12.8%',
  lockDays: 30,
  booster: 1.3,
  status: 'active',
  featured: false,
  phase: 'post-tge'
}, {
  id: 'solayer',
  name: 'Solayer',
  ticker: 'LAYER',
  tvl: '0',
  apy: 'TBD',
  lockDays: 60,
  booster: 1.6,
  status: 'soon',
  featured: false,
  phase: 'pre-tge'
}, {
  id: 'sahara',
  name: 'Sahara AI',
  ticker: 'SAHARA',
  tvl: '321.7M',
  apy: '16.2%',
  lockDays: 45,
  booster: 1.5,
  status: 'active',
  featured: false,
  phase: 'pre-tge'
}, {
  id: 'nomad',
  name: 'Nomad Capital',
  ticker: 'NMD',
  tvl: '0',
  apy: 'TBD',
  lockDays: 90,
  booster: 2.0,
  status: 'soon',
  featured: false,
  phase: 'pre-tge'
}];
function EarnApp() {
  const [phase, setPhase] = useState('all');
  const [stakePool, setStakePool] = useState(null);
  const [toast, setToast] = useState(null);
  const [theme, setTheme] = useState('dark');
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);
  const visible = POOLS.filter(p => phase === 'all' || p.phase === phase);
  const tvlTotal = POOLS.filter(p => p.status === 'active').reduce((s, p) => s + parseFloat(p.tvl), 0).toFixed(1);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      minHeight: '100vh',
      background: 'var(--background)',
      color: 'var(--foreground)'
    }
  }, /*#__PURE__*/React.createElement(EarnNavbar, {
    theme: theme,
    onToggleTheme: () => setTheme(theme === 'light' ? 'dark' : 'light')
  }), /*#__PURE__*/React.createElement("section", {
    style: {
      textAlign: 'center',
      padding: '56px 32px 40px',
      maxWidth: 1000,
      margin: '0 auto'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "badge badge-success",
    style: {
      marginBottom: 16
    }
  }, "Boosted Earn"), /*#__PURE__*/React.createElement("h1", {
    style: {
      font: 'var(--fw-bold) var(--text-5xl)/1.15 var(--font-sans)',
      letterSpacing: 'var(--tracking-tight)',
      margin: '0 0 14px'
    }
  }, "Stake through Buidlpad to unlock ", /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--success)'
    }
  }, "exclusive boosters"), "."), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--text-lg)/1.5 var(--font-sans)',
      color: 'var(--muted-foreground)',
      margin: '0 auto',
      maxWidth: 560
    }
  }, "Skin in the game for long-term believers. Pre-TGE and post-TGE pools, native token rewards."), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 28,
      display: 'inline-flex',
      gap: 0,
      background: 'var(--card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-xl)',
      padding: '16px 24px',
      boxShadow: 'var(--shadow-sm)'
    }
  }, [{
    k: 'Total value locked',
    v: `$${tvlTotal}M`
  }, {
    k: 'Active pools',
    v: POOLS.filter(p => p.status === 'active').length
  }, {
    k: 'Campaigns',
    v: POOLS.length
  }].map((s, i, arr) => /*#__PURE__*/React.createElement(React.Fragment, {
    key: s.k
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 24px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--muted-foreground)',
      textTransform: 'uppercase',
      letterSpacing: 'var(--tracking-wider)',
      marginBottom: 6
    }
  }, s.k), /*#__PURE__*/React.createElement("div", {
    className: "font-mono",
    style: {
      fontSize: 'var(--text-2xl)'
    }
  }, s.v)), i < arr.length - 1 && /*#__PURE__*/React.createElement("div", {
    className: "separator separator-v",
    style: {
      height: 36
    }
  }))))), /*#__PURE__*/React.createElement("main", {
    style: {
      maxWidth: 1280,
      margin: '0 auto',
      padding: '0 32px 80px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "tabs-list",
    style: {
      marginBottom: 28
    }
  }, [{
    id: 'all',
    label: 'All campaigns'
  }, {
    id: 'pre-tge',
    label: 'Pre-TGE'
  }, {
    id: 'post-tge',
    label: 'Post-TGE'
  }].map(p => /*#__PURE__*/React.createElement("button", {
    key: p.id,
    className: "tabs-trigger",
    "data-state": phase === p.id ? 'active' : undefined,
    onClick: () => setPhase(p.id)
  }, p.label))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill,minmax(360px,1fr))',
      gap: 16
    }
  }, visible.map(pool => /*#__PURE__*/React.createElement(HodlPoolCard, {
    key: pool.id,
    pool: pool,
    onStake: setStakePool
  })))), /*#__PURE__*/React.createElement(StakeDialog, {
    pool: stakePool,
    open: !!stakePool,
    onClose: () => setStakePool(null),
    onConfirm: ({
      pool,
      amount
    }) => {
      setStakePool(null);
      setToast(`Staked ${amount || '0'} ${pool.ticker} — unlocks in ${pool.lockDays} days.`);
      setTimeout(() => setToast(null), 4000);
    }
  }), toast && /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'fixed',
      bottom: 32,
      left: '50%',
      transform: 'translateX(-50%)',
      background: 'var(--popover)',
      color: 'var(--popover-foreground)',
      border: '1px solid color-mix(in oklch, var(--success) 40%, transparent)',
      padding: '12px 20px',
      borderRadius: 'var(--radius-full)',
      font: 'var(--fw-medium) var(--text-sm)/1 var(--font-sans)',
      boxShadow: 'var(--shadow-2xl)',
      zIndex: 200
    }
  }, toast));
}
ReactDOM.createRoot(document.getElementById('root')).render(/*#__PURE__*/React.createElement(EarnApp, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/earn/EarnApp.jsx", error: String((e && e.message) || e) }); }

// ui_kits/earn/EarnNavbar.jsx
try { (() => {
// EarnNavbar.jsx — same shadcn Navbar with "Boosted Earn" chip
function EarnNavbar({
  active = 'earn',
  onToggleTheme,
  theme
}) {
  return /*#__PURE__*/React.createElement("header", {
    className: "bp-navbar"
  }, /*#__PURE__*/React.createElement("div", {
    className: "bp-brand"
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/buidlpad-wordmark.svg",
    height: 20,
    alt: "Buidlpad"
  }), /*#__PURE__*/React.createElement("span", {
    className: "badge badge-success"
  }, "Boosted Earn")), /*#__PURE__*/React.createElement("nav", {
    className: "bp-nav-items"
  }, [{
    id: 'invest',
    label: 'Invest'
  }, {
    id: 'vibe',
    label: 'Vibe'
  }, {
    id: 'earn',
    label: 'Earn'
  }].map(i => /*#__PURE__*/React.createElement("a", {
    key: i.id,
    className: "nav-link",
    "data-state": active === i.id ? 'active' : undefined
  }, i.label))), /*#__PURE__*/React.createElement("div", {
    className: "bp-nav-right"
  }, onToggleTheme && /*#__PURE__*/React.createElement("button", {
    className: "btn btn-outline btn-sm",
    onClick: onToggleTheme
  }, theme === 'light' ? '☾ Dark' : '☀ Light'), /*#__PURE__*/React.createElement("button", {
    className: "btn btn-outline btn-sm font-mono"
  }, "0x8F3a\u2026c41e")));
}
window.EarnNavbar = EarnNavbar;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/earn/EarnNavbar.jsx", error: String((e && e.message) || e) }); }

// ui_kits/earn/HodlPoolCard.jsx
try { (() => {
// HodlPoolCard.jsx — shadcn Card variant for staking pool
function HodlPoolCard({
  pool,
  onStake
}) {
  const {
    name,
    ticker,
    tvl,
    apy,
    lockDays,
    booster,
    featured,
    status = 'active'
  } = pool;
  return /*#__PURE__*/React.createElement("div", {
    className: "card",
    style: featured ? {
      borderColor: 'color-mix(in oklch, var(--success) 40%, transparent)',
      boxShadow: '0 0 0 1px color-mix(in oklch, var(--success) 25%, transparent), 0 0 40px color-mix(in oklch, var(--success) 12%, transparent)'
    } : null
  }, /*#__PURE__*/React.createElement("div", {
    className: "card-header"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h3", {
    className: "card-title"
  }, name), /*#__PURE__*/React.createElement("p", {
    className: "card-desc font-mono",
    style: {
      marginTop: 2
    }
  }, ticker)), status === 'active' ? /*#__PURE__*/React.createElement("span", {
    className: "badge badge-success"
  }, "\u25CF Active") : /*#__PURE__*/React.createElement("span", {
    className: "badge badge-outline"
  }, "Coming soon"))), /*#__PURE__*/React.createElement("div", {
    className: "card-content"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4,1fr)',
      gap: 12
    }
  }, [{
    k: 'TVL',
    v: `$${tvl}`,
    highlight: true
  }, {
    k: 'Booster',
    v: `${booster}×`
  }, {
    k: 'APY',
    v: apy
  }, {
    k: 'Lock',
    v: `${lockDays}d`
  }].map(s => /*#__PURE__*/React.createElement("div", {
    key: s.k
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--muted-foreground)',
      textTransform: 'uppercase',
      letterSpacing: 'var(--tracking-wider)',
      marginBottom: 4
    }
  }, s.k), /*#__PURE__*/React.createElement("div", {
    className: "font-mono",
    style: {
      fontSize: 'var(--text-xl)',
      color: s.highlight ? 'var(--success)' : 'var(--foreground)'
    }
  }, s.v))))), /*#__PURE__*/React.createElement("div", {
    className: "card-footer"
  }, /*#__PURE__*/React.createElement("button", {
    className: `btn ${status === 'active' ? 'btn-primary' : 'btn-secondary'}`,
    style: {
      width: '100%'
    },
    disabled: status !== 'active',
    onClick: () => onStake && onStake(pool)
  }, status === 'active' ? `Stake ${ticker}` : 'Notify me')));
}
window.HodlPoolCard = HodlPoolCard;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/earn/HodlPoolCard.jsx", error: String((e && e.message) || e) }); }

// ui_kits/earn/StakeDialog.jsx
try { (() => {
// StakeDialog.jsx — shadcn Dialog for stake flow
function StakeDialog({
  pool,
  open,
  onClose,
  onConfirm
}) {
  const [amount, setAmount] = React.useState('');
  if (!open || !pool) return null;
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    className: "dialog-overlay",
    onClick: onClose
  }), /*#__PURE__*/React.createElement("div", {
    className: "dialog-content",
    onClick: e => e.stopPropagation()
  }, /*#__PURE__*/React.createElement("div", {
    className: "dialog-header"
  }, /*#__PURE__*/React.createElement("h2", {
    className: "dialog-title"
  }, "Stake ", pool.ticker), /*#__PURE__*/React.createElement("p", {
    className: "dialog-desc"
  }, "Lock for ", pool.lockDays, " days \xB7 ", pool.booster, "\xD7 booster multiplier.")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("label", {
    className: "label",
    style: {
      marginBottom: 6,
      display: 'block'
    }
  }, "Amount"), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("input", {
    className: "input font-mono",
    style: {
      fontSize: 'var(--text-lg)',
      paddingRight: 88
    },
    type: "number",
    placeholder: "0.00",
    value: amount,
    onChange: e => setAmount(e.target.value)
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      right: 8,
      top: '50%',
      transform: 'translateY(-50%)',
      display: 'flex',
      alignItems: 'center',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "font-mono",
    style: {
      fontSize: 'var(--text-xs)',
      color: 'var(--muted-foreground)'
    }
  }, pool.ticker), /*#__PURE__*/React.createElement("button", {
    className: "btn btn-ghost btn-sm",
    style: {
      height: 24,
      padding: '0 8px'
    },
    onClick: () => setAmount('1000')
  }, "MAX"))), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--text-xs)',
      color: 'var(--muted-foreground)',
      marginTop: 6
    }
  }, "Balance: 1,000 ", pool.ticker)), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--muted)',
      borderRadius: 'var(--radius-md)',
      padding: 14
    }
  }, /*#__PURE__*/React.createElement("dl", {
    className: "dl-grid"
  }, /*#__PURE__*/React.createElement("dt", null, "Estimated APY"), /*#__PURE__*/React.createElement("dd", {
    style: {
      color: 'var(--success)'
    }
  }, pool.apy), /*#__PURE__*/React.createElement("dt", null, "Booster"), /*#__PURE__*/React.createElement("dd", null, pool.booster, "\xD7"), /*#__PURE__*/React.createElement("dt", null, "Lock period"), /*#__PURE__*/React.createElement("dd", null, pool.lockDays, " days"), /*#__PURE__*/React.createElement("dt", null, "Unlock date"), /*#__PURE__*/React.createElement("dd", {
    className: "font-mono"
  }, new Date(Date.now() + pool.lockDays * 864e5).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: '2-digit'
  })))), /*#__PURE__*/React.createElement("div", {
    className: "dialog-footer"
  }, /*#__PURE__*/React.createElement("button", {
    className: "btn btn-outline",
    onClick: onClose
  }, "Cancel"), /*#__PURE__*/React.createElement("button", {
    className: "btn btn-primary",
    onClick: () => onConfirm && onConfirm({
      pool,
      amount
    })
  }, "Stake ", amount || '0', " ", pool.ticker))));
}
window.StakeDialog = StakeDialog;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/earn/StakeDialog.jsx", error: String((e && e.message) || e) }); }

// ui_kits/invest/App.jsx
try { (() => {
const {
  useState
} = React;
const PROJECTS = [{
  id: 'sahara',
  name: 'Sahara AI',
  desc: 'First full-stack, AI-native blockchain for building and monetizing models.',
  tokenTicker: 'SAHARA',
  fdv: '$400,000,000',
  allocation: '$6,000,000 (1.5%)',
  target: 10000000,
  raised: 7200000,
  start: '14/Mar/26 12:00:00 UTC',
  end: '21/Mar/26 12:00:00 UTC',
  state: 'ongoing'
}, {
  id: 'lombard',
  name: 'Lombard',
  desc: 'Bitcoin-backed liquidity infrastructure for institutions.',
  tokenTicker: 'LMB',
  fdv: '$250,000,000',
  allocation: '$3,500,000 (1.4%)',
  target: 5000000,
  raised: 2100000,
  start: '20/Mar/26 14:00:00 UTC',
  end: '27/Mar/26 14:00:00 UTC',
  state: 'ongoing'
}, {
  id: 'momentum',
  name: 'Momentum',
  desc: 'DEX and liquidity hub on Sui — perps, spot, shared CLOB.',
  tokenTicker: 'MOMO',
  fdv: '$180,000,000',
  allocation: '$2,000,000 (1.1%)',
  target: 4000000,
  raised: 0,
  start: '02/Apr/26 10:00:00 UTC',
  end: '09/Apr/26 10:00:00 UTC',
  state: 'upcoming'
}, {
  id: 'nomad',
  name: 'Nomad Capital',
  desc: 'On-chain venture capital with tokenized LP positions.',
  tokenTicker: 'NMD',
  fdv: '$120,000,000',
  allocation: '$1,800,000 (1.5%)',
  target: 3000000,
  raised: 3000000,
  start: '10/Feb/26 10:00:00 UTC',
  end: '17/Feb/26 10:00:00 UTC',
  state: 'ended'
}, {
  id: 'solayer',
  name: 'Solayer',
  desc: 'Restaking on Solana — securing new services with existing SOL.',
  tokenTicker: 'LAYER',
  fdv: '$620,000,000',
  allocation: '$4,200,000 (0.68%)',
  target: 6000000,
  raised: 6000000,
  start: '01/Jan/26 10:00:00 UTC',
  end: '08/Jan/26 10:00:00 UTC',
  state: 'ended'
}, {
  id: 'falcon',
  name: 'Falcon',
  desc: 'Stablecoin rails built for pre- and post-TGE yield.',
  tokenTicker: 'FLC',
  fdv: '$320,000,000',
  allocation: '$4,800,000 (1.5%)',
  target: 5500000,
  raised: 5500000,
  start: '15/Dec/25 10:00:00 UTC',
  end: '22/Dec/25 10:00:00 UTC',
  state: 'ended'
}];
function App() {
  const [view, setView] = useState('list');
  const [sel, setSel] = useState(null);
  const [loggedIn, setLoggedIn] = useState(false);
  const [contributed, setContributed] = useState(false);
  const [filter, setFilter] = useState('all');
  const [theme, setTheme] = useState('light');
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);
  const visible = PROJECTS.filter(p => filter === 'all' || p.state === filter);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      minHeight: '100vh',
      background: 'var(--secondary)'
    }
  }, /*#__PURE__*/React.createElement(Navbar, {
    active: "invest",
    loggedIn: loggedIn,
    onNav: t => {
      if (t === 'login') setView('login');
    }
  }), view === 'detail' && sel ? /*#__PURE__*/React.createElement(ProjectDetails, {
    project: sel,
    contributed: contributed,
    onBack: () => setView('list'),
    onContribute: () => {
      if (!loggedIn) {
        setView('login');
        return;
      }
      setContributed(true);
    }
  }) : /*#__PURE__*/React.createElement("main", {
    style: {
      maxWidth: 1280,
      margin: '0 auto',
      padding: '40px 32px'
    }
  }, /*#__PURE__*/React.createElement("section", {
    style: {
      textAlign: 'center',
      padding: '32px 0 40px'
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      font: 'var(--fw-bold) var(--text-5xl)/1.1 var(--font-sans)',
      letterSpacing: 'var(--tracking-tight)',
      margin: '0 0 12px'
    }
  }, "Revolutionizing Token Launches"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--text-lg)/1.5 var(--font-sans)',
      color: 'var(--muted-foreground)',
      margin: 0,
      maxWidth: 560,
      marginInline: 'auto'
    }
  }, "Skin in the game for long-term community. Pre-token access with transparent, VC-grade terms.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "tabs-list"
  }, ['all', 'ongoing', 'upcoming', 'ended'].map(f => /*#__PURE__*/React.createElement("button", {
    key: f,
    className: "tabs-trigger",
    "data-state": filter === f ? 'active' : undefined,
    onClick: () => setFilter(f)
  }, f[0].toUpperCase() + f.slice(1)))), /*#__PURE__*/React.createElement("button", {
    className: "btn btn-outline btn-sm",
    onClick: () => setTheme(theme === 'light' ? 'dark' : 'light')
  }, theme === 'light' ? '☾ Dark' : '☀ Light')), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill,minmax(320px,1fr))',
      gap: 16
    }
  }, visible.map(p => /*#__PURE__*/React.createElement(ProjectCard, {
    key: p.id,
    project: p,
    onOpen: pr => {
      setSel(pr);
      setView('detail');
      setContributed(false);
    }
  })))), /*#__PURE__*/React.createElement(LoginDialog, {
    open: view === 'login',
    onClose: () => setView(sel ? 'detail' : 'list'),
    onLogin: () => {
      setLoggedIn(true);
      setView(sel ? 'detail' : 'list');
    }
  }));
}
ReactDOM.createRoot(document.getElementById('root')).render(/*#__PURE__*/React.createElement(App, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/invest/App.jsx", error: String((e && e.message) || e) }); }

// ui_kits/invest/LoginDialog.jsx
try { (() => {
// LoginDialog.jsx — shadcn Dialog + Tabs
function LoginDialog({
  open,
  onClose,
  onLogin
}) {
  const [tab, setTab] = React.useState('wallet');
  const [email, setEmail] = React.useState('');
  if (!open) return null;
  const wallets = ['MetaMask', 'WalletConnect', 'Coinbase Wallet', 'Phantom', 'OKX', 'TronLink'];
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    className: "dialog-overlay",
    onClick: onClose
  }), /*#__PURE__*/React.createElement("div", {
    className: "dialog-content",
    onClick: e => e.stopPropagation()
  }, /*#__PURE__*/React.createElement("div", {
    className: "dialog-header"
  }, /*#__PURE__*/React.createElement("h2", {
    className: "dialog-title"
  }, "Log in to Buidlpad"), /*#__PURE__*/React.createElement("p", {
    className: "dialog-desc"
  }, "Choose your preferred login method.")), /*#__PURE__*/React.createElement("div", {
    className: "tabs-list",
    style: {
      alignSelf: 'stretch'
    }
  }, /*#__PURE__*/React.createElement("button", {
    className: "tabs-trigger",
    "data-state": tab === 'wallet' ? 'active' : undefined,
    onClick: () => setTab('wallet'),
    style: {
      flex: 1
    }
  }, "Wallet"), /*#__PURE__*/React.createElement("button", {
    className: "tabs-trigger",
    "data-state": tab === 'email' ? 'active' : undefined,
    onClick: () => setTab('email'),
    style: {
      flex: 1
    }
  }, "Email")), tab === 'wallet' ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 8
    }
  }, wallets.map(w => /*#__PURE__*/React.createElement("button", {
    key: w,
    className: "btn btn-outline",
    onClick: () => onLogin && onLogin({
      wallet: w
    })
  }, w))) : /*#__PURE__*/React.createElement("form", {
    onSubmit: e => {
      e.preventDefault();
      onLogin && onLogin({
        email
      });
    },
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("label", {
    className: "label"
  }, "Email", /*#__PURE__*/React.createElement("input", {
    className: "input",
    style: {
      marginTop: 6
    },
    type: "email",
    required: true,
    value: email,
    onChange: e => setEmail(e.target.value),
    placeholder: "name@example.com"
  })), /*#__PURE__*/React.createElement("button", {
    type: "submit",
    className: "btn btn-primary"
  }, "Send magic link")), /*#__PURE__*/React.createElement("div", {
    className: "dialog-footer"
  }, /*#__PURE__*/React.createElement("button", {
    className: "btn btn-ghost btn-sm",
    onClick: onClose
  }, "Cancel"))));
}
window.LoginDialog = LoginDialog;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/invest/LoginDialog.jsx", error: String((e && e.message) || e) }); }

// ui_kits/invest/Navbar.jsx
try { (() => {
// Navbar.jsx — shadcn-style top nav using semantic tokens
function Navbar({
  active = 'invest',
  onNav,
  loggedIn = false
}) {
  const items = [{
    id: 'invest',
    label: 'Invest'
  }, {
    id: 'vibe',
    label: 'Vibe'
  }, {
    id: 'earn',
    label: 'Earn'
  }];
  return /*#__PURE__*/React.createElement("header", {
    className: "bp-navbar"
  }, /*#__PURE__*/React.createElement("div", {
    className: "bp-brand"
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/buidlpad-wordmark.svg",
    height: 20,
    alt: "Buidlpad"
  }), /*#__PURE__*/React.createElement("span", {
    className: "badge badge-secondary"
  }, "Launchpad")), /*#__PURE__*/React.createElement("nav", {
    className: "bp-nav-items"
  }, items.map(i => /*#__PURE__*/React.createElement("a", {
    key: i.id,
    className: "nav-link",
    "data-state": active === i.id ? 'active' : undefined,
    onClick: () => onNav && onNav(i.id)
  }, i.label))), /*#__PURE__*/React.createElement("div", {
    className: "bp-nav-right"
  }, /*#__PURE__*/React.createElement("span", {
    className: "kbd"
  }, "\u2318K"), loggedIn ? /*#__PURE__*/React.createElement("div", {
    className: "bp-avatar"
  }, "MA") : /*#__PURE__*/React.createElement("button", {
    className: "btn btn-primary btn-sm",
    onClick: () => onNav && onNav('login')
  }, "Log in")));
}
window.Navbar = Navbar;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/invest/Navbar.jsx", error: String((e && e.message) || e) }); }

// ui_kits/invest/ProjectCard.jsx
try { (() => {
// ProjectCard.jsx — shadcn Card composition
function ProjectCard({
  project,
  onOpen
}) {
  const {
    name,
    desc,
    target,
    raised,
    state,
    start,
    end,
    tokenTicker
  } = project;
  const pct = Math.min(100, Math.round(raised / target * 100));
  const stateBadge = {
    ongoing: /*#__PURE__*/React.createElement("span", {
      className: "badge badge-success"
    }, "\u25CF Ongoing"),
    upcoming: /*#__PURE__*/React.createElement("span", {
      className: "badge badge-secondary"
    }, "Upcoming"),
    ended: /*#__PURE__*/React.createElement("span", {
      className: "badge badge-outline"
    }, "Ended")
  }[state];
  return /*#__PURE__*/React.createElement("div", {
    className: "card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "card-header"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    className: "card-title"
  }, name), stateBadge), /*#__PURE__*/React.createElement("p", {
    className: "card-desc"
  }, desc)), /*#__PURE__*/React.createElement("div", {
    className: "card-content",
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "progress"
  }, /*#__PURE__*/React.createElement("i", {
    style: {
      width: `${pct}%`,
      background: state === 'ended' ? 'var(--muted-foreground)' : 'var(--primary)'
    }
  })), /*#__PURE__*/React.createElement("dl", {
    className: "dl-grid"
  }, /*#__PURE__*/React.createElement("dt", null, "Target"), /*#__PURE__*/React.createElement("dd", {
    className: "font-mono"
  }, "$", target.toLocaleString()), /*#__PURE__*/React.createElement("dt", null, "Raised"), /*#__PURE__*/React.createElement("dd", {
    className: "font-mono"
  }, "$", raised.toLocaleString()), /*#__PURE__*/React.createElement("dt", null, "Token"), /*#__PURE__*/React.createElement("dd", null, tokenTicker), start && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("dt", null, "Start"), /*#__PURE__*/React.createElement("dd", {
    style: {
      fontSize: 'var(--text-xs)'
    }
  }, start)), end && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("dt", null, "End"), /*#__PURE__*/React.createElement("dd", {
    style: {
      fontSize: 'var(--text-xs)'
    }
  }, end)))), /*#__PURE__*/React.createElement("div", {
    className: "card-footer"
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--text-xs)',
      color: 'var(--muted-foreground)'
    }
  }, pct, "% filled"), /*#__PURE__*/React.createElement("button", {
    className: "btn btn-primary btn-sm",
    style: {
      marginLeft: 'auto'
    },
    onClick: () => onOpen && onOpen(project)
  }, "Project Details")));
}
window.ProjectCard = ProjectCard;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/invest/ProjectCard.jsx", error: String((e && e.message) || e) }); }

// ui_kits/invest/ProjectDetails.jsx
try { (() => {
// ProjectDetails.jsx — public-sale detail page
function ProjectDetails({
  project,
  onBack,
  onContribute,
  contributed
}) {
  const {
    name,
    fdv,
    allocation,
    start,
    end,
    target,
    raised,
    tokenTicker,
    desc
  } = project;
  const pct = Math.round(raised / target * 100);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--background)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '24px 32px',
      borderBottom: '1px solid var(--border)'
    }
  }, /*#__PURE__*/React.createElement("button", {
    className: "btn btn-ghost btn-sm",
    onClick: onBack
  }, "\u2190 Back")), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 1200,
      margin: '0 auto',
      padding: '32px',
      display: 'grid',
      gridTemplateColumns: '2fr 1fr',
      gap: 24
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 20
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("span", {
    className: "badge badge-success"
  }, "\u25CF Ongoing"), /*#__PURE__*/React.createElement("h1", {
    style: {
      font: 'var(--fw-bold) var(--text-4xl)/1.1 var(--font-sans)',
      margin: '12px 0 10px',
      letterSpacing: 'var(--tracking-tight)'
    }
  }, name), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--text-lg)/1.5 var(--font-sans)',
      color: 'var(--muted-foreground)',
      margin: 0
    }
  }, desc)), /*#__PURE__*/React.createElement("div", {
    className: "card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "card-header"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "card-title"
  }, "Terms")), /*#__PURE__*/React.createElement("div", {
    className: "card-content"
  }, /*#__PURE__*/React.createElement("dl", {
    className: "dl-grid"
  }, /*#__PURE__*/React.createElement("dt", null, "Token"), /*#__PURE__*/React.createElement("dd", null, tokenTicker), /*#__PURE__*/React.createElement("dt", null, "FDV"), /*#__PURE__*/React.createElement("dd", {
    className: "font-mono"
  }, fdv), /*#__PURE__*/React.createElement("dt", null, "Allocation"), /*#__PURE__*/React.createElement("dd", {
    className: "font-mono"
  }, allocation), /*#__PURE__*/React.createElement("dt", null, "Vesting"), /*#__PURE__*/React.createElement("dd", null, "20% TGE, 12-month linear"), /*#__PURE__*/React.createElement("dt", null, "Min / Max"), /*#__PURE__*/React.createElement("dd", {
    className: "font-mono"
  }, "$100 / $10,000"), /*#__PURE__*/React.createElement("dt", null, "Start"), /*#__PURE__*/React.createElement("dd", {
    className: "font-mono",
    style: {
      fontSize: 'var(--text-xs)'
    }
  }, start), /*#__PURE__*/React.createElement("dt", null, "End"), /*#__PURE__*/React.createElement("dd", {
    className: "font-mono",
    style: {
      fontSize: 'var(--text-xs)'
    }
  }, end)))), /*#__PURE__*/React.createElement("div", {
    className: "card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "card-header"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "card-title"
  }, "Timeline")), /*#__PURE__*/React.createElement("div", {
    className: "card-content",
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 14
    }
  }, [{
    n: '01',
    t: 'Skin in the game',
    s: 'Stake through Buidlpad',
    state: 'done'
  }, {
    n: '02',
    t: 'KYC & wallet verification',
    s: 'Confirm eligibility',
    state: 'done'
  }, {
    n: '03',
    t: 'Contribution window',
    s: 'Deposit USDC',
    state: 'active'
  }, {
    n: '04',
    t: 'Token claim',
    s: 'Starts on TGE + 7 days',
    state: 'pending'
  }].map(step => /*#__PURE__*/React.createElement("div", {
    key: step.n,
    style: {
      display: 'flex',
      gap: 14
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "font-mono",
    style: {
      fontSize: 'var(--text-2xl)',
      fontWeight: 500,
      width: 44,
      color: step.state === 'active' ? 'var(--primary)' : step.state === 'done' ? 'var(--success)' : 'var(--muted-foreground)'
    }
  }, step.n), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--fw-semibold) var(--text-sm)/1.3 var(--font-sans)'
    }
  }, step.t), /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-xs)/1.4 var(--font-sans)',
      color: 'var(--muted-foreground)',
      marginTop: 2
    }
  }, step.s))))))), /*#__PURE__*/React.createElement("aside", null, /*#__PURE__*/React.createElement("div", {
    className: "card",
    style: {
      position: 'sticky',
      top: 24
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "card-header"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "card-title font-mono",
    style: {
      fontSize: 'var(--text-3xl)',
      letterSpacing: 'var(--tracking-tight)'
    }
  }, "$", raised.toLocaleString()), /*#__PURE__*/React.createElement("p", {
    className: "card-desc font-mono"
  }, "of $", target.toLocaleString(), " \xB7 ", pct, "%")), /*#__PURE__*/React.createElement("div", {
    className: "card-content",
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 14
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "progress"
  }, /*#__PURE__*/React.createElement("i", {
    style: {
      width: `${pct}%`
    }
  })), contributed ? /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 12,
      background: 'color-mix(in oklch, var(--success) 12%, transparent)',
      borderRadius: 'var(--radius-md)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      color: 'var(--success)',
      font: 'var(--fw-semibold) var(--text-sm)/1 var(--font-sans)'
    }
  }, "\u2713 Contribution confirmed"), /*#__PURE__*/React.createElement("div", {
    className: "font-mono",
    style: {
      fontSize: 'var(--text-lg)',
      marginTop: 4
    }
  }, "$1,000.00 USDC"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--text-xs)',
      color: 'var(--muted-foreground)',
      marginTop: 6
    }
  }, "Tokens claimable at TGE + 7 days.")) : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("label", {
    className: "label",
    style: {
      marginBottom: 6,
      display: 'block'
    }
  }, "Amount (USDC)"), /*#__PURE__*/React.createElement("input", {
    className: "input font-mono",
    type: "number",
    defaultValue: "1000",
    placeholder: "0.00",
    style: {
      fontSize: 'var(--text-lg)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--text-xs)',
      color: 'var(--muted-foreground)',
      marginTop: 4
    }
  }, "Min $100 \xB7 Max $10,000")), /*#__PURE__*/React.createElement("button", {
    className: "btn btn-primary btn-lg",
    onClick: onContribute
  }, "Contribute")), /*#__PURE__*/React.createElement("div", {
    style: {
      paddingTop: 12,
      borderTop: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      fontSize: 'var(--text-sm)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--muted-foreground)'
    }
  }, "Your allocation"), /*#__PURE__*/React.createElement("span", {
    className: "font-mono"
  }, "$10,000")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--muted-foreground)'
    }
  }, "Wallet"), /*#__PURE__*/React.createElement("span", {
    className: "font-mono"
  }, "0x8F3a\u2026c41e"))))))));
}
window.ProjectDetails = ProjectDetails;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/invest/ProjectDetails.jsx", error: String((e && e.message) || e) }); }

})();
