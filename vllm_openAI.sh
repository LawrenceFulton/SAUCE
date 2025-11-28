#!/bin/bash
#SBATCH --job-name=vllm-openAI
#SBATCH --partition=c23g 
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=100G
#SBATCH --time=01:00:00
#SBATCH --output=logs/vllm_openAI_%j.log


module load GCC/13.3.0
module load Python/3.12.3
module load CUDA/12.6.3


# Activate environment
source ../../vllm_env/bin/activate

export TORCH_CUDA_ARCH_LIST="9.0" # For H100 GPUs

# Force the use of GCC for compiling CUDA extensions
export CC=gcc
export CXX=g++



# Make sure log dir exists
mkdir -p logs

echo "Current GPU status before vLLM launch:"
nvidia-smi

export HOME=/work/cj010365
export HF_HOME=/work/cj010365/.hf_home
export HF_HUB_CACHE=/work/cj010365/.hf_cache
export TRANSFORMERS_CACHE=/work/cj010365/.hf_cache
export VLLM_LOGGING_LEVEL=DEBUG



# Start vLLM server in background
echo "Starting vLLM server..."
vllm serve openai/gpt-oss-120b \
    --port 8001 &

# Get the PID of the vLLM server
VLLM_PID=$!
echo "vLLM server started with PID: $VLLM_PID"


# Wait for the server to start
echo "Waiting for vLLM server to start..."
for i in {1..300}; do
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo "vLLM server is ready!"
        break
    fi
    echo "Waiting... (attempt $i/300)"
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
python -u run_iterations.py --llm-name "gpt-oss"

# Stop the vLLM server
echo "Stopping vLLM server..."
kill $VLLM_PID 2>/dev/null
echo "vLLM server stopped."
