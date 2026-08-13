import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader

def get_page_seo(page_filename, site_info):
    pages_seo = site_info.get("pages_seo", {})
    seo_global = site_info.get("seo_global", {})
    p_data = pages_seo.get(page_filename, {})
    
    title = p_data.get("title") or "EcoLuxe Bharat | Sustainable Road Safety & Traffic Management Solutions"
    desc = p_data.get("description") or "Premier manufacturer and supplier of high-quality road safety products, solar blinkers, speed breakers, road delineators, and traffic control systems in India."
    keywords = p_data.get("keywords") or seo_global.get("default_keywords", "")
    og_image = p_data.get("og_image") or seo_global.get("default_og_image", "img/branding/og-share-card.jpg")
    
    enable_kw = p_data.get("enable_keywords") if "enable_keywords" in p_data else seo_global.get("enable_keywords", True)
    
    return {
        "title": title,
        "description": desc,
        "keywords": keywords,
        "enable_keywords": enable_kw,
        "og_image": og_image,
        "og_title": p_data.get("og_title") or title,
        "og_description": p_data.get("og_description") or desc,
        "canonical_path": page_filename if page_filename != "index.html" else ""
    }

def get_category_seo(cat, site_info):
    seo_global = site_info.get("seo_global", {})
    cat_title = cat.get("title", "")
    
    title = cat.get("seo_title") or f"{cat_title} - Road Safety Products | EcoLuxe Bharat"
    desc = cat.get("seo_description") or f"Browse high-quality {cat_title} manufactured by EcoLuxe Bharat. Durable, reflective, and solar-powered highway safety solutions."
    
    cat_img = cat.get("image") or f"img/categories/{cat['slug']}.jpg"
    og_image = cat.get("og_image") or cat_img
    enable_kw = cat.get("enable_keywords") if "enable_keywords" in cat else seo_global.get("enable_keywords", True)
    
    return {
        "title": title,
        "description": desc,
        "keywords": cat.get("keywords") or seo_global.get("default_keywords", ""),
        "enable_keywords": enable_kw,
        "og_image": og_image,
        "og_title": cat.get("og_title") or title,
        "og_description": cat.get("og_description") or desc,
        "canonical_path": f"categories/{cat['slug']}.html"
    }

def get_product_seo(prod, cat_info, site_info):
    import re
    seo_global = site_info.get("seo_global", {})
    prod_title = prod.get("title", "")
    model = prod.get("model", "")
    cat_title = cat_info.get("title", "") if cat_info else ""
    
    default_title = f"{prod_title} | EcoLuxe Bharat"
    title = prod.get("seo_title") or default_title
    
    raw_desc = prod.get("description", "") or prod.get("short_desc", "")
    clean_desc = re.sub(r'<[^>]+>', '', raw_desc).strip()
    if clean_desc:
        default_desc = f"Inquire {prod_title} ({model}). {clean_desc[:120]}..."
    else:
        default_desc = f"Buy high-quality {prod_title} ({model}) by EcoLuxe Bharat. Engineered for maximum durability and roadway safety."
        
    desc = prod.get("seo_description") or default_desc
    
    images = prod.get("images", [])
    if images and len(images) > 0 and images[0].get("src"):
        default_og_image = images[0]["src"]
    elif cat_info and cat_info.get("image"):
        default_og_image = cat_info.get("image")
    else:
        default_og_image = seo_global.get("default_og_image", "img/branding/og-share-card.jpg")
        
    og_image = prod.get("og_image") or default_og_image
    enable_kw = prod.get("enable_keywords") if "enable_keywords" in prod else seo_global.get("enable_keywords", True)
    
    return {
        "title": title,
        "description": desc,
        "keywords": prod.get("keywords") or seo_global.get("default_keywords", ""),
        "enable_keywords": enable_kw,
        "og_image": og_image,
        "og_title": prod.get("og_title") or f"{prod_title} ({model})",
        "og_description": prod.get("og_description") or desc,
        "canonical_path": f"products/{prod.get('category_slug')}/{prod['id']}.html"
    }

