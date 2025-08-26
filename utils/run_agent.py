import openai
import random
import time

def run_agent_openai(graph, inputs, config, max_retries=3):
    """Runs the agent with rate limit handling and real-time display"""
    for attempt in range(max_retries):
        try:
            for event in graph.stream(inputs, config=config):
                print("\n") 
                print(event) 
            return  # If we get here, everything went well

        except openai.RateLimitError as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
            print(f"⏳ Rate limit - waiting {wait_time:.2f}s (retry {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
            print("🔄 Resuming execution...")