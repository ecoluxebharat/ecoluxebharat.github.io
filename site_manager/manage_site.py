import sys
import os
import json
import shutil
import re
import subprocess
import webbrowser
import time
import uuid
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

from PySide6.QtCore import Qt, QThread, Slot, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit,
    QComboBox, QFileDialog, QDialog, QMessageBox, QFormLayout, QHeaderView,
    QListWidget, QListWidgetItem, QGroupBox, QFrame,
    QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QAbstractItemView,
    QSlider, QScrollArea, QRadioButton, QButtonGroup, QSplitter, QCheckBox, QMenu
)
from PySide6.QtGui import QIcon, QFont, QPixmap, QColor

from PIL import Image

# Import builder
from site_builder import build_site

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "site_data.json")
TRASH_DIR = os.path.join(SCRIPT_DIR, "trash")
TRASH_DB_PATH = os.path.join(TRASH_DIR, "trash_db.json")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

# Default root is parent of SCRIPT_DIR
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)

def load_config():
    global WORKSPACE_DIR
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                root = cfg.get("website_root", "")
                if root and os.path.exists(root):
                    WORKSPACE_DIR = root
        except Exception:
            pass

def save_config(root_path):
    global WORKSPACE_DIR
    WORKSPACE_DIR = root_path
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"website_root": root_path}, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")

load_config()

def get_default_site_info():
    return {
        "header_footer": {
            "header_phones": [
                "+91 92118 09192",
                "+91 90452 90167"
            ],
            "footer_phones": [
                "+91 92118 09192",
                "+91 90452 90167"
            ],
            "footer_emails": [
                "ecoluxebharat@gmail.com"
            ],
            "address": "B10, Supertech Ecovillage 1,\nSector 1, Greater Noida,\nUttar Pradesh, 201306",
            "social_links": {
                "facebook": "https://facebook.com/EcoLuxeBharat",
                "twitter": "https://twitter.com/EcoLuxeBharat",
                "instagram": "https://instagram.com/EcoLuxeBharat",
                "youtube": "https://www.youtube.com/@EcoLuxeBharat",
                "linkedin": "https://linkedin.com/company/EcoLuxeBharat",
                "whatsapp": "https://wa.me/919211809192",
                "phone": "tel:+919211809192"
            },
            "formsubmit_url": "https://formsubmit.co/ajax/temp2temp2222@gmail.com"
        },
        "index_page": {
            "hero_tagline": "Engineering Safer Roads Through Reliable Solutions"
        },
        "about_page": {
            "who_we_are_subtitle": "Who We Are",
            "who_we_are_title": "About Us",
            "about_text": "EcoLuxe Bharat is a premier manufacturer and supplier of high-quality, sustainable road safety products and traffic control systems. We specialize in enhancing highway and urban roadway safety across India.",
            "extended_info_text": "We offer comprehensive roadway safety solutions, blending durable solar technology, high-visibility reflective materials, and modular rubber structures. From municipal roadways to industrial parking complexes, our products are engineered for maximum durability, visual guidance, and traffic calming, supporting a safer and more sustainable infrastructure.",
            "mission_text": "To manufacture and install high-visibility, durable, and eco-friendly road safety products that protect human lives and streamline traffic flow across India's growing transit networks.",
            "vision_text": "To be India's most trusted partner in smart highway engineering, transforming roads into safe, solar-powered, and visually guided pathways with zero accidental hazards.",
            "why_choose_us_subtitle": "Why choose us?",
            "why_choose_us_heading": "Our ability to bring outstanding results to our customers."
        },
        "contact_page": {
            "phones": [
                "+91 92118 09192",
                "+91 90452 90167"
            ],
            "emails": [
                "ecoluxebharat@gmail.com"
            ],
            "address": "B10, Supertech Ecovillage 1,\nSector 1, Greater Noida,\nUttar Pradesh, 201306",
            "map_iframe_url": "https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d1751.8539303021143!2d77.44066!3d28.578534!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390cef83d6bd5539%3A0x8a60989d05702486!2sEcoLuxe%20Bharat!5e0!3m2!1sen!2sin!4v1754814584979!5m2!1sen!2sin"
        },
        "site_images": {
            "logo": "img/logo.png",
            "hero_bg": "img/hero/hero-1.jpg",
            "breadcrumb_bg": "img/breadcrumb-bg.jpg",
            "call_bg": "img/call-bg.jpg",
            "footer_bg": "img/footer-bg.jpg"
        },
        "seo_global": {
            "site_url": "https://ecoluxebharat.com/",
            "site_name": "EcoLuxe Bharat",
            "default_og_image": "img/branding/og-share-card.jpg",
            "default_keywords": "EcoLuxe Bharat, Road Safety, Traffic Management, Solar Blinkers, Speed Breakers, Road Studs, Road Delineators, Traffic Cones, Safety Barriers",
            "twitter_username": "@EcoLuxeBharat"
        },
        "pages_seo": {
            "index.html": {
                "title": "EcoLuxe Bharat | Sustainable Road Safety & Traffic Management Solutions",
                "description": "Premier manufacturer and supplier of high-quality road safety products, solar blinkers, speed breakers, road delineators, and traffic control systems in India."
            },
            "about.html": {
                "title": "About Us | EcoLuxe Bharat Road Safety",
                "description": "EcoLuxe Bharat specializes in enhancing highway and urban roadway safety across India through sustainable solar technology and high-visibility road safety products."
            },
            "contact.html": {
                "title": "Contact Us | EcoLuxe Bharat",
                "description": "Get in touch with EcoLuxe Bharat for product quotes, bulk inquiries, and highway safety project consultations."
            },
            "products.html": {
                "title": "Road Safety Products Catalog | EcoLuxe Bharat",
                "description": "Explore our comprehensive catalog of certified road safety products including barriers, solar blinkers, delineators, studs, and signages."
            }
        }
    }

def merge_site_info_defaults(loaded):
    defaults = get_default_site_info()
    if not isinstance(loaded, dict):
        return defaults
    for section, subdict in defaults.items():
        if section not in loaded or not isinstance(loaded[section], dict):
            loaded[section] = subdict
        else:
            for key, val in subdict.items():
                if key not in loaded[section]:
                    loaded[section][key] = val
    # Migration checks for header_footer
    hf = loaded.get("header_footer", {})
    if "header_phones" not in hf:
        p1 = hf.get("phone_1")
        p2 = hf.get("phone_2")
        hf["header_phones"] = [p for p in [p1, p2] if p] or defaults["header_footer"]["header_phones"]
    if "footer_phones" not in hf:
        p1 = hf.get("phone_1")
        p2 = hf.get("phone_2")
        hf["footer_phones"] = [p for p in [p1, p2] if p] or defaults["header_footer"]["footer_phones"]
    if "footer_emails" not in hf:
        em = hf.get("email")
        hf["footer_emails"] = [em] if em else defaults["header_footer"]["footer_emails"]

    # Migration checks for contact_page
    cnt = loaded.get("contact_page", {})
    if "phones" not in cnt:
        p1 = cnt.get("phone_1")
        p2 = cnt.get("phone_2")
        cnt["phones"] = [p for p in [p1, p2] if p] or defaults["contact_page"]["phones"]
    if "emails" not in cnt:
        em = cnt.get("email")
        cnt["emails"] = [em] if em else defaults["contact_page"]["emails"]

    return loaded

class EditItemSEODialog(QDialog):
    def __init__(self, item_data, site_info, categories, products, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.site_info = site_info
        self.categories = categories
        self.products = products
        
        self.item_type = item_data.get("type")
        self.item_key = item_data.get("key")
        
        self.setWindowTitle(f"Edit SEO & Social Card - {self.get_item_label()}")
        self.resize(880, 640)
        
        main_layout = QVBoxLayout(self)
        
        # Header
        lbl_header = QLabel(f"Editing SEO & Social Share Card: {self.get_item_label()}")
        lbl_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_header.setStyleSheet("color: #50ab3c; border-bottom: 2px solid #50ab3c; padding-bottom: 6px;")
        main_layout.addWidget(lbl_header)
        
        # Splitter: Left Controls, Right Live Preview
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel (Controls)
        left_widget = QWidget()
        left_form = QFormLayout(left_widget)
        left_form.setContentsMargins(0, 5, 10, 0)
        
        # Title LineEdit
        t_layout = QHBoxLayout()
        self.txt_title = QLineEdit()
        self.txt_title.textChanged.connect(self.update_live_preview)
        btn_revert_t = QPushButton("Revert Auto")
        btn_revert_t.setToolTip("Clear custom title and restore automatic default title.")
        btn_revert_t.clicked.connect(self.revert_title)
        t_layout.addWidget(self.txt_title, 1)
        t_layout.addWidget(btn_revert_t)
        
        self.lbl_t_count = QLabel("0 / 60 chars")
        self.lbl_t_count.setStyleSheet("color: #777; font-size: 11px;")
        
        # Meta Description TextEdit
        self.txt_desc = QTextEdit()
        self.txt_desc.setMinimumHeight(70)
        self.txt_desc.setMaximumHeight(95)
        self.txt_desc.textChanged.connect(self.update_live_preview)
        
        self.lbl_d_count = QLabel("0 / 160 chars")
        self.lbl_d_count.setStyleSheet("color: #777; font-size: 11px;")
        
        # Custom Social Share Image (og:image)
        img_layout = QHBoxLayout()
        self.txt_og_image = QLineEdit()
        self.txt_og_image.setPlaceholderText("Auto (Product photo / Category image)")
        self.txt_og_image.textChanged.connect(self.update_live_preview)
        btn_browse_img = QPushButton("Browse...")
        btn_browse_img.clicked.connect(self.browse_custom_og_image)
        img_layout.addWidget(self.txt_og_image, 1)
        img_layout.addWidget(btn_browse_img)
        
        # Enable Meta Keywords Checkbox
        self.chk_enable_keywords = QCheckBox("Include <meta name=\"keywords\"> tag in HTML head")
        self.chk_enable_keywords.setChecked(True)
        self.chk_enable_keywords.toggled.connect(self.on_keywords_toggled)
        
        self.txt_keywords = QLineEdit()
        self.txt_keywords.setPlaceholderText("Page-specific keywords (comma separated)")
        
        left_form.addRow("Page Title (<title>):", t_layout)
        left_form.addRow("", self.lbl_t_count)
        left_form.addRow("Meta Description:", self.txt_desc)
        left_form.addRow("", self.lbl_d_count)
        left_form.addRow("Custom Social Image:", img_layout)
        left_form.addRow("Meta Keywords Option:", self.chk_enable_keywords)
        left_form.addRow("Keywords List:", self.txt_keywords)
        
        # Right Panel (Live Link Preview)
        right_widget = QWidget()
        right_vbox = QVBoxLayout(right_widget)
        right_vbox.setContentsMargins(10, 5, 0, 0)
        
        preview_label = QLabel("Live Card Preview Switcher:")
        preview_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        switcher_layout = QHBoxLayout()
        self.radio_whatsapp = QRadioButton("💬 WhatsApp Share Card")
        self.radio_whatsapp.setChecked(True)
        self.radio_whatsapp.toggled.connect(self.update_live_preview)
        self.radio_google = QRadioButton("🔍 Google SERP Result")
        self.radio_google.toggled.connect(self.update_live_preview)
        
        switcher_layout.addWidget(self.radio_whatsapp)
        switcher_layout.addWidget(self.radio_google)
        
        self.lbl_preview_box = QLabel()
        self.lbl_preview_box.setMinimumHeight(260)
        self.lbl_preview_box.setStyleSheet(
            "border: 1px solid #d0d7de; border-radius: 8px; background-color: #f8f9fa; padding: 14px;"
            "font-family: 'Segoe UI', sans-serif;"
        )
        self.lbl_preview_box.setWordWrap(True)
        
        right_vbox.addWidget(preview_label)
        right_vbox.addLayout(switcher_layout)
        right_vbox.addWidget(self.lbl_preview_box, 1)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([460, 420])
        
        main_layout.addWidget(splitter, 1)
        
        # Action Buttons
        btn_box = QHBoxLayout()
        btn_save = QPushButton("Save Changes")
        btn_save.setObjectName("action_btn")
        btn_save.setMinimumHeight(38)
        btn_save.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.clicked.connect(self.reject)
        
        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        
        main_layout.addLayout(btn_box)
        
        self.load_item_data()

    def get_item_label(self):
        if self.item_type == "static":
            return f"Static Page [{self.item_key}]"
        elif self.item_type == "category":
            cat = next((c for c in self.categories if c.get("slug") == self.item_key), None)
            return f"Category [{cat.get('title') if cat else self.item_key}]"
        elif self.item_type == "product":
            prod = next((p for p in self.products if p.get("id") == self.item_key), None)
            if prod:
                return f"Product [{prod.get('title')} ({prod.get('model')})]" if prod.get("model") else f"Product [{prod.get('title')}]"
            return f"Product [{self.item_key}]"
        return self.item_key

    def load_item_data(self):
        from site_builder import get_page_seo, get_category_seo, get_product_seo
        
        pseo = self.site_info.get("pages_seo", {})
        gseo = self.site_info.get("seo_global", {})
        
        if self.item_type == "static":
            eff = get_page_seo(self.item_key, self.site_info)
            p_data = pseo.get(self.item_key, {})
            enable_kw = p_data.get("enable_keywords") if "enable_keywords" in p_data else gseo.get("enable_keywords", True)
        elif self.item_type == "category":
            cat = next((c for c in self.categories if c.get("slug") == self.item_key), None)
            eff = get_category_seo(cat if cat else {"slug": self.item_key}, self.site_info)
            enable_kw = cat.get("enable_keywords") if (cat and "enable_keywords" in cat) else gseo.get("enable_keywords", True)
        elif self.item_type == "product":
            prod = next((p for p in self.products if p.get("id") == self.item_key), None)
            cat_slug = prod.get("category_slug") if prod else ""
            cat_info = next((c for c in self.categories if c.get("slug") == cat_slug), None)
            eff = get_product_seo(prod if prod else {"id": self.item_key}, cat_info, self.site_info)
            enable_kw = prod.get("enable_keywords") if (prod and "enable_keywords" in prod) else gseo.get("enable_keywords", True)
            
        self.txt_title.setText(eff.get("title", ""))
        self.txt_desc.setText(eff.get("description", ""))
        self.txt_og_image.setText(eff.get("og_image", ""))
        self.chk_enable_keywords.setChecked(bool(enable_kw))
        self.txt_keywords.setText(eff.get("keywords", ""))
        self.txt_keywords.setEnabled(bool(enable_kw))
        
        self.update_live_preview()

    def revert_title(self):
        self.txt_title.setText("")
        self.update_live_preview()

    def on_keywords_toggled(self, checked):
        self.txt_keywords.setEnabled(checked)

    def browse_custom_og_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Custom Social Share Card Image", WORKSPACE_DIR,
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if not file_path:
            return
        dest_dir = os.path.join(WORKSPACE_DIR, "img", "branding")
        os.makedirs(dest_dir, exist_ok=True)
        ext = os.path.splitext(file_path)[1]
        dest_filename = f"og_{self.item_key.replace('.html','')}_{int(time.time())}{ext}"
        dest_abs = os.path.join(dest_dir, dest_filename)
        try:
            shutil.copy2(file_path, dest_abs)
            rel_path = f"img/branding/{dest_filename}".replace("\\", "/")
            self.txt_og_image.setText(rel_path)
        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"Failed to copy custom image: {e}")

    def update_live_preview(self):
        t_val = self.txt_title.text().strip()
        d_val = self.txt_desc.toPlainText().strip()
        img_val = self.txt_og_image.text().strip()
        
        site_url = self.site_info.get("seo_global", {}).get("site_url", "https://ecoluxebharat.com/")
        
        if self.item_type == "static":
            page_path = self.item_key if self.item_key != "index.html" else ""
            full_url = f"{site_url}{page_path}"
            if not t_val: t_val = f"EcoLuxe Bharat | {self.item_key.replace('.html','').title()}"
            if not d_val: d_val = "Premier manufacturer of road safety products across India."
            if not img_val: img_val = "img/branding/og-share-card.jpg"
        elif self.item_type == "category":
            cat = next((c for c in self.categories if c.get("slug") == self.item_key), None)
            c_title = cat.get("title") if cat else self.item_key
            full_url = f"{site_url}categories/{self.item_key}.html"
            if not t_val: t_val = f"{c_title} - Road Safety Products | EcoLuxe Bharat"
            if not d_val: d_val = f"Browse high-quality {c_title} manufactured by EcoLuxe Bharat."
            if not img_val: img_val = cat.get("image") or f"img/categories/{self.item_key}.jpg" if cat else "img/branding/og-share-card.jpg"
        elif self.item_type == "product":
            prod = next((p for p in self.products if p.get("id") == self.item_key), None)
            p_title = prod.get("title") if prod else self.item_key
            model = prod.get("model") if prod else ""
            cat_slug = prod.get("category_slug") if prod else ""
            full_url = f"{site_url}products/{cat_slug}/{self.item_key}.html"
            if not t_val: t_val = f"{p_title} | EcoLuxe Bharat"
            if not d_val: d_val = f"Inquire {p_title} ({model}) engineered for high durability."
            if not img_val:
                images = prod.get("images", []) if prod else []
                img_val = images[0]["src"] if (images and len(images) > 0 and images[0].get("src")) else "img/branding/og-share-card.jpg"

        # Character counts
        t_len = len(t_val)
        d_len = len(d_val)
        t_color = "#e74c3c" if t_len > 60 else ("#27ae60" if 50 <= t_len <= 60 else "#777")
        d_color = "#e74c3c" if d_len > 160 else ("#27ae60" if 120 <= d_len <= 160 else "#777")
        
        self.lbl_t_count.setText(f"{t_len} / 60 chars")
        self.lbl_t_count.setStyleSheet(f"color: {t_color}; font-size: 11px; font-weight: bold;")
        self.lbl_d_count.setText(f"{d_len} / 160 chars")
        self.lbl_d_count.setStyleSheet(f"color: {d_color}; font-size: 11px; font-weight: bold;")

        # Visual Image Thumbnail Block
        img_abs = os.path.join(WORKSPACE_DIR, img_val.replace('/', os.sep))
        if os.path.exists(img_abs):
            img_file_url = f"file:///{img_abs.replace(os.sep, '/')}"
            img_preview_html = f'<div style="text-align: center; margin-top: 6px; background: #f0f2f5; padding: 6px; border-radius: 6px; border: 1px solid #e1e4e8;"><img src="{img_file_url}" style="max-width: 140px; max-height: 75px; object-fit: contain; border-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,0.12);" /><br/><span style="font-size: 10px; color: #666; margin-top: 3px; display: block;">🖼️ <b>Preview Image:</b> {img_val}</span></div>'
        else:
            img_preview_html = f'<div style="background: #f4f6f8; padding: 6px 8px; border-radius: 6px; border: 1px solid #eef1f4; margin-top: 6px;"><span style="font-size: 11px; color: #666;">🖼️ <b>Preview Image Path:</b> {img_val}</span></div>'

        if self.radio_whatsapp.isChecked():
            html_preview = f"""
            <div style="background:#ffffff; border: 1px solid #e1e4e8; border-left: 5px solid #25d366; padding: 14px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="font-size: 11px; font-weight: 600; color: #128c7e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">💬 Social Share Card Mockup</div>
                <div style="font-size: 14px; font-weight: bold; color: #111; line-height: 1.3; margin-bottom: 6px;">{t_val}</div>
                <div style="font-size: 12px; color: #4a4a4a; line-height: 1.4; margin-bottom: 8px;">{d_val}</div>
                <div style="background: #f4f6f8; padding: 6px 10px; border-radius: 6px; border: 1px solid #eef1f4;">
                    <span style="font-size: 11px; color: #0066cc; word-break: break-all;">🌐 <b>URL:</b> {full_url}</span>
                </div>
                {img_preview_html}
            </div>
            """
        else: # Google SERP preview
            html_preview = f"""
            <div style="background:#ffffff; border: 1px solid #e1e4e8; padding: 14px; border-radius: 8px; font-family: Arial, sans-serif;">
                <div style="font-size: 11px; font-weight: 600; color: #5f6368; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">🔍 Google Search Result Snippet</div>
                <div style="font-size: 12px; color: #202124; margin-bottom: 2px;">{full_url}</div>
                <h3 style="font-size: 18px; color: #1a0dab; margin: 0 0 6px 0; font-weight: 400; cursor: pointer; text-decoration: underline;">{t_val}</h3>
                <div style="font-size: 13px; color: #4d5156; line-height: 1.5;">{d_val}</div>
            </div>
            """

        self.lbl_preview_box.setText(html_preview)

    def get_edited_data(self):
        return {
            "title": self.txt_title.text().strip(),
            "description": self.txt_desc.toPlainText().strip(),
            "og_image": self.txt_og_image.text().strip(),
            "enable_keywords": self.chk_enable_keywords.isChecked(),
            "keywords": self.txt_keywords.text().strip()
        }