def get_breadcrumb_schema(page_type, site_info, item_info=None):
    site_url = site_info.get("seo_global", {}).get("site_url", "https://ecoluxebharat.com/").rstrip("/") + "/"
    
    items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site_url}index.html"}
    ]
    
    if page_type == "products":
        items.append({"@type": "ListItem", "position": 2, "name": "Products", "item": f"{site_url}products.html"})
    elif page_type in ["about", "contact"]:
        name_map = {"about": "About Us", "contact": "Contact Us"}
        items.append({"@type": "ListItem", "position": 2, "name": name_map[page_type], "item": f"{site_url}{page_type}.html"})
    elif page_type == "category" and item_info:
        items.append({"@type": "ListItem", "position": 2, "name": "Products", "item": f"{site_url}products.html"})
        items.append({"@type": "ListItem", "position": 3, "name": item_info.get("title", ""), "item": f"{site_url}categories/{item_info.get('slug')}.html"})
    elif page_type == "product" and item_info:
        cat_info = item_info.get("category_info", {})
        prod = item_info.get("product_info", {})
        prod_name = f"{prod.get('title')} ({prod.get('model')})" if prod.get("model") else prod.get("title", "")
        
        items.append({"@type": "ListItem", "position": 2, "name": "Products", "item": f"{site_url}products.html"})
        items.append({"@type": "ListItem", "position": 3, "name": cat_info.get("title", ""), "item": f"{site_url}categories/{cat_info.get('slug')}.html"})
        items.append({"@type": "ListItem", "position": 4, "name": prod_name, "item": f"{site_url}products/{prod.get('category_slug')}/{prod.get('id')}.html"})
        
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }

