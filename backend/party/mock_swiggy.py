def get_mock_restaurants(query, guests):
    return {
        "success": True,
        "data": {
            "restaurants": [
                {
                    "id": "rest_001",
                    "name": "Punjab Grill",
                    "cuisines": ["North Indian", "Punjabi"],
                    "rating": 4.3,
                    "deliveryTime": "30-35 mins",
                    "distanceKm": 2.1,
                    "availabilityStatus": "OPEN",
                    "costForTwo": 600,
                    "menu": [
                        {
                            "id": "item_001",
                            "name": "Paneer Butter Masala",
                            "price": 280,
                            "isVeg": True,
                            "isJainCompatible": True,
                            "isDiabeticFriendly": False
                        },
                        {
                            "id": "item_002",
                            "name": "Dal Makhani",
                            "price": 220,
                            "isVeg": True,
                            "isJainCompatible": True,
                            "isDiabeticFriendly": True
                        },
                        {
                            "id": "item_003",
                            "name": "Chicken Tikka",
                            "price": 320,
                            "isVeg": False,
                            "isJainCompatible": False,
                            "isDiabeticFriendly": True
                        },
                        {
                            "id": "item_004",
                            "name": "Tandoori Roti",
                            "price": 40,
                            "isVeg": True,
                            "isJainCompatible": True,
                            "isDiabeticFriendly": True
                        }
                    ]
                },
                {
                    "id": "rest_002",
                    "name": "Barbeque Nation",
                    "cuisines": ["Barbecue", "Multi-Cuisine"],
                    "rating": 4.5,
                    "deliveryTime": "45-50 mins",
                    "distanceKm": 3.8,
                    "availabilityStatus": "OPEN",
                    "costForTwo": 800,
                    "menu": [
                        {
                            "id": "item_005",
                            "name": "Veg Seekh Kebab",
                            "price": 260,
                            "isVeg": True,
                            "isJainCompatible": False,
                            "isDiabeticFriendly": True
                        },
                        {
                            "id": "item_006",
                            "name": "Mutton Seekh Kebab",
                            "price": 380,
                            "isVeg": False,
                            "isJainCompatible": False,
                            "isDiabeticFriendly": True
                        }
                    ]
                }
            ]
        },
        "message": "Found 2 restaurants near you"
    }