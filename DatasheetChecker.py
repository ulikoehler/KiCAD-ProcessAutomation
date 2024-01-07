#!/usr/bin/env python3
import httpx
import asyncio
from io import BytesIO
import magic
import re
from tqdm import tqdm
import os
import html
import yaml
from urllib.parse import urlparse
from collections import defaultdict, namedtuple
from SExpressions import parse_sexpr, extract_datasheets

CONCURRENT_LIMIT_PER_HOST = 5  # Adjust this as needed
# NOTE: Some websites may block requests that do not have a valid User-Agent header
# As an example, consider "https://assets.nexperia.com/documents/data-sheet/BAS16_SER.pdf"
# which returns a 403 error if the User-Agent header is not set to a browser-like value
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/88.0.4324.96 Chrome/88.0.4324.96 Safari/537.36'

DatasheetWarning = namedtuple('DatasheetWarning', ['library', 'symbol', 'url', 'message'])
DatasheetError = namedtuple('DatasheetError', ['library', 'symbol', 'url', 'message'])

class DatasheetFetcher(object):
    def __init__(self):
        self.tasks_done = 0
        self.tasks_total = 0
    
    async def fetch_url(self, client, library, symbol, url, prefix="", redirects_left=3, warn_http=False):
        results = []
        
        # Parse and validate the URL
        parsed_url = urlparse(url)
        if parsed_url.scheme == '':
            results.append(DatasheetError(library=library, symbol=symbol, url=url, message=prefix + "Invalid URL: missing protocol"))
        if parsed_url.netloc == '':
            results.append(DatasheetError(library=library, symbol=symbol, url=url, message=prefix + "Invalid URL: missing hostname"))
        if parsed_url.scheme not in ['http', 'https']:
            results.append(DatasheetError(library=library, symbol=symbol, url=url, message=prefix + f"URL does not have HTTP or HTTPS protocol but {parsed_url.scheme}"))
        # If the URL uses HTTP and not HTTPS, add a warning
        if parsed_url.scheme == 'http' and warn_http:
            results.append(DatasheetWarning(library=library, symbol=symbol, url=url, message=prefix + "URL uses HTTP instead of HTTPS"))

        # if results has any Error items, return them immediately
        if any(isinstance(x, DatasheetError) for x in results):
            return results
        
        try:
            response = await client.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)

            # Handle redirects
            if response.status_code == 301 or response.status_code == 302:
                # Check if we have any redirects left
                if redirects_left == 0:
                    results.append(DatasheetError(library=library, symbol=symbol, url=url,
                                        message=prefix + f"Too many redirects. Final redirect was to {response.headers['Location']}"))
                    return results
                # Check if the protocol has changed from HTTP to HTTPS
                redirect_url = urlparse(response.headers['Location'])
                if parsed_url.scheme == 'http' and redirect_url.scheme == 'https':
                    # Check if everything else is the same by creating a test URL by
                    # setting the original URL's protocol to HTTPS
                    # and comparing the result to the location header
                    _test_url = parsed_url._replace(scheme='https')
                    # Compare to the original URL
                    if _test_url == redirect_url: # Only the protocol changed
                        results.append(DatasheetWarning(library=library, symbol=symbol, url=response.headers['Location'],
                                            message=prefix + f"URL has changed from HTTP to HTTPS (no other changes)"))
                    else:
                        results.append(DatasheetError(library=library, symbol=symbol, url=response.headers['Location'],
                                            message=prefix + f"URL has changed to {response.headers['Location']}"))
                else: # The protocol has not changed -> Treat as generic URL change
                    results.append(DatasheetWarning(library=library, symbol=symbol, url=url,
                                        message=prefix + f"URL has changed to {response.headers['Location']}"))
                # Now repeat the request with the new URL (keep our original warnings)
                return results + await self.fetch_url(client, library, symbol, response.headers['Location'], prefix=prefix + "[Redirected] ", redirects_left=redirects_left-1)
            elif response.status_code != 200:
                results.append(DatasheetError(library=library, symbol=symbol, url=url,
                                    message=prefix + f"URL returns status code {response.status_code}"))
            # Download the data into BytesIO
            data = BytesIO(response.content)
            
            # Check if the content has zero bytes
            if data.getbuffer().nbytes == 0:
                results.append(DatasheetError(library=library, symbol=symbol, url=url, message=prefix + "Response is empty (0 bytes)"))
                return results

            # Verify if the content is a PDF
            mime = magic.from_buffer(data.getvalue(), mime=True)
            if mime == 'application/pdf':
                # Success! Nothing to do here
                return results
            else:
                results.append(DatasheetError(library=library, symbol=symbol, url=url, message=prefix + f"Content is not a PDF but {mime}"))
        except httpx.ConnectTimeout as e:
            results.append(DatasheetError(library=library, symbol=symbol, url=url, message=prefix + f"Connect timeout while fetching datasheet"))
        except httpx.ReadTimeout as e:
            results.append(DatasheetError(library=library, symbol=symbol, url=url, message=prefix + f"Read timeout while fetching datasheet"))
        except httpx.RequestError as e:
            results.append(DatasheetError(library=library, symbol=symbol, url=url, message=prefix + f"Exception while fetching datasheet: {type(e)}: {str(e)}"))
        return results

    async def worker(self, host, queue, results):
        async with httpx.AsyncClient() as client:
            while not queue.empty():
                library, symbol, url = await queue.get()
                try:
                    result = await self.fetch_url(client, library, symbol, url)
                except Exception as e:
                    result = [DatasheetError(library=library, symbol=symbol, url=url,
                                    message=f"Exception while fetching datasheet: {type(e)}: {str(e)}")
                    ]
                self.tasks_done += 1
                queue.task_done()
                if result is not None:
                    results += result

    async def fetch_and_verify_urls(self, library: str, url_dict: dict):
        """
        Asynchronously fetches URLs from a given dictionary of symbols to URLs, verifies their content,
        and checks for specific HTTP response statuses. It limits the number of concurrent requests per host.

        The function creates a queue for each unique host found in the URL dictionary. Each queue is processed
        by a group of worker coroutines, with the number of concurrent workers per host limited to a preset maximum.
        Each worker fetches the URL, checks for HTTP redirect status (301/302), downloads the content, and verifies if
        the content is a PDF file. 

        URL validation is performed to ensure that each URL has a valid HTTP/HTTPS protocol. If the URL is invalid,
        an error is reported. If a fetched URL returns a 301/302 status code, a warning is generated indicating that
        the URL has been permanently moved.

        Parameters:
        url_dict (dict): A dictionary where keys are symbols (string) representing the item (e.g., electronic component)
                        and values are URLs (string) pointing to the resources (e.g., datasheets) associated with the symbols.

        Returns:
        list: A list of namedtuple objects (either DatasheetWarning or DatasheetError). Warning objects contain information about URLs that
            have been permanently moved (status code 301/302). Error objects contain information about URLs that are invalid
            or caused a request error.

        Example:
        url_dict = {"ComponentA": "http://example.com/datasheetA.pdf",
                    "ComponentB": "http://example.com/datasheetB.pdf"}
        results = asyncio.run(fetch_and_verify_urls(url_dict))
        for result in results:
            if isinstance(result, DatasheetError):
                print(f"Error for {result.symbol}: {result.message}")
            elif isinstance(result, DatasheetWarning):
                print(f"Warning for {result.symbol}: {result.message}")

        Notes:
        - The function leverages asyncio for asynchronous I/O and httpx for making HTTP requests.
        - The 'magic' library is used to check if the content type of the downloaded data is a PDF.
        - The function implements error handling for request failures and invalid URLs.
        - The concurrency limit per host is defined by the CONCURRENT_LIMIT_PER_HOST constant.
        """
        queues = defaultdict(asyncio.Queue)
        tasks = []
        results = []

        # Group URLs by host
        for symbol, url in url_dict.items():
            host = urlparse(url).hostname
            self.tasks_total += 1
            await queues[host].put((library, symbol, url))

        # Create workers for each host
        for host, queue in queues.items():
            for _ in range(CONCURRENT_LIMIT_PER_HOST):
                task = asyncio.create_task(self.worker(host, queue, results))
                tasks.append(task)

        # Wait for tasks to finish with progress bar
        progress_bar = tqdm(total=self.tasks_total, desc=f"{library}.kicad_sym")
        while self.tasks_done < self.tasks_total:
            # Update progress bar
            progress_bar.update(self.tasks_done - progress_bar.n)
            await asyncio.sleep(0.2)
        
        # Wait for all tasks in the queues to be processed
        for queue in queues.values():
            await queue.join()

        # Cancel all workers after the work is done
        for task in tasks:
            task.cancel()
        
        # Wait for all tasks to be completed i.e. cancelled
        await asyncio.wait(tasks)
        
        # Append all results into a single list & return
        return results


