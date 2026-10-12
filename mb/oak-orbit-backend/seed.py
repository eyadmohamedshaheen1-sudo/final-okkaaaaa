"""Seed organized demo data: admins, sellers (with shops + products), buyers.

Run once:  python seed.py   (safe to re-run, skips existing rows).
To fully reset: delete the instance/ folder, then run seed.py again.
"""
import sqlite3
import time

from werkzeug.security import generate_password_hash

from db import DB_PATH, init_db

now = lambda: int(time.time() * 1000)

ADMINS = [
    ("Store Admin", "admin@oakorbit.com", "Admin@123"),
    ("Super Admin", "root@oakorbit.com",  "Root@123"),
]

SELLERS = [
    ("Omar Hassan", "omar@niletech.com",  "Seller@123", "Nile Tech"),
    ("Sara Adel",   "sara@cozyhome.com",  "Seller@123", "Cozy Home"),
    ("Laila Nabil", "laila@stylehub.com", "Seller@123", "Style Hub"),
    ("Mona Samy",   "mona@fitlife.com",   "Seller@123", "Fit Life"),
]

BUYERS = [
    ("Karim Ali",    "karim@example.com", "Buyer@123"),
    ("Nour Mostafa", "nour@example.com",  "Buyer@123"),
    ("Hana Youssef", "hana@example.com",  "Buyer@123"),
]

# منتجات كل بائع حسب متجره
CATALOG = {
    "Nile Tech": [
        ("Studio Headphones", "Tech", 129, "🎧", "Wireless, 40h battery"),
        ("Smart Watch", "Tech", 179, "⌚", "Heart rate and GPS"),
        ("Bluetooth Speaker", "Tech", 64, "🔊", "Waterproof, 12h playtime"),
        ("Mechanical Keyboard", "Tech", 99, "⌨️", "Hot-swappable switches"),
        ("Power Bank 20,000 mAh", "Tech", 29, "🔋", "Fast charging, two USB ports"),
        ("Gaming Mouse", "Tech", 45, "🖱️", "Lightweight, 12,000 DPI"),
    ],
    "Cozy Home": [
        ("Ceramic Plant Pot", "Home", 24, "🪴", "Hand-glazed, 20 cm"),
        ("Pour-Over Coffee Set", "Home", 58, "☕", "Dripper, carafe and filters"),
        ("Desk Lamp", "Home", 42, "💡", "Dimmable warm light"),
        ("Soy Candle", "Home", 18, "🕯️", "Cedar and amber, 40h burn"),
        ("Knit Throw Blanket", "Home", 48, "🛋️", "Soft cotton, 130 x 170 cm"),
        ("Minimal Wall Clock", "Home", 33, "🕰️", "Silent movement, 30 cm"),
    ],
    "Style Hub": [
        ("Trail Runner Shoes", "Style", 89, "👟", "Light and grippy"),
        ("Canvas Backpack", "Style", 74, "🎒", 'Fits a 15" laptop'),
        ("Sunglasses", "Style", 49, "🕶️", "Polarized, UV400"),
        ("Denim Jacket", "Style", 95, "🧥", "Washed cotton, relaxed fit"),
        ("Wool Scarf", "Style", 28, "🧣", "Warm, soft and lightweight"),
        ("Leather Wallet", "Style", 39, "👛", "Slim, holds 8 cards"),
    ],
    "Fit Life": [
        ("Non-Slip Yoga Mat", "Sports", 35, "🧘", "6 mm cushioning, carry strap"),
        ("Adjustable Dumbbell Set", "Sports", 69, "🏋️", "2 to 12 kg per hand"),
        ("Match Football", "Sports", 25, "⚽", "Size 5, durable stitching"),
        ("Insulated Water Bottle", "Sports", 17, "🥤", "Keeps drinks cold for 24h"),
        ("Cycling Helmet", "Sports", 59, "🚴", "Lightweight with rear light"),
    ],
}

