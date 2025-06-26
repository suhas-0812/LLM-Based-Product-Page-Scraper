import streamlit as st
import json
from batch_extract import extract_details
import subprocess
import sys
import os

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Product Data Extractor",
    page_icon="🛍️",
    layout="centered"
)

# Install Playwright browsers on first run (for Streamlit Cloud)
@st.cache_resource
def install_playwright():
    try:
        # Only install chromium browser (dependencies handled by packages.txt)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Playwright browser installation failed: {e.stderr}")
        return False
    except Exception as e:
        st.error(f"Unexpected error installing Playwright: {e}")
        return False

# Install browsers
install_playwright()

# Hardcoded Azure OpenAI credentials
AZURE_PROVIDER = st.secrets["AZURE_PROVIDER"]
API_TOKEN = st.secrets["API_TOKEN"]
BASE_URL = st.secrets["BASE_URL"]

# Main header
st.title("🛍️ Product Data Extractor")
st.write("Extract comprehensive product information from e-commerce pages")

# URL input options
st.subheader("🔗 Enter Product URL(s)")

# Single input for both single and multiple URLs
urls_input = st.text_area(
    "Product URLs (one per line):",
    placeholder="https://www.myntra.com/product1/...\nhttps://www.myntra.com/product2/...\n\nFor single product, just enter one URL",
    help="Enter one or more URLs, one per line",
    height=450
)

if st.button("🔍 Extract Product Data", type="primary", use_container_width=True):
    if not urls_input.strip():
        st.error("Please enter at least one product URL")
    else:
        # Split URLs by newlines and clean them
        urls_to_process = [url.strip() for url in urls_input.strip().split('\n') if url.strip()]

# Process URLs if any button was clicked
if 'urls_to_process' in locals():
    with st.spinner(f"Extracting data from {len(urls_to_process)} product(s)..."):
        try:
            results = extract_details(
                urls=urls_to_process,
                azure_provider=AZURE_PROVIDER,
                api_token=API_TOKEN,
                base_url=BASE_URL
            )
            
            if results["successful_extractions"] > 0:
                st.success(f"✅ Successfully extracted {results['successful_extractions']} out of {results['total_urls']} products!")
                
                # Show summary
                st.write(f"**📊 Summary:**")
                st.write(f"- Total URLs: {results['total_urls']}")
                st.write(f"- Successful: {results['successful_extractions']}")
                st.write(f"- Failed: {results['failed_extractions']}")
                st.write(f"- Success Rate: {results['summary']['success_rate']:.1f}%")
                st.write(f"- Processing Time: {results['summary']['total_processing_time']}s")
                
                # Display each successful product
                for idx, result in enumerate(results["results"]):
                    if result["success"]:
                        data = result["data"]
                        
                        with st.expander(f"📦 Product {idx+1}: {data.get('product', 'Unknown Product')}", expanded=len(urls_to_process)==1):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Product:** {data.get('product', 'N/A')}")
                                st.write(f"**Brand:** {data.get('brand', 'N/A')}")
                                st.write(f"**Price:** {data.get('price', 'N/A')}")
                                st.write(f"**Gender:** {data.get('gender', 'N/A')}")
                                st.write(f"**Price Bracket:** {data.get('price_bracket', 'N/A')}")
                                
                                if data.get('product_description'):
                                    st.write(f"**Description:** {data.get('product_description')}")
                                
                                if data.get('everything_you_need_to_know'):
                                    st.write(f"**Details:** {data.get('everything_you_need_to_know')}")
                                
                                if data.get('why_we_love_it'):
                                    st.write(f"**Why We Love It:** {data.get('why_we_love_it')}")
                                
                                # Show occasions and personalities as boolean values
                                st.write("**🎉 Suitable Occasions:**")
                                st.write(f"Valentine's Day: {data.get('valentines', False)}")
                                st.write(f"Baby Shower: {data.get('baby_shower', False)}")
                                st.write(f"Anniversaries & Weddings: {data.get('anniversaries_weddings', False)}")
                                st.write(f"Birthdays: {data.get('birthdays', False)}")
                                st.write(f"House Warmings: {data.get('house_warmings', False)}")
                                st.write(f"Festivals: {data.get('festivals', False)}")
                                
                                st.write("**👤 Suitable Personalities:**")
                                st.write(f"Fitness/Sports Enthusiast: {data.get('fitness_sports_enthusiast', False)}")
                                st.write(f"Aesthete: {data.get('aesthete', False)}")
                                st.write(f"Minimalist/Functional: {data.get('minimalist_functional', False)}")
                                st.write(f"Maximalist: {data.get('maximalist', False)}")
                                st.write(f"Fashionable: {data.get('fashionable', False)}")
                                st.write(f"Foodie: {data.get('foodie', False)}")
                                st.write(f"Wellness Seeker: {data.get('wellness_seeker', False)}")
                                st.write(f"New Parent: {data.get('new_parent', False)}")
                                st.write(f"Teenagers: {data.get('teenagers', False)}")
                                st.write(f"Working Professionals: {data.get('working_professionals', False)}")
                                st.write(f"Parents: {data.get('parents', False)}")
                                st.write(f"Bride/Groom to be: {data.get('bride_groom_to_be', False)}")
                            
                            with col2:
                                # Show images
                                if data.get('image_links'):
                                    st.write("**🖼️ Images:**")
                                    for img_idx, img_url in enumerate(data['image_links'][:2]):
                                        try:
                                            st.image(img_url, width=150)
                                        except:
                                            st.write(f"Image {img_idx+1}")
                    else:
                        with st.expander(f"❌ Failed: {result['url']}", expanded=False):
                            st.error(f"Error: {result['error']}")
                
                # Download options
                st.write("**💾 Download Data:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download all results as JSON
                    json_str = json.dumps(results, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download All Results (JSON)",
                        data=json_str,
                        file_name="batch_extraction_results.json",
                        mime="application/json"
                    )
                
                with col2:
                    # Download only successful products
                    successful_products = [result["data"] for result in results["results"] if result["success"]]
                    if successful_products:
                        products_json = json.dumps(successful_products, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="📥 Download Products Only (JSON)",
                            data=products_json,
                            file_name="extracted_products.json",
                            mime="application/json"
                        )
            else:
                st.error("❌ No products were successfully extracted!")
                
                # Show failed attempts
                for result in results["results"]:
                    if not result["success"]:
                        st.error(f"Failed to extract from {result['url']}: {result['error']}")
                        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Powered by Azure OpenAI & Crawl4AI*", unsafe_allow_html=True)
