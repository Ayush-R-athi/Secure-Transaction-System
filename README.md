# 🛡️ Zero-Trust Secure Online Transaction System

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![Redis](https://img.shields.io/badge/Redis-In--Memory_Cache-dc382d.svg)
![Security](https://img.shields.io/badge/Security-AES--256%20%7C%20RSA--4096-success.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

</p>

<p align="center">
<b>Enterprise Grade Secure Financial Transaction Framework</b><br>
Built using <b>Zero Trust Security Principles</b> with Hybrid Cryptography
</p>

---

# 📌 Project Overview

With the rapid growth of **digital payments**, traditional password-based security systems are no longer sufficient.

This project simulates a **real-world banking security architecture** where security is enforced directly at the **application layer**.

The system protects transaction payloads using a **Digital Envelope Architecture** combining:

- 🔐 **Asymmetric Encryption (RSA-4096)**
- 🔒 **Symmetric Encryption (AES-256 GCM)**
- ✍️ **Digital Signatures**
- 🚫 **Anti-Replay Protection**

This ensures **Confidentiality, Integrity, Authentication, and Non-Repudiation** for financial transactions.

---

# ⚠️ Threat Model & Security Mitigations

The system follows **Zero-Trust Security Principles** to protect against major cyber threats.

| Threat | Description | Defense |
|------|------|------|
| 🕵️ Packet Sniffing | Attackers capture network traffic | AES-256 GCM Encryption |
| 🔄 Replay Attack | Reusing valid transaction packets | Redis Nonce Burn System |
| 🛑 Data Tampering | MITM modifies encrypted data | AES-GCM Authentication Tag |
| 🎭 Identity Theft | Fake transaction sender | RSA-PSS Digital Signature |

If even **one byte** of encrypted data changes, the system **automatically rejects the transaction**.

---

# 🏗️ System Architecture – Digital Envelope Protocol

### Step 1 — Secure Handshake
The server generates a **one-time Nonce** and stores it in **Redis**.

### Step 2 — Digital Signature
Client hashes:

```

SHA256(transaction_data + nonce)

```

Then signs the hash using its **RSA Private Key**.

### Step 3 — Payload Encryption

The transaction payload is encrypted using:

```

AES-256 GCM

```

### Step 4 — Key Wrapping

The **AES session key** is encrypted using the **Server’s RSA Public Key**.

### Step 5 — Zero Knowledge Validation

Server performs:

1. Decrypt AES key using RSA  
2. Decrypt payload  
3. Verify digital signature  
4. Validate nonce  
5. Burn nonce in Redis  

If any step fails → **Transaction rejected**

---

# 💻 Tech Stack

| Layer | Technology |
|------|------|
| Backend | FastAPI (Python) |
| Cryptography | PyCryptodome |
| Cache / Anti-Replay | Redis |
| Frontend Dashboard | HTML5 + CSS3 + Vanilla JS |
| UI Style | Glassmorphism SOC Dashboard |

---

# 📂 Project Structure

```

secure-transaction-system/
│
├── client/
│   ├── generate_keys.py
│   ├── client.py
│   └── attacker.py
│
├── server/
│   └── main.py
│
├── frontend/
│   └── dashboard.html
│
├── keys/
│
└── requirements.txt

````

### File Description

| File | Purpose |
|----|----|
| generate_keys.py | Generates RSA-4096 key pairs |
| client.py | Sends secure encrypted transactions |
| attacker.py | Simulates replay & tampering attacks |
| main.py | FastAPI Zero-Trust validation engine |
| dashboard.html | Interactive SOC dashboard |

---

# 🚀 Setup & Installation

## 1️⃣ Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````

---

## 2️⃣ Generate Cryptographic Keys

```bash
cd client
python3 generate_keys.py
cd ..
```

---

## 3️⃣ Start Redis Database

(Ensure Redis is installed on your system)

```bash
sudo service redis-server start
```

---

## 4️⃣ Run Secure Backend Server

```bash
uvicorn server.main:app --reload
```

---

## 5️⃣ Launch SOC Dashboard

```bash
cd frontend
python3 -m http.server 9000
```

Open in browser:

```
http://localhost:9000/dashboard.html
```

---

# 💥 Hacker Simulation Module

This project includes a **cyber attack simulation system** to demonstrate the effectiveness of the security architecture.

### Execute Secure Protocol

Valid encrypted transaction is processed successfully.

### Inject Replay Attack

Redis detects duplicate nonce and returns:

```
HTTP 403 Forbidden
```

### Inject MITM Tampering

AES-GCM authentication tag fails and returns:

```
HTTP 400 Bad Request
```

---

# 🔐 Security Features

✔ Hybrid Cryptography (AES + RSA)
✔ Digital Signature Authentication
✔ Anti-Replay Token System
✔ Tamper Detection via Authentication Tags
✔ Zero-Trust Architecture
✔ Defense-in-Depth Security Design

---

# 📊 Example Workflow

```
Client
 │
 │  Sign Payload (RSA)
 │
 │  Encrypt Payload (AES)
 │
 │  Encrypt AES Key (RSA)
 │
 ▼
Server
 │
 │  Decrypt AES Key
 │
 │  Decrypt Payload
 │
 │  Verify Signature
 │
 │  Validate Nonce
 │
 ▼
Transaction Approved
```

---

# 🧠 Learning Outcomes

This project demonstrates practical implementation of:

* Hybrid Cryptography
* Secure Protocol Design
* Zero-Trust Architecture
* Digital Signatures
* Anti-Replay Mechanisms
* Secure Backend API Development

---

# 👨‍💻 Author

<p align="center">

### Made with ❤️ by **Ayush Rathi**

Cybersecurity • Cryptography • Secure Systems

</p>

---

# 📜 License

This project is released under the **MIT License**.

You are free to use, modify, and distribute it.

---

⭐ If you found this project useful, consider **starring the repository**.

```
```