def stage_and_reindex_images(image_list, target_dir_rel, prefix, workspace_dir, trash_dir, log_func=print):
    """
    Two-Pass Atomic Staging Algorithm for showcase/gallery images.
    - image_list: list of dicts containing 'src', 'w', 'h' (and optional 'alt').
    - target_dir_rel: relative target folder e.g. "img/categories/showcase/road-delineators"
    - prefix: e.g. "road-delineators-showcase" or "eb-tc-flx75"
    - workspace_dir: root website directory
    - trash_dir: site_manager/trash directory
    """
    target_dir_abs = os.path.join(workspace_dir, target_dir_rel)

    if not image_list:
        # Move any remaining files in target folder to trash if empty
        if os.path.exists(target_dir_abs):
            for filename in os.listdir(target_dir_abs):
                file_abs = os.path.join(target_dir_abs, filename)
                if os.path.isfile(file_abs):
                    trash_img_dir = os.path.join(trash_dir, "images")
                    os.makedirs(trash_img_dir, exist_ok=True)
                    dest_abs = os.path.join(trash_img_dir, filename)
                    if os.path.exists(dest_abs):
                        name_part, ext_part = os.path.splitext(filename)
                        dest_abs = os.path.join(trash_img_dir, f"{name_part}_{int(time.time())}{ext_part}")
                    try:
                        shutil.move(file_abs, dest_abs)
                        log_func(f"Moved removed asset {filename} to trash/images/")
                    except Exception as e:
                        log_func(f"Error trashing asset {filename}: {e}")
        return []

    os.makedirs(target_dir_abs, exist_ok=True)

    session_id = uuid.uuid4().hex[:8]
    staged_items = []
    staged_tmp_basenames = []
    
    # PASS 1: Atomic Staging to unique temporary files
    for idx, img_info in enumerate(image_list):
        src_raw = img_info["src"]
        ext = os.path.splitext(src_raw)[1] or ".jpg"
        tmp_filename = f"_tmp_stage_{session_id}_{idx}{ext}"
        tmp_rel = f"{target_dir_rel}/{tmp_filename}"
        tmp_abs = os.path.join(workspace_dir, tmp_rel)

        # Check if src_raw is inside workspace or external
        src_abs = src_raw if os.path.isabs(src_raw) else os.path.join(workspace_dir, src_raw)

        try:
            if os.path.exists(src_abs):
                # If src_abs is already in target_dir_abs, rename/move to tmp_abs
                if os.path.dirname(os.path.abspath(src_abs)) == os.path.abspath(target_dir_abs):
                    shutil.move(src_abs, tmp_abs)
                else:
                    shutil.copy2(src_abs, tmp_abs)
            else:
                # If file doesn't exist, log warning
                log_func(f"Warning: Image source path {src_raw} not found")
                continue

            item_copy = dict(img_info)
            item_copy["_tmp_abs"] = tmp_abs
            item_copy["_ext"] = ext
            staged_items.append(item_copy)
            staged_tmp_basenames.append(tmp_filename)
        except Exception as e:
            log_func(f"Error staging image {src_raw}: {e}")

    # PASS 2: Orphan Cleanup (Move ALL non-staged files to trash BEFORE sequential renaming!)
    if os.path.exists(target_dir_abs):
        for filename in os.listdir(target_dir_abs):
            if filename in staged_tmp_basenames:
                continue

            if filename.startswith("_tmp_stage_"):
                # Clean leftover tmp file from old session
                try:
                    os.remove(os.path.join(target_dir_abs, filename))
                except Exception:
                    pass
                continue

            file_abs = os.path.join(target_dir_abs, filename)
            if os.path.isfile(file_abs):
                trash_img_dir = os.path.join(trash_dir, "images")
                os.makedirs(trash_img_dir, exist_ok=True)
                dest_abs = os.path.join(trash_img_dir, filename)
                if os.path.exists(dest_abs):
                    name_part, ext_part = os.path.splitext(filename)
                    dest_abs = os.path.join(trash_img_dir, f"{name_part}_{int(time.time())}{ext_part}")
                try:
                    shutil.move(file_abs, dest_abs)
                    log_func(f"Moved orphan image {filename} to trash/images/")
                except Exception as e:
                    log_func(f"Error trashing orphan image {filename}: {e}")

    # PASS 3: Final Sequential Renaming
    final_list = []

    for idx, staged_item in enumerate(staged_items):
        ext = staged_item["_ext"]
        final_filename = f"{prefix}-{idx}{ext}"
        final_rel = f"{target_dir_rel}/{final_filename}"
        final_abs = os.path.join(workspace_dir, final_rel)

        tmp_abs = staged_item.pop("_tmp_abs")
        staged_item.pop("_ext")

        try:
            if os.path.exists(tmp_abs):
                shutil.move(tmp_abs, final_abs)
            staged_item["src"] = final_rel
            final_list.append(staged_item)
        except Exception as e:
            log_func(f"Error finalizing image {final_filename}: {e}")

    return final_list

# Premium Dark Stylesheet
STYLESHEET = """
QMainWindow, QDialog, QMessageBox {
    background-color: #121212;
}
QWidget {
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #2d2d2d;
    background: #1e1e1e;
    border-radius: 8px;
    top: -1px;
}
QTabWidget::tab-bar {
    alignment: left;
}
QTabBar::tab {
    background: #232323;
    border: 1px solid #2d2d2d;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    color: #888888;
}
QTabBar::tab:hover {
    background: #2d2d2d;
    color: #ffffff;
}
QTabBar::tab:selected {
    background: #1e1e1e;
    border-color: #2d2d2d;
    border-bottom-color: #1e1e1e;
    color: #50ab3c;
    font-weight: bold;
}
QPushButton {
    background-color: #282828;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px 14px;
    color: #e0e0e0;
}
QPushButton:hover {
    background-color: #383838;
    border-color: #50ab3c;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #1e1e1e;
}
QPushButton:disabled {
    color: #555555;
    background-color: #181818;
    border-color: #222222;
}
QPushButton#action_btn {
    background-color: #50ab3c;
    color: #ffffff;
    font-weight: bold;
    border: none;
    padding: 10px 18px;
    font-size: 14px;
}
QPushButton#action_btn:hover {
    background-color: #3d8c2e;
}
QPushButton#danger_btn {
    background-color: #a83232;
    color: #ffffff;
    border: none;
}
QPushButton#danger_btn:hover {
    background-color: #cc3f3f;
}
QTableWidget {
    background-color: #181818;
    border: 1px solid #2d2d2d;
    gridline-color: #2d2d2d;
    alternate-background-color: #1f1f1f;
}
QTableWidget::item:selected {
    background-color: #2c4228;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #232323;
    color: #bbbbbb;
    padding: 6px;
    border: 1px solid #2d2d2d;
    font-weight: bold;
}
QLineEdit, QTextEdit, QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px;
    color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #50ab3c;
}
QLabel {
    font-weight: 500;
}
QGroupBox {
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 15px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #50ab3c;
}
QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
}
QListWidget::item {
    padding: 5px;
    border-bottom: 1px solid #2a2a2a;
}
QListWidget::item:selected {
    background-color: #2c4228;
    color: #ffffff;
}
QTreeWidget {
    background-color: #181818;
    border: 1px solid #2d2d2d;
    color: #e0e0e0;
}
QTreeWidget::item {
    padding: 8px;
    border-bottom: 1px solid #252525;
}
QTreeWidget::item:hover {
    background-color: #2a2a2a;
    color: #ffffff;
}
QTreeWidget::item:selected {
    background-color: #2c4228;
    color: #ffffff;
}
QComboBox QAbstractItemView {
    background-color: #181818;
    color: #ffffff;
    selection-background-color: #2c4228;
    selection-color: #ffffff;
    border: 1px solid #2d2d2d;
}
QMessageBox QLabel {
    color: #ffffff;
}
QMessageBox QPushButton {
    background-color: #282828;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    padding: 5px 15px;
    min-width: 70px;
}
QMessageBox QPushButton:hover {
    background-color: #383838;
    border-color: #50ab3c;
}
"""

class PreviewServerThread(QThread):
    def __init__(self, directory, port=8000):
        super().__init__()
        self.directory = directory
        self.port = port
        self.server = None

    def run(self):
        dir_to_serve = self.directory
        
        # Safe Handler supporting directory parameter
        class CustomHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=dir_to_serve, **kwargs)
            def end_headers(self):
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                super().end_headers()
                
        TCPServer.allow_reuse_address = True
        try:
            self.server = TCPServer(("", self.port), CustomHandler)
            print(f"Server started on port {self.port}")
            self.server.serve_forever()
        except Exception as e:
            print(f"Preview server exception: {e}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()

class ShowcaseSelectorDialog(QDialog):
    def __init__(self, parent=None, candidates=None):
        super().__init__(parent)
        self.candidates = candidates if candidates is not None else []
        self.setWindowTitle("Select Images from Catalog")
        self.resize(550, 450)
        self.setStyleSheet(STYLESHEET)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Check the images you want to include in the Spotlight Showcase Gallery:")
        label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(label)
        
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(60, 60))
        layout.addWidget(self.list_widget)
        
        self.checkboxes = []
        for c in candidates:
            item = QListWidgetItem()
            item.setText(c["label"])
            
            path = os.path.join(WORKSPACE_DIR, c["src"])
            if os.path.exists(path):
                pixmap = QPixmap(path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(QIcon(pixmap))
            
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            
            self.list_widget.addItem(item)
            self.checkboxes.append((item, c))
            
        actions_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Add Selected")
        self.btn_ok.setObjectName("action_btn")
        self.btn_ok.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_cancel)
        actions_layout.addWidget(self.btn_ok)
        
        layout.addLayout(actions_layout)

    def get_selected(self):
        selected = []
        for item, c in self.checkboxes:
            if item.checkState() == Qt.Checked:
                selected.append(c)
        return selected


class CategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.setWindowTitle("Add Category" if not category else "Edit Category")
        self.resize(750, 700)
        self.setStyleSheet(STYLESHEET)
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        
        self.showcase_images = []
        if category:
            self.showcase_images = list(category.get("showcase_images", []))
            
        self.init_ui()
        if category:
            self.load_category()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Traffic Cones")
        
        self.slug_input = QLineEdit()
        self.slug_input.setPlaceholderText("e.g. traffic-cones")
        if self.category:
            self.slug_input.setEnabled(False) # Slug is key, disable edits
            
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description of this product category...")
        
        self.img_path_input = QLineEdit()
        self.img_path_input.setReadOnly(True)
        self.btn_select_img = QPushButton("Browse...")
        self.btn_select_img.clicked.connect(self.select_image)
        
        img_layout = QHBoxLayout()
        img_layout.addWidget(self.img_path_input)
        img_layout.addWidget(self.btn_select_img)
        
        form_layout.addRow("Category Name:", self.title_input)
        form_layout.addRow("URL Slug:", self.slug_input)
        form_layout.addRow("Description:", self.desc_input)
        form_layout.addRow("Category Image:", img_layout)
        
        layout.addLayout(form_layout)
        
        # Showcase Spotlight Gallery Group
        showcase_group = QGroupBox("Category Showcase Spotlight Gallery")
        showcase_layout = QHBoxLayout(showcase_group)
        
        self.showcase_list = QListWidget()
        self.showcase_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.showcase_list.setIconSize(QSize(60, 60))
        self.refresh_showcase_list()
        
        ctrl_layout = QVBoxLayout()
        self.btn_add_custom_sc = QPushButton("Add Custom Image(s)...")
        self.btn_add_custom_sc.clicked.connect(self.add_custom_showcase)
        
        self.btn_select_catalog = QPushButton("Select from Catalog...")
        self.btn_select_catalog.clicked.connect(self.select_catalog_images)
        
        self.btn_remove_sc = QPushButton("Remove Selected")
        self.btn_remove_sc.clicked.connect(self.remove_showcase)
        
        self.btn_sc_up = QPushButton("Move Up")
        self.btn_sc_up.clicked.connect(self.move_showcase_up)
        
        self.btn_sc_down = QPushButton("Move Down")
        self.btn_sc_down.clicked.connect(self.move_showcase_down)
        
        ctrl_layout.addWidget(self.btn_add_custom_sc)
        ctrl_layout.addWidget(self.btn_select_catalog)
        ctrl_layout.addWidget(self.btn_remove_sc)
        ctrl_layout.addWidget(self.btn_sc_up)
        ctrl_layout.addWidget(self.btn_sc_down)
        ctrl_layout.addStretch()
        
        showcase_layout.addWidget(self.showcase_list, 2)
        showcase_layout.addLayout(ctrl_layout, 1)
        
        layout.addWidget(showcase_group)
        
        if not self.category:
            self.title_input.textChanged.connect(self.auto_slugify)
            
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Category")
        self.btn_save.setObjectName("action_btn")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)

    def auto_slugify(self, text):
        slug = text.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        self.slug_input.setText(slug)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Category Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self.img_path_input.setText(file_path)

    def load_category(self):
        self.title_input.setText(self.category.get("title", ""))
        self.slug_input.setText(self.category.get("slug", ""))
        self.desc_input.setPlainText(self.category.get("description", ""))
        self.img_path_input.setText(self.category.get("image", ""))
        self.refresh_showcase_list()

    def refresh_showcase_list(self):
        self.showcase_list.clear()
        for img in self.showcase_images:
            filename = os.path.basename(img["src"])
            item = QListWidgetItem(f"{filename} ({img.get('w', 1024)}x{img.get('h', 1024)})")
            
            path = os.path.join(WORKSPACE_DIR, img["src"])
            if os.path.exists(path):
                pixmap = QPixmap(path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(QIcon(pixmap))
            else:
                if os.path.exists(img["src"]):
                    pixmap = QPixmap(img["src"]).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item.setIcon(QIcon(pixmap))
            self.showcase_list.addItem(item)

    def add_custom_showcase(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Showcase Images", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        for file in files:
            try:
                with Image.open(file) as img:
                    w, h = img.size
            except Exception:
                w, h = 1024, 1024
            self.showcase_images.append({
                "src": file,
                "w": w,
                "h": h
            })
        self.refresh_showcase_list()

    def select_catalog_images(self):
        slug = self.slug_input.text().strip()
        cat_img = self.img_path_input.text().strip()
        
        candidates = []
        if cat_img:
            candidates.append({
                "src": cat_img,
                "label": f"Category Image: {os.path.basename(cat_img)}",
                "type": "category"
            })
            
        main_win = self.parent()
        if main_win and hasattr(main_win, "products"):
            for prod in main_win.products:
                if prod.get("category_slug", "") == slug:
                    for idx, img_info in enumerate(prod.get("images", [])):
                        candidates.append({
                            "src": img_info["src"],
                            "label": f"Product: {prod.get('title')} - Image {idx+1}",
                            "type": "product"
                        })
                        
        if not candidates:
            QMessageBox.information(self, "No Catalog Images", "There are no category or product images associated with this slug yet. Select custom files or populate products first.")
            return
            
        dialog = ShowcaseSelectorDialog(self, candidates)
        if dialog.exec() == QDialog.Accepted:
            selected = dialog.get_selected()
            for s in selected:
                if any(x["src"] == s["src"] for x in self.showcase_images):
                    continue
                try:
                    w, h = 1024, 1024
                    path = os.path.join(WORKSPACE_DIR, s["src"])
                    if os.path.exists(path):
                        with Image.open(path) as img:
                            w, h = img.size
                except Exception:
                    w, h = 1024, 1024
                    
                self.showcase_images.append({
                    "src": s["src"],
                    "w": w,
                    "h": h
                })
            self.refresh_showcase_list()

    def remove_showcase(self):
        selected_indexes = self.showcase_list.selectedIndexes()
        if not selected_indexes:
            return
        selected_rows = sorted(list(set(idx.row() for idx in selected_indexes)), reverse=True)
        for row in selected_rows:
            if 0 <= row < len(self.showcase_images):
                del self.showcase_images[row]
        self.refresh_showcase_list()

    def move_showcase_up(self):
        row = self.showcase_list.currentRow()
        if row > 0:
            self.showcase_images[row], self.showcase_images[row - 1] = self.showcase_images[row - 1], self.showcase_images[row]
            self.refresh_showcase_list()
            self.showcase_list.setCurrentRow(row - 1)

    def move_showcase_down(self):
        row = self.showcase_list.currentRow()
        if 0 <= row < len(self.showcase_images) - 1:
            self.showcase_images[row], self.showcase_images[row + 1] = self.showcase_images[row + 1], self.showcase_images[row]
            self.refresh_showcase_list()
            self.showcase_list.setCurrentRow(row + 1)

    def accept(self):
        slug = self.slug_input.text().strip().lower()
        title = self.title_input.text().strip()
        if not title or not slug:
            QMessageBox.warning(self, "Validation Error", "Category Name and URL Slug cannot be empty.")
            return
        if not re.match(r"^[a-z0-9\-]+$", slug):
            QMessageBox.warning(self, "Validation Error", "URL Slug can only contain lowercase letters, numbers, and hyphens (e.g. traffic-cones). No spaces, slashes, or special characters allowed.")
            return
        super().accept()

    def get_data(self):
        return {
            "title": self.title_input.text().strip(),
            "slug": self.slug_input.text().strip().lower(),
            "description": self.desc_input.toPlainText().strip(),
            "image": self.img_path_input.text().strip(),
            "showcase_images": self.showcase_images
        }

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None, categories=None):
        super().__init__(parent)
        self.product = product
        self.categories = categories if categories is not None else []
        self.setWindowTitle("Add Product" if not product else "Edit Product")
        self.resize(850, 800)
        self.setStyleSheet(STYLESHEET)
        
        # Support maximizing and minimizing
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        
        # Internal state for images
        self.product_images = [] # holds list of {"src": "...", "w": 1024, "h": 1024, "alt": "..."}
        if product:
            self.product_images = list(product.get("images", []))
            
        self.init_ui()
        if product:
            self.load_product()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g. eb-tc-flx75")
        if self.product:
            self.id_input.setEnabled(False) # ID is key, disable edits
            
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g. EB-TC-FLX75")
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Flexible PU Cone")
        
        self.cat_selector = QComboBox()
        for cat in self.categories:
            self.cat_selector.addItem(cat.get("title", ""), cat.get("slug", ""))
            
        self.short_desc_input = QLineEdit()
        self.short_desc_input.setPlaceholderText("Short summary tagline...")
        
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("e.g. UV-Stabilized HDPE")
        
        self.dimensions_input = QLineEdit()
        self.dimensions_input.setPlaceholderText("e.g. 1500 x 450 x 800 mm")
        
        self.features_input = QTextEdit()
        self.features_input.setMinimumHeight(60)
        self.features_input.setMaximumHeight(85)
        self.features_input.setPlaceholderText("Key bullet features (one feature per line)...")
            
        self.desc_input = QTextEdit()
        self.desc_input.setMinimumHeight(70)
        self.desc_input.setPlaceholderText("Full detailed product description...")
        
        form_layout.addRow("Product ID:", self.id_input)
        form_layout.addRow("Model Number:", self.model_input)
        form_layout.addRow("Product Title:", self.title_input)
        form_layout.addRow("Category:", self.cat_selector)
        form_layout.addRow("Short Tagline:", self.short_desc_input)
        form_layout.addRow("Material Build:", self.material_input)
        form_layout.addRow("Dimensions:", self.dimensions_input)
        form_layout.addRow("Key Features:", self.features_input)
        form_layout.addRow("Full Description:", self.desc_input)
        
        layout.addLayout(form_layout)
        
        # Spec Editor Group
        spec_group = QGroupBox("Technical Specifications")
        spec_layout = QVBoxLayout(spec_group)
        
        self.spec_table = QTableWidget(0, 2)
        self.spec_table.setHorizontalHeaderLabels(["Specification Label", "Value"])
        self.spec_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.spec_table.setMinimumHeight(200)
        
        spec_btn_layout = QHBoxLayout()
        self.btn_add_spec = QPushButton("Add Specification")
        self.btn_add_spec.clicked.connect(self.add_spec_row)
        self.btn_remove_spec = QPushButton("Remove Selected Spec")
        self.btn_remove_spec.clicked.connect(self.remove_spec_row)
        
        spec_btn_layout.addWidget(self.btn_add_spec)
        spec_btn_layout.addWidget(self.btn_remove_spec)
        spec_btn_layout.addStretch()
        
        spec_layout.addWidget(self.spec_table)
        spec_layout.addLayout(spec_btn_layout)
        
        layout.addWidget(spec_group)
        
        # Image Uploader Group
        img_group = QGroupBox("Product Gallery Images")
        img_layout = QHBoxLayout(img_group)
        
        self.img_list = QListWidget()
        self.img_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.img_list.setIconSize(QSize(50, 50))
        self.refresh_image_list()
        
        img_ctrl_layout = QVBoxLayout()
        self.btn_add_img = QPushButton("Add Image")
        self.btn_add_img.clicked.connect(self.add_product_image)
        
        self.btn_remove_img = QPushButton("Remove Selected")
        self.btn_remove_img.clicked.connect(self.remove_product_image)
        
        self.btn_move_up = QPushButton("Move Up")
        self.btn_move_up.clicked.connect(self.move_image_up)
        
        self.btn_move_down = QPushButton("Move Down")
        self.btn_move_down.clicked.connect(self.move_image_down)
        
        img_ctrl_layout.addWidget(self.btn_add_img)
        img_ctrl_layout.addWidget(self.btn_remove_img)
        img_ctrl_layout.addWidget(self.btn_move_up)
        img_ctrl_layout.addWidget(self.btn_move_down)
        img_ctrl_layout.addStretch()
        
        img_layout.addWidget(self.img_list, 2)
        img_layout.addLayout(img_ctrl_layout, 1)
        
        layout.addWidget(img_group)
        
        # Automatic ID generation
        if not self.product:
            self.model_input.textChanged.connect(self.auto_id)
            
        # Dialog Action buttons
        actions_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Product")
        self.btn_save.setObjectName("action_btn")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_cancel)
        actions_layout.addWidget(self.btn_save)
        
        layout.addLayout(actions_layout)

    def auto_id(self, text):
        prod_id = text.lower().strip()
        prod_id = re.sub(r"[^\w\s-]", "", prod_id)
        prod_id = re.sub(r"[-\s]+", "-", prod_id)
        self.id_input.setText(prod_id)

    def add_spec_row(self, label="", value=""):
        row = self.spec_table.rowCount()
        self.spec_table.insertRow(row)
        self.spec_table.setItem(row, 0, QTableWidgetItem(label))
        self.spec_table.setItem(row, 1, QTableWidgetItem(value))

    def remove_spec_row(self):
        row = self.spec_table.currentRow()
        if row >= 0:
            self.spec_table.removeRow(row)

    def refresh_image_list(self):
        self.img_list.clear()
        for idx, img in enumerate(self.product_images):
            # Create list item
            filename = os.path.basename(img["src"])
            item = QListWidgetItem(f"{filename} (Alt: {img.get('alt', '')})")
            
            # Display thumbnail if file exists
            path = os.path.join(WORKSPACE_DIR, img["src"])
            if os.path.exists(path):
                pixmap = QPixmap(path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(QIcon(pixmap))
            else:
                # Preview temporary files
                temp_path = img["src"]
                if os.path.exists(temp_path):
                    pixmap = QPixmap(temp_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item.setIcon(QIcon(pixmap))
            
            self.img_list.addItem(item)

    def add_product_image(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Product Images", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        for file in files:
            # Load dimension using PIL
            try:
                with Image.open(file) as img:
                    w, h = img.size
            except Exception:
                w, h = 1024, 1024
                
            # Set default Alt text as Product Title
            alt = self.title_input.text().strip() or "Product Image"
            self.product_images.append({
                "src": file, # store absolute path temporarily, copied to correct structure on save
                "w": w,
                "h": h,
                "alt": alt
            })
        self.refresh_image_list()

    def remove_product_image(self):
        selected_indexes = self.img_list.selectedIndexes()
        if not selected_indexes:
            return
        selected_rows = sorted(list(set(idx.row() for idx in selected_indexes)), reverse=True)
        for row in selected_rows:
            if 0 <= row < len(self.product_images):
                del self.product_images[row]
        self.refresh_image_list()

    def move_image_up(self):
        row = self.img_list.currentRow()
        if row > 0:
            # swap
            self.product_images[row], self.product_images[row - 1] = self.product_images[row - 1], self.product_images[row]
            self.refresh_image_list()
            self.img_list.setCurrentRow(row - 1)

    def move_image_down(self):
        row = self.img_list.currentRow()
        if 0 <= row < len(self.product_images) - 1:
            # swap
            self.product_images[row], self.product_images[row + 1] = self.product_images[row + 1], self.product_images[row]
            self.refresh_image_list()
            self.img_list.setCurrentRow(row + 1)

    def load_product(self):
        self.id_input.setText(self.product.get("id", ""))
        self.model_input.setText(self.product.get("model", ""))
        self.title_input.setText(self.product.get("title", ""))
        
        # Select category
        idx = self.cat_selector.findData(self.product.get("category_slug", ""))
        if idx >= 0:
            self.cat_selector.setCurrentIndex(idx)
            
        self.short_desc_input.setText(self.product.get("short_desc", ""))
        self.material_input.setText(self.product.get("material", ""))
        
        dims_val = self.product.get("dimensions", "")
        if isinstance(dims_val, dict):
            dims_val = dims_val.get("text", "")
        self.dimensions_input.setText(str(dims_val))
        
        feats = self.product.get("features", [])
        if isinstance(feats, list):
            self.features_input.setPlainText("\n".join(feats))
        else:
            self.features_input.setPlainText(str(feats))
            
        self.desc_input.setPlainText(self.product.get("description", ""))
        
        # Specs
        specs = self.product.get("specifications", [])
        # Set default empty specs if none
        if not specs:
            specs = [
                {"label": "Dimensions / Capacity", "value": ""},
                {"label": "Material Build", "value": ""},
                {"label": "Key Specifications", "value": ""}
            ]
        for s in specs:
            self.add_spec_row(s.get("label", ""), s.get("value", ""))
            
        self.refresh_image_list()

    def accept(self):
        p_id = self.id_input.text().strip().lower()
        title = self.title_input.text().strip()
        if not title or not p_id:
            QMessageBox.warning(self, "Validation Error", "Product ID and Product Title cannot be empty.")
            return
        if not re.match(r"^[a-z0-9\-]+$", p_id):
            QMessageBox.warning(self, "Validation Error", "Product ID can only contain lowercase letters, numbers, and hyphens (e.g. eb-br-wf15). No spaces, slashes, or special characters allowed.")
            return
        super().accept()

    def get_data(self):
        # Extract specs
        specs = []
        for row in range(self.spec_table.rowCount()):
            label_item = self.spec_table.item(row, 0)
            value_item = self.spec_table.item(row, 1)
            
            label = label_item.text().strip() if label_item else ""
            value = value_item.text().strip() if value_item else ""
            if label:
                specs.append({"label": label, "value": value})
                
        feats = [f.strip() for f in self.features_input.toPlainText().splitlines() if f.strip()]
        dims_str = self.dimensions_input.text().strip()
        dims = {"text": dims_str} if dims_str else {}
        
        data = {
            "id": self.id_input.text().strip().lower(),
            "model": self.model_input.text().strip(),
            "title": self.title_input.text().strip(),
            "category_slug": self.cat_selector.currentData(),
            "short_desc": self.short_desc_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "features": feats,
            "material": self.material_input.text().strip(),
            "dimensions": dims,
            "specifications": specs,
            "images": self.product_images
        }
        # Preserve custom SEO fields if editing existing product
        if self.product:
            for k in ["seo_title", "seo_description", "og_image", "keywords", "enable_keywords"]:
                if k in self.product:
                    data[k] = self.product[k]
        return data


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EcoLuxe Bharat | Website Manager Dashboard")
        self.resize(1000, 700)
        self.setStyleSheet(STYLESHEET)
        
        # Load database
        self.categories = []
        self.products = []
        self.load_database()
        
        self.trash_items = []
        self.load_trash_database()
        
        self.preview_thread = None
        
        self.init_ui()

    def load_database(self):
        self.categories = []
        self.products = []
        self.clients = []
        self.site_info = get_default_site_info()
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.categories = data.get("categories", [])
                    self.products = data.get("products", [])
                    self.site_info = merge_site_info_defaults(data.get("site_info"))
                    
                    if "clients" not in data:
                        self.clients = [
                            {"id": "client-1", "name": "Client 1", "logo": "img/logo/logo-1.png", "link": "#", "link_enabled": False},
                            {"id": "client-2", "name": "Client 2", "logo": "img/logo/logo-2.png", "link": "#", "link_enabled": False},
                            {"id": "client-3", "name": "Client 3", "logo": "img/logo/logo-3.png", "link": "#", "link_enabled": False},
                            {"id": "client-4", "name": "Client 4", "logo": "img/logo/logo-4.png", "link": "#", "link_enabled": False},
                            {"id": "client-5", "name": "Client 5", "logo": "img/logo/logo-5.png", "link": "#", "link_enabled": False}
                        ]
                        self.save_database()
                    else:
                        self.clients = data.get("clients", [])
                        # Ensure names exist on all loaded clients
                        modified = False
                        for c in self.clients:
                            if "name" not in c:
                                filename = os.path.basename(c.get("logo", ""))
                                base_name = os.path.splitext(filename)[0]
                                c["name"] = base_name.replace("-", " ").replace("_", " ").title()
                                modified = True
                        if modified:
                            self.save_database()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to load database: {e}")
        else:
            # Seed default categories
            self.categories = []
            self.products = []
            self.clients = [
                {"id": "client-1", "name": "Client 1", "logo": "img/logo/logo-1.png", "link": "#", "link_enabled": False},
                {"id": "client-2", "name": "Client 2", "logo": "img/logo/logo-2.png", "link": "#", "link_enabled": False},
                {"id": "client-3", "name": "Client 3", "logo": "img/logo/logo-3.png", "link": "#", "link_enabled": False},
                {"id": "client-4", "name": "Client 4", "logo": "img/logo/logo-4.png", "link": "#", "link_enabled": False},
                {"id": "client-5", "name": "Client 5", "logo": "img/logo/logo-5.png", "link": "#", "link_enabled": False}
            ]
            self.site_info = get_default_site_info()
            self.save_database()

    def save_database(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        backups_dir = os.path.join(DATA_DIR, "backups")
        os.makedirs(backups_dir, exist_ok=True)
        
        db_payload = {
            "categories": self.categories,
            "products": self.products,
            "clients": getattr(self, 'clients', []),
            "site_info": getattr(self, 'site_info', get_default_site_info())
        }
        
        tmp_db_path = DB_PATH + ".tmp"
        try:
            # 1. Atomic save via temp file and fsync
            with open(tmp_db_path, "w", encoding="utf-8") as f:
                json.dump(db_payload, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_db_path, DB_PATH)
            
            # 2. Rolling timestamped backup (keep max 10)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backups_dir, f"site_data_{timestamp}.json")
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(db_payload, f, indent=4)
                
            b_files = sorted([os.path.join(backups_dir, bf) for bf in os.listdir(backups_dir) if bf.startswith("site_data_") and bf.endswith(".json")])
            if len(b_files) > 10:
                for old_b in b_files[:-10]:
                    try:
                        os.remove(old_b)
                    except Exception:
                        pass
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save database atomically: {e}")

    def restore_database_from_backup(self):
        backups_dir = os.path.join(DATA_DIR, "backups")
        if not os.path.exists(backups_dir):
            QMessageBox.information(self, "No Backups Found", "No automatic backups exist yet.")
            return
            
        b_files = sorted([bf for bf in os.listdir(backups_dir) if bf.startswith("site_data_") and bf.endswith(".json")], reverse=True)
        if not b_files:
            QMessageBox.information(self, "No Backups Found", "No automatic backups exist yet.")
            return
            
        items = []
        for bf in b_files:
            abs_p = os.path.join(backups_dir, bf)
            try:
                mtime = os.path.getmtime(abs_p)
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                with open(abs_p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cat_count = len(data.get("categories", []))
                prod_count = len(data.get("products", []))
                items.append((f"📅 {time_str}  —  {prod_count} Products, {cat_count} Categories [{bf}]", abs_p))
            except Exception:
                items.append((f"{bf}", abs_p))
                
        dialog = QDialog(self)
        dialog.setWindowTitle("Restore Database from Auto-Backup")
        dialog.resize(650, 420)
        vbox = QVBoxLayout(dialog)
        
        lbl_info = QLabel("Select an automatic backup to restore. Your current state will be backed up automatically before restoring.")
        lbl_info.setStyleSheet("font-weight: bold; color: #50ab3c; margin-bottom: 6px;")
        lbl_info.setWordWrap(True)
        vbox.addWidget(lbl_info)
        
        list_widget = QListWidget()
        for label, abs_p in items:
            l_item = QListWidgetItem(label)
            l_item.setData(Qt.UserRole, abs_p)
            list_widget.addItem(l_item)
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)
        vbox.addWidget(list_widget, 1)
        
        btn_box = QHBoxLayout()
        btn_restore = QPushButton("Restore Selected Backup")
        btn_restore.setObjectName("action_btn")
        btn_cancel = QPushButton("Cancel")
        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_restore)
        vbox.addLayout(btn_box)
        
        btn_restore.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            curr_item = list_widget.currentItem()
            if not curr_item:
                return
            selected_path = curr_item.data(Qt.UserRole)
            
            reply = QMessageBox.question(
                self, "Confirm Backup Restore",
                f"Are you sure you want to restore the database from backup:\n\n{os.path.basename(selected_path)}?\n\nAll current products and categories will be reloaded from this snapshot.",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    self.save_database() # Save current state before restoring
                    
                    tmp_p = DB_PATH + ".tmp"
                    shutil.copy2(selected_path, tmp_p)
                    os.replace(tmp_p, DB_PATH)
                    
                    self.load_database()
                    self.refresh_catalog_tree()
                    self.refresh_site_content_fields()
                    self.compile_site()
                    QMessageBox.information(self, "Restore Complete", "Database restored successfully from backup and website rebuilt!")
                except Exception as e:
                    QMessageBox.critical(self, "Restore Error", f"Failed to restore database from backup: {e}")

    def load_trash_database(self):
        self.trash_items = []
        self.log(f"[DEBUG] Loading trash from: {TRASH_DB_PATH}")
        if os.path.exists(TRASH_DB_PATH):
            try:
                with open(TRASH_DB_PATH, "r", encoding="utf-8") as f:
                    self.trash_items = json.load(f)
                self.log(f"[DEBUG] Loaded {len(self.trash_items)} trash records.")
            except Exception as e:
                self.log(f"[DEBUG] Failed to load trash database: {e}")
                
    def save_trash_database(self):
        os.makedirs(TRASH_DIR, exist_ok=True)
        self.log(f"[DEBUG] Saving trash database to: {TRASH_DB_PATH}")
        tmp_trash_path = TRASH_DB_PATH + ".tmp"
        try:
            with open(tmp_trash_path, "w", encoding="utf-8") as f:
                json.dump(self.trash_items, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_trash_path, TRASH_DB_PATH)
            self.log(f"[DEBUG] Saved {len(self.trash_items)} trash records successfully.")
        except Exception as e:
            self.log(f"[DEBUG] Failed to save trash database: {e}")

    def init_ui(self):
        # Startup validation check
        if not os.path.exists(os.path.join(WORKSPACE_DIR, "index.html")):
            self.prompt_change_web_root()
            
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.create_dashboard_tab()
        self.create_catalog_tab()
        self.create_trash_tab()
        self.create_clients_tab()
        self.create_site_content_tab()
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
    def on_tab_changed(self, index):
        if index == 0:
            self.lbl_categories_count.setText(f"Total Categories: {len(self.categories)}")
            self.lbl_products_count.setText(f"Total Products: {len(self.products)}")
        elif index == 1:
            self.refresh_catalog_tree()
        elif index == 2:
            self.refresh_trash_table()
        elif index == 3:
            self.refresh_clients_table()
        elif index == 4:
            self.refresh_site_content_fields()

    def prompt_change_web_root(self):
        QMessageBox.information(
            self, "Configure Website Root",
            "Please select the root directory of your website (containing index.html)."
        )
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Website Root Folder", WORKSPACE_DIR)
        if selected_dir:
            save_config(selected_dir)
            self.log(f"Website root updated to: {selected_dir}")
            self.load_database()
            if hasattr(self, 'catalog_tree'):
                self.refresh_catalog_tree()
            if hasattr(self, 'trash_tree'):
                self.refresh_trash_table()

    def create_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header Info
        header = QLabel("EcoLuxe Bharat - Static Website Manager")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #50ab3c; padding-bottom: 10px;")
        layout.addWidget(header)
        
        # Stats layout
        stats_layout = QHBoxLayout()
        
        self.lbl_products_count = QLabel(f"Total Products: {len(self.products)}")
        self.lbl_products_count.setStyleSheet("font-size: 16px; background-color: #232323; padding: 20px; border-radius: 6px; border: 1px solid #333;")
        
        self.lbl_categories_count = QLabel(f"Total Categories: {len(self.categories)}")
        self.lbl_categories_count.setStyleSheet("font-size: 16px; background-color: #232323; padding: 20px; border-radius: 6px; border: 1px solid #333;")
        
        stats_layout.addWidget(self.lbl_products_count)
        stats_layout.addWidget(self.lbl_categories_count)
        layout.addLayout(stats_layout)
        
        # Rebuilder and Preview controls
        ctrl_layout = QGroupBox("Website Compiling & Publishing Actions")
        ctrl_box = QHBoxLayout(ctrl_layout)
        
        self.btn_compile = QPushButton("Build Webpages")
        self.btn_compile.setObjectName("action_btn")
        self.btn_compile.setMinimumHeight(45)
        self.btn_compile.clicked.connect(self.compile_site)
        
        self.btn_preview = QPushButton("Launch Site Local Preview")
        self.btn_preview.setMinimumHeight(45)
        self.btn_preview.clicked.connect(self.toggle_preview_server)
        
        self.btn_restore_backup = QPushButton("Restore from Auto-Backup...")
        self.btn_restore_backup.setMinimumHeight(45)
        self.btn_restore_backup.clicked.connect(self.restore_database_from_backup)
        
        self.btn_change_root = QPushButton("Change Web Root")
        self.btn_change_root.setMinimumHeight(45)
        self.btn_change_root.clicked.connect(self.prompt_change_web_root)
        
        ctrl_box.addWidget(self.btn_compile)
        ctrl_box.addWidget(self.btn_preview)
        ctrl_box.addWidget(self.btn_restore_backup)
        ctrl_box.addWidget(self.btn_change_root)
        
        layout.addWidget(ctrl_layout)
        
        # Log Output terminal
        log_group = QGroupBox("System Output Console Log")
        log_layout = QVBoxLayout(log_group)
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setStyleSheet("font-family: 'Courier New'; background-color: #0b0b0b; color: #a1e292;")
        log_layout.addWidget(self.txt_console)
        
        layout.addWidget(log_group)
        
        self.log("EcoLuxe Bharat Website Manager loaded successfully.")
        self.log(f"Current workspace: {WORKSPACE_DIR}")
        
        self.tabs.addTab(widget, "Dashboard")

    def create_catalog_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter & Search header
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search catalog items by name or model...")
        self.search_input.textChanged.connect(self.refresh_catalog_tree)
        
        self.filter_cat_selector = QComboBox()
        self.filter_cat_selector.addItem("All Categories", "")
        for cat in self.categories:
            self.filter_cat_selector.addItem(cat.get("title", ""), cat.get("slug", ""))
        self.filter_cat_selector.currentIndexChanged.connect(self.refresh_catalog_tree)
        
        filter_layout.addWidget(self.search_input, 2)
        filter_layout.addWidget(self.filter_cat_selector, 1)
        
        layout.addLayout(filter_layout)
        
        # Unified Catalog Tree Widget
        self.catalog_tree = QTreeWidget()
        self.catalog_tree.setHeaderLabels(["Item Name / Title", "Model / URL Key", "Description"])
        self.catalog_tree.setColumnWidth(0, 300)
        self.catalog_tree.setColumnWidth(1, 180)
        self.catalog_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.catalog_tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.catalog_tree.itemSelectionChanged.connect(self.on_catalog_selection_changed)
        self.catalog_tree.itemDoubleClicked.connect(self.on_catalog_item_double_clicked)
        
        layout.addWidget(self.catalog_tree)
        
        # Controls Layout
        btn_layout = QHBoxLayout()
        
        self.btn_add_item = QPushButton("Add New Item")
        self.btn_add_item.setObjectName("action_btn")
        self.btn_add_item.clicked.connect(self.on_add_item_clicked)
        
        self.btn_edit_item = QPushButton("Edit")
        self.btn_edit_item.clicked.connect(self.on_edit_item_clicked)
        
        self.btn_delete_multiple = QPushButton("Select Multiple")
        self.btn_delete_multiple.setCheckable(True)
        self.btn_delete_multiple.toggled.connect(self.toggle_multiple_delete_mode)
        
        self.btn_rearrange = QPushButton("Rearrange Items")
        self.btn_rearrange.clicked.connect(self.open_rearrange_dialog)
        
        self.btn_del_item = QPushButton("Delete")
        self.btn_del_item.setObjectName("danger_btn")
        self.btn_del_item.clicked.connect(self.on_delete_item_clicked)
        
        btn_layout.addWidget(self.btn_add_item)
        btn_layout.addWidget(self.btn_edit_item)
        btn_layout.addWidget(self.btn_delete_multiple)
        btn_layout.addWidget(self.btn_rearrange)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_del_item)
        
        layout.addLayout(btn_layout)
        self.refresh_catalog_tree()
        self.tabs.addTab(widget, "Catalog Manager")

    def refresh_catalog_tree(self):
        self.catalog_tree.blockSignals(True)
        self.catalog_tree.clear()
        
        search_txt = self.search_input.text().lower().strip()
        selected_cat = self.filter_cat_selector.currentData()
        
        # Populate Category nodes
        for cat in self.categories:
            cat_slug = cat.get("slug", "")
            cat_title = cat.get("title", "")
            cat_desc = cat.get("description", "")
            
            # Apply category filter
            if selected_cat and cat_slug != selected_cat:
                continue
                
            # Filter matches category itself
            cat_match = (not search_txt) or (search_txt in cat_title.lower() or search_txt in cat_slug.lower())
            
            # Find matching products under this category
            matching_products = []
            for prod in self.products:
                if prod.get("category_slug", "") != cat_slug:
                    continue
                prod_title = prod.get("title", "").lower()
                prod_model = prod.get("model", "").lower()
                
                prod_search_match = (not search_txt) or (search_txt in prod_title or search_txt in prod_model)
                if prod_search_match:
                    matching_products.append(prod)
            
            # If search text is set, only show category if it matches search OR has matching products
            if search_txt and not (cat_match or matching_products):
                continue
                
            # Add category item
            cat_item = QTreeWidgetItem(self.catalog_tree)
            cat_item.setText(0, cat_title)
            cat_item.setText(1, cat_slug) # Directory Name
            cat_item.setText(2, cat_desc)
            cat_item.setData(0, Qt.UserRole, {"type": "category", "data": cat})
            cat_item.setFont(0, QFont("Segoe UI", 12, QFont.Bold))
            cat_item.setForeground(0, QColor("#50ab3c"))
            
            # Add product items under category
            prods_to_show = matching_products if search_txt else [p for p in self.products if p.get("category_slug", "") == cat_slug]
            for prod in prods_to_show:
                prod_item = QTreeWidgetItem(cat_item)
                prod_item.setText(0, prod.get("title", ""))
                prod_item.setText(1, prod.get("model", ""))
                prod_item.setText(2, prod.get("description", ""))
                prod_item.setData(0, Qt.UserRole, {"type": "product", "data": prod})
                prod_item.setFont(0, QFont("Segoe UI", 11))
                
            # Keep categories expanded only if searching, otherwise collapsed
            if search_txt:
                cat_item.setExpanded(True)
            else:
                cat_item.setExpanded(False)
            
        # Re-apply multiple delete checkboxes if toggled
        if self.btn_delete_multiple.isChecked():
            self.enable_tree_checkboxes(True)
            
        self.catalog_tree.blockSignals(False)
        self.on_catalog_selection_changed()

    def on_catalog_selection_changed(self):
        selected = self.catalog_tree.selectedItems()
        if self.btn_delete_multiple.isChecked():
            # If in multi-delete mode, disable editing and moving
            self.btn_edit_item.setEnabled(False)
            self.btn_del_item.setEnabled(True)
            self.btn_del_item.setText("Delete Checked Items")
            return
            
        if not selected:
            self.btn_edit_item.setEnabled(False)
            self.btn_edit_item.setText("Edit")
            self.btn_del_item.setEnabled(False)
            self.btn_del_item.setText("Delete")
            return
            
        item = selected[0]
        user_data = item.data(0, Qt.UserRole)
        if not user_data:
            self.btn_edit_item.setEnabled(False)
            self.btn_del_item.setEnabled(False)
            return
            
        item_type = user_data["type"]
        if item_type == "category":
            self.btn_edit_item.setEnabled(True)
            self.btn_edit_item.setText("Edit Category")
            self.btn_del_item.setEnabled(True)
            self.btn_del_item.setText("Delete Category")
            
        elif item_type == "product":
            self.btn_edit_item.setEnabled(True)
            self.btn_edit_item.setText("Edit Product")
            self.btn_del_item.setEnabled(True)
            self.btn_del_item.setText("Delete Product")

    def on_catalog_item_double_clicked(self, item, column):
        user_data = item.data(0, Qt.UserRole)
        if not user_data:
            return
        if user_data["type"] == "category":
            self.edit_category()
        elif user_data["type"] == "product":
            self.edit_product()

    def on_add_item_clicked(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Catalog Item")
        dialog.setMinimumWidth(320)
        layout = QVBoxLayout(dialog)
        
        lbl = QLabel("Which type of item would you like to create?")
        lbl.setStyleSheet("padding: 10px 0px; font-weight: bold;")
        layout.addWidget(lbl)
        
        btn_cat = QPushButton("Add New Category")
        btn_cat.setMinimumHeight(40)
        btn_cat.clicked.connect(lambda: dialog.done(1))
        
        btn_prod = QPushButton("Add New Product")
        btn_prod.setMinimumHeight(40)
        btn_prod.clicked.connect(lambda: dialog.done(2))
        
        layout.addWidget(btn_cat)
        layout.addWidget(btn_prod)
        
        res = dialog.exec()
        if res == 1:
            self.add_category()
        elif res == 2:
            self.add_product()

    def on_edit_item_clicked(self):
        selected = self.catalog_tree.selectedItems()
        if not selected:
            return
        user_data = selected[0].data(0, Qt.UserRole)
        if not user_data:
            return
        if user_data["type"] == "category":
            self.edit_category()
        elif user_data["type"] == "product":
            self.edit_product()

    def on_delete_item_clicked(self):
        if self.btn_delete_multiple.isChecked():
            self.batch_delete_checked()
        else:
            selected = self.catalog_tree.selectedItems()
            if not selected:
                return
            user_data = selected[0].data(0, Qt.UserRole)
            if not user_data:
                return
            if user_data["type"] == "category":
                self.delete_category()
            elif user_data["type"] == "product":
                self.delete_product()

    def toggle_multiple_delete_mode(self, checked):
        self.catalog_tree.clearSelection()
        self.enable_tree_checkboxes(checked)
        self.on_catalog_selection_changed()

    def enable_tree_checkboxes(self, enabled):
        iterator = QTreeWidgetItemIterator(self.catalog_tree)
        while iterator.value():
            item = iterator.value()
            if enabled:
                item.setCheckState(0, Qt.Unchecked)
            else:
                item.setData(0, Qt.CheckStateRole, None)
            iterator += 1

    def batch_delete_checked(self):
        checked_categories = []
        checked_products = []
        
        iterator = QTreeWidgetItemIterator(self.catalog_tree)
        while iterator.value():
            item = iterator.value()
            if item.checkState(0) == Qt.Checked:
                data = item.data(0, Qt.UserRole)
                if data:
                    if data["type"] == "category":
                        checked_categories.append(data["data"])
                    elif data["type"] == "product":
                        checked_products.append(data["data"])
            iterator += 1
            
        if not checked_categories and not checked_products:
            QMessageBox.information(self, "No Checked Items", "No items have been checked for deletion.")
            return
            
        num_cats = len(checked_categories)
        num_prods = len(checked_products)
        msg = f"You are about to move {num_cats} categories and {num_prods} products to the Trash Bin."
        if num_cats > 0:
            msg += "\nWarning: Trashing a category will automatically trash all its products as well."
        msg += "\n\nDo you want to proceed?"
        
        confirm = QMessageBox.question(
            self, "Confirm Batch Delete",
            msg, QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return
            
        confirm2 = QMessageBox.question(
            self, "Are you absolutely sure?",
            "This action will move all selected items and assets to the Trash. Please confirm.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm2 == QMessageBox.No:
            return
            
        trashed_cat_slugs = {c["slug"] for c in checked_categories}
        
        for cat in checked_categories:
            self.trash_category_item(cat)
            
        for prod in checked_products:
            if prod["category_slug"] not in trashed_cat_slugs:
                self.trash_product_item(prod)
                
        self.save_database()
        self.refresh_catalog_tree()
        self.lbl_categories_count.setText(f"Total Categories: {len(self.categories)}")
        self.lbl_products_count.setText(f"Total Products: {len(self.products)}")
        self.refresh_trash_table()
        
        self.btn_delete_multiple.setChecked(False)
        self.compile_site()

    def open_rearrange_dialog(self):
        dialog = RearrangeDialog(self, self.categories, self.products)
        if dialog.exec() == QDialog.Accepted:
            result = dialog.saved_order
            if not result:
                return
                
            if result["type"] == "categories":
                order = result["order"]
                # Sort categories matching order
                new_categories = []
                for slug in order:
                    cat = next((c for c in self.categories if c["slug"] == slug), None)
                    if cat:
                        new_categories.append(cat)
                self.categories = new_categories
                self.save_database()
                self.refresh_catalog_tree()
                self.log("Reordered categories sequence successfully.")
                self.compile_site(show_dialog=False)
                
            elif result["type"] == "products":
                cat_slug = result["category_slug"]
                order = result["order"]
                # Get non-category products
                other_prods = [p for p in self.products if p.get("category_slug") != cat_slug]
                # Get this category's products ordered matching list
                ordered_prods = []
                for p_id in order:
                    prod = next((p for p in self.products if p["id"] == p_id), None)
                    if prod:
                        ordered_prods.append(prod)
                
                # Reconstruct flat products preserving position of category
                new_prods = []
                inserted = False
                for p in self.products:
                    if p.get("category_slug") == cat_slug:
                        if not inserted:
                            new_prods.extend(ordered_prods)
                            inserted = True
                    else:
                        new_prods.append(p)
                self.products = new_prods
                self.save_database()
                self.refresh_catalog_tree()
                self.select_product_in_tree(order[0] if order else None)
                self.log(f"Reordered products inside category '{cat_slug}' successfully.")
                self.compile_site(show_dialog=False)

    def select_product_in_tree(self, prod_id):
        iterator = QTreeWidgetItemIterator(self.catalog_tree)
        while iterator.value():
            item = iterator.value()
            data = item.data(0, Qt.UserRole)
            if data and data.get("type") == "product" and data["data"]["id"] == prod_id:
                self.catalog_tree.setCurrentItem(item)
                item.setSelected(True)
                if item.parent():
                    item.parent().setExpanded(True)
                break
            iterator += 1

    # --- Category CRUD ---
    def add_category(self):
        dialog = CategoryDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Check duplicate slug
            if any(c.get("slug", "") == data["slug"] for c in self.categories):
                QMessageBox.warning(self, "Validation Error", f"A category with slug '{data['slug']}' already exists.")
                return
                
            if not data["slug"] or not data["title"]:
                QMessageBox.warning(self, "Validation Error", "Category slug and title cannot be empty.")
                return
                
            # Copy image if selected and not already in img/categories
            if data["image"] and not data["image"].startswith("img/categories/"):
                old_img = data["image"]
                ext = os.path.splitext(old_img)[1] or ".png"
                new_img_rel = f"img/categories/{data['slug']}{ext}"
                new_img_abs = os.path.join(WORKSPACE_DIR, new_img_rel)
                
                try:
                    shutil.copy2(old_img, new_img_abs)
                    data["image"] = new_img_rel
                except Exception as e:
                    self.log(f"Error copying category image: {e}")
                    
            # Stage & reindex showcase images
            sc_dir_rel = f"img/categories/showcase/{data['slug']}"
            prefix = f"{data['slug']}-showcase"
            data["showcase_images"] = stage_and_reindex_images(
                data.get("showcase_images", []),
                sc_dir_rel,
                prefix,
                WORKSPACE_DIR,
                TRASH_DIR,
                log_func=self.log
            )

            self.categories.append(data)
            self.save_database()
            self.refresh_catalog_tree()
            # Select new category in tree
            for i in range(self.catalog_tree.topLevelItemCount()):
                item = self.catalog_tree.topLevelItem(i)
                if item.text(1) == data["slug"]:
                    self.catalog_tree.setCurrentItem(item)
                    item.setSelected(True)
                    break
            self.lbl_categories_count.setText(f"Total Categories: {len(self.categories)}")
            self.log(f"Added category: {data['title']} ({data['slug']})")
            self.compile_site()

    def edit_category(self):
        selected = self.catalog_tree.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a category to edit.")
            return
            
        item = selected[0]
        user_data = item.data(0, Qt.UserRole)
        if not user_data or user_data["type"] != "category":
            return
            
        cat = user_data["data"]
        slug = cat["slug"]
            
        dialog = CategoryDialog(self, cat)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Check if main category image changed and clean up old main image if different extension
            old_main_img_rel = cat.get("image", "")
            if data["image"] and not data["image"].startswith("img/categories/"):
                old_img = data["image"]
                ext = os.path.splitext(old_img)[1] or ".png"
                new_img_rel = f"img/categories/{slug}{ext}"
                new_img_abs = os.path.join(WORKSPACE_DIR, new_img_rel)
                
                try:
                    shutil.copy2(old_img, new_img_abs)
                    data["image"] = new_img_rel
                except Exception as e:
                    self.log(f"Error copying category image: {e}")

            if old_main_img_rel and data["image"] != old_main_img_rel:
                old_main_abs = os.path.join(WORKSPACE_DIR, old_main_img_rel)
                if os.path.exists(old_main_abs) and os.path.abspath(old_main_abs) != os.path.abspath(os.path.join(WORKSPACE_DIR, data["image"])):
                    trash_img_dir = os.path.join(TRASH_DIR, "images")
                    os.makedirs(trash_img_dir, exist_ok=True)
                    dest_abs = os.path.join(trash_img_dir, os.path.basename(old_main_img_rel))
                    try:
                        shutil.move(old_main_abs, dest_abs)
                        self.log(f"Moved replaced main category image {old_main_img_rel} to trash/images/")
                    except Exception as e:
                        self.log(f"Error trashing main category image: {e}")
            
            # Stage & reindex showcase images
            sc_dir_rel = f"img/categories/showcase/{slug}"
            prefix = f"{slug}-showcase"
            final_showcase = stage_and_reindex_images(
                data.get("showcase_images", []),
                sc_dir_rel,
                prefix,
                WORKSPACE_DIR,
                TRASH_DIR,
                log_func=self.log
            )
            
            # Update values
            actual_cat = next((c for c in self.categories if c["slug"] == slug), None)
            if actual_cat:
                actual_cat["title"] = data["title"]
                actual_cat["description"] = data["description"]
                actual_cat["image"] = data["image"]
                actual_cat["showcase_images"] = final_showcase

            # Clean up orphan images in category showcase directory
            sc_dir_abs = os.path.join(WORKSPACE_DIR, "img", "categories", "showcase", slug)
            if os.path.exists(sc_dir_abs):
                final_basenames = [os.path.basename(img["src"]) for img in final_showcase]
                for filename in os.listdir(sc_dir_abs):
                    file_abs = os.path.join(sc_dir_abs, filename)
                    if os.path.isfile(file_abs) and filename not in final_basenames:
                        trash_img_dir = os.path.join(TRASH_DIR, "images")
                        os.makedirs(trash_img_dir, exist_ok=True)
                        dest_abs = os.path.join(trash_img_dir, filename)
                        if os.path.exists(dest_abs):
                            name_part, ext_part = os.path.splitext(filename)
                            dest_abs = os.path.join(trash_img_dir, f"{name_part}_{int(time.time())}{ext_part}")
                        try:
                            shutil.move(file_abs, dest_abs)
                            self.log(f"Moved removed showcase image {filename} to trash/images/")
                        except Exception as e:
                            self.log(f"Error trashing removed showcase image {filename}: {e}")
            
            self.save_database()
            self.refresh_catalog_tree()
            # Select edited category
            for i in range(self.catalog_tree.topLevelItemCount()):
                item = self.catalog_tree.topLevelItem(i)
                if item.text(1) == slug:
                    self.catalog_tree.setCurrentItem(item)
                    item.setSelected(True)
                    break
            self.log(f"Updated category: {cat['title']}")
            self.compile_site()

    def delete_category(self):
        selected_items = self.catalog_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a category to delete.")
            return
        item = selected_items[0]
        user_data = item.data(0, Qt.UserRole)
        if not user_data or user_data["type"] != "category":
            return
            
        cat = user_data["data"]
        slug = cat["slug"]
        
        count = sum(1 for p in self.products if p.get("category_slug", "") == slug)
        
        # Stage 1 Warning
        msg = f"Are you sure you want to delete category '{cat['title']}'? (This will move it to the Trash Bin)"
        if count > 0:
            msg += f"\nWarning: This category has {count} associated products which will also be trashed."
            
        confirm = QMessageBox.question(
            self, "Confirm Delete (Stage 1)",
            msg, QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return
            
        # Stage 2 Double Confirm Warning
        confirm2 = QMessageBox.question(
            self, "Are you absolutely sure? (Stage 2)",
            f"Please double confirm: Are you absolutely sure you want to delete category '{cat['title']}' and all its products?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm2 == QMessageBox.No:
            return
                
        self.trash_category_item(cat)
        self.save_database()
        self.refresh_catalog_tree()
        self.lbl_categories_count.setText(f"Total Categories: {len(self.categories)}")
        self.lbl_products_count.setText(f"Total Products: {len(self.products)}")
        self.refresh_trash_table()
        self.compile_site()

    def trash_category_item(self, cat):
        slug = cat["slug"]
        trash_id = f"cat_{slug}_{int(time.time())}"
        
        trash_cat_dir = os.path.join(TRASH_DIR, "categories", trash_id)
        os.makedirs(trash_cat_dir, exist_ok=True)
        
        cat_img_rel = cat.get("image", "")
        if cat_img_rel:
            src_abs = os.path.join(WORKSPACE_DIR, cat_img_rel)
            if os.path.exists(src_abs):
                filename = os.path.basename(cat_img_rel)
                dest_abs = os.path.join(trash_cat_dir, filename)
                try:
                    shutil.move(src_abs, dest_abs)
                    self.log(f"Moved category image {cat_img_rel} to trash")
                except Exception as e:
                    self.log(f"Error trashing category image {cat_img_rel}: {e}")
                    
        sc_images_rel = cat.get("showcase_images", [])
        if sc_images_rel:
            trash_sc_dir = os.path.join(trash_cat_dir, "showcase")
            os.makedirs(trash_sc_dir, exist_ok=True)
            for sc_img in sc_images_rel:
                src_rel = sc_img["src"]
                if src_rel.startswith("img/categories/showcase/"):
                    src_abs = os.path.join(WORKSPACE_DIR, src_rel)
                    if os.path.exists(src_abs):
                        filename = os.path.basename(src_rel)
                        dest_abs = os.path.join(trash_sc_dir, filename)
                        try:
                            shutil.move(src_abs, dest_abs)
                        except Exception as e:
                            self.log(f"Error trashing category showcase image: {e}")
                            
            sc_dir_abs = os.path.join(WORKSPACE_DIR, "img", "categories", "showcase", slug)
            if os.path.exists(sc_dir_abs) and not os.listdir(sc_dir_abs):
                try:
                    os.rmdir(sc_dir_abs)
                except Exception:
                    pass
                    
        associated_prods = [p for p in self.products if p.get("category_slug", "") == slug]
        associated_ids = []
        for prod in associated_prods:
            associated_ids.append(prod["id"])
            self.trash_product_item(prod, parent_trash_id=trash_id)
            
        html_rel = f"categories/{slug}.html"
        html_abs = os.path.join(WORKSPACE_DIR, html_rel)
        if os.path.exists(html_abs):
            try:
                os.remove(html_abs)
                self.log(f"Removed category page: {html_rel}")
            except Exception as e:
                self.log(f"Error removing category page html: {e}")
                
        metadata_path = os.path.join(trash_cat_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=4)
            
        record = {
            "trash_id": trash_id,
            "type": "category",
            "id": slug,
            "name": cat["title"],
            "deleted_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metadata_path": os.path.relpath(metadata_path, SCRIPT_DIR),
            "associated_product_ids": associated_ids
        }
        self.trash_items.append(record)
        self.save_trash_database()
        
        actual_cat = next((c for c in self.categories if c["slug"] == slug), None)
        if actual_cat:
            self.categories.remove(actual_cat)
        self.log(f"Moved category '{cat['title']}' to Trash Bin.")

    # --- Product CRUD ---
    def add_product(self):
        if not self.categories:
            QMessageBox.warning(self, "No Categories", "Please create at least one category before adding products.")
            return
            
        dialog = ProductDialog(self, product=None, categories=self.categories)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Validate ID
            if any(p.get("id", "") == data["id"] for p in self.products):
                QMessageBox.warning(self, "Validation Error", f"A product with ID '{data['id']}' already exists.")
                return
                
            if not data["id"] or not data["title"] or not data["model"]:
                QMessageBox.warning(self, "Validation Error", "Product ID, Model, and Title cannot be empty.")
                return
                
            # Stage & reindex product images
            cat_slug = data.get("category_slug", "uncategorized")
            prod_dir_rel = f"img/products/{cat_slug}/{data['id']}"
            data["images"] = stage_and_reindex_images(
                data["images"],
                prod_dir_rel,
                data['id'],
                WORKSPACE_DIR,
                TRASH_DIR,
                log_func=self.log
            )
                            
            self.products.append(data)
            self.save_database()
            self.refresh_catalog_tree()
            self.select_product_in_tree(data["id"])
            self.lbl_products_count.setText(f"Total Products: {len(self.products)}")
            self.log(f"Added product: {data['title']} ({data['model']})")
            self.compile_site()

    def edit_product(self):
        selected = self.catalog_tree.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a product to edit.")
            return
            
        item = selected[0]
        user_data = item.data(0, Qt.UserRole)
        if not user_data or user_data["type"] != "product":
            return
            
        prod = user_data["data"]
        prod_id = prod["id"]
            
        dialog = ProductDialog(self, product=prod, categories=self.categories)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            cat_slug = data.get("category_slug", "uncategorized")
            old_cat_slug = prod.get("category_slug", "")
            
            # Clean up old category HTML and image folder if migrated
            if old_cat_slug and old_cat_slug != cat_slug:
                # Remove old compiled product HTML
                old_html_rel = f"products/{old_cat_slug}/{prod_id}.html"
                old_html_abs = os.path.join(WORKSPACE_DIR, old_html_rel)
                if os.path.exists(old_html_abs):
                    try:
                        os.remove(old_html_abs)
                    except Exception:
                        pass
                
                # Move old image folder contents to new category folder if existing
                old_img_dir = os.path.join(WORKSPACE_DIR, "img", "products", old_cat_slug, prod_id)
                new_img_dir = os.path.join(WORKSPACE_DIR, "img", "products", cat_slug, prod_id)
                if os.path.exists(old_img_dir):
                    os.makedirs(new_img_dir, exist_ok=True)
                    for fn in os.listdir(old_img_dir):
                        try:
                            shutil.move(os.path.join(old_img_dir, fn), os.path.join(new_img_dir, fn))
                        except Exception:
                            pass
                    try:
                        os.rmdir(old_img_dir)
                    except Exception:
                        pass

            # Stage & reindex product images
            prod_dir_rel = f"img/products/{cat_slug}/{prod_id}"
            structured_images = stage_and_reindex_images(
                data["images"],
                prod_dir_rel,
                prod_id,
                WORKSPACE_DIR,
                TRASH_DIR,
                log_func=self.log
            )

            # Update product
            actual_prod = next((p for p in self.products if p["id"] == prod_id), None)
            if actual_prod:
                actual_prod.update(data)
                actual_prod["images"] = structured_images
            
            self.save_database()
            self.refresh_catalog_tree()
            self.select_product_in_tree(prod_id)
            self.log(f"Updated product: {data['title']}")
            self.compile_site()

    def delete_product(self):
        selected_items = self.catalog_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a product to delete.")
            return
        item = selected_items[0]
        user_data = item.data(0, Qt.UserRole)
        if not user_data or user_data["type"] != "product":
            return
        prod = user_data["data"]
            
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete product '{prod['title']}'? (This will move it to the Trash Bin)",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.trash_product_item(prod)
            self.save_database()
            self.refresh_catalog_tree()
            self.lbl_products_count.setText(f"Total Products: {len(self.products)}")
            self.refresh_trash_table()
            self.compile_site()

    def trash_product_item(self, prod, parent_trash_id=None):
        prod_id = prod["id"]
        cat_slug = prod.get("category_slug", "uncategorized")
        trash_id = f"prod_{prod_id}_{int(time.time())}"
        
        trash_prod_dir = os.path.join(TRASH_DIR, "products", trash_id)
        trash_images_dir = os.path.join(trash_prod_dir, "images")
        os.makedirs(trash_images_dir, exist_ok=True)
        
        for img in prod.get("images", []):
            src_rel = img["src"]
            src_abs = os.path.join(WORKSPACE_DIR, src_rel)
            if os.path.exists(src_abs):
                filename = os.path.basename(src_rel)
                dest_abs = os.path.join(trash_images_dir, filename)
                try:
                    shutil.move(src_abs, dest_abs)
                    self.log(f"Moved image {src_rel} to trash")
                except Exception as e:
                    self.log(f"Error trashing product image {src_rel}: {e}")
                    
        model_dir_abs = os.path.join(WORKSPACE_DIR, "img", "products", cat_slug, prod_id)
        if os.path.exists(model_dir_abs) and not os.listdir(model_dir_abs):
            try:
                os.rmdir(model_dir_abs)
            except Exception:
                pass
                
        html_rel = f"products/{cat_slug}/{prod_id}.html"
        html_abs = os.path.join(WORKSPACE_DIR, html_rel)
        if os.path.exists(html_abs):
            try:
                os.remove(html_abs)
                self.log(f"Removed product page: {html_rel}")
            except Exception as e:
                self.log(f"Error removing product page {html_rel}: {e}")
                
        metadata_path = os.path.join(trash_prod_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(prod, f, indent=4)
            
        record = {
            "trash_id": trash_id,
            "type": "product",
            "id": prod_id,
            "name": prod["title"],
            "deleted_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metadata_path": os.path.relpath(metadata_path, SCRIPT_DIR),
            "original_images": prod.get("images", []),
            "parent_trash_id": parent_trash_id
        }
        self.trash_items.append(record)
        self.save_trash_database()
        
        actual_prod = next((p for p in self.products if p["id"] == prod_id), None)
        if actual_prod:
            self.products.remove(actual_prod)
        self.log(f"Moved product '{prod['title']}' to Trash Bin.")

    def create_trash_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QLabel("Trash Bin - Trashed Categories & Products")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #e06c75; padding-bottom: 10px;")
        layout.addWidget(header)
        
        main_layout = QHBoxLayout()
        
        self.trash_tree = QTreeWidget()
        self.trash_tree.setHeaderLabels(["Item Name", "Original Location / Type", "Deleted Date"])
        self.trash_tree.setColumnWidth(0, 300)
        self.trash_tree.setColumnWidth(1, 200)
        self.trash_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.trash_tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.trash_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.trash_tree.itemSelectionChanged.connect(self.on_trash_selection_changed)
        
        btn_layout = QVBoxLayout()
        self.btn_restore = QPushButton("Restore Selected")
        self.btn_restore.setMinimumHeight(40)
        self.btn_restore.clicked.connect(self.restore_trash_item)
        
        self.btn_delete_perm = QPushButton("Delete Permanently")
        self.btn_delete_perm.setMinimumHeight(40)
        self.btn_delete_perm.setStyleSheet("background-color: #722424;")
        self.btn_delete_perm.clicked.connect(self.delete_permanently)
        
        self.btn_empty_trash = QPushButton("Empty Trash Bin")
        self.btn_empty_trash.setMinimumHeight(40)
        self.btn_empty_trash.setStyleSheet("background-color: #923434;")
        self.btn_empty_trash.clicked.connect(self.empty_trash_bin)
        
        self.btn_refresh_trash = QPushButton("Refresh List")
        self.btn_refresh_trash.setMinimumHeight(40)
        self.btn_refresh_trash.clicked.connect(self.refresh_trash_table)
        
        btn_layout.addWidget(self.btn_restore)
        btn_layout.addWidget(self.btn_delete_perm)
        btn_layout.addWidget(self.btn_empty_trash)
        btn_layout.addWidget(self.btn_refresh_trash)
        btn_layout.addStretch()
        
        main_layout.addWidget(self.trash_tree, 4)
        main_layout.addLayout(btn_layout, 1)
        
        layout.addLayout(main_layout)
        self.refresh_trash_table()
        self.tabs.addTab(widget, "Trash Bin")

    def refresh_trash_table(self):
        self.trash_tree.clear()
        self.load_trash_database()
        
        cat_records = [x for x in self.trash_items if x.get("type") == "category"]
        prod_records = [x for x in self.trash_items if x.get("type") == "product"]
        
        self.log(f"[DEBUG] refresh_trash_table: {len(cat_records)} categories, {len(prod_records)} products.")
        for p in prod_records:
            self.log(f"  [DEBUG] Trashed product: id={p.get('id')}, name={p.get('name')}, parent_trash_id={p.get('parent_trash_id')}")
            
        cat_nodes = {}
        for rec in cat_records:
            cat_item = QTreeWidgetItem(self.trash_tree)
            cat_item.setText(0, rec.get("name", ""))
            cat_item.setText(1, f"Category (slug: {rec.get('id', '')})")
            cat_item.setText(2, rec.get("deleted_date", ""))
            cat_item.setData(0, Qt.UserRole, rec)
            cat_item.setForeground(0, QColor("#e06c75"))
            cat_item.setFont(0, QFont("Segoe UI", 12, QFont.Bold))
            cat_nodes[rec.get("trash_id")] = cat_item
            
            # Find child products whose parent_trash_id matches this category's trash_id
            child_prods = [p for p in prod_records if p.get("parent_trash_id") == rec.get("trash_id")]
            for p_rec in child_prods:
                p_item = QTreeWidgetItem(cat_item)
                p_item.setText(0, p_rec.get("name", ""))
                p_item.setText(1, "Product")
                p_item.setText(2, p_rec.get("deleted_date", ""))
                p_item.setData(0, Qt.UserRole, p_rec)
                
            cat_item.setExpanded(True)
            
        # Find products whose parent_trash_id is None (deleted individually)
        individual_prods = [p for p in prod_records if not p.get("parent_trash_id")]
        
        if individual_prods:
            virtual_item = QTreeWidgetItem(self.trash_tree)
            virtual_item.setText(0, "Individually Trashed Products")
            virtual_item.setText(1, "Virtual Folder")
            virtual_item.setText(2, "")
            v_font = QFont("Segoe UI", 12, QFont.Bold)
            v_font.setItalic(True)
            virtual_item.setFont(0, v_font)
            virtual_item.setForeground(0, QColor("#e5c07b"))
            virtual_item.setForeground(1, QColor("#e5c07b"))
            virtual_item.setForeground(2, QColor("#e5c07b"))
            
            for p_rec in individual_prods:
                p_item = QTreeWidgetItem(virtual_item)
                p_item.setText(0, p_rec.get("name", ""))
                
                cat_slug = p_rec.get("category_slug", "")
                if not cat_slug:
                    meta_rel = p_rec.get("metadata_path", "")
                    if meta_rel:
                        meta_abs = os.path.join(SCRIPT_DIR, meta_rel)
                        if os.path.exists(meta_abs):
                            try:
                                with open(meta_abs, "r", encoding="utf-8") as f:
                                    meta_data = json.load(f)
                                    cat_slug = meta_data.get("category_slug", "")
                            except Exception:
                                pass
                cat_str = f"Product (Category: {cat_slug})" if cat_slug else "Product"
                p_item.setText(1, cat_str)
                p_item.setText(2, p_rec.get("deleted_date", ""))
                p_item.setData(0, Qt.UserRole, p_rec)
                p_item.setForeground(0, QColor("#e0e0e0"))
                p_item.setForeground(1, QColor("#e0e0e0"))
                p_item.setForeground(2, QColor("#e0e0e0"))
                
            virtual_item.setExpanded(True)

    def on_trash_selection_changed(self):
        selected_items = self.trash_tree.selectedItems()
        records = []
        for item in selected_items:
            rec = item.data(0, Qt.UserRole)
            if rec and rec not in records:
                records.append(rec)
        has_sel = len(records) > 0
        self.btn_restore.setEnabled(has_sel)
        self.btn_delete_perm.setEnabled(has_sel)

    def restore_single_trash_record(self, record):
        if not record or record not in self.trash_items:
            return False
            
        item_type = record.get("type")
        metadata_abs = os.path.join(SCRIPT_DIR, record.get("metadata_path", ""))
        if not os.path.exists(metadata_abs):
            self.log(f"Error: Missing metadata file for trashed item {record.get('name')}")
            return False

        try:
            with open(metadata_abs, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception as e:
            self.log(f"Error reading metadata for {record.get('name')}: {e}")
            return False

        if item_type == "product":
            cat_slug = metadata.get("category_slug", "")
            if not any(c["slug"] == cat_slug for c in self.categories):
                self.log(f"Restore skipped for product '{metadata.get('title')}': category '{cat_slug}' does not exist.")
                return False
                
            trash_images_dir = os.path.join(os.path.dirname(metadata_abs), "images")
            for img in record.get("original_images", []):
                src_path = img["src"]
                filename = os.path.basename(src_path)
                trash_img_abs = os.path.join(trash_images_dir, filename)
                dest_img_abs = os.path.join(WORKSPACE_DIR, src_path)
                if os.path.exists(trash_img_abs):
                    try:
                        os.makedirs(os.path.dirname(dest_img_abs), exist_ok=True)
                        shutil.move(trash_img_abs, dest_img_abs)
                    except Exception as e:
                        self.log(f"Error restoring image {src_path}: {e}")

            if not any(p["id"] == metadata["id"] for p in self.products):
                self.products.append(metadata)
            self.log(f"Restored product: {metadata['title']} ({metadata.get('model', '')})")

        elif item_type == "category":
            trash_folder = os.path.dirname(metadata_abs)
            cat_img_rel = metadata.get("image", "")
            if cat_img_rel:
                filename = os.path.basename(cat_img_rel)
                trash_img_abs = os.path.join(trash_folder, filename)
                dest_img_abs = os.path.join(WORKSPACE_DIR, cat_img_rel)
                if os.path.exists(trash_img_abs):
                    try:
                        os.makedirs(os.path.dirname(dest_img_abs), exist_ok=True)
                        shutil.move(trash_img_abs, dest_img_abs)
                    except Exception as e:
                        self.log(f"Error restoring category image: {e}")

            trash_sc_dir = os.path.join(trash_folder, "showcase")
            for sc_img in metadata.get("showcase_images", []):
                src_rel = sc_img["src"]
                if src_rel.startswith("img/categories/showcase/"):
                    filename = os.path.basename(src_rel)
                    trash_img_abs = os.path.join(trash_sc_dir, filename)
                    dest_img_abs = os.path.join(WORKSPACE_DIR, src_rel)
                    if os.path.exists(trash_img_abs):
                        try:
                            os.makedirs(os.path.dirname(dest_img_abs), exist_ok=True)
                            shutil.move(trash_img_abs, dest_img_abs)
                        except Exception as e:
                            self.log(f"Error restoring category showcase image: {e}")

            if not any(c["slug"] == metadata["slug"] for c in self.categories):
                self.categories.append(metadata)
            self.log(f"Restored category: {metadata['title']} ({metadata['slug']})")

            # Restore associated child products automatically if present
            associated_trashed = [
                x for x in list(self.trash_items)
                if x.get("type") == "product" and x.get("parent_trash_id") == record.get("trash_id")
            ]
            for prod_rec in associated_trashed:
                self.restore_single_trash_record(prod_rec)

        trash_dir_abs = os.path.dirname(metadata_abs)
        if os.path.exists(trash_dir_abs):
            try:
                shutil.rmtree(trash_dir_abs)
            except Exception as e:
                self.log(f"Error removing trash folder: {e}")

        if record in self.trash_items:
            self.trash_items.remove(record)
        return True

    def restore_trash_item(self):
        selected_items = self.trash_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select one or more trashed items to restore.")
            return

        records = []
        for item in selected_items:
            rec = item.data(0, Qt.UserRole)
            if rec and rec not in records:
                records.append(rec)

        if not records:
            return

        num = len(records)
        msg = f"Are you sure you want to restore the {num} selected item(s)?" if num > 1 else f"Are you sure you want to restore '{records[0]['name']}'?"
        confirm = QMessageBox.question(self, "Confirm Restore", msg, QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        # Process categories first so child products can find their parent categories
        categories_first = sorted(records, key=lambda x: 0 if x.get("type") == "category" else 1)
        restored_count = 0
        for rec in categories_first:
            if rec in self.trash_items:
                if self.restore_single_trash_record(rec):
                    restored_count += 1

        self.save_database()
        self.save_trash_database()
        self.refresh_catalog_tree()
        self.refresh_trash_table()
        self.lbl_categories_count.setText(f"Total Categories: {len(self.categories)}")
        self.lbl_products_count.setText(f"Total Products: {len(self.products)}")
        self.log(f"Restored {restored_count} item(s) from Trash Bin.")
        self.compile_site(show_dialog=False)

    def delete_single_trash_record(self, record):
        if not record or record not in self.trash_items:
            return
            
        metadata_abs = os.path.join(SCRIPT_DIR, record.get("metadata_path", ""))
        trash_dir_abs = os.path.dirname(metadata_abs)
        if os.path.exists(trash_dir_abs):
            try:
                shutil.rmtree(trash_dir_abs)
            except Exception as e:
                self.log(f"Error removing trash directory: {e}")

        if record.get("type") == "category":
            associated_trashed = [
                x for x in list(self.trash_items)
                if x.get("type") == "product" and x.get("parent_trash_id") == record.get("trash_id")
            ]
            for prod_rec in associated_trashed:
                p_metadata_abs = os.path.join(SCRIPT_DIR, prod_rec.get("metadata_path", ""))
                p_trash_dir_abs = os.path.dirname(p_metadata_abs)
                if os.path.exists(p_trash_dir_abs):
                    try:
                        shutil.rmtree(p_trash_dir_abs)
                    except Exception:
                        pass
                if prod_rec in self.trash_items:
                    self.trash_items.remove(prod_rec)

        if record in self.trash_items:
            self.trash_items.remove(record)

    def delete_permanently(self):
        selected_items = self.trash_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select one or more trashed items to delete permanently.")
            return

        records = []
        for item in selected_items:
            rec = item.data(0, Qt.UserRole)
            if rec and rec not in records:
                records.append(rec)

        if not records:
            return

        num = len(records)
        name_str = f"'{records[0]['name']}'" if num == 1 else f"{num} selected items"
        
        # Stage 1 Confirmation
        confirm1 = QMessageBox.question(
            self, "Confirm Permanent Delete (Stage 1)",
            f"Are you sure you want to permanently delete {name_str}? This action CANNOT be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm1 == QMessageBox.No:
            return

        # Stage 2 Double Confirmation
        confirm2 = QMessageBox.question(
            self, "Are you ABSOLUTELY sure? (Stage 2)",
            f"Double Confirmation: Permanent deletion of {name_str} will DESTROY all associated images and metadata files forever. Proceed?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm2 == QMessageBox.No:
            return

        for rec in list(records):
            self.delete_single_trash_record(rec)

        self.save_trash_database()
        self.refresh_trash_table()
        self.log(f"Permanently destroyed {num} trashed record(s).")
        self.compile_site(show_dialog=False)
        self.log(f"Permanently deleted: {record['name']}")
        self.compile_site(show_dialog=False)

    def empty_trash_bin(self):
        if not self.trash_items:
            QMessageBox.information(self, "Trash Already Empty", "The Trash Bin is already empty.")
            return
            
        confirm = QMessageBox.question(
            self, "Confirm Empty Trash",
            "Are you sure you want to permanently delete EVERYTHING inside the Trash Bin? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return
            
        for folder in ["products", "categories", "images"]:
            folder_abs = os.path.join(TRASH_DIR, folder)
            if os.path.exists(folder_abs):
                try:
                    shutil.rmtree(folder_abs)
                except Exception as e:
                    self.log(f"Error clearing {folder} folder: {e}")
                    
        self.trash_items = []
        self.save_trash_database()
        self.refresh_trash_table()
        self.log("Trash Bin emptied successfully.")
        self.compile_site(show_dialog=False)

    def log(self, message):
        if hasattr(self, "txt_console") and self.txt_console:
            self.txt_console.append(message)
            self.txt_console.ensureCursorVisible()
        else:
            print(message)

    def compile_site(self, show_dialog=True):
        self.log("\nStarting website generation...")
        self.btn_compile.setEnabled(False)
        QApplication.processEvents()
        
        res = build_site(WORKSPACE_DIR)
        
        self.btn_compile.setEnabled(True)
        is_ok = res.get("success", False) if isinstance(res, dict) else bool(res)
        total = res.get("total_generated", 0) if isinstance(res, dict) else 0
        errs = res.get("errors", []) if isinstance(res, dict) else []
        
        if is_ok:
            self.log(f"Website built successfully! ({total} pages generated)")
            if show_dialog:
                QMessageBox.information(self, "Build Complete", f"All {total} webpages generated successfully!")
        else:
            err_str = "\n".join(errs) if errs else "Unknown build error."
            self.log(f"Build failed with errors:\n{err_str}")
            if show_dialog:
                QMessageBox.critical(self, "Build Failed", f"Static site builder encountered errors:\n\n{err_str}")

    def toggle_preview_server(self):
        if self.preview_thread and self.preview_thread.isRunning():
            # Stop server
            self.preview_thread.stop()
            self.preview_thread.wait()
            self.preview_thread = None
            self.btn_preview.setText("Launch Site Local Preview")
            self.log("Preview HTTP server stopped.")
        else:
            # Start server
            self.log("Starting local preview web server at http://localhost:8000 ...")
            self.preview_thread = PreviewServerThread(WORKSPACE_DIR, port=8000)
            self.preview_thread.start()
            
            self.btn_preview.setText("Stop Local Preview Server")
            self.log("Server running. Opening web browser to http://localhost:8000...")
            webbrowser.open("http://localhost:8000")

    def closeEvent(self, event):
        # Stop local server thread on close
        if self.preview_thread and self.preview_thread.isRunning():
            self.preview_thread.stop()
            self.preview_thread.wait()
        event.accept()

    def create_clients_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QLabel("Clients Logo Manager")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #50ab3c; padding-bottom: 5px;")
        layout.addWidget(header)
        
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels(["Client Name", "Logo Image", "Scale", "Link URL", "Link Status"])
        self.clients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.clients_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.clients_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.clients_table.setSelectionMode(QAbstractItemView.ExtendedSelection) # Enable multi-row selection
        self.clients_table.itemSelectionChanged.connect(self.on_client_selection_changed)
        
        btn_layout = QVBoxLayout()
        
        self.btn_add_client = QPushButton("Add Client Logo...")
        self.btn_add_client.clicked.connect(self.add_client_logo)
        
        self.btn_replace_logo = QPushButton("Replace Logo Image...")
        self.btn_replace_logo.clicked.connect(self.replace_client_logo)
        
        self.btn_edit_client_link = QPushButton("Edit Client Details...")
        self.btn_edit_client_link.clicked.connect(self.edit_client_link)
        
        self.btn_client_up = QPushButton("Move Up")
        self.btn_client_up.clicked.connect(self.move_client_up)
        
        self.btn_client_down = QPushButton("Move Down")
        self.btn_client_down.clicked.connect(self.move_client_down)
        
        self.btn_remove_client = QPushButton("Remove Client")
        self.btn_remove_client.setObjectName("danger_btn")
        self.btn_remove_client.clicked.connect(self.remove_client)
        
        # Slider & Textbox scale control directly on left panel
        scale_group = QGroupBox("Selected Logo Scale")
        scale_layout = QHBoxLayout(scale_group)
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(1, 100) # 0.1x to 10.0x
        self.scale_slider.setValue(100)
        self.scale_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_slider.setTickInterval(10)
        self.scale_slider.setEnabled(False)
        self.scale_slider.valueChanged.connect(self.on_scale_slider_changed)
        self.scale_slider.sliderReleased.connect(self.on_scale_slider_released)
        
        self.scale_text = QLineEdit()
        self.scale_text.setFixedWidth(55)
        self.scale_text.setAlignment(Qt.AlignCenter)
        self.scale_text.setText("1.0x")
        self.scale_text.setEnabled(False)
        self.scale_text.editingFinished.connect(self.on_scale_text_changed)
        
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_text)
        
        btn_layout.addWidget(self.btn_add_client)
        btn_layout.addWidget(self.btn_replace_logo)
        btn_layout.addWidget(self.btn_edit_client_link)
        btn_layout.addWidget(self.btn_client_up)
        btn_layout.addWidget(self.btn_client_down)
        btn_layout.addWidget(self.btn_remove_client)
        btn_layout.addWidget(scale_group)
        
        # Logo preview label with checkerboard background
        preview_group = QGroupBox("Selected Logo Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.lbl_client_preview = QLabel("No Selection")
        self.lbl_client_preview.setAlignment(Qt.AlignCenter)
        self.lbl_client_preview.setMinimumSize(120, 80)
        self.lbl_client_preview.setStyleSheet(
            "border: 1px dashed #3d3d3d;"
            "background-color: #ffffff;"
            "background-image: linear-gradient(45deg, #e0e0e0 25%, transparent 25%), linear-gradient(-45deg, #e0e0e0 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #e0e0e0 75%), linear-gradient(-45deg, transparent 75%, #e0e0e0 75%);"
            "background-size: 16px 16px;"
            "background-position: 0 0, 0 8px, 8px -8px, -8px 0px;"
            "padding: 5px;"
        )
        preview_layout.addWidget(self.lbl_client_preview)
        btn_layout.addWidget(preview_group)
        
        btn_layout.addStretch()
        
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.clients_table, 4)
        main_layout.addLayout(btn_layout, 1)
        
        layout.addLayout(main_layout)
        
        self.tabs.addTab(widget, "Clients")

    def make_scrollable(self, content_widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(content_widget)
        return scroll

    def create_site_content_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)

        header = QLabel("Page Content & Global Settings Manager")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #50ab3c; padding-bottom: 5px;")
        main_layout.addWidget(header)

        self.content_sub_tabs = QTabWidget()

        # 1. Header, Footer & Global Forms Subtab
        hf_widget = QWidget()
        hf_layout = QVBoxLayout(hf_widget)
        
        # Group 1: Header & Footer Contact Info (Multiline Editors)
        contact_group = QGroupBox("Header & Footer Contact Information")
        contact_form = QFormLayout(contact_group)

        self.txt_header_phones = QTextEdit()
        self.txt_header_phones.setMinimumHeight(70)
        self.txt_header_phones.setPlaceholderText("Enter 1 or more phone numbers (one per line)")

        self.txt_footer_phones = QTextEdit()
        self.txt_footer_phones.setMinimumHeight(70)
        self.txt_footer_phones.setPlaceholderText("Enter 1 or more phone numbers (one per line)")

        self.txt_footer_emails = QTextEdit()
        self.txt_footer_emails.setMinimumHeight(60)
        self.txt_footer_emails.setPlaceholderText("Enter 1 or more email addresses (one per line)")

        self.txt_global_address = QTextEdit()
        self.txt_global_address.setMinimumHeight(70)

        contact_form.addRow("Header Phones (one per line):", self.txt_header_phones)
        contact_form.addRow("Footer Phones (one per line):", self.txt_footer_phones)
        contact_form.addRow("Footer Emails (one per line):", self.txt_footer_emails)
        contact_form.addRow("Office Address:", self.txt_global_address)

        btn_sync_contact = QPushButton("Sync Phones, Emails & Address to Contact Us Page")
        btn_sync_contact.setMinimumHeight(35)
        btn_sync_contact.clicked.connect(self.sync_header_to_contact)

        # Group 2: Social Links & FormSubmit Endpoint
        social_group = QGroupBox("Social Links & FormSubmit Settings")
        social_form = QFormLayout(social_group)

        self.txt_social_facebook = QLineEdit()
        self.txt_social_twitter = QLineEdit()
        self.txt_social_instagram = QLineEdit()
        self.txt_social_youtube = QLineEdit()
        self.txt_social_linkedin = QLineEdit()
        self.txt_social_whatsapp = QLineEdit()
        self.txt_social_phone = QLineEdit()

        self.txt_formsubmit_url = QLineEdit()
        self.txt_formsubmit_url.setToolTip("FormSubmit.co action URL e.g. https://formsubmit.co/ajax/your_email@domain.com")

        social_form.addRow("Facebook Link:", self.txt_social_facebook)
        social_form.addRow("Twitter / X Link:", self.txt_social_twitter)
        social_form.addRow("Instagram Link:", self.txt_social_instagram)
        social_form.addRow("YouTube Link:", self.txt_social_youtube)
        social_form.addRow("LinkedIn Link:", self.txt_social_linkedin)
        social_form.addRow("WhatsApp Link:", self.txt_social_whatsapp)
        social_form.addRow("Phone Link (tel:):", self.txt_social_phone)
        social_form.addRow("FormSubmit.co URL:", self.txt_formsubmit_url)

        hf_layout.addWidget(contact_group)
        hf_layout.addWidget(btn_sync_contact)
        hf_layout.addWidget(social_group)
        hf_layout.addStretch()

        self.content_sub_tabs.addTab(self.make_scrollable(hf_widget), "Header, Footer & Social")

        # 2. Home Page (index.html) Subtab
        idx_widget = QWidget()
        idx_layout = QVBoxLayout(idx_widget)

        idx_form_group = QGroupBox("Index / Home Page Content")
        idx_form = QFormLayout(idx_form_group)

        self.txt_hero_tagline = QLineEdit()
        idx_form.addRow("Hero Tagline Heading:", self.txt_hero_tagline)

        idx_layout.addWidget(idx_form_group)
        idx_layout.addStretch()

        self.content_sub_tabs.addTab(self.make_scrollable(idx_widget), "Home Page (index.html)")

        # 3. About Us Page (about.html) Subtab
        abt_widget = QWidget()
        abt_layout = QVBoxLayout(abt_widget)

        abt_form_group = QGroupBox("About Us Page Content")
        abt_form = QFormLayout(abt_form_group)

        self.txt_about_who_subtitle = QLineEdit()
        self.txt_about_who_title = QLineEdit()
        self.txt_about_para = QTextEdit()
        self.txt_about_para.setMinimumHeight(75)
        self.txt_about_extended = QTextEdit()
        self.txt_about_extended.setMinimumHeight(85)
        self.txt_about_mission = QTextEdit()
        self.txt_about_mission.setMinimumHeight(75)
        self.txt_about_vision = QTextEdit()
        self.txt_about_vision.setMinimumHeight(75)
        self.txt_about_why_subtitle = QLineEdit()
        self.txt_about_why_heading = QTextEdit()
        self.txt_about_why_heading.setMinimumHeight(60)

        abt_form.addRow("Who We Are Subtitle:", self.txt_about_who_subtitle)
        abt_form.addRow("Who We Are Title:", self.txt_about_who_title)
        abt_form.addRow("Who We Are Paragraph:", self.txt_about_para)
        abt_form.addRow("Extended Info Paragraph:", self.txt_about_extended)
        abt_form.addRow("Our Mission Statement:", self.txt_about_mission)
        abt_form.addRow("Our Vision Statement:", self.txt_about_vision)
        abt_form.addRow("Why Choose Us Subtitle:", self.txt_about_why_subtitle)
        abt_form.addRow("Why Choose Us Heading:", self.txt_about_why_heading)

        abt_layout.addWidget(abt_form_group)
        abt_layout.addStretch()

        self.content_sub_tabs.addTab(self.make_scrollable(abt_widget), "About Us Page")

        # 4. Contact Us Page (contact.html) Subtab
        cnt_widget = QWidget()
        cnt_layout = QVBoxLayout(cnt_widget)

        cnt_form_group = QGroupBox("Contact Us Page Content")
        cnt_form = QFormLayout(cnt_form_group)

        self.txt_contact_phones = QTextEdit()
        self.txt_contact_phones.setMinimumHeight(70)
        self.txt_contact_phones.setPlaceholderText("Enter 1 or more phone numbers (one per line)")

        self.txt_contact_emails = QTextEdit()
        self.txt_contact_emails.setMinimumHeight(60)
        self.txt_contact_emails.setPlaceholderText("Enter 1 or more email addresses (one per line)")

        self.txt_contact_address = QTextEdit()
        self.txt_contact_address.setMinimumHeight(70)

        self.txt_contact_map_url = QTextEdit()
        self.txt_contact_map_url.setMinimumHeight(70)

        cnt_form.addRow("Contact Page Phones (one per line):", self.txt_contact_phones)
        cnt_form.addRow("Contact Page Emails (one per line):", self.txt_contact_emails)
        cnt_form.addRow("Contact Office Address:", self.txt_contact_address)
        cnt_form.addRow("Google Maps Embed Link (iframe src):", self.txt_contact_map_url)

        cnt_layout.addWidget(cnt_form_group)
        cnt_layout.addStretch()

        self.content_sub_tabs.addTab(self.make_scrollable(cnt_widget), "Contact Us Page")

        # 5. Branding & Page Images Subtab
        img_widget = QWidget()
        img_layout = QVBoxLayout(img_widget)

        img_form_group = QGroupBox("Branding Logos & Page Background Images")
        img_form_vbox = QVBoxLayout(img_form_group)

        self.img_previews = {}
        self.img_edits = {}

        image_definitions = [
            ("logo", "Website Logo (Header, Mobile Menu & Footer):", "img/logo.png"),
            ("hero_bg", "Home Page Hero Slider Background:", "img/hero/hero-1.jpg"),
            ("breadcrumb_bg", "Page Header Breadcrumb Banner Background:", "img/breadcrumb-bg.jpg"),
            ("call_bg", "About Us Page Call To Action Background:", "img/call-bg.jpg"),
            ("footer_bg", "Footer Section Background:", "img/footer-bg.jpg"),
        ]

        for key_name, title, default_path in image_definitions:
            box = QGroupBox(title)
            box_layout = QHBoxLayout(box)

            preview_lbl = QLabel()
            preview_lbl.setFixedSize(140, 60)
            preview_lbl.setAlignment(Qt.AlignCenter)
            preview_lbl.setStyleSheet(
                "border: 1px dashed #3d3d3d;"
                "background-color: #ffffff;"
                "background-image: linear-gradient(45deg, #e0e0e0 25%, transparent 25%), linear-gradient(-45deg, #e0e0e0 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #e0e0e0 75%), linear-gradient(-45deg, transparent 75%, #e0e0e0 75%);"
                "background-size: 16px 16px;"
                "background-position: 0 0, 0 8px, 8px -8px, -8px 0px;"
                "padding: 2px;"
            )

            path_edit = QLineEdit(default_path)
            btn_browse = QPushButton("Browse / Replace...")
            btn_browse.clicked.connect(lambda checked=False, k=key_name, e=path_edit, p=preview_lbl: self.browse_setting_image(k, e, p))

            box_layout.addWidget(preview_lbl)
            box_layout.addWidget(path_edit, 1)
            box_layout.addWidget(btn_browse)

            img_form_vbox.addWidget(box)
            self.img_previews[key_name] = preview_lbl
            self.img_edits[key_name] = path_edit

        img_layout.addWidget(img_form_group)
        img_layout.addStretch()

        self.content_sub_tabs.addTab(self.make_scrollable(img_widget), "Branding & Images")

        # 6. Page Titles & SEO Cards Subtab
        seo_widget = QWidget()
        seo_main_layout = QVBoxLayout(seo_widget)

        # Combined Compact Global SEO Defaults & AI Assistant GroupBox
        # --- Sub-tab 6: Page Titles & SEO Cards ---
        seo_widget = QWidget()
        seo_main_layout = QVBoxLayout(seo_widget)

        gseo_group = QGroupBox("Global SEO Defaults & Selective AI Assistant")
        gseo_hbox = QHBoxLayout(gseo_group)

        # Left Column: Global SEO Settings
        gseo_form = QFormLayout()
        self.txt_seo_site_url = QLineEdit()
        self.txt_seo_site_name = QLineEdit()
        
        self.chk_global_enable_keywords = QCheckBox("Include <meta name=\"keywords\"> tag in HTML head globally")
        self.chk_global_enable_keywords.setChecked(True)
        self.chk_global_enable_keywords.toggled.connect(self.on_global_keywords_toggled)
        
        self.txt_seo_keywords = QLineEdit()

        self.txt_seo_default_og_image = QLineEdit()
        self.txt_seo_default_og_image.setPlaceholderText("img/branding/og-share-card.jpg")
        btn_browse_global_og = QPushButton("Browse...")
        btn_browse_global_og.clicked.connect(self.browse_global_og_image)
        og_layout = QHBoxLayout()
        og_layout.addWidget(self.txt_seo_default_og_image)
        og_layout.addWidget(btn_browse_global_og)

        gseo_form.addRow("Base Website URL:", self.txt_seo_site_url)
        gseo_form.addRow("Website Name:", self.txt_seo_site_name)
        gseo_form.addRow("Static Pages Default OG Image (index, about, contact, products):", og_layout)
        gseo_form.addRow("Global Keywords Tag:", self.chk_global_enable_keywords)
        gseo_form.addRow("Default Keywords:", self.txt_seo_keywords)

        # Right Column: AI Assistant Export/Import Buttons
        ai_tools_vbox = QVBoxLayout()
        ai_tools_vbox.setContentsMargins(10, 0, 0, 0)
        ai_label = QLabel("Selective AI Workflow:")
        ai_label.setFont(QFont("Segoe UI", 9, QFont.Bold))

        btn_export_selected = QPushButton("Export Selected Items for AI (JSON)...")
        btn_export_selected.setMinimumHeight(36)
        btn_export_selected.setToolTip("Export checked pages & products with full specs & instructions for AI.")
        btn_export_selected.clicked.connect(self.export_selected_seo_prompt_json)

        btn_import_seo_file = QPushButton("Import AI SEO File (JSON)...")
        btn_import_seo_file.setMinimumHeight(36)
        btn_import_seo_file.setObjectName("action_btn")
        btn_import_seo_file.setToolTip("Import AI response file to update ONLY the items present in the file.")
        btn_import_seo_file.clicked.connect(self.import_seo_response_json)

        ai_tools_vbox.addWidget(ai_label)
        ai_tools_vbox.addWidget(btn_export_selected)
        ai_tools_vbox.addWidget(btn_import_seo_file)
        ai_tools_vbox.addStretch()

        gseo_hbox.addLayout(gseo_form, 2)
        gseo_hbox.addLayout(ai_tools_vbox, 1)

        # Splitter Layout: Left Selection Tree + Search, Right Live Data Inspector
        splitter = QSplitter(Qt.Horizontal)

        # Left Selection Tree Widget
        tree_container = QWidget()
        tree_vbox = QVBoxLayout(tree_container)
        tree_vbox.setContentsMargins(0, 0, 0, 0)

        tree_label = QLabel("Select Pages/Products to Edit & Export:")
        tree_label.setFont(QFont("Segoe UI", 10, QFont.Bold))

        # Search Filter Bar above tree
        self.txt_tree_search = QLineEdit()
        self.txt_tree_search.setPlaceholderText("🔍 Search pages & products...")
        self.txt_tree_search.textChanged.connect(self.filter_seo_tree)

        self.seo_tree = QTreeWidget()
        self.seo_tree.setHeaderLabels(["Page / Item Name", "SEO Status"])
        self.seo_tree.setColumnWidth(0, 220)
        self.seo_tree.setMinimumHeight(280)
        self.seo_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.seo_tree.customContextMenuRequested.connect(self.on_seo_tree_context_menu)
        self.seo_tree.itemDoubleClicked.connect(self.on_seo_tree_double_clicked)
        self.seo_tree.itemSelectionChanged.connect(self.on_seo_tree_selection_changed)

        btn_tree_all = QPushButton("Select All")
        btn_tree_all.clicked.connect(self.seo_select_all)
        btn_tree_unconfig = QPushButton("Select Unconfigured")
        btn_tree_unconfig.clicked.connect(self.seo_select_unconfigured)
        btn_tree_none = QPushButton("Clear")
        btn_tree_none.clicked.connect(self.seo_select_none)

        tree_btn_layout = QHBoxLayout()
        tree_btn_layout.addWidget(btn_tree_all)
        tree_btn_layout.addWidget(btn_tree_unconfig)
        tree_btn_layout.addWidget(btn_tree_none)

        btn_edit_tree_selected = QPushButton("✏️ Edit Selected SEO & Social Card (Pop-up Window)...")
        btn_edit_tree_selected.setObjectName("action_btn")
        btn_edit_tree_selected.setMinimumHeight(34)
        btn_edit_tree_selected.setToolTip("Open pop-up editor for double-clicked or highlighted item.")
        btn_edit_tree_selected.clicked.connect(self.open_selected_tree_item_dialog)

        tree_vbox.addWidget(tree_label)
        tree_vbox.addWidget(self.txt_tree_search)
        tree_vbox.addLayout(tree_btn_layout)
        tree_vbox.addWidget(self.seo_tree, 1)
        tree_vbox.addWidget(btn_edit_tree_selected)

        # Right Panel: Live Data Inspector Panel
        inspector_container = QWidget()
        inspector_container.setMinimumHeight(450)
        inspector_vbox = QVBoxLayout(inspector_container)
        inspector_vbox.setContentsMargins(0, 0, 0, 0)

        inspector_group = QGroupBox("Selected Item Live Data Inspector")
        inspector_group_vbox = QVBoxLayout(inspector_group)

        self.lbl_inspector_header = QLabel("Select an item on the left to inspect its SEO configuration")
        self.lbl_inspector_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_inspector_header.setStyleSheet("color: #50ab3c; padding-bottom: 2px;")

        self.lbl_inspector_details = QLabel()
        self.lbl_inspector_details.setMinimumHeight(320)
        self.lbl_inspector_details.setStyleSheet(
            "border: 1px solid #d0d7de; border-radius: 8px; background-color: #f8f9fa; padding: 14px;"
            "font-family: 'Segoe UI', sans-serif;"
        )
        self.lbl_inspector_details.setWordWrap(True)

        btn_launch_inspector_editor = QPushButton("✏️ Launch Dedicated Pop-up Editor...")
        btn_launch_inspector_editor.setObjectName("action_btn")
        btn_launch_inspector_editor.setMinimumHeight(38)
        btn_launch_inspector_editor.clicked.connect(self.open_selected_tree_item_dialog)

        inspector_group_vbox.addWidget(self.lbl_inspector_header)
        inspector_group_vbox.addWidget(self.lbl_inspector_details, 1)
        inspector_group_vbox.addWidget(btn_launch_inspector_editor)

        inspector_vbox.addWidget(inspector_group)

        splitter.addWidget(tree_container)
        splitter.addWidget(inspector_container)
        splitter.setSizes([340, 560])

        seo_main_layout.addWidget(gseo_group)
        seo_main_layout.addWidget(splitter, 1)

        self.content_sub_tabs.addTab(self.make_scrollable(seo_widget), "Page Titles & SEO Cards")

        main_layout.addWidget(self.content_sub_tabs)

        # Save Button
        self.btn_save_site_content = QPushButton("Save Content & Rebuild Website")
        self.btn_save_site_content.setObjectName("action_btn")
        self.btn_save_site_content.setMinimumHeight(45)
        self.btn_save_site_content.clicked.connect(self.save_site_content_and_rebuild)
        main_layout.addWidget(self.btn_save_site_content)

        self.tabs.addTab(widget, "Page Content & Global Settings")
        self.refresh_site_content_fields()

    def refresh_site_content_fields(self):
        info = getattr(self, 'site_info', get_default_site_info())
        hf = info.get("header_footer", {})
        sl = hf.get("social_links", {})
        idx = info.get("index_page", {})
        abt = info.get("about_page", {})
        cnt = info.get("contact_page", {})

        # Header/Footer
        header_phones = hf.get("header_phones", [])
        footer_phones = hf.get("footer_phones", [])
        footer_emails = hf.get("footer_emails", [])
        self.txt_header_phones.setPlainText("\n".join(header_phones))
        self.txt_footer_phones.setPlainText("\n".join(footer_phones))
        self.txt_footer_emails.setPlainText("\n".join(footer_emails))
        self.txt_global_address.setPlainText(hf.get("address", ""))

        self.txt_social_facebook.setText(sl.get("facebook", ""))
        self.txt_social_twitter.setText(sl.get("twitter", ""))
        self.txt_social_instagram.setText(sl.get("instagram", ""))
        self.txt_social_youtube.setText(sl.get("youtube", ""))
        self.txt_social_linkedin.setText(sl.get("linkedin", ""))
        self.txt_social_whatsapp.setText(sl.get("whatsapp", ""))
        self.txt_social_phone.setText(sl.get("phone", ""))

        self.txt_formsubmit_url.setText(hf.get("formsubmit_url", ""))

        # Index
        self.txt_hero_tagline.setText(idx.get("hero_tagline", ""))

        # About
        self.txt_about_who_subtitle.setText(abt.get("who_we_are_subtitle", ""))
        self.txt_about_who_title.setText(abt.get("who_we_are_title", ""))
        self.txt_about_para.setPlainText(abt.get("about_text", ""))
        self.txt_about_extended.setPlainText(abt.get("extended_info_text", ""))
        self.txt_about_mission.setPlainText(abt.get("mission_text", ""))
        self.txt_about_vision.setPlainText(abt.get("vision_text", ""))
        self.txt_about_why_subtitle.setText(abt.get("why_choose_us_subtitle", ""))
        self.txt_about_why_heading.setPlainText(abt.get("why_choose_us_heading", ""))

        # Contact
        contact_phones = cnt.get("phones", [])
        contact_emails = cnt.get("emails", [])
        self.txt_contact_phones.setPlainText("\n".join(contact_phones))
        self.txt_contact_emails.setPlainText("\n".join(contact_emails))
        self.txt_contact_address.setPlainText(cnt.get("address", ""))
        self.txt_contact_map_url.setPlainText(cnt.get("map_iframe_url", ""))

        # Branding Images
        imgs = info.get("site_images", {})
        defaults_img = get_default_site_info()["site_images"]
        for key in ["logo", "hero_bg", "breadcrumb_bg", "call_bg", "footer_bg"]:
            rel_path = imgs.get(key, defaults_img.get(key, ""))
            if key in self.img_edits:
                self.img_edits[key].setText(rel_path)
            if key in self.img_previews:
                self.update_image_preview_label(self.img_previews[key], rel_path)

        # Global SEO Settings
        gseo = info.get("seo_global", {})
        defaults_seo = get_default_site_info()["seo_global"]
        if hasattr(self, 'txt_seo_site_url'):
            self.txt_seo_site_url.setText(gseo.get("site_url", defaults_seo["site_url"]))
            self.txt_seo_site_name.setText(gseo.get("site_name", defaults_seo["site_name"]))
            enable_kw = gseo.get("enable_keywords", True)
            if hasattr(self, 'chk_global_enable_keywords'):
                self.chk_global_enable_keywords.setChecked(bool(enable_kw))
            self.txt_seo_keywords.setText(gseo.get("default_keywords", defaults_seo["default_keywords"]))
            self.txt_seo_keywords.setEnabled(bool(enable_kw))
            if hasattr(self, 'txt_seo_default_og_image'):
                self.txt_seo_default_og_image.setText(gseo.get("default_og_image", defaults_seo.get("default_og_image", "img/branding/og-share-card.jpg")))

        if hasattr(self, 'seo_tree'):
            self.populate_seo_tree()

    def on_global_keywords_toggled(self, checked):
        if hasattr(self, 'txt_seo_keywords'):
            self.txt_seo_keywords.setEnabled(checked)

    def filter_seo_tree(self, text):
        query = text.strip().lower()
        it = QTreeWidgetItemIterator(self.seo_tree)
        while it.value():
            item = it.value()
            if not query:
                item.setHidden(False)
            else:
                label = item.text(0).lower()
                data = item.data(0, Qt.UserRole)
                match = query in label
                if data and isinstance(data, dict):
                    key = str(data.get("key", "")).lower()
                    if query in key:
                        match = True
                item.setHidden(not match)
                if match and item.parent():
                    item.parent().setHidden(False)
            it += 1

    def on_seo_tree_context_menu(self, position):
        item = self.seo_tree.itemAt(position)
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        if not data or not isinstance(data, dict):
            return
        
        menu = QMenu(self)
        act_edit = menu.addAction("✏️ Edit SEO & Social Card...")
        act_revert = menu.addAction("🔄 Revert to Auto Defaults")
        menu.addSeparator()
        act_check = menu.addAction("☑️ Check for AI Export")
        act_uncheck = menu.addAction("🔳 Uncheck")
        
        action = menu.exec_(self.seo_tree.viewport().mapToGlobal(position))
        if action == act_edit:
            self.open_seo_editor_dialog_for_item(data)
        elif action == act_revert:
            self.revert_item_seo_to_auto(data)
        elif action == act_check:
            item.setCheckState(0, Qt.Checked)
        elif action == act_uncheck:
            item.setCheckState(0, Qt.Unchecked)

    def on_seo_tree_double_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if data and isinstance(data, dict):
            self.open_seo_editor_dialog_for_item(data)

    def open_selected_tree_item_dialog(self):
        items = self.seo_tree.selectedItems()
        if not items:
            QMessageBox.information(self, "No Item Selected", "Please select a page or product from the tree view to edit.")
            return
        data = items[0].data(0, Qt.UserRole)
        if data and isinstance(data, dict):
            self.open_seo_editor_dialog_for_item(data)

    def open_seo_editor_dialog_for_item(self, item_data):
        dlg = EditItemSEODialog(
            item_data=item_data,
            site_info=self.site_info,
            categories=self.categories,
            products=self.products,
            parent=self
        )
        if dlg.exec_() == QDialog.Accepted:
            edited = dlg.get_edited_data()
            item_type = item_data.get("type")
            item_key = item_data.get("key")
            
            if item_type == "static":
                if "pages_seo" not in self.site_info:
                    self.site_info["pages_seo"] = {}
                self.site_info["pages_seo"][item_key] = edited
            elif item_type == "category":
                cat = next((c for c in getattr(self, 'categories', []) if c.get("slug") == item_key), None)
                if cat:
                    cat["seo_title"] = edited.get("title")
                    cat["og_title"] = edited.get("og_title")
                    cat["seo_description"] = edited.get("description")
                    cat["og_image"] = edited.get("og_image")
                    cat["enable_keywords"] = edited.get("enable_keywords")
                    cat["keywords"] = edited.get("keywords")
            elif item_type == "product":
                prod = next((p for p in getattr(self, 'products', []) if p.get("id") == item_key), None)
                if prod:
                    prod["seo_title"] = edited.get("title")
                    prod["og_title"] = edited.get("og_title")
                    prod["seo_description"] = edited.get("description")
                    prod["og_image"] = edited.get("og_image")
                    prod["enable_keywords"] = edited.get("enable_keywords")
                    prod["keywords"] = edited.get("keywords")
            
            self.populate_seo_tree()
            self.update_seo_inspector()

    def revert_item_seo_to_auto(self, item_data):
        item_type = item_data.get("type")
        item_key = item_data.get("key")
        
        if item_type == "static":
            if "pages_seo" in self.site_info and item_key in self.site_info["pages_seo"]:
                del self.site_info["pages_seo"][item_key]
        elif item_type == "category":
            cat = next((c for c in getattr(self, 'categories', []) if c.get("slug") == item_key), None)
            if cat:
                for k in ["seo_title", "og_title", "seo_description", "og_image", "enable_keywords", "keywords"]:
                    cat.pop(k, None)
        elif item_type == "product":
            prod = next((p for p in getattr(self, 'products', []) if p.get("id") == item_key), None)
            if prod:
                for k in ["seo_title", "og_title", "seo_description", "og_image", "enable_keywords", "keywords"]:
                    prod.pop(k, None)
                    
        self.populate_seo_tree()
        self.update_seo_inspector()

    def on_seo_tree_selection_changed(self):
        self.update_seo_inspector()

    def update_seo_inspector(self):
        items = self.seo_tree.selectedItems()
        if not items or not hasattr(self, 'lbl_inspector_details'):
            return
        item = items[0]
        data = item.data(0, Qt.UserRole)
        if not data or not isinstance(data, dict):
            return

        item_type = data.get("type")
        item_key = data.get("key")
        site_url = self.txt_seo_site_url.text().strip() if hasattr(self, 'txt_seo_site_url') else "https://ecoluxebharat.com/"
        g_enable_kw = self.chk_global_enable_keywords.isChecked() if hasattr(self, 'chk_global_enable_keywords') else True

        if item_type == "static":
            self.lbl_inspector_header.setText(f"Inspecting: Static Page [{item_key}]")
            p_data = self.site_info.get("pages_seo", {}).get(item_key, {})
            custom_t = p_data.get("title", "")
            custom_d = p_data.get("description", "")
            custom_img = p_data.get("og_image", "")
            custom_kw = p_data.get("keywords", "")
            enable_kw = p_data.get("enable_keywords") if "enable_keywords" in p_data else g_enable_kw
            
            page_path = item_key if item_key != "index.html" else ""
            full_url = f"{site_url}{page_path}"
            default_t = f"EcoLuxe Bharat | {item_key.replace('.html','').title()}"
            default_d = "Premier manufacturer of road safety products across India."
            default_img = "img/branding/og-share-card.jpg"

        elif item_type == "category":
            cat = next((c for c in getattr(self, 'categories', []) if c.get("slug") == item_key), None)
            c_title = cat.get("title") if cat else item_key
            self.lbl_inspector_header.setText(f"Inspecting: Category [{c_title}]")
            custom_t = cat.get("seo_title", "") if cat else ""
            custom_d = cat.get("seo_description", "") if cat else ""
            custom_img = cat.get("og_image", "") if cat else ""
            custom_kw = cat.get("keywords", "") if cat else ""
            enable_kw = cat.get("enable_keywords") if (cat and "enable_keywords" in cat) else g_enable_kw
            
            full_url = f"{site_url}categories/{item_key}.html"
            default_t = f"{c_title} - Road Safety Products | EcoLuxe Bharat"
            default_d = f"Browse high-quality {c_title} manufactured by EcoLuxe Bharat."
            default_img = cat.get("image") or f"img/categories/{item_key}.jpg" if cat else "img/branding/og-share-card.jpg"

        elif item_type == "product":
            prod = next((p for p in getattr(self, 'products', []) if p.get("id") == item_key), None)
            p_title = prod.get("title") if prod else item_key
            model = prod.get("model") if prod else ""
            cat_slug = prod.get("category_slug") if prod else ""
            cat_info = next((c for c in getattr(self, 'categories', []) if c.get("slug") == cat_slug), None)
            cat_name = cat_info.get("title") if cat_info else ""
            
            label_name = f"{p_title} ({model})" if model else p_title
            self.lbl_inspector_header.setText(f"Inspecting: Product [{label_name}]")
            
            custom_t = prod.get("seo_title", "") if prod else ""
            custom_d = prod.get("seo_description", "") if prod else ""
            custom_img = prod.get("og_image", "") if prod else ""
            custom_kw = prod.get("keywords", "") if prod else ""
            enable_kw = prod.get("enable_keywords") if (prod and "enable_keywords" in prod) else g_enable_kw
            
            full_url = f"{site_url}products/{cat_slug}/{item_key}.html"
            default_t = f"{p_title} | EcoLuxe Bharat"
            default_d = f"Inquire {p_title} ({model}) engineered for high durability."
            images = prod.get("images", []) if prod else []
            default_img = images[0]["src"] if (images and len(images) > 0 and images[0].get("src")) else "img/branding/og-share-card.jpg"

        final_t = custom_t if custom_t else default_t
        final_d = custom_d if custom_d else default_d
        final_img = custom_img if custom_img else default_img
        has_custom = bool(custom_t or custom_d or custom_img or custom_kw)
        
        status_badge = "<span style='background:#50ab3c; color:#fff; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>🟢 CUSTOM SEO APPLIED</span>" if has_custom else "<span style='background:#0066cc; color:#fff; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>🔵 AUTO DEFAULTS</span>"
        kw_badge = "<span style='color:#27ae60; font-weight:bold;'>Enabled</span>" if enable_kw else "<span style='color:#e74c3c; font-weight:bold;'>Disabled (Omitted)</span>"

        img_abs = os.path.join(WORKSPACE_DIR, final_img.replace('/', os.sep))
        if os.path.exists(img_abs):
            img_file_url = f"file:///{img_abs.replace(os.sep, '/')}"
            img_preview_html = f'<div style="text-align: center; margin-top: 6px; background: #f0f2f5; padding: 6px; border-radius: 6px; border: 1px solid #e1e4e8;"><img src="{img_file_url}" style="max-width: 140px; max-height: 75px; object-fit: contain; border-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,0.12);" /><br/><span style="font-size: 10px; color: #666; margin-top: 3px; display: block;">🖼️ <b>Share Image:</b> {final_img}</span></div>'
        else:
            img_preview_html = f'<p style="margin: 4px 0;"><b>🖼️ Social Share Image:</b> <span style="color:#666;">{final_img}</span></p>'

        details_html = f"""
        <div style="font-size: 13px; line-height: 1.5; color: #333;">
            <div style="margin-bottom: 6px;">{status_badge}</div>
            <p style="margin: 3px 0;"><b>🌐 Master Canonical URL:</b> <a href="{full_url}" style="color:#0066cc;">{full_url}</a></p>
            <p style="margin: 3px 0;"><b>🏷️ Rendered Meta Title (&lt;title&gt;):</b> <br/><span style="color:#111; font-weight:600;">{final_t}</span></p>
            <p style="margin: 3px 0;"><b>📝 Meta Description:</b> <br/><span style="color:#555;">{final_d}</span></p>
            <p style="margin: 3px 0;"><b>🏷️ Meta Keywords Tag:</b> {kw_badge}</p>
            {img_preview_html}
        </div>
        """
        self.lbl_inspector_details.setText(details_html)

    def populate_seo_tree(self):
        if not hasattr(self, 'seo_tree'):
            return
        self.seo_tree.blockSignals(True)
        self.seo_tree.clear()

        info = getattr(self, 'site_info', get_default_site_info())
        pseo = info.get("pages_seo", {})

        # Node 1: Static Pages
        node_static = QTreeWidgetItem(self.seo_tree, ["Static Main Pages", ""])
        node_static.setFlags(node_static.flags() | Qt.ItemIsUserCheckable)
        node_static.setCheckState(0, Qt.Checked)

        static_list = [
            ("index.html", "Home Page (index.html)"),
            ("about.html", "About Us Page (about.html)"),
            ("contact.html", "Contact Us Page (contact.html)"),
            ("products.html", "Products Catalog (products.html)")
        ]
        for page_file, label in static_list:
            p_data = pseo.get(page_file, {})
            has_custom = bool(p_data.get("title") or p_data.get("description") or p_data.get("og_image") or p_data.get("keywords"))
            status = "🟢 Custom" if has_custom else "🔵 Auto"
            item = QTreeWidgetItem(node_static, [label, status])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Checked)
            item.setData(0, Qt.UserRole, {"type": "static", "key": page_file})

        # Node 2: Category Pages
        node_cats = QTreeWidgetItem(self.seo_tree, ["Category Pages", ""])
        node_cats.setFlags(node_cats.flags() | Qt.ItemIsUserCheckable)
        node_cats.setCheckState(0, Qt.Checked)

        for c in getattr(self, 'categories', []):
            has_custom = bool(c.get("seo_title") or c.get("seo_description") or c.get("og_image") or c.get("keywords"))
            status = "🟢 Custom" if has_custom else "🔵 Auto"
            cat_item = QTreeWidgetItem(node_cats, [c.get("title", c.get("slug")), status])
            cat_item.setFlags(cat_item.flags() | Qt.ItemIsUserCheckable)
            cat_item.setCheckState(0, Qt.Checked)
            cat_item.setData(0, Qt.UserRole, {"type": "category", "key": c.get("slug")})

            # Sub-node: Products under this category
            cat_prods = [p for p in getattr(self, 'products', []) if p.get("category_slug") == c.get("slug")]
            for p in cat_prods:
                p_has_custom = bool(p.get("seo_title") or p.get("seo_description") or p.get("og_image") or p.get("keywords"))
                p_status = "🟢 Custom" if p_has_custom else "🔵 Auto"
                prod_label = f"{p.get('title')} ({p.get('model')})" if p.get("model") else p.get("title")
                p_item = QTreeWidgetItem(cat_item, [prod_label, p_status])
                p_item.setFlags(p_item.flags() | Qt.ItemIsUserCheckable)
                p_item.setCheckState(0, Qt.Checked)
                p_item.setData(0, Qt.UserRole, {"type": "product", "key": p.get("id")})

        self.seo_tree.expandAll()
        self.seo_tree.blockSignals(False)

    def seo_select_all(self):
        it = QTreeWidgetItemIterator(self.seo_tree)
        while it.value():
            it.value().setCheckState(0, Qt.Checked)
            it += 1

    def seo_select_none(self):
        it = QTreeWidgetItemIterator(self.seo_tree)
        while it.value():
            it.value().setCheckState(0, Qt.Unchecked)
            it += 1

    def seo_select_unconfigured(self):
        it = QTreeWidgetItemIterator(self.seo_tree)
        while it.value():
            item = it.value()
            status = item.text(1)
            if status == "🔵 Auto":
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)
            it += 1

    def export_selected_seo_prompt_json(self):
        export_file, _ = QFileDialog.getSaveFileName(
            self, "Save Selective SEO AI Prompt File",
            os.path.join(WORKSPACE_DIR, "seo_prompt_export.json"),
            "JSON Files (*.json)"
        )
        if not export_file:
            return

        selected_statics = []
        selected_cat_slugs = set()
        selected_prod_ids = set()

        it = QTreeWidgetItemIterator(self.seo_tree)
        while it.value():
            item = it.value()
            if item.checkState(0) == Qt.Checked:
                data = item.data(0, Qt.UserRole)
                if data and isinstance(data, dict):
                    t = data.get("type")
                    k = data.get("key")
                    if t == "static": selected_statics.append(k)
                    elif t == "category": selected_cat_slugs.add(k)
                    elif t == "product": selected_prod_ids.add(k)
            it += 1

        pages_data = {}
        info = getattr(self, 'site_info', {})
        pseo = info.get("pages_seo", {})
        for page_file in selected_statics:
            pages_data[page_file] = pseo.get(page_file, {})

        categories_data = []
        for c in getattr(self, 'categories', []):
            if c.get("slug") in selected_cat_slugs:
                categories_data.append({
                    "slug": c.get("slug"),
                    "title": c.get("title"),
                    "description": c.get("description", ""),
                    "current_seo_title": c.get("seo_title", ""),
                    "current_seo_description": c.get("seo_description", "")
                })

        products_data = []
        for p in getattr(self, 'products', []):
            if p.get("id") in selected_prod_ids:
                products_data.append({
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "model": p.get("model", ""),
                    "category_slug": p.get("category_slug", ""),
                    "short_desc": p.get("short_desc", ""),
                    "full_description": p.get("description", ""),
                    "specifications": p.get("specifications", {}),
                    "features": p.get("features", []),
                    "dimensions": p.get("dimensions", {}),
                    "material_build": p.get("material", ""),
                    "primary_image": p.get("images", [{}])[0].get("src") if p.get("images") else "",
                    "current_seo_title": p.get("seo_title", ""),
                    "current_seo_description": p.get("seo_description", "")
                })

        prompt_payload = {
            "system_instruction": (
                "CRITICAL SYSTEM INSTRUCTION: You are an expert SEO copywriter for EcoLuxe Bharat. "
                "Analyze full product specifications, dimensions, material builds, and descriptions provided.\n"
                "Generate compelling, keyword-rich SEO Titles (50-60 chars) and Meta Descriptions (120-155 chars).\n\n"
                "STRICT SCHEMA RULES:\n"
                "1. Maintain the EXACT JSON structure key-for-key.\n"
                "2. Do NOT add extra commentary, markdown headers, or change key names.\n"
                "3. Fill in 'recommended_seo_title' and 'recommended_seo_description' for items.\n"
                "4. Return strictly valid JSON."
            ),
            "site_info": {
                "site_name": info.get("seo_global", {}).get("site_name", "EcoLuxe Bharat"),
                "site_url": info.get("seo_global", {}).get("site_url", "https://ecoluxebharat.com/"),
                "pages_seo": pages_data
            },
            "categories": categories_data,
            "products": products_data
        }

        try:
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(prompt_payload, f, indent=4)
            QMessageBox.information(
                self, "Selective Export Successful",
                f"Exported {len(selected_statics)} pages, {len(categories_data)} categories, and {len(products_data)} products to:\n{export_file}\n\n"
                "Paste or drag this file into Antigravity or Gemini Chat to generate high-converting SEO copy!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export selective SEO prompt file: {e}")

    def import_seo_response_json(self):
        import_file, _ = QFileDialog.getOpenFileName(
            self, "Select AI Generated SEO File", WORKSPACE_DIR,
            "JSON Files (*.json)"
        )
        if not import_file:
            return

        try:
            with open(import_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Import pages_seo
            imported_pages = data.get("site_info", {}).get("pages_seo") or data.get("pages_seo")
            if imported_pages and isinstance(imported_pages, dict):
                if "pages_seo" not in self.site_info:
                    self.site_info["pages_seo"] = {}
                for page, p_dict in imported_pages.items():
                    if isinstance(p_dict, dict):
                        self.site_info["pages_seo"][page] = p_dict

            # Import categories
            imported_cats = data.get("categories", [])
            cat_updated_count = 0
            if isinstance(imported_cats, list):
                cat_map = {c.get("slug"): c for c in imported_cats if c.get("slug")}
                for c in getattr(self, 'categories', []):
                    c_slug = c.get("slug")
                    if c_slug in cat_map:
                        item = cat_map[c_slug]
                        new_t = item.get("recommended_seo_title") or item.get("seo_title")
                        new_d = item.get("recommended_seo_description") or item.get("seo_description")
                        if new_t: c["seo_title"] = new_t
                        if new_d: c["seo_description"] = new_d
                        cat_updated_count += 1

            # Import products
            imported_prods = data.get("products", [])
            prod_updated_count = 0
            if isinstance(imported_prods, list):
                prod_map = {p.get("id"): p for p in imported_prods if p.get("id")}
                for p in getattr(self, 'products', []):
                    p_id = p.get("id")
                    if p_id in prod_map:
                        item = prod_map[p_id]
                        new_t = item.get("recommended_seo_title") or item.get("seo_title")
                        new_d = item.get("recommended_seo_description") or item.get("seo_description")
                        if new_t: p["seo_title"] = new_t
                        if new_d: p["seo_description"] = new_d
                        prod_updated_count += 1

            self.refresh_site_content_fields()
            self.save_database()
            self.compile_site()
            QMessageBox.information(
                self, "Selective Import Successful",
                f"Successfully imported AI SEO metadata!\n"
                f"Updated static pages, {cat_updated_count} categories, and {prod_updated_count} products."
            )
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Failed to parse or import AI SEO file: {e}")

    def browse_setting_image(self, key_name, path_edit, preview_label):
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select Replacement Image for {key_name}", WORKSPACE_DIR,
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if not file_path:
            return

        dest_dir = os.path.join(WORKSPACE_DIR, "img", "branding")
        os.makedirs(dest_dir, exist_ok=True)

        ext = os.path.splitext(file_path)[1]
        dest_filename = f"{key_name}_{int(time.time())}{ext}"
        dest_abs = os.path.join(dest_dir, dest_filename)

        try:
            shutil.copy2(file_path, dest_abs)
            rel_path = f"img/branding/{dest_filename}".replace("\\", "/")
            path_edit.setText(rel_path)
            self.update_image_preview_label(preview_label, rel_path)
        except Exception as e:
            QMessageBox.critical(self, "Image Copy Error", f"Failed to copy image: {e}")

    def update_image_preview_label(self, preview_label, rel_path):
        if not rel_path:
            preview_label.setText("No Image")
            return
        abs_path = os.path.join(WORKSPACE_DIR, rel_path.replace("/", os.sep))
        if os.path.exists(abs_path):
            pixmap = QPixmap(abs_path)
            if not pixmap.isNull():
                preview_label.setPixmap(pixmap.scaled(preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        preview_label.setText("Image Missing")

    def browse_global_og_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Global Default OG Social Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if not file_path:
            return
        dest_dir = os.path.join(WORKSPACE_DIR, "img", "branding")
        os.makedirs(dest_dir, exist_ok=True)
        ext = os.path.splitext(file_path)[1]
        dest_filename = f"og_share_card_{int(time.time())}{ext}"
        dest_abs = os.path.join(dest_dir, dest_filename)
        try:
            shutil.copy2(file_path, dest_abs)
            rel_path = f"img/branding/{dest_filename}".replace("\\", "/")
            self.txt_seo_default_og_image.setText(rel_path)
        except Exception as e:
            QMessageBox.critical(self, "Image Copy Error", f"Failed to copy global default OG image: {e}")

    def sync_header_to_contact(self):
        self.txt_contact_phones.setPlainText(self.txt_header_phones.toPlainText().strip())
        self.txt_contact_emails.setPlainText(self.txt_footer_emails.toPlainText().strip())
        self.txt_contact_address.setPlainText(self.txt_global_address.toPlainText().strip())
        QMessageBox.information(self, "Synced", "Header/Footer phones, emails, and address copied to Contact Us Page fields!")

    def save_site_content_and_rebuild(self):
        header_phones = [p.strip() for p in self.txt_header_phones.toPlainText().splitlines() if p.strip()]
        footer_phones = [p.strip() for p in self.txt_footer_phones.toPlainText().splitlines() if p.strip()]
        footer_emails = [e.strip() for e in self.txt_footer_emails.toPlainText().splitlines() if e.strip()]
        contact_phones = [p.strip() for p in self.txt_contact_phones.toPlainText().splitlines() if p.strip()]
        contact_emails = [e.strip() for e in self.txt_contact_emails.toPlainText().splitlines() if e.strip()]

        site_images = {}
        for key in ["logo", "hero_bg", "breadcrumb_bg", "call_bg", "footer_bg"]:
            if key in self.img_edits:
                site_images[key] = self.img_edits[key].text().strip()

        self.site_info = {
            "header_footer": {
                "header_phones": header_phones,
                "footer_phones": footer_phones,
                "footer_emails": footer_emails,
                "address": self.txt_global_address.toPlainText().strip(),
                "social_links": {
                    "facebook": self.txt_social_facebook.text().strip(),
                    "twitter": self.txt_social_twitter.text().strip(),
                    "instagram": self.txt_social_instagram.text().strip(),
                    "youtube": self.txt_social_youtube.text().strip(),
                    "linkedin": self.txt_social_linkedin.text().strip(),
                    "whatsapp": self.txt_social_whatsapp.text().strip(),
                    "phone": self.txt_social_phone.text().strip()
                },
                "formsubmit_url": self.txt_formsubmit_url.text().strip()
            },
            "index_page": {
                "hero_tagline": self.txt_hero_tagline.text().strip()
            },
            "about_page": {
                "who_we_are_subtitle": self.txt_about_who_subtitle.text().strip(),
                "who_we_are_title": self.txt_about_who_title.text().strip(),
                "about_text": self.txt_about_para.toPlainText().strip(),
                "extended_info_text": self.txt_about_extended.toPlainText().strip(),
                "mission_text": self.txt_about_mission.toPlainText().strip(),
                "vision_text": self.txt_about_vision.toPlainText().strip(),
                "why_choose_us_subtitle": self.txt_about_why_subtitle.text().strip(),
                "why_choose_us_heading": self.txt_about_why_heading.toPlainText().strip()
            },
            "contact_page": {
                "phones": contact_phones,
                "emails": contact_emails,
                "address": self.txt_contact_address.toPlainText().strip(),
                "map_iframe_url": self.txt_contact_map_url.toPlainText().strip()
            },
            "site_images": site_images,
            "seo_global": {
                "site_url": self.txt_seo_site_url.text().strip() if hasattr(self, 'txt_seo_site_url') else "https://ecoluxebharat.com/",
                "site_name": self.txt_seo_site_name.text().strip() if hasattr(self, 'txt_seo_site_name') else "EcoLuxe Bharat",
                "enable_keywords": self.chk_global_enable_keywords.isChecked() if hasattr(self, 'chk_global_enable_keywords') else True,
                "default_keywords": self.txt_seo_keywords.text().strip() if hasattr(self, 'txt_seo_keywords') else "",
                "twitter_username": self.txt_social_twitter.text().strip() if hasattr(self, 'txt_social_twitter') else "",
                "default_og_image": self.txt_seo_default_og_image.text().strip() if hasattr(self, 'txt_seo_default_og_image') and self.txt_seo_default_og_image.text().strip() else getattr(self, 'site_info', {}).get("seo_global", {}).get("default_og_image", "img/branding/og-share-card.jpg")
            },
            "pages_seo": getattr(self, 'site_info', {}).get("pages_seo", {})
        }
        self.save_database()
        self.compile_site()
        QMessageBox.information(self, "Success", "Site page content & global settings saved and website rebuilt successfully!")

    def refresh_clients_table(self):
        self.clients_table.blockSignals(True)
        self.clients_table.setRowCount(0)
        
        for idx, client in enumerate(self.clients):
            self.clients_table.insertRow(idx)
            
            # Column 0: Client Name
            name_item = QTableWidgetItem(client.get("name", f"Client {idx+1}"))
            self.clients_table.setItem(idx, 0, name_item)
            
            # Column 1: Logo path and Icon
            logo_rel = client.get("logo", "")
            logo_abs = os.path.join(WORKSPACE_DIR, logo_rel)
            logo_item = QTableWidgetItem(logo_rel)
            if os.path.exists(logo_abs):
                pixmap = QPixmap(logo_abs).scaled(60, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_item.setIcon(QIcon(pixmap))
            self.clients_table.setItem(idx, 1, logo_item)
            
            # Column 2: Scale
            scale_item = QTableWidgetItem(f"{client.get('scale', 1.0):.1f}x")
            self.clients_table.setItem(idx, 2, scale_item)
            
            # Column 3: Link URL
            link_item = QTableWidgetItem(client.get("link", ""))
            self.clients_table.setItem(idx, 3, link_item)
            
            # Column 4: Link Status
            status_text = "Active" if client.get("link_enabled", False) else "Disabled"
            status_item = QTableWidgetItem(status_text)
            if client.get("link_enabled", False):
                status_item.setForeground(QColor("#50ab3c"))
            else:
                status_item.setForeground(QColor("#888888"))
            self.clients_table.setItem(idx, 4, status_item)
            
        self.clients_table.blockSignals(False)
        self.on_client_selection_changed()

    def on_client_selection_changed(self):
        selected_ranges = self.clients_table.selectedRanges()
        selected_rows = []
        for r in selected_ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                selected_rows.append(row)
        selected_rows = list(set(selected_rows))
        num_selected = len(selected_rows)
        has_sel = num_selected > 0
        is_single = num_selected == 1
        
        self.btn_replace_logo.setEnabled(is_single)
        self.btn_edit_client_link.setEnabled(is_single)
        self.btn_remove_client.setEnabled(has_sel)
        
        curr_row = self.clients_table.currentRow() if is_single else -1
        self.btn_client_up.setEnabled(is_single and curr_row > 0)
        self.btn_client_down.setEnabled(is_single and curr_row >= 0 and curr_row < self.clients_table.rowCount() - 1)
        
        # Manage scale controls directly
        self.scale_slider.blockSignals(True)
        self.scale_text.blockSignals(True)
        
        if is_single and curr_row >= 0 and curr_row < len(self.clients):
            client = self.clients[curr_row]
            self.scale_slider.setEnabled(True)
            self.scale_text.setEnabled(True)
            scale = client.get("scale", 1.0)
            self.scale_slider.setValue(int(scale * 10))
            self.scale_text.setText(f"{scale:.1f}x")
            
            logo_rel = client.get("logo", "")
            logo_abs = os.path.join(WORKSPACE_DIR, logo_rel)
            if os.path.exists(logo_abs):
                pw = int(140 * scale)
                ph = int(70 * scale)
                pw = max(20, min(pw, 200))
                ph = max(10, min(ph, 100))
                pixmap = QPixmap(logo_abs).scaled(pw, ph, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_client_preview.setPixmap(pixmap)
                self.lbl_client_preview.setText("")
            else:
                self.lbl_client_preview.setPixmap(QPixmap())
                self.lbl_client_preview.setText("Image not found")
        else:
            self.scale_slider.setEnabled(False)
            self.scale_text.setEnabled(False)
            self.scale_slider.setValue(10)
            self.scale_text.setText("1.0x")
            self.lbl_client_preview.setPixmap(QPixmap())
            self.lbl_client_preview.setText("No Selection" if not has_sel else f"{num_selected} Selected")
            
        self.scale_slider.blockSignals(False)
        self.scale_text.blockSignals(False)

    def on_scale_slider_changed(self, value):
        val = value / 10.0
        self.scale_text.blockSignals(True)
        self.scale_text.setText(f"{val:.1f}x")
        self.scale_text.blockSignals(False)
        
        curr_row = self.clients_table.currentRow()
        if curr_row >= 0 and curr_row < len(self.clients):
            client = self.clients[curr_row]
            client["scale"] = val
            
            self.clients_table.blockSignals(True)
            self.clients_table.item(curr_row, 2).setText(f"{val:.1f}x")
            self.clients_table.blockSignals(False)
            
            logo_rel = client.get("logo", "")
            logo_abs = os.path.join(WORKSPACE_DIR, logo_rel)
            if os.path.exists(logo_abs):
                pw = int(140 * (val / 2.0))
                ph = int(70 * (val / 2.0))
                pw = max(10, min(pw, 200))
                ph = max(5, min(ph, 100))
                pixmap = QPixmap(logo_abs).scaled(pw, ph, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_client_preview.setPixmap(pixmap)
                self.lbl_client_preview.setText("")

    def on_scale_slider_released(self):
        curr_row = self.clients_table.currentRow()
        if curr_row >= 0 and curr_row < len(self.clients):
            client = self.clients[curr_row]
            self.save_database()
            self.log(f"Scale for client '{client['name']}' updated to {client['scale']}x")
            self.compile_site(show_dialog=False)

    def on_scale_text_changed(self):
        text = self.scale_text.text().lower().replace("x", "").strip()
        try:
            val = float(text)
            val = max(0.1, min(val, 10.0))
            val = round(val, 1)
        except ValueError:
            val = 1.0
            
        curr_row = self.clients_table.currentRow()
        if curr_row >= 0 and curr_row < len(self.clients):
            client = self.clients[curr_row]
            client["scale"] = val
            
            self.scale_slider.blockSignals(True)
            self.scale_slider.setValue(int(val * 10))
            self.scale_slider.blockSignals(False)
            
            self.scale_text.blockSignals(True)
            self.scale_text.setText(f"{val:.1f}x")
            self.scale_text.blockSignals(False)
            
            self.clients_table.blockSignals(True)
            self.clients_table.item(curr_row, 2).setText(f"{val:.1f}x")
            self.clients_table.blockSignals(False)
            
            logo_rel = client.get("logo", "")
            logo_abs = os.path.join(WORKSPACE_DIR, logo_rel)
            if os.path.exists(logo_abs):
                pw = int(140 * (val / 2.0))
                ph = int(70 * (val / 2.0))
                pw = max(10, min(pw, 200))
                ph = max(5, min(ph, 100))
                pixmap = QPixmap(logo_abs).scaled(pw, ph, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_client_preview.setPixmap(pixmap)
                self.lbl_client_preview.setText("")
                
            self.save_database()
            self.log(f"Scale for client '{client['name']}' updated to {client['scale']}x via text box.")
            self.compile_site(show_dialog=False)

    def add_client_logo(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Client Logo Images", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_paths:
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                dest_dir_rel = "img/logo"
                dest_dir_abs = os.path.join(WORKSPACE_DIR, dest_dir_rel)
                os.makedirs(dest_dir_abs, exist_ok=True)
                
                base_name, ext = os.path.splitext(filename)
                uniq_name = filename
                counter = 1
                while os.path.exists(os.path.join(dest_dir_abs, uniq_name)):
                    uniq_name = f"{base_name}_{counter}{ext}"
                    counter += 1
                    
                dest_file_rel = f"{dest_dir_rel}/{uniq_name}"
                dest_file_abs = os.path.join(WORKSPACE_DIR, dest_file_rel)
                
                try:
                    shutil.copy2(file_path, dest_file_abs)
                    default_name = base_name.replace("-", " ").replace("_", " ").title()
                    new_client = {
                        "id": f"client_{int(time.time())}_{uniq_name}",
                        "name": default_name,
                        "logo": dest_file_rel,
                        "link": "#",
                        "link_enabled": False,
                        "scale": 1.0
                    }
                    self.clients.append(new_client)
                    self.log(f"Added new client logo: {dest_file_rel} ({default_name})")
                except Exception as e:
                    self.log(f"Error copying client logo image {filename}: {e}")
                    
            self.save_database()
            self.refresh_clients_table()
            self.compile_site(show_dialog=False)

    def replace_client_logo(self):
        row = self.clients_table.currentRow()
        if row < 0:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Replacement Logo Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            filename = os.path.basename(file_path)
            dest_dir_rel = "img/logo"
            dest_dir_abs = os.path.join(WORKSPACE_DIR, dest_dir_rel)
            os.makedirs(dest_dir_abs, exist_ok=True)
            
            base_name, ext = os.path.splitext(filename)
            uniq_name = filename
            counter = 1
            while os.path.exists(os.path.join(dest_dir_abs, uniq_name)):
                uniq_name = f"{base_name}_{counter}{ext}"
                counter += 1
                
            dest_file_rel = f"{dest_dir_rel}/{uniq_name}"
            dest_file_abs = os.path.join(WORKSPACE_DIR, dest_file_rel)
            
            try:
                # Move old logo file to site_manager/trash/images/ to avoid leaving it orphaned
                old_logo_rel = self.clients[row].get("logo", "")
                old_logo_abs = os.path.join(WORKSPACE_DIR, old_logo_rel)
                if old_logo_rel and os.path.exists(old_logo_abs):
                    dest_dir = os.path.join(TRASH_DIR, "images")
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, os.path.basename(old_logo_rel))
                    if os.path.exists(dest_path):
                        old_base, old_ext = os.path.splitext(os.path.basename(old_logo_rel))
                        c = 1
                        while os.path.exists(os.path.join(dest_dir, f"{old_base}_{c}{old_ext}")):
                            c += 1
                        dest_path = os.path.join(dest_dir, f"{old_base}_{c}{old_ext}")
                    try:
                        shutil.move(old_logo_abs, dest_path)
                        self.log(f"Moved replaced logo asset {old_logo_rel} to trash/images/")
                    except Exception as e:
                        self.log(f"Error moving replaced logo asset: {e}")

                shutil.copy2(file_path, dest_file_abs)
                self.clients[row]["logo"] = dest_file_rel
                self.save_database()
                self.refresh_clients_table()
                self.log(f"Replaced client logo in row {row+1} with: {dest_file_rel}")
                self.compile_site(show_dialog=False)
            except Exception as e:
                self.log(f"Error replacing logo image: {e}")
                QMessageBox.critical(self, "Copy Error", f"Failed to replace logo image: {e}")

    def edit_client_link(self):
        row = self.clients_table.currentRow()
        if row < 0:
            return
            
        client = self.clients[row]
        dialog = ClientEditDialog(self, client)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            client["name"] = data["name"]
            client["link"] = data["link"]
            client["link_enabled"] = data["link_enabled"]
            client["scale"] = data["scale"]
            
            self.save_database()
            self.refresh_clients_table()
            self.log(f"Updated link and name details for client: {client['name']} (Scale: {client['scale']}x)")
            self.compile_site(show_dialog=False)

    def remove_client(self):
        selected_ranges = self.clients_table.selectedRanges()
        selected_rows = []
        for r in selected_ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                selected_rows.append(row)
        selected_rows = sorted(list(set(selected_rows)), reverse=True)
        
        if not selected_rows:
            return
            
        num_selected = len(selected_rows)
        if num_selected == 1:
            row = selected_rows[0]
            confirm = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to remove client '{self.clients[row].get('name')}' from the list?",
                QMessageBox.Yes | QMessageBox.No
            )
        else:
            confirm = QMessageBox.question(
                self, "Confirm Delete Multiple",
                f"Are you sure you want to remove the {num_selected} selected clients from the list?",
                QMessageBox.Yes | QMessageBox.No
            )
            
        if confirm == QMessageBox.Yes:
            for row in selected_rows:
                client = self.clients.pop(row)
                
                # Move removed logo file to site_manager/trash/images/
                logo_rel = client.get("logo", "")
                logo_abs = os.path.join(WORKSPACE_DIR, logo_rel)
                if logo_rel and os.path.exists(logo_abs):
                    dest_dir = os.path.join(TRASH_DIR, "images")
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, os.path.basename(logo_rel))
                    if os.path.exists(dest_path):
                        base_name, ext = os.path.splitext(os.path.basename(logo_rel))
                        counter = 1
                        while os.path.exists(os.path.join(dest_dir, f"{base_name}_{counter}{ext}")):
                            counter += 1
                        dest_path = os.path.join(dest_dir, f"{base_name}_{counter}{ext}")
                    try:
                        shutil.move(logo_abs, dest_path)
                        self.log(f"Moved removed logo asset {logo_rel} to trash/images/")
                    except Exception as e:
                        self.log(f"Error moving logo asset: {e}")
                        
            self.save_database()
            self.refresh_clients_table()
            self.log(f"Removed {num_selected} client logo(s).")
            self.compile_site(show_dialog=False)

    def move_client_up(self):
        row = self.clients_table.currentRow()
        if row > 0:
            self.clients[row], self.clients[row-1] = self.clients[row-1], self.clients[row]
            self.save_database()
            self.refresh_clients_table()
            self.clients_table.setCurrentCell(row-1, 0)
            self.log(f"Moved client logo row {row+1} up to row {row}")
            self.compile_site(show_dialog=False)

    def move_client_down(self):
        row = self.clients_table.currentRow()
        if row >= 0 and row < len(self.clients) - 1:
            self.clients[row], self.clients[row+1] = self.clients[row+1], self.clients[row]
            self.save_database()
            self.refresh_clients_table()
            self.clients_table.setCurrentCell(row+1, 0)
            self.log(f"Moved client logo row {row+1} down to row {row+2}")
            self.compile_site(show_dialog=False)

class ClientEditDialog(QDialog):
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QCheckBox, QLineEdit, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QDoubleSpinBox
        self.client = client
        self.setWindowTitle("Edit Client Details")
        self.resize(450, 250)
        self.setStyleSheet(STYLESHEET)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setText(client.get("name", client.get("id", "")))
        self.name_input.setPlaceholderText("e.g. Acme Corporation")
        
        self.link_input = QLineEdit()
        self.link_input.setText(client.get("link", ""))
        self.link_input.setPlaceholderText("e.g. https://www.clientwebsite.com")
        
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 10.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setValue(client.get("scale", 1.0))
        self.scale_spin.setSuffix("x")
        
        self.enabled_chk = QCheckBox("Enable Logo Link")
        self.enabled_chk.setChecked(client.get("link_enabled", False))
        
        form_layout.addRow("Client Name:", self.name_input)
        form_layout.addRow("Link URL:", self.link_input)
        form_layout.addRow("Scale Multiplier:", self.scale_spin)
        form_layout.addRow("", self.enabled_chk)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("action_btn")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        
    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "link": self.link_input.text().strip(),
            "link_enabled": self.enabled_chk.isChecked(),
            "scale": round(self.scale_spin.value(), 1)
        }

class RearrangeDialog(QDialog):
    def __init__(self, parent, categories, products):
        super().__init__(parent)
        self.setWindowTitle("Rearrange Catalog Sequence")
        self.setMinimumSize(550, 450)
        self.categories = list(categories)
        self.products = list(products)
        self.saved_order = None
        
        layout = QVBoxLayout(self)
        
        # Header description
        info_lbl = QLabel("Drag & drop items to reorder, or use the Move buttons. Click Save to apply changes.")
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet("color: #abb2bf; margin-bottom: 10px;")
        layout.addWidget(info_lbl)
        
        # Controls layout
        ctrl_layout = QHBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Categories", "categories")
        self.mode_combo.addItem("Products under Category", "products")
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        
        self.cat_label = QLabel("Category:")
        self.cat_label.setVisible(False)
        self.cat_combo = QComboBox()
        self.cat_combo.setVisible(False)
        for cat in self.categories:
            self.cat_combo.addItem(cat.get("title", ""), cat.get("slug", ""))
        self.cat_combo.currentIndexChanged.connect(self.load_items)
        
        ctrl_layout.addWidget(QLabel("Mode:"))
        ctrl_layout.addWidget(self.mode_combo, 1)
        ctrl_layout.addWidget(self.cat_label)
        ctrl_layout.addWidget(self.cat_combo, 2)
        
        layout.addLayout(ctrl_layout)
        
        # Main List Widget and Side Buttons
        list_layout = QHBoxLayout()
        
        self.list_widget = QListWidget()
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        list_layout.addWidget(self.list_widget, 4)
        
        # Move up/down buttons on side
        side_layout = QVBoxLayout()
        self.btn_up = QPushButton("Move Up")
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down = QPushButton("Move Down")
        self.btn_down.clicked.connect(self.move_down)
        side_layout.addWidget(self.btn_up)
        side_layout.addWidget(self.btn_down)
        side_layout.addStretch()
        
        list_layout.addLayout(side_layout, 1)
        layout.addLayout(list_layout)
        
        # Save / Cancel Buttons at bottom
        action_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Order")
        self.btn_save.setObjectName("action_btn")
        self.btn_save.clicked.connect(self.save_order_data)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        action_layout.addStretch()
        action_layout.addWidget(self.btn_save)
        action_layout.addWidget(self.btn_cancel)
        layout.addLayout(action_layout)
        
        # Initial load
        self.load_items()

    def on_mode_changed(self):
        is_products = (self.mode_combo.currentData() == "products")
        self.cat_label.setVisible(is_products)
        self.cat_combo.setVisible(is_products)
        self.load_items()

    def load_items(self):
        self.list_widget.clear()
        mode = self.mode_combo.currentData()
        
        if mode == "categories":
            for cat in self.categories:
                item = QListWidgetItem(cat.get("title", ""))
                item.setData(Qt.UserRole, cat.get("slug", ""))
                self.list_widget.addItem(item)
        else:
            cat_slug = self.cat_combo.currentData()
            if not cat_slug:
                return
            cat_prods = [p for p in self.products if p.get("category_slug") == cat_slug]
            for prod in cat_prods:
                item = QListWidgetItem(f"{prod.get('title', '')} ({prod.get('model', '')})")
                item.setData(Qt.UserRole, prod.get("id", ""))
                self.list_widget.addItem(item)

    def move_up(self):
        curr_row = self.list_widget.currentRow()
        if curr_row > 0:
            item = self.list_widget.takeItem(curr_row)
            self.list_widget.insertItem(curr_row - 1, item)
            self.list_widget.setCurrentRow(curr_row - 1)

    def move_down(self):
        curr_row = self.list_widget.currentRow()
        if curr_row >= 0 and curr_row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(curr_row)
            self.list_widget.insertItem(curr_row + 1, item)
            self.list_widget.setCurrentRow(curr_row + 1)

    def save_order_data(self):
        mode = self.mode_combo.currentData()
        ordered_keys = []
        for i in range(self.list_widget.count()):
            ordered_keys.append(self.list_widget.item(i).data(Qt.UserRole))
            
        if mode == "categories":
            self.saved_order = {
                "type": "categories",
                "order": ordered_keys
            }
        else:
            self.saved_order = {
                "type": "products",
                "category_slug": self.cat_combo.currentData(),
                "order": ordered_keys
            }
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
