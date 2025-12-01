#!/bin/bash
# LangChain Vulnerable Server Setup Script

set -e

echo "=== LangChain Target Setup ==="

# Install dependencies
apt-get update
apt-get install -y python3.11 python3.11-venv python3-pip

# Create vulnerable LangChain server
mkdir -p /opt/langchain-server
cd /opt/langchain-server

# Install old vulnerable version of LangChain
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install langchain==0.0.150 fastapi uvicorn openai

# Create vulnerable server app
cat > app.py << 'PYAPP'
from fastapi import FastAPI
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import PALChain
from langchain.tools import PythonREPLTool
import os

app = FastAPI()

# Initialize chains (vulnerable configurations)
llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY", "dummy-key"))

@app.post("/agent")
async def agent_endpoint(query: dict):
    """Vulnerable agent endpoint"""
    user_query = query.get("query", "")
    chain_type = query.get("chain_type", "basic")
    
    if chain_type == "PAL":
        # Vulnerable PALChain - allows code execution
        pal_chain = PALChain.from_math_prompt(llm, verbose=True)
        result = pal_chain.run(user_query)
    elif chain_type == "python_repl":
        # Vulnerable Python REPL
        python_repl = PythonREPLTool()
        result = python_repl.run(user_query)
    else:
        # Basic chain
        prompt = PromptTemplate(template="{query}", input_variables=["query"])
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(query=user_query)
    
    return {"result": result}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYAPP

# Create systemd service
cat > /etc/systemd/system/langchain.service << 'SERVICE'
[Unit]
Description=Vulnerable LangChain Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/langchain-server
ExecStart=/opt/langchain-server/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable langchain
systemctl start langchain

echo "=== LangChain Setup Complete ==="
echo "API available at: http://$(hostname -I | awk '{print $1}'):8000"
