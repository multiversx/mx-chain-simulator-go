import queue
import subprocess
import threading
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


def enqueue_output(pipe, q):
    for line in iter(pipe.readline, b''):
        q.put(line)
    pipe.close()


def extract_port_from_process(proc, index):
    port_pattern = re.compile(r'INFO.*chain simulator\'s is accessible through the URL localhost:(\d+)')
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

    q = queue.Queue()

    # Start threads to read stdout and stderr
    threading.Thread(target=enqueue_output, args=(proc.stdout, q)).start()
    threading.Thread(target=enqueue_output, args=(proc.stderr, q)).start()

    while True:
        try:
            line = q.get_nowait()  # Get line from the queue non-blocking
        except queue.Empty:
            if proc.poll() is not None:
                break  # Process has finished and queue is empty
            continue

        # Decode the line and remove ANSI escape sequences
        line = line.decode('utf-8').strip()
        cleaned_line = ansi_escape.sub('', line)
        print(f"{index} - {cleaned_line}")
        # Search for the port number
        match = port_pattern.search(cleaned_line)
        if match:
            return match.group(1)

    return None


def find_and_print_duplicates(arr):
    seen = set()
    duplicates = set()

    for num in arr:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)

    if duplicates:
        print(f"Duplicated values: {', '.join(map(str, duplicates))}")
        return True
    else:
        return False


def start_instance(index, used_ports):
    print(f"Start process index={index}")
    proc = subprocess.Popen(['./chainsimulator', '--server-port', "0"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    port = extract_port_from_process(proc, index)
    used_ports.add(port)

    print(f"Started instance of chain simulator - index={index}, port={port}")

    return proc, port


def start_instances(num_instances):
    processes = []
    used_ports = set()

    with ThreadPoolExecutor(max_workers=num_instances) as executor:
        futures = {executor.submit(start_instance, i, used_ports): i for i in range(num_instances)}
        for future in as_completed(futures):
            proc, port = future.result()
            processes.append((proc, port))

    res= find_and_print_duplicates(used_ports)

    print(f"Duplicated ports={res}")

    return processes


def get_api_response(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get response: {response.status_code}, url:{url}")
    except Exception as e:
        print(f"Error getting API response: {e}")
    return None


def post_generate_blocks(port):
    try:
        print(f"Generating blocks for chain simulator instance with port={port}")

        api_url = f"http://localhost:{port}/simulator/generate-blocks/10"
        response = requests.post(api_url)
        if response.status_code == 200:
            return True
        else:
            print(f"Failed to generate blocks: {response.status_code}")
    except Exception as e:
        print(f"Error generating blocks: {e}")
    return False


def check_for_duplicate_ports(processes):
    ports = {}
    duplicates = []
    for proc, port in processes:
        # post_generate_blocks(port)

        api_url = f"http://localhost:{port}/simulator/observers"  # Adjust the URL pattern as needed
        response = get_api_response(api_url)
        if response:
            for key, value in response.get("data", {}).items():
                api_port = value.get("api-port")
                if api_port in ports:
                    duplicates.append(api_port)
                else:
                    ports[api_port] = 1
    return duplicates


def terminate_instances(processes):
    for proc, _ in processes:
        proc.terminate()


def main():
    num_instances = 30

    print("Starting instances...")
    processes = start_instances(num_instances)

    print("Collecting API responses and checking for duplicate ports...")
    duplicates = check_for_duplicate_ports(processes)

    if duplicates:
        print(f"Duplicate ports found: {duplicates}")
    else:
        print("No duplicate ports found.")

    print("Terminating instances...")
    terminate_instances(processes)


if __name__ == "__main__":
    main()