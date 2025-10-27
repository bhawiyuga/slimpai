# slimpAI Quick Start Guide

## 🎯 Management Commands

### Start the Server
```bash
./slimpy start
```
✅ Starts slimpAI in the background  
🌐 Opens at: http://localhost:5000

### Stop the Server
```bash
./slimpy stop
```
🛑 Gracefully stops the server

### Restart the Server
```bash
./slimpy restart
```
🔄 Stops and starts the server (useful after code changes)

### Check Status
```bash
./slimpy status
```
📊 Shows if server is running, PID, and recent logs

### View Logs
```bash
./slimpy logs
```
📋 Live tail of server logs (Ctrl+C to exit)

---

## 📁 Project Structure

```
hackhaton/
├── slimpy              # Management script (start/stop/restart)
├── server.py           # Flask web server
├── index.html          # Frontend UI
├── agent.js            # JavaScript bridge
├── my_agent/           # 5-Agent System
│   ├── guide_agent.py      # Agent 1: Supervisor
│   ├── tester_agent.py     # Agent 2: Test Creator
│   ├── planner_agent.py    # Agent 3: Lesson Planner
│   ├── explainer_agent.py  # Agent 4: Professor Pizza
│   ├── quizzer_agent.py    # Agent 5: Quiz Creator
│   └── slimp_ai.py         # Orchestrator
├── .env                # API keys
└── slimpy.log          # Server logs
```

---

## 🔧 Common Tasks

### After Making Code Changes
```bash
./slimpy restart
```

### Debugging Issues
```bash
./slimpy logs
# or
cat slimpy.log
```

### Check if Server is Running
```bash
./slimpy status
```

### Clean Restart
```bash
./slimpy stop
rm slimpy.log .slimpy.pid
./slimpy start
```

---

## 🌐 Access the App

Once started, open your browser to:
**http://localhost:5000**

---

## 🎓 How It Works

1. **User visits** → Welcome screen
2. **Click "Yes, let's go!"** → Tester Agent creates baseline test
3. **Answer 3 questions** → System assesses knowledge
4. **Planner Agent** → Creates personalized lesson plan
5. **Explainer Agent** → Teaches concepts with fun analogies
6. **Quizzer Agent** → Tests understanding
7. **Repeat** → Until all lessons complete

---

## 🆘 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill any process using port 5000
kill -9 $(lsof -t -i:5000)

# Try starting again
./slimpy start
```

### Server crashes
```bash
# Check logs for errors
./slimpy logs

# Or view full log
cat slimpy.log
```

### API Key Issues
```bash
# Make sure .env file exists with:
GOOGLE_API_KEY=your_api_key_here
```

---

## 📚 Learn More

- **Agent Documentation**: See `my_agent/README.md`
- **Full README**: See `README.md`
- **Server Code**: See `server.py`
- **Frontend Code**: See `index.html`

---

Made with ❤️ using Google ADK
