import streamlit as st
import json
from llmextract import extract_product_sync
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
st.write("Extract comprehensive product information from any e-commerce page")

# URL input
st.subheader("🔗 Enter Product URL")
url = st.text_input(
    "Product Page URL:",
    placeholder="https://www.myntra.com/product/...",
    help="Paste the URL of the product page you want to extract data from"
)

# Extract button
if st.button("🔍 Extract Product Data", type="primary", use_container_width=True):
    if not url:
        st.error("Please enter a product URL")
    else:
        with st.spinner("Extracting product data..."):
            try:
                result = extract_product_sync(
                    url=url,
                    azure_provider=AZURE_PROVIDER,
                    api_token=API_TOKEN,
                    base_url=BASE_URL
                )
                
                if result["success"]:
                    data = result["data"]
                    
                    st.success("✅ Product data extracted successfully!")
                    
                    # Display key information one by one
                    st.write(f"**Product:** {data.get('product', 'N/A')}")
                    st.write(f"**Brand:** {data.get('brand', 'N/A')}")
                    st.write(f"**Product Description:** {data.get('product_description', 'N/A')}")
                    st.write(f"**Everything You Need To Know:** {data.get('everything_you_need_to_know', 'N/A')}")
                    st.write(f"**Why We Love It:** {data.get('why_we_love_it', 'N/A')}")
                    st.write(f"**Price:** {data.get('price', 'N/A')}")
                    st.write(f"**Website:** {data.get('website', 'N/A')}")
                    st.write(f"**Delivery Timeline:** {data.get('delivery_timeline', 'N/A')}")
                    st.write(f"**Gender:** {data.get('gender', 'N/A')}")
                    st.write(f"**Price Bracket:** {data.get('price_bracket', 'N/A')}")
                    
                    st.write(f"**Cities:** {data.get('cities', 'N/A')}")
                    
                    st.write(f"**Style Tags:** {data.get('style_tags', 'N/A')}")
                    
                    st.write(f"Personas: {data.get('personas', 'N/A')}")


                    # Show occasions and personalities
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
                    
                    
                    # Show images
                    if data.get('image_links'):
                        st.write("**🖼️ Product Images:**")
                        cols = st.columns(min(3, len(data['image_links'])))
                        for idx, img_url in enumerate(data['image_links'][:3]):
                            with cols[idx]:
                                try:
                                    st.image(img_url, width=200)
                                except:
                                    st.write(f"Image {idx+1}")
                    
                    # Download JSON
                    st.write("**💾 Download Data:**")
                    json_str = json.dumps(data, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name="product_data.json",
                        mime="application/json"
                    )
                        
                else:
                    st.error(f"❌ Extraction failed: {result['error']}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Powered by Azure OpenAI & Crawl4AI*", unsafe_allow_html=True)
