import sys
import time
import random
from colorama import init, Fore, Style
from googlesearch import search
import os
import re
from datetime import datetime

# Initialize colorama for colored terminal output
init()

# List of top visited websites (based on Semrush/VisualCapitalist data, May 2025)
TOP_WEBSITES = {
    "google.com": 105.41e9,  # Monthly visits in billions
    "youtube.com": 47.04e9,
    "facebook.com": 10.47e9,
    "instagram.com": 9.24e9,
    "reddit.com": 5.3e9,
    "wikipedia.org": 4.8e9,
    "chatgpt.com": 4.7e9,
    "amazon.com": 3.5e9,
    "yahoo.com": 3.0e9,
    "baidu.com": 2.0e9
}

# Simple loading animation
def loading_animation(text="Searching"):
    chars = "/—\\|"
    for _ in range(5):
        for char in chars:
            sys.stdout.write(f"\r{text} {char}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(text) + 2) + "\r")

# Generate a better description for the search query
def generate_description(query):
    descriptions = {
        "flutter": "Flutter is an open-source UI software development kit created by Google, used for building natively compiled applications for mobile, web, and desktop from a single codebase.",
        "python": "Python is a high-level, interpreted programming language known for its simplicity and versatility, widely used in web development, data science, and automation.",
        "javascript": "JavaScript is a programming language primarily used for creating interactive web applications and dynamic content on websites."
    }
    return descriptions.get(query.lower(), f"Search query '{query}' may refer to information, services, or content related to {query.lower()}. Explore the results below for more details.")

# Search web with priority to popular websites
def search_web(query, max_results=5):
    results = []
    try:
        loading_animation("Fetching web results")
        for url in search(query, num_results=max_results * 2):  # Fetch more to filter
            domain = re.search(r"https?://(www\.)?([^\./]+)\.", url)
            if domain:
                domain = domain.group(2) + ".com"  # Simplify domain for matching
                score = TOP_WEBSITES.get(domain, 1)  # Default score if not in top websites
                results.append({"url": url, "score": score})
            else:
                results.append({"url": url, "score": 1})
        # Sort by score (traffic) and then by relevance
        results.sort(key=lambda x: (x["score"], any(word.lower() in x["url"].lower() for word in query.split())), reverse=True)
        return results[:max_results]
    except Exception as e:
        return [{"url": f"Error: {str(e)}", "score": 0}]

# Search local files (fixed to avoid variable access error)
def search_local(query, directory="."):
    results = []
    try:
        loading_animation("Scanning local files")
        for root, _, files in os.walk(directory):
            for file in files:
                # Only add files that match the query
                if any(word.lower() in file.lower() for word in query.split()):
                    file_path = os.path.join(root, file)
                    results.append({"path": file_path, "score": 2})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5] if results else [{"path": "No matching local files found.", "score": 0}]
    except Exception as e:
        return [{"path": f"Error: {str(e)}", "score": 0}]

# Display results with colors
def display_results(results, title, result_type="url"):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{title}{Style.RESET_ALL}")
    if not results:
        print(f"{Fore.RED}No results found.{Style.RESET_ALL}")
        return
    for i, result in enumerate(results, 1):
        item = result[result_type]
        score = result["score"]
        color = Fore.GREEN if score > 1 else Fore.YELLOW
        print(f"{Fore.MAGENTA}{i}. {color}{item}{Style.RESET_ALL} (Score: {score})")

# Save results to file
def save_results(results, query):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Search Query: {query}\n")
        f.write("=" * 50 + "\n")
        for result in results:
            f.write(f"{result['url']}\n")
    print(f"{Fore.GREEN}Results saved to {filename}{Style.RESET_ALL}")

# Main function
def main():
    print(f"{Fore.BLUE}{Style.BRIGHT}🚀 Welcome to HyperSearch - The Ultimate CLI Search Engine! 🚀{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to quit or 'save' to save last results.{Style.RESET_ALL}")
    
    last_results = []
    last_query = ""
    
    while True:
        query = input(f"\n{Fore.GREEN}🔍 Enter search query: {Style.RESET_ALL}")
        if query.lower() == "exit":
            print(f"{Fore.BLUE}👋 Goodbye!{Style.RESET_ALL}")
            break
        if query.lower() == "save" and last_results:
            save_results(last_results, last_query)
            continue
        if not query.strip():
            print(f"{Fore.RED}❌ Please enter a valid query.{Style.RESET_ALL}")
            continue

        last_query = query
        # Display description
        print(f"\n{Fore.BLUE}{Style.BRIGHT}📜 About '{query}':{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{generate_description(query)}{Style.RESET_ALL}")
        
        # Search web
        web_results = search_web(query)
        display_results(web_results, "🌐 Web Results")
        
        # Search local files
        local_results = search_local(query)
        display_results(local_results, "💾 Local Files", result_type="path")
        
        last_results = web_results

if __name__ == "__main__":
    main()