# منتجات مملوكة للمتجر نفسه (حساب الأدمن)
STORE_CATALOG = [
    ("Hydrating Serum", "Beauty", 32, "🧴", "Hyaluronic acid, 30 ml"),
    ("Matte Lipstick", "Beauty", 19, "💄", "Long-wear, 12 shades"),
    ("Floral Perfume", "Beauty", 78, "🌸", "Eau de parfum, 50 ml"),
    ("Chef Knife", "Kitchen", 54, "🔪", "Stainless steel, 20 cm blade"),
    ("Air Fryer 5L", "Kitchen", 119, "🍟", "Digital presets, easy clean"),
    ("Glass Tea Kettle", "Kitchen", 38, "🫖", "1.7 L with auto shut-off"),
    ("Cast Iron Pan", "Kitchen", 44, "🍳", "Pre-seasoned, 26 cm"),
]


def run():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM settings WHERE id = 1")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO settings (id, ship, express, free_over, commission, announcement, support_email) "
            "VALUES (1, 5, 15, 50, 10, "
            "'Free shipping over $50. Use code WELCOME10 for 10% off your order.', 'support@oakorbit.com')"
        )

    cur.execute("SELECT 1 FROM promo_codes WHERE code='WELCOME10'")
    if not cur.fetchone():
        cur.execute("INSERT INTO promo_codes (code, pct, active) VALUES ('WELCOME10', 10, 1)")

    # ---- admins ----
    for name, email, pw in ADMINS:
        cur.execute("SELECT 1 FROM users WHERE email=?", (email,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (name,email,password_hash,role,shop,status,created_at) "
                "VALUES (?,?,?,'admin','','active',?)",
                (name, email, generate_password_hash(pw), now()),
            )

    # ---- sellers + their products (seller_id مربوط بصاحب المتجر) ----
    for name, email, pw, shop in SELLERS:
        cur.execute("SELECT id FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        if row:
            sid = row["id"]
        else:
            cur.execute(
                "INSERT INTO users (name,email,password_hash,role,shop,status,created_at) "
                "VALUES (?,?,?,'seller',?,'active',?)",
                (name, email, generate_password_hash(pw), shop, now()),
            )
            sid = cur.lastrowid
        for pname, cat, price, emoji, desc in CATALOG[shop]:
            cur.execute("SELECT 1 FROM products WHERE name=? AND seller_id=?", (pname, sid))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO products (name,category,price,stock,description,emoji,bg,base_rating,"
                    "images_json,hidden,seller_id) VALUES (?,?,?,25,?,?,?,'4.5','[]',0,?)",
                    (pname, cat, price, desc, emoji, "#eee", sid),
                )

    # ---- store-owned products (Beauty / Kitchen) ----
    cur.execute("SELECT id FROM users WHERE email='admin@oakorbit.com'")
    row = cur.fetchone()
    store_id = row["id"] if row else None
    for pname, cat, price, emoji, desc in STORE_CATALOG:
        cur.execute("SELECT 1 FROM products WHERE name=?", (pname,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO products (name,category,price,stock,description,emoji,bg,base_rating,"
                "images_json,hidden,seller_id) VALUES (?,?,?,25,?,?,?,'4.5','[]',0,?)",
                (pname, cat, price, desc, emoji, "#eee", store_id),
            )

    # ---- buyers ----
    for name, email, pw in BUYERS:
        cur.execute("SELECT 1 FROM users WHERE email=?", (email,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (name,email,password_hash,role,shop,status,created_at) "
                "VALUES (?,?,?,'buyer','','active',?)",
                (name, email, generate_password_hash(pw), now()),
            )

    conn.commit()
    conn.close()
    print("Seed complete.")
    print("  Admin : admin@oakorbit.com / Admin@123")
    print("          root@oakorbit.com  / Root@123")
    print("  Seller: omar@niletech.com  / Seller@123  (+ sara, laila, mona)")
    print("  Buyer : karim@example.com  / Buyer@123   (+ nour, hana)")


if __name__ == "__main__":
    run()