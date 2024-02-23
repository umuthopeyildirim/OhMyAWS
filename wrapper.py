import os
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed


def ingest_file(file_path):
    # Determine the loader type based on the file extension
    _, ext = os.path.splitext(file_path)
    loader_type = {
        '.pdf': 'pdf',
        '.rst': 'rst',
        # Add other file extensions and their corresponding loader types here
    }.get(ext.lower())

    if loader_type:
        # Assuming ingest.py is in the same directory and executable
        result = subprocess.run(['python', 'ingest.py', '--loader_type',
                                loader_type, '--fname', file_path], capture_output=True)
        return result.stdout
    else:
        return f"Unsupported file type for file: {file_path}"


def walk_and_ingest(start_path, max_workers=None):
    files_to_ingest = [os.path.join(root, file)
                       for root, _, files in os.walk(start_path)
                       for file in files
                       if os.path.splitext(file)[1].lower() in ['.pdf', '.rst']]

    # Automatically set max_workers based on available CPUs
    if max_workers is None:
        # Ensure at least one worker if cpu_count is None
        max_workers = os.cpu_count() or 1

    # Using ProcessPoolExecutor to parallelize ingestion
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Mapping files to the executor
        future_to_file = {executor.submit(
            ingest_file, file_path): file_path for file_path in files_to_ingest}

        # Progress bar setup
        with tqdm(total=len(files_to_ingest), desc="Ingesting files") as progress:
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    # Process result if needed
                except Exception as exc:
                    print(f'{file_path} generated an exception: {exc}')
                finally:
                    # Update progress bar each time a future completes
                    progress.update(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively ingest documents from a directory using multicore processing.")
    parser.add_argument("start_path", type=str,
                        help="The starting path of the directory to ingest documents from.")

    args = parser.parse_args()
    walk_and_ingest(args.start_path)
