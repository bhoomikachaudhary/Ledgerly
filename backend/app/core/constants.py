DEFAULT_CATEGORIES: list[dict[str, str]] = [
    {"name": "Food", "color": "#f97316", "icon": "utensils"},
    {"name": "Travel", "color": "#3b82f6", "icon": "plane"},
    {"name": "Rent", "color": "#8b5cf6", "icon": "home"},
    {"name": "Utilities", "color": "#eab308", "icon": "zap"},
    {"name": "Shopping", "color": "#ec4899", "icon": "shopping-bag"},
    {"name": "Health", "color": "#22c55e", "icon": "heart-pulse"},
    {"name": "Entertainment", "color": "#06b6d4", "icon": "film"},
    {"name": "Other", "color": "#64748b", "icon": "tag"},
]

RECEIPT_MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
RECEIPT_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