def build_site(workspace_dir=None):
    # Always resolve templates relative to the location of site_builder.py
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    if workspace_dir:
        website_root = workspace_dir
    else:
        website_root = os.path.dirname(app_dir)
    
    data_dir = os.path.join(app_dir, "data")
    db_path = os.path.join(data_dir, "site_data.json")
    
    errors = []
    generated_count = 0
    
    if not os.path.exists(db_path):
        err_msg = f"Database not found at {db_path}"
        print(f"Error: {err_msg}")
        return {"success": False, "total_generated": 0, "errors": [err_msg]}
        
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        err_msg = f"Failed to load database {db_path}: {e}"
        print(f"Error: {err_msg}")
        return {"success": False, "total_generated": 0, "errors": [err_msg]}
        
    categories = data.get("categories", [])
    products = data.get("products", [])
    clients = data.get("clients", [])
    site_info = data.get("site_info", {})
    
    templates_dir = os.path.join(app_dir, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    # 1. Build index.html
    try:
        index_template = env.get_template("index.html")
        page_seo = get_page_seo("index.html", site_info)
        bc_schema = get_breadcrumb_schema("index", site_info)
        index_html = index_template.render(categories=categories, clients=clients, site_info=site_info, page_seo=page_seo, breadcrumb_schema=bc_schema, root_path="", active_menu="home")
        with open(os.path.join(website_root, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)
        generated_count += 1
        print("Generated index.html")
    except Exception as e:
        msg = f"Error rendering index.html: {e}"
        errors.append(msg)
        print(msg)
        
    # 2. Build products.html
    try:
        products_template = env.get_template("products.html")
        page_seo = get_page_seo("products.html", site_info)
        bc_schema = get_breadcrumb_schema("products", site_info)
        products_html = products_template.render(categories=categories, site_info=site_info, page_seo=page_seo, breadcrumb_schema=bc_schema, root_path="", active_menu="products")
        with open(os.path.join(website_root, "products.html"), "w", encoding="utf-8") as f:
            f.write(products_html)
        generated_count += 1
        print("Generated products.html")
    except Exception as e:
        msg = f"Error rendering products.html: {e}"
        errors.append(msg)
        print(msg)
        
    # 3. Build about.html
    try:
        about_template = env.get_template("about.html")
        page_seo = get_page_seo("about.html", site_info)
        bc_schema = get_breadcrumb_schema("about", site_info)
        about_html = about_template.render(site_info=site_info, page_seo=page_seo, breadcrumb_schema=bc_schema, root_path="", active_menu="about")
        with open(os.path.join(website_root, "about.html"), "w", encoding="utf-8") as f:
            f.write(about_html)
        generated_count += 1
        print("Generated about.html")
    except Exception as e:
        msg = f"Error rendering about.html: {e}"
        errors.append(msg)
        print(msg)
        
    # 4. Build contact.html
    try:
        contact_template = env.get_template("contact.html")
        page_seo = get_page_seo("contact.html", site_info)
        bc_schema = get_breadcrumb_schema("contact", site_info)
        contact_html = contact_template.render(site_info=site_info, page_seo=page_seo, breadcrumb_schema=bc_schema, root_path="", active_menu="contact")
        with open(os.path.join(website_root, "contact.html"), "w", encoding="utf-8") as f:
            f.write(contact_html)
        generated_count += 1
        print("Generated contact.html")
    except Exception as e:
        msg = f"Error rendering contact.html: {e}"
        errors.append(msg)
        print(msg)
        
    # 5. Build Category pages under categories/ (e.g. categories/traffic-cones.html)
    categories_out_dir = os.path.join(website_root, "categories")
    os.makedirs(categories_out_dir, exist_ok=True)
    try:
        category_template = env.get_template("category.html")
        for cat in categories:
            cat_slug = cat.get("slug", "")
            if not cat_slug:
                continue
            cat_products = [p for p in products if p.get("category_slug") == cat_slug]
            page_seo = get_category_seo(cat, site_info)
            bc_schema = get_breadcrumb_schema("category", site_info, cat)
            cat_html = category_template.render(
                category=cat,
                products=cat_products,
                categories=categories,
                site_info=site_info,
                page_seo=page_seo,
                breadcrumb_schema=bc_schema,
                root_path="../",
                active_menu="products"
            )
            cat_file_path = os.path.join(categories_out_dir, f"{cat_slug}.html")
            with open(cat_file_path, "w", encoding="utf-8") as f:
                f.write(cat_html)
            generated_count += 1
            print(f"Generated category page: categories/{cat_slug}.html")
    except Exception as e:
        msg = f"Error rendering category pages: {e}"
        errors.append(msg)
        print(msg)
        
    # 6. Build Product pages grouped by category under products/ (e.g. products/traffic-cones/eb-tc-flx75.html)
    products_out_dir = os.path.join(website_root, "products")
    os.makedirs(products_out_dir, exist_ok=True)
    
    # Safe cleanup: Only remove old .html files inside products/ subdirectories (preserves non-HTML custom assets)
    for root_dir, dirs, files in os.walk(products_out_dir):
        for file in files:
            if file.endswith(".html"):
                try:
                    os.remove(os.path.join(root_dir, file))
                except Exception as e:
                    print(f"Notice: Could not remove old file {file}: {e}")
    
    try:
        product_template = env.get_template("product.html")
        for prod in products:
            prod_id = prod.get("id", "")
            cat_slug = prod.get("category_slug", "")
            if not prod_id or not cat_slug:
                continue
                
            cat_info = next((c for c in categories if c.get("slug") == cat_slug), None)
            if not cat_info:
                cat_info = {"slug": cat_slug, "title": cat_slug.replace("-", " ").title()}
                
            related_products = [p for p in products if p.get("category_slug") == cat_slug and p.get("id") != prod_id]
            page_seo = get_product_seo(prod, cat_info, site_info)
            bc_schema = get_breadcrumb_schema("product", site_info, {"category_info": cat_info, "product_info": prod})
            
            prod_html = product_template.render(
                product=prod,
                category=cat_info,
                related_products=related_products,
                categories=categories,
                site_info=site_info,
                page_seo=page_seo,
                breadcrumb_schema=bc_schema,
                root_path="../../",
                active_menu="products"
            )
            prod_cat_dir = os.path.join(products_out_dir, cat_slug)
            os.makedirs(prod_cat_dir, exist_ok=True)
            
            prod_file_path = os.path.join(prod_cat_dir, f"{prod_id}.html")
            with open(prod_file_path, "w", encoding="utf-8") as f:
                f.write(prod_html)
            generated_count += 1
            print(f"Generated product page: products/{cat_slug}/{prod_id}.html")
    except Exception as e:
        msg = f"Error rendering product pages: {e}"
        errors.append(msg)
        print(msg)
        
    return {
        "success": len(errors) == 0,
        "total_generated": generated_count,
        "errors": errors
    }

if __name__ == "__main__":
    app_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(app_dir, "config.json")
    custom_root = None
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                custom_root = cfg.get("website_root")
        except Exception:
            pass
    if not custom_root:
        custom_root = os.path.dirname(app_dir)
    build_site(custom_root)