def group_results_by_library_and_symbol(results):
    grouped_results = defaultdict(lambda: defaultdict(list))

    for result in results:
        # Assuming result has attributes 'library', 'symbol', and 'message'
        library = result.library
        symbol = result.symbol

        # Group by library and then by symbol
        grouped_results[library][symbol].append(result)

    return grouped_results


def create_html_page_for_library(library_name, symbols_dict):
    symbol_count = count_symbols_by_status(symbols_dict)
    html_content = f"""
    <html>
    <head>
        <title>{library_name} - Library Report</title>
        <style>
            .error {{ color: red !important; }}
            .warning {{ color: orange !important; }}
            a {{ color: blue; }}
        </style>
    </head>
    <body>
        <h1>Library: {library_name}: {symbol_count.symbols_with_error} errors, {symbol_count.symbols_with_warning_only} warnings</h1>
    """

    for symbol, results in symbols_dict.items():
        html_content += f"<h2>Symbol: {symbol}</h2><ul>"
        for result in results:
            # Determine the type of result (Warning or Error) and format message
            css_class = "warning" if isinstance(result, DatasheetWarning) else "error"
            message_with_links = html.escape(result.message)  # Convert special characters to HTML equivalents
            if result.url:
                message_with_links += f' <a href="{result.url}">[Link]</a>'

            html_content += f"<li class='{css_class}'>{message_with_links}</li>"
        html_content += "</ul>"

    html_content += "</body></html>"
    return html_content

