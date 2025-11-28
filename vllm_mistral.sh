#!/bin/bash
#SBATCH --job-name=vllm-mistral
#SBATCH --partition=c23g 
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:30:00
#SBATCH --output=logs/vllm_mistral_%j.log


# Activate environment
source ../../vllm_env/bin/activate

# Make sure log dir exists
mkdir -p logs

echo "Current GPU status before vLLM launch:"
nvidia-smi

# Start vLLM server in background
echo "Starting vLLM server..."
vllm serve mistralai/Mistral-Small-3.1-24B-Instruct-2503 \
    --tokenizer_mode mistral \
    --config_format mistral \
    --load_format mistral \
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

# Final check if the server is running
if ! curl -s http://localhost:8001/health >/dev/null 2>&1; then
    echo "vLLM server failed to start or is not responding."
    kill $VLLM_PID 2>/dev/null
    exit 1
fi

echo "vLLM server started successfully."

echo "Current GPU status after vLLM launch:"
nvidia-smi

# Run the Python script
echo "Running Python script..."
python -u run_iterations.py --llm-name "mistral"

# Stop the vLLM server
echo "Stopping vLLM server..."
kill $VLLM_PID 2>/dev/null
echo "vLLM server stopped."
