# Updated Streamlit app to reflect new content structure and clean errors
import streamlit as st
import pandas as pd
import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Product Listing Automation", layout="wide")
st.title("📦 Product Listing Automation Tool")

# Brand Tonality Dictionary - Embedded in code
BRAND_TONALITIES = {
    "MakeMeeBold": """Confident, not cocky: Customers are sure about our products because they work, not because of overselling.
Modern & aspirational: Sleek, smart, and relevant to today's beauty consumer — informed but not clinical.
Empowering: Encourages self-expression, not perfection. The name itself speaks to inner and outer confidence.
Clean & refined: Language is crisp and minimal, avoiding clutter or fluff.
Contemporary feminine: It's a women-focused brand, however it is gender-neutral enough to feel inclusive, but still elegant and aspirational.
Results-oriented: clear about efficacy, with evidence, or focus on USPs""",

    "Urban Yog": """Playful, not pretentious: Skincare is fun and expressive; never boring or overly serious
Relatable, not preachy: Speaks like a best-friend who gets it - conversational, and easy to connect with
Bold & unapologetic: owns topics that others avoid such as body hair, acne, etc with confidence, humour and zero shame.
Yummy & sensory: language is colourful & indulgent - textures, adjectives, scents, and visuals that make skincare feel like a treat 
Youthful & vibrant: fresh, pop-culture-driven, socially fluent, resonates with Gen Z and young millenials
Witty & confident: Uses playful quips & puns sometimes, that add spunk & personality without losing meaning or clarity.
Miniso, cutesy vibes: The brand gives off a miniso-esqe, cutesy vibe""",

    "Urban Gabru": """Confident, not arrogant: Speaks to men who take charge of their lives — ambitious, self-assured, and results-driven.
Sharp & modern: Sleek, innovative, and tuned to the needs of the contemporary Indian man.
Empowering & aspirational: Encourages self-improvement and personal growth — grooming is positioned as the start of greatness, not the end goal.
Practical & purposeful: Clear, direct messaging that communicates product efficacy and everyday relevance — built to support hustle, fitness, and professional ambitions.
Masculine, yet approachable: Maintains a strong, confident tone without being intimidating — relatable to men from all walks of life.
Dynamic & motivating: Language inspires action and upward momentum.
Premium & credible: the brand positions itself as a premium and credible brand with authenticity and trustworthiness.
To-the-point: Clearly defined USPs and no extra fluff just the way most men communicate.""",

    "Seoulskin": """Calm, not flashy: Focuses on simplicity and serenity, avoiding hype and quick-fix messaging.
Consistent & reliable: Emphasizes long-term results and daily rituals, positioning the brand as a trustworthy skincare companion.
Purposeful & minimal: Every product and message is intentional — no clutter, no unnecessary complexity, only what truly benefits the skin.
Gentle & nurturing: Soft, caring language conveys comfort and reassurance, appealing to those seeking mindful self-care.
Authentic & credible: Rooted in the principles of Korean skincare, the brand communicates expertise without being clinical or intimidating.
Sophisticated & understated: Elegant, refined, and approachable — appeals to consumers who value quality and efficacy over trends.
Mindful & reassuring: Speaks to the desire for slow, consistent care — emphasizing trust, comfort, and skin confidence."""
}

