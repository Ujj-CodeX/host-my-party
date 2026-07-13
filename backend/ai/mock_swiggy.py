# Mock Swiggy Data — All distances are from host's dummy address (Kondapur, Hyderabad)
# distanceKm is hardcoded; in production this would come from Swiggy's geolocation API

RESTAURANTS = [
    # ── EXISTING ──────────────────────────────────────────────────────────────
    {
        "id": "rest_001",
        "name": "Punjab Grill",
        "cuisines": ["North Indian", "Punjabi", "Biryani"],
        "rating": 4.3,
        "deliveryTime": "30-35 mins",
        "deliveryMins": 33,
        "distanceKm": 1.2,
        "availabilityStatus": "OPEN",
        "costForTwo": 600,
        "menu": [
            {"id": "item_001", "name": "Paneer Butter Masala", "price": 280, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_002", "name": "Dal Makhani", "price": 220, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_003", "name": "Chicken Tikka", "price": 320, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_004", "name": "Tandoori Roti", "price": 40, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_005", "name": "Jeera Rice", "price": 160, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_006", "name": "Butter Naan", "price": 55, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
        ]
    },
    {
        "id": "rest_002",
        "name": "Barbeque Nation",
        "cuisines": ["Barbecue", "Multi-Cuisine"],
        "rating": 4.5,
        "deliveryTime": "45-50 mins",
        "deliveryMins": 48,
        "distanceKm": 2.8,
        "availabilityStatus": "OPEN",
        "costForTwo": 800,
        "menu": [
            {"id": "item_007", "name": "Veg Seekh Kebab", "price": 260, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_008", "name": "Mutton Seekh Kebab", "price": 380, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_009", "name": "Paneer Tikka", "price": 300, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_010", "name": "Fish Tikka", "price": 350, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
        ]
    },
    {
        "id": "rest_003",
        "name": "Satvic Jain Kitchen",
        "cuisines": ["Jain", "Pure Veg"],
        "rating": 4.1,
        "deliveryTime": "25-30 mins",
        "deliveryMins": 28,
        "distanceKm": 0.9,
        "availabilityStatus": "OPEN",
        "costForTwo": 400,
        "menu": [
            {"id": "item_011", "name": "Jain Dal Baati Churma", "price": 240, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_012", "name": "Jain Paneer Sabzi", "price": 210, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_013", "name": "Jain Khichdi", "price": 150, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_014", "name": "Jain Chapati (4 pcs)", "price": 60, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
        ]
    },
    {
        "id": "rest_004",
        "name": "Green Bowl Vegan Co.",
        "cuisines": ["Vegan", "Healthy"],
        "rating": 4.2,
        "deliveryTime": "35-40 mins",
        "deliveryMins": 38,
        "distanceKm": 1.8,
        "availabilityStatus": "OPEN",
        "costForTwo": 550,
        "menu": [
            {"id": "item_015", "name": "Vegan Buddha Bowl", "price": 290, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_016", "name": "Tofu Stir Fry", "price": 260, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_017", "name": "Multigrain Wrap", "price": 180, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_018", "name": "Chia Seed Pudding", "price": 120, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
        ]
    },
    {
        "id": "rest_005",
        "name": "Spice Route Non-Veg",
        "cuisines": ["Mughlai", "Non-Veg", "Biryani"],
        "rating": 4.4,
        "deliveryTime": "40-45 mins",
        "deliveryMins": 42,
        "distanceKm": 3.5,
        "availabilityStatus": "OPEN",
        "costForTwo": 700,
        "menu": [
            {"id": "item_019", "name": "Butter Chicken", "price": 340, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_020", "name": "Mutton Biryani", "price": 420, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_021", "name": "Egg Curry", "price": 220, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_022", "name": "Rumali Roti", "price": 35, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
        ]
    },
    {
        "id": "rest_006",
        "name": "DiabEats Health Kitchen",
        "cuisines": ["Healthy", "Low GI"],
        "rating": 4.0,
        "deliveryTime": "30-35 mins",
        "deliveryMins": 32,
        "distanceKm": 2.2,
        "availabilityStatus": "OPEN",
        "costForTwo": 480,
        "menu": [
            {"id": "item_023", "name": "Millets Bowl", "price": 200, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_024", "name": "Grilled Chicken Salad", "price": 280, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_025", "name": "Quinoa Khichdi", "price": 220, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_026", "name": "Steamed Fish Fillet", "price": 320, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
        ]
    },

    # ── PIZZA ─────────────────────────────────────────────────────────────────
    {
        "id": "rest_007",
        "name": "Domino's Pizza",
        "cuisines": ["Pizza", "Italian", "Fast Food"],
        "rating": 4.2,
        "deliveryTime": "25-30 mins",
        "deliveryMins": 27,
        "distanceKm": 1.0,
        "availabilityStatus": "OPEN",
        "costForTwo": 500,
        "menu": [
            {"id": "item_027", "name": "Margherita Pizza (M)", "price": 239, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_028", "name": "Peppy Paneer Pizza (M)", "price": 349, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_029", "name": "Chicken Dominator (M)", "price": 499, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_030", "name": "Farmhouse Pizza (M)", "price": 399, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_031", "name": "Garlic Breadsticks", "price": 109, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_032", "name": "Cheese Dip", "price": 49, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
        ]
    },
    {
        "id": "rest_008",
        "name": "La Pino'z Pizza",
        "cuisines": ["Pizza", "Italian"],
        "rating": 4.1,
        "deliveryTime": "30-35 mins",
        "deliveryMins": 32,
        "distanceKm": 1.5,
        "availabilityStatus": "OPEN",
        "costForTwo": 450,
        "menu": [
            {"id": "item_033", "name": "Cheesy 7 Pizza (M)", "price": 345, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_034", "name": "Burn to Hell Pizza (M)", "price": 425, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_035", "name": "Veg Overloaded Pizza (M)", "price": 365, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_036", "name": "Jain Margherita Pizza (M)", "price": 299, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_037", "name": "Choco Lava Cake", "price": 110, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
        ]
    },
    {
        "id": "rest_009",
        "name": "Pizza Hut",
        "cuisines": ["Pizza", "Italian", "Fast Food"],
        "rating": 4.0,
        "deliveryTime": "35-40 mins",
        "deliveryMins": 37,
        "distanceKm": 2.1,
        "availabilityStatus": "OPEN",
        "costForTwo": 550,
        "menu": [
            {"id": "item_038", "name": "Veggie Supreme Pizza (M)", "price": 379, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_039", "name": "Chicken BBQ Pizza (M)", "price": 449, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_040", "name": "Paneer Makhani Pizza (M)", "price": 399, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_041", "name": "Stuffed Garlic Bread", "price": 149, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_042", "name": "Coleslaw", "price": 79, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
        ]
    },

    # ── BURGERS ───────────────────────────────────────────────────────────────
    {
        "id": "rest_010",
        "name": "Burger Singh",
        "cuisines": ["Burgers", "Fast Food", "American"],
        "rating": 4.3,
        "deliveryTime": "20-25 mins",
        "deliveryMins": 22,
        "distanceKm": 0.8,
        "availabilityStatus": "OPEN",
        "costForTwo": 400,
        "menu": [
            {"id": "item_043", "name": "Punjab Da Burger (Veg)", "price": 189, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_044", "name": "Udta Punjab Chicken Burger", "price": 249, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_045", "name": "Aloo Tikki Burger", "price": 149, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_046", "name": "Crispy Veg Burger", "price": 169, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_047", "name": "Large Fries", "price": 99, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_048", "name": "Masala Buttermilk", "price": 59, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
        ]
    },
    {
        "id": "rest_011",
        "name": "McDonald's",
        "cuisines": ["Burgers", "Fast Food", "American"],
        "rating": 4.1,
        "deliveryTime": "20-25 mins",
        "deliveryMins": 23,
        "distanceKm": 1.1,
        "availabilityStatus": "OPEN",
        "costForTwo": 350,
        "menu": [
            {"id": "item_049", "name": "McVeggie Burger", "price": 149, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_050", "name": "McAloo Tikki Burger", "price": 109, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_051", "name": "McSpicy Chicken Burger", "price": 219, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_052", "name": "Mc Egg Burger", "price": 149, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_053", "name": "Medium Fries", "price": 119, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_054", "name": "McFlurry Oreo", "price": 89, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
        ]
    },
    {
        "id": "rest_012",
        "name": "Burger King",
        "cuisines": ["Burgers", "Fast Food", "American"],
        "rating": 4.0,
        "deliveryTime": "25-30 mins",
        "deliveryMins": 27,
        "distanceKm": 1.6,
        "availabilityStatus": "OPEN",
        "costForTwo": 380,
        "menu": [
            {"id": "item_055", "name": "Veg Whopper", "price": 199, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_056", "name": "Chicken Whopper", "price": 259, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_057", "name": "Paneer King Burger", "price": 179, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_058", "name": "Crispy Veg Burger", "price": 139, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_059", "name": "Onion Rings", "price": 89, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_060", "name": "Choco Shake", "price": 99, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
        ]
    },

    # ── BIRYANI ───────────────────────────────────────────────────────────────
    {
        "id": "rest_013",
        "name": "Behrouz Biryani",
        "cuisines": ["Biryani", "Mughlai", "Non-Veg"],
        "rating": 4.5,
        "deliveryTime": "40-45 mins",
        "deliveryMins": 43,
        "distanceKm": 2.0,
        "availabilityStatus": "OPEN",
        "costForTwo": 750,
        "menu": [
            {"id": "item_061", "name": "Subz-e-Falafel Biryani (Veg)", "price": 329, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_062", "name": "Murgh Afghani Biryani", "price": 449, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_063", "name": "Gosht Biryani (Mutton)", "price": 499, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_064", "name": "Prawn Biryani", "price": 479, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_065", "name": "Burhani Raita", "price": 89, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_066", "name": "Gulab Jamun (2 pcs)", "price": 89, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
        ]
    },
    {
        "id": "rest_014",
        "name": "Biryani Blues",
        "cuisines": ["Biryani", "Hyderabadi", "North Indian"],
        "rating": 4.3,
        "deliveryTime": "35-40 mins",
        "deliveryMins": 38,
        "distanceKm": 1.4,
        "availabilityStatus": "OPEN",
        "costForTwo": 600,
        "menu": [
            {"id": "item_067", "name": "Hyderabadi Veg Biryani", "price": 279, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_068", "name": "Hyderabadi Chicken Biryani", "price": 369, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_069", "name": "Mutton Dum Biryani", "price": 449, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_070", "name": "Jain Veg Biryani", "price": 299, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_071", "name": "Salan Gravy", "price": 79, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_072", "name": "Mirchi Ka Salan", "price": 99, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
        ]
    },
    {
        "id": "rest_015",
        "name": "Paradise Biryani",
        "cuisines": ["Biryani", "Hyderabadi"],
        "rating": 4.6,
        "deliveryTime": "45-50 mins",
        "deliveryMins": 47,
        "distanceKm": 3.0,
        "availabilityStatus": "OPEN",
        "costForTwo": 700,
        "menu": [
            {"id": "item_073", "name": "Special Chicken Biryani", "price": 399, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_074", "name": "Special Mutton Biryani", "price": 479, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_075", "name": "Veg Dum Biryani", "price": 299, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_076", "name": "Diabetic Friendly Millets Biryani", "price": 349, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_077", "name": "Egg Biryani", "price": 299, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_078", "name": "Shorba Soup", "price": 99, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
        ]
    },

    # ── CHINESE ───────────────────────────────────────────────────────────────
    {
        "id": "rest_016",
        "name": "Wow! China",
        "cuisines": ["Chinese", "Asian", "Indo-Chinese"],
        "rating": 4.2,
        "deliveryTime": "25-30 mins",
        "deliveryMins": 27,
        "distanceKm": 1.3,
        "availabilityStatus": "OPEN",
        "costForTwo": 450,
        "menu": [
            {"id": "item_079", "name": "Veg Hakka Noodles", "price": 179, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_080", "name": "Chicken Hakka Noodles", "price": 229, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_081", "name": "Veg Fried Rice", "price": 169, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_082", "name": "Chicken Fried Rice", "price": 219, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_083", "name": "Veg Manchurian (Dry)", "price": 199, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_084", "name": "Chilli Paneer (Dry)", "price": 249, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_085", "name": "Chicken Manchurian", "price": 279, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
        ]
    },
    {
        "id": "rest_017",
        "name": "Chinese Wok",
        "cuisines": ["Chinese", "Indo-Chinese", "Asian"],
        "rating": 4.0,
        "deliveryTime": "30-35 mins",
        "deliveryMins": 32,
        "distanceKm": 2.3,
        "availabilityStatus": "OPEN",
        "costForTwo": 400,
        "menu": [
            {"id": "item_086", "name": "Veg Spring Rolls (6 pcs)", "price": 149, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_087", "name": "Chicken Spring Rolls (6 pcs)", "price": 199, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_088", "name": "Kung Pao Tofu", "price": 229, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_089", "name": "Steamed Veg Dimsums (6 pcs)", "price": 199, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_090", "name": "Chicken Dimsums (6 pcs)", "price": 249, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_091", "name": "Schezwan Egg Fried Rice", "price": 199, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_092", "name": "Honey Chilli Potato", "price": 179, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
        ]
    },
    {
        "id": "rest_018",
        "name": "Dragon House",
        "cuisines": ["Chinese", "Asian", "Thai"],
        "rating": 4.3,
        "deliveryTime": "35-40 mins",
        "deliveryMins": 37,
        "distanceKm": 3.2,
        "availabilityStatus": "OPEN",
        "costForTwo": 500,
        "menu": [
            {"id": "item_093", "name": "Veg Tom Yum Soup", "price": 179, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_094", "name": "Chicken Tom Yum Soup", "price": 219, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_095", "name": "Veg Thai Green Curry", "price": 279, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
            {"id": "item_096", "name": "Chicken Thai Green Curry", "price": 329, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
            {"id": "item_097", "name": "Steamed Rice", "price": 89, "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
            {"id": "item_098", "name": "Veg Pad Thai Noodles", "price": 249, "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
            {"id": "item_099", "name": "Prawn Pad Thai", "price": 349, "isVeg": False, "isJainCompatible": False, "isDiabeticFriendly": True},
        ]
    },
]

# ── UPSELL ITEMS ──────────────────────────────────────────────────────────────
UPSELL_ITEMS = [
    {"id": "upsell_001", "name": "Gulab Jamun (4 pcs)", "price": 120, "category": "Dessert", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
    {"id": "upsell_002", "name": "Raita Bowl", "price": 80, "category": "Side", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
    {"id": "upsell_003", "name": "Masala Papad (3 pcs)", "price": 60, "category": "Starter", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
    {"id": "upsell_004", "name": "Mango Lassi", "price": 100, "category": "Drink", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
    {"id": "upsell_005", "name": "Mineral Water (1L)", "price": 40, "category": "Drink", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
    {"id": "upsell_006", "name": "Choco Lava Cake", "price": 130, "category": "Dessert", "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
    {"id": "upsell_007", "name": "Butter Garlic Bread", "price": 110, "category": "Starter", "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
    {"id": "upsell_008", "name": "Cold Brew Coffee", "price": 150, "category": "Drink", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
    {"id": "upsell_009", "name": "Fruit Custard Cup", "price": 90, "category": "Dessert", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
    {"id": "upsell_010", "name": "Jain Halwa", "price": 100, "category": "Dessert", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
    {"id": "upsell_011", "name": "Coke (330ml)", "price": 60, "category": "Drink", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
    {"id": "upsell_012", "name": "Veg Soup Bowl", "price": 90, "category": "Starter", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
    {"id": "upsell_013", "name": "Chocolate Brownie", "price": 110, "category": "Dessert", "isVeg": True, "isJainCompatible": False, "isDiabeticFriendly": False},
    {"id": "upsell_014", "name": "Jain Kheer", "price": 80, "category": "Dessert", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": False},
    {"id": "upsell_015", "name": "Green Tea", "price": 50, "category": "Drink", "isVeg": True, "isJainCompatible": True, "isDiabeticFriendly": True},
]


def _item_passes_pref(item, pref):
    p = pref.lower().strip()
    if p == 'jain':
        return item['isJainCompatible']
    elif p in ('veg', 'pure veg', 'vegan'):
        return item['isVeg']
    elif p == 'diabetic':
        return item['isDiabeticFriendly']
    else:  # non-veg, any
        return True


def get_restaurants_for_guest(pref, max_distance_km=5.0):
    matching = []
    for r in RESTAURANTS:
        if r['distanceKm'] > max_distance_km:
            continue
        if r['availabilityStatus'] != 'OPEN':
            continue
        eligible_items = [i for i in r['menu'] if _item_passes_pref(i, pref)]
        if eligible_items:
            matching.append({**r, 'eligibleMenu': eligible_items})
    matching.sort(key=lambda x: x['distanceKm'])
    return matching


def get_mock_restaurants(query, guests):
    return {
        "success": True,
        "data": {"restaurants": RESTAURANTS},
        "message": f"Found {len(RESTAURANTS)} restaurants near you"
    }


def get_upsell_items_for_guests(guests):
    safe = []
    for item in UPSELL_ITEMS:
        if all(_item_passes_pref(item, g.get('pref', 'any')) for g in guests):
            safe.append(item)
    return safe