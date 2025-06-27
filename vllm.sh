#!/bin/bash
#SBATCH --job-name=vllm-merged
#SBATCH --partition=c23g 
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=00:20:00
#SBATCH --output=logs/vllm_merged_%j.log

# Activate environment
source vllm_env/bin/activate

# Make sure log dir exists
mkdir -p logs

# Start vLLM server in background
echo "Starting vLLM server..."
vllm serve mistralai/Mistral-Small-3.1-24B-Instruct-2503 --tokenizer_mode mistral --config_format mistral --load_format mistral --tool-call-parser mistral --enable-auto-tool-choice --limit_mm_per_prompt 'image=10' --tensor-parallel-size 2 &

# Get the PID of the vLLM server
VLLM_PID=$!
echo "vLLM server started with PID: $VLLM_PID"

# Wait for the server to start with shorter intervals
echo "Waiting for vLLM server to start..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "vLLM server is ready!"
        break
    fi
    echo "Waiting... (attempt $i/60)"
    sleep 10
done

# Final check if the server is running
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "vLLM server failed to start or is not responding."
    kill $VLLM_PID 2>/dev/null
    exit 1
fi

echo "vLLM server started successfully."

# Run the Python script
echo "Running Python script..."
python -u vllm_server_2.py

# Stop the vLLM server
echo "Stopping vLLM server..."
kill $VLLM_PID 2>/dev/null
echo "vLLM server stopped."