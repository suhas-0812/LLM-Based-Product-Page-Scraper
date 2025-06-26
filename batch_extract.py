import json
import time
from typing import List, Dict, Any
from llmextract import extract_product_sync


def extract_details(
    urls: List[str],
    azure_provider: str = "azure/gpt-4o",
    api_token: str = "",
    base_url: str = "",
    show_usage: bool = False,
    delay_between_requests: float = 1.0
) -> Dict[str, Any]:
    """
    Extract product data from a list of URLs.
    
    Args:
        urls: List of URLs to process (can contain just one URL)
        azure_provider: Azure provider format (e.g., "azure/gpt-4o")
        api_token: Azure OpenAI API token
        base_url: Azure OpenAI base URL
        show_usage: Whether to show token usage stats
        delay_between_requests: Delay in seconds between requests to avoid rate limiting
        
    Returns:
        Dict containing results for all URLs with success/failure status
    """
    results = {
        "total_urls": len(urls),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "results": [],
        "summary": {
            "success_rate": 0.0,
            "total_processing_time": 0.0
        }
    }
    
    start_time = time.time()
    
    print(f"Starting extraction for {len(urls)} URL(s)...")
    print("-" * 50)
    
    for idx, url in enumerate(urls, 1):
        print(f"Processing {idx}/{len(urls)}: {url}")
        
        try:
            # Extract product data
            result = extract_product_sync(
                url=url,
                azure_provider=azure_provider,
                api_token=api_token,
                base_url=base_url,
                show_usage=show_usage
            )
            
            if result["success"]:
                results["successful_extractions"] += 1
                print(f"✅ Success: {result['data'].get('product', 'Unknown Product')}")
            else:
                results["failed_extractions"] += 1
                print(f"❌ Failed: {result['error']}")
            
            results["results"].append(result)
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "url": url
            }
            results["results"].append(error_result)
            results["failed_extractions"] += 1
            print(f"❌ Exception: {str(e)}")
        
        # Add delay between requests (except for the last one)
        if idx < len(urls) and delay_between_requests > 0:
            print(f"⏳ Waiting {delay_between_requests}s before next request...")
            time.sleep(delay_between_requests)
        
        print("-" * 30)
    
    # Calculate summary statistics
    end_time = time.time()
    total_time = end_time - start_time
    
    results["summary"]["success_rate"] = (
        results["successful_extractions"] / results["total_urls"] * 100
        if results["total_urls"] > 0 else 0
    )
    results["summary"]["total_processing_time"] = round(total_time, 2)
    
    # Print final summary
    print("=" * 50)
    print("EXTRACTION SUMMARY")
    print("=" * 50)
    print(f"Total URLs processed: {results['total_urls']}")
    print(f"Successful extractions: {results['successful_extractions']}")
    print(f"Failed extractions: {results['failed_extractions']}")
    print(f"Success rate: {results['summary']['success_rate']:.1f}%")
    print(f"Total processing time: {results['summary']['total_processing_time']}s")
    print("=" * 50)
    
    return results
