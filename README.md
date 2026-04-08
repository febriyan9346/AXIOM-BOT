# AXIOM BOT 🤖

> **Auto-farming bot for Axiom Oracle — daily check-in, point submission, and uptime ping.**

🌐 **Dashboard:** [https://axiomoracle.xyz/dashboard?ref=AXIOM-VUHW](https://axiomoracle.xyz/dashboard?ref=AXIOM-VUHW)

---

## ✨ Features

- ✅ Auto Register wallet
- ✅ Auto Daily Check-in
- ✅ Auto Submit Points (farming)
- ✅ Auto Ping Uptime
- ✅ Multi-account support
- ✅ Proxy support (optional)
- ✅ Real-time leaderboard rank tracking
- ✅ Live ticker feeds from OKX

---

## 📋 Requirements

- Python 3.8+
- pip packages:
  - `requests`
  - `colorama`
  - `pytz`
  - `solders`

---

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/febriyan9346/AXIOM-BOT.git
cd AXIOM-BOT

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Setup

1. **Buat file `accounts.txt`** — satu private key Solana per baris:

```
YOUR_PRIVATE_KEY_1
YOUR_PRIVATE_KEY_2
```

2. *(Opsional)* **Buat file `proxy.txt`** — satu proxy per baris:

```
http://user:pass@ip:port
http://user:pass@ip:port
```

---

## ▶️ Usage

```bash
python bot.py
```

Pilih mode:
- `1` → Run with proxy
- `2` → Run without proxy

---

## 📁 File Structure

```
AXIOM-BOT/
├── bot.py          # Main bot script
├── accounts.txt    # Private keys (buat sendiri)
├── proxy.txt       # Proxy list (opsional)
├── requirements.txt
└── README.md
```

---

## ⚠️ Disclaimer

> Gunakan bot ini dengan risiko Anda sendiri. Pastikan Anda memahami risiko dalam menggunakan private key. Jangan bagikan private key kepada siapa pun.

---

## 💰 Support Us with Cryptocurrency

You can make a contribution using any of the following blockchain networks:

| Network | Wallet Address |
|---------|---------------|
| **EVM** | `0x216e9b3a5428543c31e659eb8fea3b4bf770bdfd` |
| **TON** | `UQCEzXLDalfKKySAHuCtBZBARCYnMc0QsTYwN4qda3fE6tto` |
| **SOL** | `9XgbPg8fndBquuYXkGpNYKHHhymdmVhmF6nMkPxhXTki` |
| **SUI** | `0x8c3632ddd46c984571bf28f784f7c7aeca3b8371f146c4024f01add025f993bf` |

---

<div align="center">
  Made with ❤️ by <b>FEBRIYAN</b>
</div>
