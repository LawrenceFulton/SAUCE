#!/bin/bash
#SBATCH --job-name=vllm-llama4-scout
#SBATCH --partition=c23g 
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --output=logs/vllm_llama4_scout_%j.log

# Activate environment
source vllm_env/bin/activate

# Make sure log dir exists
mkdir -p logs

echo "Current GPU status before vLLM launch:"
nvidia-smi

# Start vLLM server in background
echo "Starting vLLM server..."
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --tokenizer meta-llama/Llama-3.1-8B-Instruct \
    --tensor-parallel-size 1 \
    --dtype bfloat16 \
    --swap-space 4 &


# Get the PID of the vLLM server
VLLM_PID=$!
echo "vLLM server started with PID: $VLLM_PID"


# Wait for the server to start
echo "Waiting for vLLM server to start..."
for i in {1..100}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "vLLM server is ready!"
        break
    fi
    echo "Waiting... (attempt $i/60)"
    sleep 5
done

# Final check if the server is running
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "vLLM server failed to start or is not responding."
    kill $VLLM_PID 2>/dev/null
    exit 1
fi

echo "vLLM server started successfully."

echo "Current GPU status after vLLM launch:"
nvidia-smi

# Run the Python script
echo "Running Python script..."
python -u vllm_server_2.py

# Stop the vLLM server
echo "Stopping vLLM server..."
kill $VLLM_PID 2>/dev/null
echo "vLLM server stopped."
