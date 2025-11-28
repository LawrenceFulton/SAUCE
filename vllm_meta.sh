#!/bin/bash
#SBATCH --job-name=vllm-llama4scout
#SBATCH --partition=c23g
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=logs/vllm_llama4scout_%j.log

# Activate environment
source ../../vllm_env/bin/activate

# Make sure log dir exists
mkdir -p logs

echo "Current GPU status before vLLM launch:"
nvidia-smi

# Start vLLM server in background with 2-way tensor parallelism
echo "Starting vLLM server..."
vllm serve meta-llama/Llama-4-Scout-17B-16E-Instruct \
    --tensor-parallel-size 2 \
    --moe --moe-num-experts 16 --moe-top-k 2 \
    --port 8001 &

# Get the PID of the vLLM server
VLLM_PID=$!
echo "vLLM server started with PID: $VLLM_PID"

# Wait for the server to start
echo "Waiting for vLLM server to start..."
for i in {1..200}; do
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo "vLLM server is ready!"
        break
    fi
    echo "Waiting... (attempt $i/200)"
    sleep 5
done

if ! curl -s http://localhost:8001/health >/dev/null 2>&1; then
    echo "vLLM server failed to start or is not responding."
    kill $VLLM_PID 2>/dev/null
    exit 1
fi

echo "vLLM server started successfully."

echo "Current GPU status after vLLM launch:"
nvidia-smi

# Run your task
echo "Running Python script..."
python -u run_iterations.py --llm-name "llama-4-scout"

# Kill vLLM server
echo "Stopping vLLM server..."
kill $VLLM_PID 2>/dev/null
echo "vLLM server stopped."
