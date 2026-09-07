from pathlib import Path
import os

def find_file(command_text: str) -> str:
    """
    Search for a file on the local machine starting from the user's home directory.
    Example: 'find resume' or 'find project report'
    """
    # Expected format: find <filename>
    query = command_text.lower().replace("find ", "").strip()
    if not query:
        return "Please specify a file to find."

    # Search in common directories to avoid long scanning times on Windows
    # For a simple assistant, we limit search to User profile directory
    search_dir = Path.home()
    
    # We will do a case-insensitive search for files containing the query in their stem
    try:
        # To avoid blocking UI for too long, we limit the search or do a quick scan
        # Note: rglob can be slow, this is a basic implementation
        results = []
        count = 0
        
        # Generator for fast yield
        for path in search_dir.rglob(f"*{query}*.*"):
            if path.is_file():
                results.append(str(path))
                count += 1
                if count >= 5: # Limit to 5 results for UI brevity
                    break
                    
        if results:
            return "Found files:\n" + "\n".join(results)
        else:
            return f"No files found matching '{query}' in {search_dir}"
            
    except Exception as e:
        return f"Error during search: {str(e)}"
