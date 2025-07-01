# 🚀 Quick Start Guide: A2A Bridge to uAgent

## ⚡ **TL;DR - 4 Steps to Success**

### **Step 1: Install Dependencies**
```bash
cd /Users/radhikadanda/agents-agentverse/currency-price-agent

# Create virtual environment (if not already created)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Start Currency uAgent & Get Address** 
```bash
# Terminal 1
cd /Users/radhikadanda/agents-agentverse/currency-price-agent
export GOOGLE_API_KEY="your_google_api_key_here"
python currency_uagent.py
```
**Look for**: `Agent Address: agent1qv...` (Copy this address!)

**⚠️ IMPORTANT**: Copy the agent address and paste it into `app/agent_executor.py` line 38:
```python
"convert_currency": "agent1qv3yr66aw2qu3gzce5ckae84uj8ea5hua90q9mzwxcr9ghvtv0xeykme4dv",  # YOUR ADDRESS HERE
```

### **Step 3: Start A2A Bridge Server**
```bash
# Terminal 2  
cd /Users/radhikadanda/agents-agentverse/currency-price-agent
export GOOGLE_API_KEY="your_google_api_key_here"
python -m app --host 0.0.0.0
```
**Look for**: `Uvicorn running on http://0.0.0.0:10000`

### **Step 4: Test Communication**
```bash
# Terminal 3
cd /Users/radhikadanda/agents-agentverse/currency-price-agent
python test_client.py
```
**Expected**: JSON response with currency conversion data

---

## 🧪 **Test Commands**

### **Single Skill Test**
```bash
python test_client.py
```

### **Multi-Skill Test**
```bash
python test_multi_skill.py
```

### **Direct HTTP Test**
```bash
curl -X POST http://localhost:10000 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "send_message", 
    "id": "test123",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "What is USD to EUR rate?"}],
        "messageId": "msg123"
      }
    }
  }'
```

---

## 🔧 **Troubleshooting**

### **Port Already in Use**
```bash
# Find and kill process on port 10000
lsof -ti:10000 | xargs kill -9
```

### **Missing API Key**
```bash
export GOOGLE_API_KEY="your_google_gemini_api_key"
```

### **uAgent Not Responding**
- Check that `currency_uagent.py` is running
- Verify agent address matches in `agent_executor.py`
- Check network connectivity to Agentverse

---

## 📊 **Success Indicators**

### ✅ **Currency uAgent Started**
```
💱 Currency uAgent Started Successfully!
📍 Agent Address: agent1qv3yr66aw2qu3gzce5ckae84uj8ea5hua90q9mzwxcr9ghvtv0xeykme4dv
🌐 Mailbox: ✅ Enabled (Agentverse registration)
```

### ✅ **A2A Bridge Started**
```
INFO: Uvicorn running on http://0.0.0.0:10000
✅ A2A Bridge to uAgent started successfully
```

### ✅ **Successful Test Response**
```json
{
  "result": {
    "artifacts": [{
      "name": "conversion_result", 
      "parts": [{"text": "The current exchange rate from USD to EUR is 0.84674."}]
    }],
    "status": {"state": "completed"}
  }
}
```

---

## 🎯 **Key Files**

| File | Purpose | Status |
|------|---------|--------|
| `currency_uagent.py` | uAgent on Agentverse | ✅ Ready |
| `app/__main__.py` | A2A Server | ✅ Ready |
| `app/agent_executor.py` | Bridge Logic | ✅ Ready |
| `test_client.py` | A2A Client Test | ✅ Ready |

---

## 🌟 **What You Achieved**

**✅ Universal A2A-to-uAgent Bridge**  
**✅ Real-time Currency Conversion**  
**✅ Multi-skill Agent Card**  
**✅ Production-ready Architecture**  

**Your system can now connect ANY A2A client to ANY uAgent on Agentverse!** 🚀