st.subheader("📥 Upload KLD Sheet")
uploaded_file = st.file_uploader("Upload your KLD Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file, header=None)
        
        # Extract columns 3 and 4 (index 3, 4) which are Particulars and Details in new format
        df_clean = df.iloc[1:, [3, 4]]
        df_clean.columns = ['Particulars', 'Details']
        
        # Remove rows where both Particulars and Details are empty
        df_clean = df_clean.dropna(subset=['Particulars', 'Details'], how='all')
        
        # Remove rows where Particulars is empty but keep rows where only Details might be empty
        df_clean = df_clean[df_clean['Particulars'].notna()]
        
        # Strip whitespace from column values
        df_clean['Particulars'] = df_clean['Particulars'].astype(str).str.strip()
        df_clean['Details'] = df_clean['Details'].astype(str).str.strip()
        
        # Remove rows where Particulars is empty string after stripping
        df_clean = df_clean[df_clean['Particulars'] != '']
        
        # Create a dictionary for easier field matching
        product_data = {}
        for _, row in df_clean.iterrows():
            key = row['Particulars']
            value = row['Details'] if pd.notna(row['Details']) and row['Details'] != 'nan' else ''
            product_data[key] = value
        
        # Helper function to get field with flexible matching (case-insensitive and partial match)
        def get_field(*possible_keys, default="Not specified"):
            """Try multiple possible keys and return first match"""
            for key in possible_keys:
                # Exact match (case-insensitive)
                for data_key, value in product_data.items():
                    if key.lower() == data_key.lower() and value:
                        return value
                # Partial match (case-insensitive)
                for data_key, value in product_data.items():
                    if key.lower() in data_key.lower() and value:
                        return value
            return default
        
        # Create normalized product_info dictionary with flexible field mapping
        product_info = pd.Series({
            'Product Name': get_field('Product Name'),
            'Brand Name': get_field('Brand Name'),
            'USPs Front': get_field('USPs Front', 'USP Front'),
            'USP Back': get_field('USP Back'),
            'USP Side': get_field('USP Side', default=''),
            'Ingredients': get_field('INGREDIENTS', 'Ingredients'),
            'Claims': get_field('Claims'),
            'How to use it?': get_field('HOW TO USE IT?', 'HOW TO USE', 'How to use it?', 'How to use'),
            'MRP (Incl. of all taxes)': get_field('MRP (Incl. of all taxes)', 'MRP'),
            'Category': get_field('Category', 'Product Type', 'Application Area', default='Beauty'),
            'Target Audience': get_field('Target Audience', 'Ideal For', default=''),
            'KNOW YOUR PRODUCT': get_field('KNOW YOUR PRODUCT', 'Know Your Product', default=''),
            'Net Qty.': get_field('Net Qty.', 'Net Qty', default=''),
            'Country Of Origin': get_field('Country Of Origin', 'Country of Origin', default=''),
            'Brand Owned & Marketed By': get_field('BRAND OWNED & MARKETED BY', 'Brand Owned & Marketed By', 'Marketed By', default=''),
            'Email': get_field('EMAIL', 'Email', 'E-mail', default=''),
            'Contact Us': get_field('CONTACT US', 'Contact Us', 'Contact', default=''),
            'Box Includes': get_field('BOX INCLUDES', 'Box Includes', 'Box includes', 'What\'s in the box', default=''),
            'Warranty': get_field('WARRANTY', 'Warranty', 'Warrenty', default=''),
        })
        
        st.success("✅ KLD sheet loaded and parsed successfully!")
        
    except Exception as e:
        st.error(f"❌ Error parsing file: {str(e)}")
        st.info("💡 Please ensure your Excel file has 'Particulars' in column D and 'Details' in column E")
        st.stop()

    # Category Selector - Mandatory field
    st.subheader("📂 Select Product Category")
    
    # Try to get category from the file first
    detected_category = product_info.get('Category', '')
    
    # Category selection with radio buttons
    selected_category = st.radio(
        "Choose the product category (Required):",
        options=["Beauty", "Electronics"],
        index=0 if not detected_category or 'Beauty' in str(detected_category) else 1,
        horizontal=True,
        help="This determines which content templates and fields to use"
    )
    
    # Update the product_info with selected category
    product_info['Category'] = selected_category
    
    # Show warning if no category is selected
    if not selected_category:
        st.warning("⚠️ Please select a product category to continue")
        st.stop()
    
    st.success(f"✅ Category set to: **{selected_category}**")
    
    # Brand Selector - Mandatory field
    st.subheader("🏷️ Select Brand")
    
    # Try to detect brand from the file
    detected_brand = product_info.get('Brand Name', '')
    
    # Get available brands from tonality file
    available_brands = list(BRAND_TONALITIES.keys()) if BRAND_TONALITIES else []
    
    if available_brands:
        # Try to match detected brand with available brands
        default_index = 0
        for idx, brand in enumerate(available_brands):
            if detected_brand and brand.lower() in detected_brand.lower():
                default_index = idx
                break
        
        selected_brand = st.selectbox(
            "Choose the brand (Required):",
            options=available_brands,
            index=default_index,
            help="This determines the tone and style of generated content"
        )
        
        # Show the tonality for selected brand
        if selected_brand and selected_brand in BRAND_TONALITIES:
            with st.expander("📖 View Brand Tonality Guidelines", expanded=False):
                st.markdown(f"**{selected_brand} Tonality:**")
                st.text(BRAND_TONALITIES[selected_brand])
        
        st.success(f"✅ Brand set to: **{selected_brand}**")
    else:
        st.warning("⚠️ No brand tonality file found. Content will be generated with generic tone.")
        selected_brand = None
    
    st.markdown("---")

    st.subheader("🔹 Product Information")
    
    # Display extracted product information in a clean table
    display_df = pd.DataFrame({
        'Field': product_info.index,
        'Value': product_info.values
    })
    # Filter out empty/not specified values for cleaner display
    display_df = display_df[display_df['Value'].astype(str).str.strip() != '']
    display_df = display_df[display_df['Value'] != 'Not specified']
    
    st.table(display_df)

    def generate_section(section_name, instruction):
        try:
            # Prepare the system message with brand tonality if available
            system_message = "You are a professional ecommerce copywriter."
            
            if selected_brand and selected_brand in BRAND_TONALITIES:
                brand_tonality = BRAND_TONALITIES[selected_brand]
                system_message += f"\n\nIMPORTANT - BRAND TONE & VOICE:\nYou are writing for the brand '{selected_brand}'. Follow this brand tonality strictly:\n\n{brand_tonality}\n\nEnsure all content reflects this brand's personality, tone, and style."
            
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": instruction}
                ],
                temperature=0.7
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error generating {section_name}: {e}")
            return ""

    def text_box(label, key, height):
        if key in st.session_state:
            st.text_area(label, st.session_state[key], height=height)

    # Amazon Content Generation
    st.session_state.setdefault('title', '')
    if st.button("Generate Product Title"):
        title_prompt = f"""
            Write an Amazon product title (max 200 characters) for a high-converting listing.
            Use this format: Brand + Product Type + Keywords + Claims.
            Do not include size, weight, or volume in the title.

            Product: {product_info.get('Product Name', 'N/A')}
            Brand: {product_info.get('Brand Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
        """
        st.session_state['title'] = generate_section("title", title_prompt)
    text_box("Amazon Product Title", 'title', 100)
    st.subheader("🛒 Amazon Content")
    st.session_state.setdefault('bullets', '')
    if st.button("Generate Bullet Points"):
        bullet_prompt = f"""
            Write 7 optimized Amazon bullet points. Each bullet should follow this format:
            BENEFIT IN CAPS: Followed by a clear, compelling benefit (250–300 characters).

            Avoid mentioning price, value for money, discounts, or any numerical cost-related details. Focus only on features, results, usage, or ingredient benefits.

            Product: {product_info.get('Product Name', 'N/A')}
            Brand: {product_info.get('Brand Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}, {product_info.get('USP Back', 'N/A')}, {product_info.get('USP Side', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
            How to Use: {product_info.get('How to use it?', 'N/A')}
        """
        st.session_state['bullets'] = generate_section("bullet points", bullet_prompt)
    text_box("Generated Bullet Points", 'bullets', 200)

    st.session_state.setdefault('description', '')
    if st.button("Generate Description"):
        desc_prompt = f"""
            Write an Amazon HTML product description (max 400 words).
            Use 2 paragraphs, <p> and <br> tags for light formatting.

            Product: {product_info.get('Product Name', 'N/A')}
            Brand: {product_info.get('Brand Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
            How to Use: {product_info.get('How to use it?', 'N/A')}
        """
        st.session_state['description'] = generate_section("description", desc_prompt)
    text_box("HTML Description", 'description', 150)

    st.session_state.setdefault('shopify', '')
    if st.button("Generate Shopify Description"):
        shopify_prompt = f"""
            Write a Shopify product description using a friendly, informative tone.
            Include small paragraphs, bullet points, and headings. Length: 1500–2000 characters.
            
            IMPORTANT: Do NOT use markdown formatting. Use plain text only.
            - Do not use ** for bold
            - Do not use # for headings
            - Do not use markdown syntax
            - Use simple text formatting only

            Product: {product_info.get('Product Name', 'N/A')}
            Brand: {product_info.get('Brand Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
            How to Use: {product_info.get('How to use it?', 'N/A')}
            MRP: {product_info.get('MRP (Incl. of all taxes)', 'N/A')}
        """
        st.session_state['shopify'] = generate_section("Shopify description", shopify_prompt)
    text_box("Shopify Description", 'shopify', 200)

    st.session_state.setdefault('hero', '')
    if st.button("Generate Hero Prompts"):
        # Use the selected category from the UI
        category = product_info.get('Category', 'Beauty')
        
        if 'Beauty' in str(category):
            hero_prompt = f"""
                Generate a series of 7 hero image prompts for a beauty product, each designed to be a standalone visual in the following sequence.  
                Each image must be exactly 1500 x 1500 pixels. For each image, include specific visual/creative directions as outlined.
                
                IMPORTANT: Provide the output in plain text format only. Do NOT use markdown syntax like **, ##, or bullet points with *. Use simple numbered lists and plain text.

                1. Hero Image: What does it do / Differentiation / Before-After  
                - Show the product with a clear before-and-after comparison, highlighting the main benefit or transformation.  
                - Use high-resolution, professional imagery with a clean, softly colored, on-brand background.  
                - Overlay concise benefit-driven text or icons.  
                - Ensure the product is the main focal point.

                2. USP  
                - Focus on the unique selling proposition that sets this product apart.  
                - Use bold text or a badge to highlight the USP.  
                - Incorporate lifestyle or in-use imagery for emotional connection.

                3. Ingredients & Their Use  
                - Visually showcase key ingredients with small icons or illustrations.  
                - Briefly mention each ingredient's benefit.  
                - Use a soft, inviting color palette.

                4. Science Behind USP  
                - Include science-related visuals (molecules, lab glassware, dermatologist icons) to reinforce efficacy.  
                - Overlay a short, clear explanation of the science behind the USP.

                5. Comparison / Do's and Don'ts  
                - Create a side-by-side comparison with alternatives or a clear Do's and Don'ts visual.  
                - Use simple icons and minimal text for clarity.

                6. How to Use  
                - Present step-by-step usage instructions in 3–4 crisp, numbered icons or steps.  
                - Keep instructions short, clear, and visually engaging.

                7. Safe for All Hair/Skin Types  
                - Use icons or imagery showing diversity in models (different skin/hair types).  
                - Add a clear statement or badge indicating suitability for all.

                General Visual/Creative Directions for All Images:  
                - Each image must be exactly 1500 x 1500 pixels.  
                - Use high-resolution, professional images.  
                - Clean, uncluttered, on-brand backgrounds.  
                - Overlay concise, benefit-driven text or icons.  
                - Maintain a consistent style, color palette, and font across all images.  
                - Optimize for both desktop and mobile screens.  
                - Avoid clutter; keep visuals focused and easy to scan.  
                - Do not include any call-to-action (CTA) buttons.  
                - Include relevant props that complement the product and provide context, without distracting from the main subject.  
                - Feature models where appropriate, ensuring diversity in skin and hair types to show inclusivity and real-world results.  
                - Use professional lighting setups (such as three-point lighting, softboxes, umbrellas, or ring lights) for soft, even illumination and to minimize harsh shadows.  
                - Capture the product from optimal angles, including close-ups for detail and lifestyle shots for context.  
                - Ensure the product is always the main focal point, with props and models used to enhance the story.

                Product details:  
                Product: {product_info.get('Product Name', 'N/A')}  
                USP: {product_info.get('USPs Front', 'N/A')}  
                Ingredients: {product_info.get('Ingredients', 'N/A')}  
                How to use: {product_info.get('How to use it?', 'N/A')}  
                Target: {product_info.get('Target Audience', '')}  
                Other details: {product_info.get('KNOW YOUR PRODUCT', '')}
                """
        elif 'Electronics' in str(category):
            hero_prompt = f"""
            Generate a series of 7 hero image prompts for an electronics product, each designed to be a standalone visual in the following sequence.  
            Each image must be exactly 1500 x 1500 pixels. For each image, include specific visual/creative directions as outlined.
            
            IMPORTANT: Provide the output in plain text format only. Do NOT use markdown syntax like **, ##, or bullet points with *. Use simple numbered lists and plain text.

            1. Hero Image: What does it do / Differentiation / Before-After  
            - Show the product in action or with a before-and-after or comparison visual.  
            - Use high-resolution, professional imagery with a clean, on-brand background.  
            - Overlay concise benefit-driven text or icons.

            2. Main USP  
            - Highlight the primary unique selling point with bold text or a badge.  
            - Use dynamic angles and close-ups to draw attention.

            3. Other USPs  
            - Present additional USPs or features with icons or short text.  
            - Arrange features for easy scanning.

            4. Comparison  
            - Create a side-by-side comparison with other products or brands.  
            - Use simple graphics and minimal text.

            5. How to Use  
            - Show 2–4 easy-to-follow steps or icons for product usage.  
            - Keep instructions short and visually engaging.

            6. All Hair Type (if relevant)  
            - Use a badge or icon to indicate compatibility with all hair types (for grooming devices).  
            - Show diverse models if applicable.

            7. What's in the Box / Customer Care  
            - Display all included accessories in a neat flat-lay or organized arrangement.  
            - Add customer care contact or warranty info in a clear, non-intrusive way.

            General Visual/Creative Directions for All Images:  
            - Each image must be exactly 1500 x 1500 pixels.  
            - Use high-resolution, professional images.  
            - Clean, uncluttered, on-brand backgrounds.  
            - Overlay concise, benefit-driven text or icons.  
            - Consistent style, color palette, and font across all images.  
            - Optimize for both desktop and mobile screens.  
            - Avoid clutter; keep visuals focused and easy to scan.  
            - Do not include any call-to-action (CTA) buttons.  
            - Include relevant props that complement the product and provide context, without distracting from the main subject.  
            - Feature models where appropriate (e.g., for scale or lifestyle context).  
            - Use professional lighting setups (such as three-point lighting, softboxes, umbrellas, or ring lights) for soft, even illumination and to minimize harsh shadows.  
            - Capture the product from optimal angles, including close-ups for detail and lifestyle shots for context.  
            - Ensure the product is always the main focal point, with props and models used to enhance the story.

            Product details:  
            Product: {product_info.get('Product Name', 'N/A')}  
            Main USP: {product_info.get('USPs Front', 'N/A')}  
            Other USPs: {product_info.get('USP Back', '')}  
            How to use: {product_info.get('How to use it?', 'N/A')}   
            Customer care: {product_info.get('Customer Care', '')}  
            Other details: {product_info.get('KNOW YOUR PRODUCT', '')}
            """
        else:
            hero_prompt = "Category not supported. Please specify 'Beauty' or 'Electronics' in the Category field."

        st.session_state['hero'] = generate_section("hero image prompts", hero_prompt)
    text_box("Hero Image Prompts", 'hero', 180)

    st.session_state.setdefault('a_plus', '')
    if st.button("Generate A+ Prompts"):
        a_plus_prompt = f"""
            Generate 7 Amazon A+ content image prompts in this format:

            Image 1:
            • Visual: 1464x600 (desktop) / 600x450 (mobile). Clean layout, brand, benefits.
            • Text: Marketing headline
            • Supporting Text: Short supporting copy

            Product: {product_info.get('Product Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}
            How to Use: {product_info.get('How to use it?', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
        """
        st.session_state['a_plus'] = generate_section("A+ image prompts", a_plus_prompt)
    text_box("A+ Image Prompts", 'a_plus', 180)

    # Website Content Generation
    if st.button("🌐 Generate Full Website Content"):
        # Use the selected category from the UI
        category = product_info.get('Category', 'Beauty')
        is_electronics = 'Electronics' in str(category)
        
        # Check if brand is Seoulskin for language preference
        brand_name = product_info.get('Brand Name', '').strip()
        is_seoulskin = 'seoulskin' in brand_name.lower()
        
        if is_seoulskin:
            review_language_instruction = """15 Customer Reviews - SEOULSKIN (PREMIUM ENGLISH FOCUS):
               - MAJORITY (10-12 reviews) should be in premium English with sophisticated tone
               - MINORITY (3-5 reviews) can include light Hinglish for authenticity
               - English reviews should emphasize K-beauty, innovation, luxury, premium skincare
               - Keep Hinglish reviews minimal and subtle (e.g., "bohot acha", "mujhe pasand aaya")
               - Use common Indian names (first + last name)
               - Format: Name – Review (no markdown, just plain text)"""
        else:
            review_language_instruction = """15 Customer Reviews in HINGLISH format:
               - Use natural Hinglish (Hindi-English mix) like: "bohot acha h", "mujhe pasand aaya", "ekdum fresh lagta h"
               - First 2 reviews: Long story-style testimonials (premium English with Hindi words)
               - Remaining 13 reviews: Short casual Hinglish reviews
               - Mix casual Hinglish with some premium English reviews
               - Use common Indian names (first + last name)
               - Format: Name – Review (no markdown, just plain text)"""
        
        if is_electronics:
            # Electronics-specific full content with Box Includes and Warranty
            full_web_prompt = f"""
            Generate the following website content in a structured format:

            1. 7 Bullet Points – focus on customer benefits, pain points, or product uniqueness.
            2. Description – 2 paragraphs, warm and benefit-driven tone, max 400 words. 
               IMPORTANT: After the description, add "What's in the Box" section with items listed as bullet points (one per line with dash), 
               followed by "Warranty Information" section.
            3. USP Points – concise value-driven phrases (2–4 words each).
            4. What do you get – brief explanation of what comes in the package.
            5. How to use – easy-to-follow, friendly, step-by-step instructions.
            6. 6 FAQs – with short, helpful answers.
            7. {review_language_instruction}
            8. Brand & Contact Information – Include brand ownership, country of origin, contact details.
            
            IMPORTANT: Provide ALL content in plain text format only. Do NOT use markdown formatting such as:
            - No ** for bold text
            - No ## for headings
            - No *** or ___ for dividers
            - No markdown bullet points with *
            - Use simple text formatting only with clear section labels

            Product Name: {product_info.get('Product Name', 'N/A')}
            Brand: {product_info.get('Brand Name', 'N/A')}
            USPs / Features: {product_info.get('USPs Front', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
            How to Use: {product_info.get('How to use it?', 'N/A')}
            MRP: {product_info.get('MRP (Incl. of all taxes)', 'N/A')}
            Brand Owned & Marketed By: {product_info.get('Brand Owned & Marketed By', 'N/A')}
            Country of Origin: {product_info.get('Country Of Origin', 'N/A')}
            Email: {product_info.get('Email', 'N/A')}
            Contact: {product_info.get('Contact Us', 'N/A')}
            Box Includes: {product_info.get('Box Includes', 'N/A')}
            Warranty: {product_info.get('Warranty', 'N/A')}
        """
        else:
            # Beauty products - original format without Box Includes and Warranty
            full_web_prompt = f"""
            Generate the following website content in a structured format:

            1. 7 Bullet Points – focus on customer benefits, pain points, or product uniqueness.
            2. Description – 2 paragraphs, warm and benefit-driven tone, max 400 words.
            3. USP Points – concise value-driven phrases (2–4 words each).
            4. What do you get – brief explanation of what comes in the package.
            5. How to use – easy-to-follow, friendly, step-by-step instructions.
            6. 6 FAQs – with short, helpful answers.
            7. {review_language_instruction}
            8. Brand & Contact Information – Include brand ownership, country of origin, contact details.
            
            IMPORTANT: Provide ALL content in plain text format only. Do NOT use markdown formatting such as:
            - No ** for bold text
            - No ## for headings
            - No *** or ___ for dividers
            - No markdown bullet points with *
            - Use simple text formatting only with clear section labels

            Product Name: {product_info.get('Product Name', 'N/A')}
            Brand: {product_info.get('Brand Name', 'N/A')}
            USPs / Features: {product_info.get('USPs Front', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
            How to Use: {product_info.get('How to use it?', 'N/A')}
            MRP: {product_info.get('MRP (Incl. of all taxes)', 'N/A')}
            Brand Owned & Marketed By: {product_info.get('Brand Owned & Marketed By', 'N/A')}
            Country of Origin: {product_info.get('Country Of Origin', 'N/A')}
            Email: {product_info.get('Email', 'N/A')}
            Contact: {product_info.get('Contact Us', 'N/A')}
        """
        
        web_full = generate_section("Website Content", full_web_prompt)
        st.session_state['web_full'] = web_full
    text_box("Full Website Content", 'web_full', 500)
    st.subheader("🌐 Website Content")

    st.session_state.setdefault('web_bullets', '')
    if st.button("Generate Website Bullet Points"):
        web_bullet_prompt = f"""
            Write 7 bullet points for website use. Each point should focus on product benefits, customer problems, or emotional triggers.

            Product: {product_info.get('Product Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}
        """
        st.session_state['web_bullets'] = generate_section("website bullets", web_bullet_prompt)
    text_box("Website Bullet Points", 'web_bullets', 200)

    st.session_state.setdefault('web_description', '')
    if st.button("Generate Website Description"):
        # Use the selected category from the UI
        category = product_info.get('Category', 'Beauty')
        is_electronics = 'Electronics' in str(category)
        
        if is_electronics:
            # Electronics-specific description with Box Includes and Warranty
            web_desc_prompt = f"""
            Write a product description for the website (max 400 words). Use a warm, benefit-oriented tone and structure it with two paragraphs.
            Include brand credibility information naturally in the content.
            
            After the main description, add two additional sections:
            1. "What's in the Box" - List all items included as bullet points (one item per line with a dash)
            2. "Warranty Information" - Include warranty details
            
            Format the box contents as simple bullet points (use - for each item, one per line).

            Product: {product_info.get('Product Name', 'N/A')}
            Brand: {product_info.get('Brand Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            Brand Owned & Marketed By: {product_info.get('Brand Owned & Marketed By', 'N/A')}
            Country of Origin: {product_info.get('Country Of Origin', 'N/A')}
            Box Includes: {product_info.get('Box Includes', 'N/A')}
            Warranty: {product_info.get('Warranty', 'N/A')}
        """
        else:
            # Beauty products - original format
            web_desc_prompt = f"""
            Write a product description for the website (max 400 words). Use a warm, benefit-oriented tone and structure it with two paragraphs.
            Include brand credibility information naturally in the content.

            Product: {product_info.get('Product Name', 'N/A')}
            Brand: {product_info.get('Brand Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}
            Claims: {product_info.get('Claims', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            Brand Owned & Marketed By: {product_info.get('Brand Owned & Marketed By', 'N/A')}
            Country of Origin: {product_info.get('Country Of Origin', 'N/A')}
        """
        st.session_state['web_description'] = generate_section("website description", web_desc_prompt)
    text_box("Website Description", 'web_description', 200)

    st.session_state.setdefault('usp', '')
    if st.button("Generate USP"):
        usp_prompt = f"""
            Generate exactly 6 concise USPs for a product listing.
            Guidelines:
            - Each USP must be a short, impactful phrase of 2–4 words.
            - Do not include full sentences.
            - Do not include explanations.
            - Format strictly as a bullet list like:
            - Frizz-control Formula
            - Lightweight & Non-Greasy
            - Safe for Daily Use

            Product: {product_info.get('Product Name', 'N/A')}
            USPs: {product_info.get('USPs Front', 'N/A')}
        """
        st.session_state['usp'] = generate_section("USP", usp_prompt)
    text_box("USP", 'usp', 100)

    st.session_state.setdefault('what_you_get', '')
    if st.button("Generate 'What Do You Get'"):
        get_prompt = f"""
            Describe what the customer will receive when they purchase the product. Mention packaging, quantity, and any bonuses.

            Product: {product_info.get('Product Name', 'N/A')}
            Net Quantity: {product_info.get('Net Qty.', 'N/A')}
        """
        st.session_state['what_you_get'] = generate_section("What Do You Get", get_prompt)
    text_box("What Do You Get", 'what_you_get', 100)

    st.session_state.setdefault('how_to_use', '')
    if st.button("Generate 'How to Use'"):
        how_to_prompt = f"""
            Describe how to use this product step-by-step in a friendly, instructional tone.

            Product: {product_info.get('Product Name', 'N/A')}
            Instructions: {product_info.get('How to use it?', 'N/A')}
        """
        st.session_state['how_to_use'] = generate_section("How to Use", how_to_prompt)
    text_box("How to Use This", 'how_to_use', 100)

    st.session_state.setdefault('faqs', '')
    if st.button("Generate FAQs"):
        faqs_prompt = f"""
            Write 6 frequently asked questions and concise answers for this Amazon product listing.
            Guidelines:
            - Do NOT include questions about certifications, result timelines, or return/refund policies.
            - Avoid questions like "What is it?" or "How do I use it?" since those are covered elsewhere.
            - Focus on practical use, compatibility, safety (general, not certifications), storage, frequency, product care, and common customer concerns.
            - Keep answers under 150 characters.
            - Use clear, customer-friendly language.
            - Naturally include relevant keywords where possible, but do not keyword stuff.
            - Do not mention price, promotions, or other brands.

            Product: {product_info.get('Product Name', 'N/A')}
            Key Features: {product_info.get('USPs Front', 'N/A')}
            Ingredients: {product_info.get('Ingredients', 'N/A')}
            How to Use: {product_info.get('How to use it?', 'N/A')}

        """
        st.session_state['faqs'] = generate_section("FAQs", faqs_prompt)
    text_box("FAQs", 'faqs', 200)

    st.session_state.setdefault('reviews', '')
    if st.button("Generate Reviews"):
        # Check if brand is Seoulskin for language preference
        brand_name = product_info.get('Brand Name', '').strip()
        is_seoulskin = 'seoulskin' in brand_name.lower()
        
        if is_seoulskin:
            language_instruction = """
            LANGUAGE & STYLE REQUIREMENTS (SEOULSKIN - PREMIUM ENGLISH FOCUS):
            - MAJORITY (10-12 reviews) should be in premium English with sophisticated tone
            - MINORITY (3-5 reviews) can include light Hinglish for authenticity
            - English reviews should emphasize K-beauty, innovation, luxury, premium skincare
            - Keep Hinglish reviews minimal and subtle (e.g., "bohot acha", "mujhe pasand aaya")
            - Focus on premium vocabulary: "radiant", "luminous", "transformative", "innovative"
            """
        else:
            language_instruction = """
            LANGUAGE & STYLE REQUIREMENTS:
            - Use natural Hinglish like real Indian customers speak (mix of Hindi and English words)
            - Use casual, conversational tone with Hindi words like: bohot, acha, laga, pasand, mujhe, thoda, ekdum, zyada, etc.
            - Hindi words should be written in Roman script (Hinglish)
            - Mix both English and Hindi naturally in the same sentence
            - Use common phrases like: "mujhe pasand aaya", "bohot acha h", "thoda zyada", "ekdum fresh"
            """
        
        review_prompt = f"""
            Write 15 customer reviews for this product.
            
            {language_instruction}
            
            REVIEW STRUCTURE:
            - First 2 reviews: Long, story-style testimonials
            - Remaining 13 reviews: Short reviews highlighting different aspects
            - All reviewer names should be common Indian names (first name + last name)
            
            EXAMPLES OF HINGLISH STYLE TO FOLLOW:
            - "Ye eye patches bohot ache hai, ekdum cooling effect deta h aur eyes fresh lagti h"
            - "First time use kiya aur dark circles thode light lag rahe h, mujhe acha laga ye product"
            - "Daily laptop pe kaam karne se meri eyes bohot tired lagti thi, ye laga ke thoda fresh feel hota h"
            - "Feels like an expensive spa treatment! cooling, de-puffing, and brightening all in one."
            - "The texture, the packaging, the results—everything about these eye patches screams luxury."
            - "pehli baar try kiya aur accha laga, mujhe lagta h regular use se aur best result milega"
            - "thanda thanda lagta h lagane ke baad, mujhe toh ye bohot pasand aaya"
            
            TONE VARIATIONS:
            - Mix casual Hinglish reviews with some premium English reviews
            - Some reviews should be very casual (more Hindi), some semi-formal (more English)
            - Include both positive experiences and realistic observations (like "thoda patience chahiye result ke liye")
            
            IMPORTANT: Provide the output in plain text format only. Do NOT use markdown formatting like **, __, or ###. Just use simple text with reviewer name followed by their review separated by " – ".

            Product: {product_info.get('Product Name', 'N/A')}
        """
        st.session_state['reviews'] = generate_section("Reviews", review_prompt)
    text_box("Customer Reviews", 'reviews', 300)

    st.session_state.setdefault('brand_info', '')
    if st.button("Generate Brand & Contact Info"):
        brand_info_prompt = f"""
            Generate a professional brand and contact information section for the website footer. 
            Format it in a clean, easy-to-read structure suitable for a website.
            Include:
            - Brand ownership and marketing information
            - Country of origin
            - Customer support contact details
            - Email address
            
            Make it concise, professional, and customer-friendly.

            Brand: {product_info.get('Brand Name', 'N/A')}
            Brand Owned & Marketed By: {product_info.get('Brand Owned & Marketed By', 'N/A')}
            Country of Origin: {product_info.get('Country Of Origin', 'N/A')}
            Email: {product_info.get('Email', 'N/A')}
            Contact: {product_info.get('Contact Us', 'N/A')}
        """
        st.session_state['brand_info'] = generate_section("Brand & Contact Info", brand_info_prompt)
    text_box("Brand & Contact Information", 'brand_info', 150)

    # Export or clear
    if st.button("📥 Download Output as Word"):
        try:
            from docx import Document
            from io import BytesIO

            doc = Document()
            doc.add_heading(f"Product Listing Content – {product_info.get('Product Name', 'Product')}", 0)

            sections = [
                ('Product Title', 'title'),
                ('Amazon Bullet Points', 'bullets'),
                ('Amazon Description', 'description'),
                ('Shopify Description', 'shopify'),
                ('Hero Image Prompts', 'hero'),
                ('A+ Image Prompts', 'a_plus'),
                ('Website Bullet Points', 'web_bullets'),
                ('Website Description', 'web_description'),
                ('USP', 'usp'),
                ('What Do You Get', 'what_you_get'),
                ('How to Use', 'how_to_use'),
                ('FAQs', 'faqs'),
                ('Customer Reviews', 'reviews'),
                ('Brand & Contact Information', 'brand_info'),
                ('Full Website Content', 'web_full')
            ]

            for title, key in sections:
                content = st.session_state.get(key, '')
                if content:
                    doc.add_heading(title, level=1)
                    doc.add_paragraph(content, style='Normal')

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                label="Download Word Document",
                data=buffer,
                file_name="product_listing.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except ImportError:
            st.error("❌ python-docx library is not installed. Please install it using: pip install python-docx")
        except Exception as e:
            st.error(f"❌ Error creating Word document: {str(e)}")
    if st.button("🧹 Clear All"):
        for key in ['title', 'bullets', 'description', 'shopify', 'hero', 'a_plus', 'web_bullets', 'web_description', 'usp', 'what_you_get', 'how_to_use', 'faqs', 'reviews', 'brand_info', 'web_full']:
            st.session_state[key] = ''
        st.success("✅ All content cleared!")
        st.rerun()

    if st.button("📥 Download Output as JSON"):
        output = {k: st.session_state.get(k, '') for k in ['title', 'bullets', 'description', 'shopify', 'hero', 'a_plus', 'web_bullets', 'web_description', 'usp', 'what_you_get', 'how_to_use', 'faqs', 'reviews', 'brand_info', 'web_full']}
        json_str = json.dumps(output, indent=2)
        st.download_button("Download JSON", data=json_str, file_name="listing_content.json", mime="application/json")

else:
    st.info("Please upload your KLD sheet to get started.")
