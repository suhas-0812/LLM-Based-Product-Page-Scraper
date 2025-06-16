import asyncio
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

class Product(BaseModel):
    # Basic Product Info
    product: str = Field(..., description="Product name or title")
    brand: str = Field(..., description="Brand or manufacturer")
    product_description: str = Field(..., description="Detailed product description")
    everything_you_need_to_know: str = Field(default="", description="Comprehensive product information and specifications")
    why_we_love_it: str = Field(default="", description="Key selling points and unique features")
    price: str = Field(..., description="Current price of the product")
    website: str = Field(default="", description="Website or platform where product is sold")
    delivery_timeline: str = Field(default="", description="Expected delivery time")
    image_links: List[str] = Field(default_factory=list, description="List of product image URLs")
    
    # Demographics
    age_kids: str = Field(default="", description="Age range if product is for kids")
    gender: str = Field(default="", description="Target gender (Men/Women/Unisex/Kids)")
    price_bracket: str = Field(default="", description="Price category (Budget/Mid-range/Premium/Luxury)")
    cities: str = Field(default="", description="Cities where product is available")
    
    # Style & Occasion
    occasion: str = Field(default="", description="Suitable occasions for the product")
    style_tags: str = Field(default="", description="Style categories and tags")
    personas: str = Field(default="", description="Target customer personas")
    
    # Suitable Occasions (Boolean)
    valentines: bool = Field(default=False, description="Suitable for Valentine's Day")
    baby_shower: bool = Field(default=False, description="Suitable for Baby Shower")
    anniversaries_weddings: bool = Field(default=False, description="Suitable for Anniversaries & Weddings")
    birthdays: bool = Field(default=False, description="Suitable for Birthdays")
    house_warmings: bool = Field(default=False, description="Suitable for House Warmings")
    festivals: bool = Field(default=False, description="Suitable for Festivals")
    
    # Personality Suited (Boolean)
    fitness_sports_enthusiast: bool = Field(default=False, description="Suited for Fitness/Sports Enthusiasts")
    aesthete: bool = Field(default=False, description="Suited for Aesthetes")
    minimalist_functional: bool = Field(default=False, description="Suited for Minimalist/Functional personalities")
    maximalist: bool = Field(default=False, description="Suited for Maximalists")
    fashionable: bool = Field(default=False, description="Suited for Fashionable personalities")
    foodie: bool = Field(default=False, description="Suited for Foodies")
    wellness_seeker: bool = Field(default=False, description="Suited for Wellness Seekers")
    new_parent: bool = Field(default=False, description="Suited for New Parents")
    teenagers: bool = Field(default=False, description="Suited for Teenagers")
    working_professionals: bool = Field(default=False, description="Suited for Working Professionals")
    parents: bool = Field(default=False, description="Suited for Parents")
    bride_groom_to_be: bool = Field(default=False, description="Suited for Bride/Groom to be")


async def extract_product_data(
    url: str,
    azure_provider: str = "azure/gpt-4o",
    api_token: str = "",
    base_url: str = "",
    show_usage: bool = False
) -> Dict[str, Any]:
    """
    Extract comprehensive product data from a product page URL.
    
    Args:
        url: Product page URL to crawl
        azure_provider: Azure provider format (e.g., "azure/gpt-4o")
        api_token: Azure OpenAI API token
        base_url: Azure OpenAI base URL
        show_usage: Whether to show token usage stats
        
    Returns:
        Dict containing extracted product data or error information
    """
    try:
        # Configure LLM
        llm_config = LLMConfig(
            provider=azure_provider,
            api_token=api_token,
            base_url=base_url
        )
        
        llm_strategy = LLMExtractionStrategy(
            llm_config=llm_config,
            schema=Product.model_json_schema(),
            extraction_type="schema",
            instruction="""Extract comprehensive product information from this product page and analyze it to fill ALL fields:

            BASIC INFO: Extract product name, brand, detailed description, specifications, key selling points, price, website, delivery info.
            
            IMAGE LINKS: Extract ALL product image URLs from the page. Look for main product images, gallery images, zoom images, and variant images. Include full URLs.
            
            DEMOGRAPHICS: Determine target gender, age range (if for kids), price bracket (Budget/Mid-range/Premium/Luxury), and available cities.
            
            STYLE & OCCASIONS: Identify suitable occasions, style tags, and target personas.
            
            BOOLEAN OCCASIONS: Analyze if product is suitable for:
            - Valentine's Day, Baby Shower, Anniversaries & Weddings, Birthdays, House Warmings, Festivals
            
            BOOLEAN PERSONALITIES: Determine if product suits these personality types:
            - Fitness/Sports Enthusiast, Aesthete, Minimalist/Functional, Maximalist, Fashionable, Foodie, Wellness Seeker, New Parent, Teenagers, Working Professionals, Parents, Bride/Groom to be
            
            Be analytical and thoughtful about the boolean fields - consider the product type, style, and use case.
            Return only ONE comprehensive product object.""",
            chunk_token_threshold=3000,
            overlap_rate=0.1,
            apply_chunking=False,
            input_format="markdown",
            extra_args={"temperature": 0.0, "max_tokens": 2000}
        )

        # Build crawler config
        crawl_config = CrawlerRunConfig(
            extraction_strategy=llm_strategy,
            cache_mode=CacheMode.BYPASS
        )

        # Create browser config
        browser_cfg = BrowserConfig(headless=True)

        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=url, config=crawl_config)

            if result.success:
                data = json.loads(result.extracted_content)
                
                # Handle case where data is a list (take first item) or dict
                if isinstance(data, list):
                    if len(data) > 0:
                        product_data = data[0]
                    else:
                        return {"success": False, "error": "No products found in extracted data"}
                else:
                    product_data = data

                if show_usage:
                    llm_strategy.show_usage()

                return {
                    "success": True,
                    "data": product_data,
                    "url": url
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message,
                    "url": url
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


def extract_product_sync(
    url: str,
    azure_provider: str = "azure/gpt-4o",
    api_token: str = "",
    base_url: str = "",
    show_usage: bool = False
) -> Dict[str, Any]:
    """
    Synchronous wrapper for extract_product_data.
    
    Args:
        url: Product page URL to crawl
        azure_provider: Azure provider format (e.g., "azure/gpt-4o")
        api_token: Azure OpenAI API token
        base_url: Azure OpenAI base URL
        show_usage: Whether to show token usage stats
        
    Returns:
        Dict containing extracted product data or error information
    """
    return asyncio.run(extract_product_data(url, azure_provider, api_token, base_url, show_usage))


async def main():
    """Example usage - only runs when script is executed directly"""
    # Example configuration
    url = "https://www.myntra.com/jeans/wrogn/wrogn-men-skinny-fit-light-fade-stretchable-mid-rise-jeans/25827266/buy"
    azure_provider = "azure/gpt-4o"
    api_token = "your-api-token-here"
    base_url = "https://your-resource.openai.azure.com/"
    
    result = await extract_product_data(url, azure_provider, api_token, base_url, show_usage=True)
    
    if result["success"]:
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