SymbolCount = namedtuple('SymbolCount', ['symbols_with_error', 'symbols_with_warning_only'])

def represent_namedtuple(dumper, data):
    return dumper.represent_dict(data._asdict())

import collections
from yaml.representer import Representer
yaml.SafeDumper.add_representer(DatasheetError, represent_namedtuple)
yaml.SafeDumper.add_representer(DatasheetWarning, represent_namedtuple)
yaml.SafeDumper.add_representer(SymbolCount, represent_namedtuple)
yaml.SafeDumper.add_representer(collections.defaultdict, Representer.represent_dict)

def count_symbols_by_status(symbols_dict):
    symbols_with_error = 0
    symbols_with_warning_only = 0

    for symbol, results in symbols_dict.items():
        has_error = any(isinstance(result, DatasheetError) for result in results)
        has_warning = any(isinstance(result, DatasheetWarning) for result in results)

        if has_error:
            symbols_with_error += 1
        elif has_warning:
            symbols_with_warning_only += 1

    return SymbolCount(symbols_with_error, symbols_with_warning_only)

async def process_library(filename, outdir):
    library_name = os.path.splitext(os.path.basename(filename))[0]
        
    with open(filename, 'r', encoding="utf-8") as f:
        parsed_data = parse_sexpr(f)
        
    datasheets = extract_datasheets(parsed_data)
    
    fetcher = DatasheetFetcher()
    
    loop = asyncio.get_event_loop()
    results = await fetcher.fetch_and_verify_urls(library_name, datasheets)
    
    symbols_dict = group_results_by_library_and_symbol(results)

    # Create HTML page
    html_content = create_html_page_for_library(library_name, symbols_dict[library_name])

    # Write HTML page to file
    with open(os.path.join(outdir, f"{library_name}.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    # Write results as YAML
    symbol_count = count_symbols_by_status(symbols_dict)
    with open(os.path.join(outdir, f"{library_name}.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump({"statistics": symbol_count,
                        "results": symbols_dict[library_name]}, f)

    # Print summary
    print(f"Library: {library_name}")
    print(f"  Symbols with errors: {symbol_count.symbols_with_error}")
    print(f"  Symbols with warnings only: {symbol_count.symbols_with_warning_only}")
    print(f"  Total symbols: {len(symbols_dict)}")
    print()
    

if __name__ == "__main__":
    import argparse
    import sys
    import os
    import re
    
    parser = argparse.ArgumentParser(description='Check datasheet URLs in KiCad symbol libraries')
    parser.add_argument('path', help='Path to KiCad symbol library or directory containing KiCad symbol libraries')
    parser.add_argument('--outdir', '-o', required=True, help='Output directory for HTML reports')
    args = parser.parse_args()
    
    # Create outdir directory if it doesn't exist
    os.makedirs(args.outdir, exist_ok=True)
    
    if os.path.isdir(args.path):
        # Process all files in the directory
        files = [os.path.join(args.path, f) for f in os.listdir(args.path) if os.path.isfile(os.path.join(args.path, f))]
    elif os.path.isfile(args.path):
        # Process a single file
        files = [args.path]
    else:
        print(f"Invalid path argument, neither a file nor a directory: {args.path}")
        sys.exit(1)
        
    # Sort files lexicographically
    files.sort()
    
    loop = asyncio.get_event_loop()
    for file in files:
        loop.run_until_complete(process_library(file, args.outdir))
    