# ============================================================
# CloudOven — Sarah Intent Library
# CloudStaff Kenya · Case Study One
# 
# Brand tone: Warm, homemade, rare, classy.
#             From the clan to the era.
#             Natural Kenyan English + Swahili touches.
# ============================================================

INTENTS = [

    # ════════════════════════════════════════════════════════
    # GREETINGS & OPENERS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "hi", "hello", "hey", "hii", "habari", "mambo", "niaje", "sasa",
            "good morning", "good afternoon", "good evening", "asubuhi", "alasiri",
            "howdy", "sup", "whatsup", "what's up", "uko aje", "uko hapo",
            "hujambo", "jambo", "karibu", "salut", "ello", "helloo", "hellooo",
            "good day", "greetings", "morning", "evening", "afternoon",
            "poa", "safi", "freshi", "fresh", "intro", "introduce",
            "start", "begin", "first time", "new here", "new customer"
        ],
        "category": "smalltalk",
        "topic": "greeting",
        "intent": "greet_customer",
        "priority": 5,
        "responses": [
            "Hey! 🍪 Welcome to CloudOven — baked fresh in Machakos. We make cookies and cupcakes that hit different. What can I get for you today?",
            "Habari! You've reached CloudOven 🍪 Machakos' finest homemade cookies. Want to see our menu or place an order?",
            "Hello hello! Welcome to CloudOven — where every cookie is baked with love from Machakos 🍪 What are you looking for today?",
            "Hey, karibu sana! 🍪 CloudOven here — fresh cookies, real flavours, no shortcuts. What can I help you with?",
            "Niaje! Welcome to CloudOven 🍪 We bake it, you love it. Ready to see what we've got?",
        ],
        "follow_up": "Would you like to see our full menu? 😊",
    },

    # ════════════════════════════════════════════════════════
    # FULL MENU REQUEST
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "menu", "menu yenu", "what do you have", "what do you sell",
            "what cookies", "show me cookies", "what flavours", "what flavors",
            "options", "choices", "list", "all cookies", "cookie list",
            "products", "what's available", "what is available", "available cookies",
            "mnauza nini", "mna nini", "mna cookies gani", "cookie gani",
            "flavour gani", "bei zenu", "nini mna", "uza nini", "naweza pata nini",
            "orodha", "catalogue", "catalog", "full menu", "complete menu",
            "everything", "all items", "all products", "what you got",
            "show menu", "see menu", "tell me about your cookies"
        ],
        "category": "transactional",
        "topic": "menu",
        "intent": "show_full_menu",
        "priority": 10,
        "responses": [
            "Here's what's fresh at CloudOven today 🍪\n\n🍪 Chocolate Chip — KSh 150\n🍫 Double Chocolate — KSh 180\n🥜 Peanut Butter — KSh 170\n🌾 Oatmeal Raisin — KSh 10\n🌰 White Choc Macadamia — KSh 200\n❤️ Red Velvet — KSh 190\n🧁 CupCake (dark choc spread) — KSh 199\n\nAll baked fresh. You can also order online at cloudoven.vercel.app 🔗",
            "Our CloudOven menu 🍪✨\n\n1. Chocolate Chip — KSh 150\n2. Double Chocolate — KSh 180\n3. Peanut Butter — KSh 170\n4. Oatmeal Raisin — KSh 10\n5. White Choc Macadamia — KSh 200\n6. Red Velvet — KSh 190\n7. CupCake (dark choc spread) — KSh 199\n\nPickup at Kenya Israel, Machakos. Order online too 👉 cloudoven.vercel.app",
            "Fresh from the oven today 🔥\n\n🍪 Choc Chip · 150/-\n🍫 Double Choc · 180/-\n🥜 Peanut Butter · 170/-\n🌾 Oatmeal Raisin · 10/-\n🌰 White Choc Macadamia · 200/-\n❤️ Red Velvet · 190/-\n🧁 CupCake · 199/-\n\nCome through Kenya Israel or order online at cloudoven.vercel.app 🍪",
        ],
        "follow_up": "Which one catches your eye? 👀",
    },

    # ════════════════════════════════════════════════════════
    # CHOCOLATE CHIP
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "chocolate chip", "choc chip", "classic cookie", "chocolate chunks",
            "chips", "chip cookie", "the classic", "regular cookie",
            "chocolate chip cookie", "bei ya choc chip", "choc chip ngapi"
        ],
        "category": "transactional",
        "topic": "product_chocolate_chip",
        "intent": "product_info_chocolate_chip",
        "priority": 8,
        "responses": [
            "🍪 Chocolate Chip — KSh 150\nThe original. Rich chocolate chunks baked into a soft, golden cookie. The one that started it all. Classic for a reason.",
            "Our Chocolate Chip is KSh 150 🍪 Soft in the middle, slightly crisp on the edges, loaded with real chocolate chunks. If you're a first-timer, this is the one to start with.",
            "Chocolate Chip cookie — KSh 150 🍪 Classic with rich chocolate chunks. Rated 4.9 by our customers. Can't go wrong with this one!",
        ],
        "follow_up": "Want to add anything else to your order?",
    },

    # ════════════════════════════════════════════════════════
    # DOUBLE CHOCOLATE
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "double chocolate", "double choc", "extra chocolate", "more chocolate",
            "chocolate overload", "dark cookie", "choco choco", "double choco",
            "for chocolate lovers", "serious chocolate", "bei ya double chocolate"
        ],
        "category": "transactional",
        "topic": "product_double_chocolate",
        "intent": "product_info_double_chocolate",
        "priority": 8,
        "responses": [
            "🍫 Double Chocolate — KSh 180\nFor serious chocolate lovers only. This isn't your average cookie — it's a full chocolate experience. Chocolate dough, chocolate chunks, pure indulgence.",
            "Double Chocolate is KSh 180 🍫 Think rich cocoa dough loaded with extra chocolate pieces. If Chocolate Chip is level one, this is the final boss. Rated 4.8 ⭐",
            "Our Double Chocolate cookie 🍫 — KSh 180. Baked for those who believe one layer of chocolate is never enough. It goes hard.",
        ],
        "follow_up": "This one pairs well with the Red Velvet if you want variety 😏",
    },

    # ════════════════════════════════════════════════════════
    # PEANUT BUTTER
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "peanut butter", "peanut", "groundnut", "butter cookie", "pb cookie",
            "peanut cookie", "bei ya peanut", "peanut ngapi", "creamy", "crunchy cookie",
            "peanut butter cookie", "groundnut cookie"
        ],
        "category": "transactional",
        "topic": "product_peanut_butter",
        "intent": "product_info_peanut_butter",
        "priority": 8,
        "responses": [
            "🥜 Peanut Butter — KSh 170\nCreamy and crunchy perfection. Real peanut butter baked into every bite. If you're a groundnut fan, this cookie was made for you.",
            "Peanut Butter cookie is KSh 170 🥜 That perfect balance of creamy and crunchy — rich peanut flavour that hits from the first bite. Rated 4.7 ⭐",
            "Our Peanut Butter cookie — KSh 170 🥜 For those who put peanut butter on everything anyway. You'll love this one.",
        ],
        "follow_up": "Still deciding? Want me to suggest a combo? 😊",
    },

    # ════════════════════════════════════════════════════════
    # OATMEAL RAISIN
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "oatmeal", "raisin", "oatmeal raisin", "oat cookie", "healthy cookie",
            "wholesome", "oats", "raisins", "oat raisin", "bei ya oatmeal",
            "healthy option", "light cookie", "diet cookie", "low sugar"
        ],
        "category": "transactional",
        "topic": "product_oatmeal_raisin",
        "intent": "product_info_oatmeal_raisin",
        "priority": 8,
        "responses": [
            "🌾 Oatmeal Raisin — KSh 10\nWholesome and delicious. Our most affordable cookie — real oats, plump raisins, naturally sweet. The healthier choice that still feels like a treat.",
            "Oatmeal Raisin is KSh 10 🌾 Yes, ten bob! Wholesome oats with sweet raisins. Perfect if you want something lighter. Great value too.",
            "Our Oatmeal Raisin cookie — just KSh 10 🌾 It's wholesome, it's filling, it's real. Don't sleep on this one because of the price — it delivers.",
        ],
        "follow_up": "At KSh 10, you can grab a few and try all the flavours! 😄",
    },

    # ════════════════════════════════════════════════════════
    # WHITE CHOCOLATE MACADAMIA
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "white chocolate", "macadamia", "white choc", "white choc macadamia",
            "premium cookie", "fancy cookie", "expensive cookie", "top cookie",
            "best cookie", "white chocolate macadamia", "nuts cookie", "macadamia nuts",
            "bei ya white choc", "premium", "luxury cookie"
        ],
        "category": "transactional",
        "topic": "product_white_choc_macadamia",
        "intent": "product_info_white_choc_macadamia",
        "priority": 8,
        "responses": [
            "🌰 White Chocolate Macadamia — KSh 200\nThis is the premium tier. Creamy white chocolate with rich macadamia nuts — the kind of cookie you remember. Rated a perfect 5.0 ⭐ by our customers.",
            "White Chocolate Macadamia is KSh 200 🌰 Our highest rated cookie — 5 stars. White choc chunks with buttery macadamia nuts. If you're treating yourself or someone special, this is the one.",
            "🌰 Our White Choc Macadamia — KSh 200. Premium indulgence. Perfect 5.0 rating. When only the best will do.",
        ],
        "follow_up": "This is our most popular gift cookie — people buy it for occasions. Just saying 😊",
    },

    # ════════════════════════════════════════════════════════
    # RED VELVET
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "red velvet", "red cookie", "velvet cookie", "pink cookie",
            "red velvet cookie", "bei ya red velvet", "smooth cookie",
            "velvety", "red", "valentines cookie", "valentine cookie",
            "romantic cookie", "special cookie", "fancy red"
        ],
        "category": "transactional",
        "topic": "product_red_velvet",
        "intent": "product_info_red_velvet",
        "priority": 8,
        "responses": [
            "❤️ Red Velvet — KSh 190\nSmooth, velvety, and absolutely stunning. Our Red Velvet cookie is a whole experience — rich flavour, beautiful colour, rated 4.9 ⭐. People buy these as gifts constantly.",
            "Red Velvet cookie is KSh 190 ❤️ Smooth and velvety texture, beautiful deep red colour. One of our most loved. Rated 4.9 stars. A great choice if you're buying for someone special.",
            "❤️ Red Velvet — KSh 190. It looks as good as it tastes. Smooth, rich, and rare. This one gets people talking.",
        ],
        "follow_up": "Red Velvet + White Choc Macadamia as a gift pair is 🔥",
    },

    # ════════════════════════════════════════════════════════
    # CUPCAKE
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "cupcake", "cup cake", "keki ndogo", "muffin", "cupcakes",
            "dark chocolate cupcake", "choc cupcake", "chocolate cupcake",
            "bei ya cupcake", "cake", "small cake", "keki",
            "cupcake ngapi", "do you have cupcakes", "mna cupcakes"
        ],
        "category": "transactional",
        "topic": "product_cupcake",
        "intent": "product_info_cupcake",
        "priority": 8,
        "responses": [
            "🧁 CupCake — KSh 199\nOur latest addition — a cupcake loaded with dark chocolate spread. Rich, indulgent, and different from everything else on the menu. Perfect when you want something more.",
            "Yes, we have CupCakes! 🧁 KSh 199 each. Made with dark chocolate spread — deep flavour, soft sponge, the works. New on the menu and already a favourite.",
            "CupCake is KSh 199 🧁 Dark chocolate spread on a freshly baked cupcake. If cookies aren't your thing today, this is your pick.",
        ],
        "follow_up": "Want to mix cookies and a cupcake in your order? We can do that!",
    },

    # ════════════════════════════════════════════════════════
    # PRICING — GENERAL
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "price", "prices", "bei", "bei gani", "ngapi", "how much",
            "cost", "costs", "how much are", "ksh", "kes", "how much do you charge",
            "what's the price", "what is the price", "price list", "pricelist",
            "bei ya cookies", "cookies bei", "are they expensive", "affordable",
            "cheap", "costly", "value", "worth it", "budget"
        ],
        "category": "transactional",
        "topic": "pricing_general",
        "intent": "general_pricing",
        "priority": 9,
        "responses": [
            "Our prices at CloudOven 🍪\n\n🍪 Chocolate Chip — KSh 150\n🍫 Double Chocolate — KSh 180\n🥜 Peanut Butter — KSh 170\n🌾 Oatmeal Raisin — KSh 10\n🌰 White Choc Macadamia — KSh 200\n❤️ Red Velvet — KSh 190\n🧁 CupCake — KSh 199\n\nSomething for every budget 😊",
            "Cookie prices at CloudOven:\n\nFrom KSh 10 (Oatmeal Raisin) to KSh 200 (White Choc Macadamia)\n\nFull list:\n• Choc Chip — 150/-\n• Double Choc — 180/-\n• Peanut Butter — 170/-\n• Oatmeal Raisin — 10/-\n• White Choc Macadamia — 200/-\n• Red Velvet — 190/-\n• CupCake — 199/-",
        ],
        "follow_up": "Which one would you like to order?",
    },

    # ════════════════════════════════════════════════════════
    # CHEAPEST / MOST AFFORDABLE
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "cheapest", "most affordable", "least expensive", "budget cookie",
            "cheap cookie", "low price", "lowest price", "minimum price",
            "what's the cheapest", "can't afford", "broke", "tight budget",
            "kidogo bei", "bei ndogo", "bei nafuu", "affordable option"
        ],
        "category": "transactional",
        "topic": "cheapest_option",
        "intent": "cheapest_product",
        "priority": 7,
        "responses": [
            "Our most affordable cookie is the Oatmeal Raisin at just KSh 10 🌾 Wholesome, filling, and genuinely delicious. Don't let the price fool you — it's real quality.",
            "Cheapest on the menu? Oatmeal Raisin — KSh 10 🌾 Ten bob for a freshly baked cookie. That's CloudOven value right there.",
            "If budget is the concern, start with our Oatmeal Raisin — KSh 10 🌾 You won't regret it. Wholesome and satisfying.",
        ],
        "follow_up": "You can mix a few flavours and still keep it affordable!",
    },

    # ════════════════════════════════════════════════════════
    # MOST EXPENSIVE / PREMIUM
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "most expensive", "premium", "luxury", "top tier", "best quality",
            "highest price", "most premium", "fancy", "treat myself",
            "special treat", "splurge", "no budget", "best you have",
            "your best cookie", "number one", "top cookie", "flagship"
        ],
        "category": "transactional",
        "topic": "premium_option",
        "intent": "premium_product",
        "priority": 7,
        "responses": [
            "Our premium pick is the White Chocolate Macadamia 🌰 at KSh 200 — and it's rated a perfect 5.0 ⭐ by every customer who's tried it. If you're treating yourself, that's the one.",
            "For the premium experience, go for White Choc Macadamia 🌰 — KSh 200, rated 5 stars. Or the Red Velvet ❤️ at KSh 190, also rated 4.9. Both are exceptional.",
        ],
        "follow_up": "Perfect if you're treating yourself or buying a gift 🎁",
    },

    # ════════════════════════════════════════════════════════
    # HOW TO ORDER
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "how to order", "how do i order", "how can i order", "ordering process",
            "place order", "make order", "i want to order", "how to buy",
            "buy cookies", "purchase", "get cookies", "order process",
            "steps to order", "how does it work", "process", "procedure",
            "naweza order vipi", "niorder vipi", "order yako", "nitumie order",
            "nataka order", "niwezaje order", "nikusendea order"
        ],
        "category": "transactional",
        "topic": "ordering_process",
        "intent": "how_to_order",
        "priority": 10,
        "responses": [
            "Ordering from CloudOven is simple 🍪\n\n1️⃣ Browse & order online at cloudoven.vercel.app\n2️⃣ Pay via M-Pesa (STK Push sent to your phone)\n3️⃣ Come pick up at Kenya Israel, Machakos\n\nOr just tell me what you want right here and we'll sort it out 😊",
            "Two ways to order 🍪\n\n📱 Online: cloudoven.vercel.app — add to cart, checkout, pay M-Pesa\n💬 WhatsApp: Tell me your order right here and I'll guide you\n\nPickup is at Kenya Israel, Machakos — 8am to 7pm while stock lasts.",
            "Easy! 🍪\n\n→ Visit cloudoven.vercel.app\n→ Pick your cookies\n→ Pay with M-Pesa\n→ Pick up at Kenya Israel\n\nOr tell me your order now — I'll help you through it!",
        ],
        "follow_up": "What would you like to order today?",
    },

    # ════════════════════════════════════════════════════════
    # PICKUP LOCATION
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "where", "location", "where are you", "where to pick", "pickup",
            "pick up", "collect", "collection point", "where do i come",
            "address", "directions", "how to find you", "uko wapi",
            "wapi", "mahali", "lipa wapi", "nikuje wapi", "niko wapi",
            "naomba location", "send location", "google maps", "maps",
            "kenya israel", "kenyaisrael", "shop location", "your shop",
            "physical location", "where is your shop", "find you",
            "where can i get", "nearest pickup", "closest"
        ],
        "category": "transactional",
        "topic": "location_pickup",
        "intent": "pickup_location",
        "priority": 10,
        "responses": [
            "📍 CloudOven is at Kenya Israel, Machakos\n\nWe're inside the shop — still renovating but open and baking! Just ask around Kenya Israel area and people know us.\n\nOpen 8am–7pm daily (while stock lasts) 🍪",
            "Come find us at Kenya Israel, Machakos 📍\n\nPickup is at our shop — 8am to 7pm while stock is available. It's easy to find once you're in the Kenya Israel area.",
            "Our pickup point is Kenya Israel, Machakos 📍 Come through between 8am and 7pm. Order online at cloudoven.vercel.app first, then pick up at the shop — or just walk in!",
        ],
        "follow_up": "Need more specific directions? I can connect you with the team 😊",
    },

    # ════════════════════════════════════════════════════════
    # DELIVERY QUESTION
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "delivery", "deliver", "can you deliver", "do you deliver",
            "delivery available", "home delivery", "bring cookies",
            "send cookies", "deliver to me", "come to me", "delivery fee",
            "delivery cost", "free delivery", "mnaweza lete", "mletee",
            "nitumie", "ntumie", "deliver nairobi", "deliver machakos",
            "deliver town", "deliver university", "dispatch", "shipping",
            "kutuma", "tuma", "peleka"
        ],
        "category": "transactional",
        "topic": "delivery",
        "intent": "delivery_info",
        "priority": 10,
        "responses": [
            "Our default is pickup at Kenya Israel, Machakos 📍\n\nDelivery is available for large orders only 🍪\n\n📦 Delivery rates (big orders):\n• Kenya Israel area — Free\n• Machakos Town — KSh 100\n• Machakos University — KSh 120\n\nFor standard orders, come through to our shop — 8am to 7pm!",
            "We primarily do pickup at Kenya Israel 📍 But if you're making a big order, we can arrange delivery:\n\n• Kenya Israel — Free 🆓\n• Machakos Town — KSh 100\n• Machakos University — KSh 120\n\nWhat's your order size?",
            "Delivery is possible for bulk orders 🍪 Otherwise, pickup is at Kenya Israel, Machakos.\n\nIf your order is large, message me the details and we'll arrange delivery to your area.",
        ],
        "follow_up": "How many cookies are you thinking of ordering?",
    },

    # ════════════════════════════════════════════════════════
    # DELIVERY TO NAIROBI
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "nairobi", "nai", "deliver to nairobi", "nairobi delivery",
            "can you come to nairobi", "i'm in nairobi", "niko nairobi",
            "outside machakos", "far delivery", "long distance",
            "other towns", "other areas", "countrywide", "nationwide"
        ],
        "category": "transactional",
        "topic": "delivery_nairobi",
        "intent": "delivery_outside_machakos",
        "priority": 8,
        "responses": [
            "Currently we serve Machakos area only 📍 Nairobi delivery isn't available yet — but it's coming!\n\nIf you're passing through Machakos, you're always welcome to pick up at Kenya Israel 🍪",
            "We're Machakos-based for now 🍪 Nairobi delivery isn't on yet, but we're growing!\n\nFor now — pickup at Kenya Israel or delivery within Machakos for large orders.",
            "Not yet reaching Nairobi, but watch this space 👀 For now we cover Machakos area. If you have someone here, they can pick up on your behalf!",
        ],
        "follow_up": "Want me to notify you when Nairobi delivery launches? 😊",
    },

    # ════════════════════════════════════════════════════════
    # OPERATING HOURS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "hours", "operating hours", "opening hours", "what time",
            "when do you open", "when do you close", "open time", "close time",
            "are you open", "are you open now", "open today", "still open",
            "late night", "early morning", "sunday open", "weekend",
            "mfungua saa ngapi", "mnafunga saa ngapi", "mko wazi",
            "time ya kufungua", "time ya kufunga", "schedule",
            "working hours", "business hours", "open on sunday",
            "open on saturday", "weekday", "holiday"
        ],
        "category": "transactional",
        "topic": "operating_hours",
        "intent": "hours_query",
        "priority": 9,
        "responses": [
            "⏰ CloudOven is open 8am – 7pm daily\n\nWe operate while stock lasts — some days we sell out early, so come early for the best selection! 🍪",
            "We're open 8am to 7pm every day 🍪 One thing to note — we close when stock runs out, so if you want to be sure we're still open, you can message us first.",
            "Hours: 8:00 AM – 7:00 PM daily ⏰\n\nBut real talk — come early. We sometimes sell out before 7pm and that's a good thing 😄 Fresh cookies go fast!",
        ],
        "follow_up": "Would you like to come in today or plan for tomorrow?",
    },

    # ════════════════════════════════════════════════════════
    # STOCK / AVAILABILITY
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "stock", "available", "in stock", "do you have", "mna",
            "are cookies available", "sold out", "out of stock", "finished",
            "imeisha", "imekwisha", "have you got", "still have",
            "any left", "how many left", "availability", "do you still have",
            "bado mna", "mna bado", "finished today"
        ],
        "category": "transactional",
        "topic": "stock_availability",
        "intent": "check_stock",
        "priority": 9,
        "responses": [
            "We currently have all flavours in stock 🍪✅\n\nChoc Chip (10), Double Choc (7), Peanut Butter (5), Oatmeal Raisin (6), White Choc Macadamia (10), Red Velvet (9), CupCake (8)\n\nCome through Kenya Israel or order online at cloudoven.vercel.app!",
            "Good news — we're stocked up today 🍪 All 7 flavours available. Come in before 7pm or order online at cloudoven.vercel.app to reserve yours.",
            "Everything's available right now 🙌 We bake daily and restock regularly. Grab yours at Kenya Israel or order online — cloudoven.vercel.app",
        ],
        "follow_up": "Want to place your order now to make sure you get your flavour?",
    },

    # ════════════════════════════════════════════════════════
    # PAYMENT METHODS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "payment", "how to pay", "pay", "mpesa", "m-pesa", "lipa",
            "payment methods", "cash", "card", "pay online", "online payment",
            "lipa na mpesa", "pesa", "nitalipia vipi", "nilipia vipi",
            "do you accept cash", "cash payment", "payment options",
            "pay at shop", "pay on pickup", "pay now", "till number",
            "paybill", "send money", "transfer", "pay on delivery"
        ],
        "category": "transactional",
        "topic": "payment",
        "intent": "payment_methods",
        "priority": 10,
        "responses": [
            "We accept two payment methods 💳\n\n📱 M-Pesa online — via cloudoven.vercel.app (STK Push sent to your phone)\n💵 Cash — at pickup, at our Kenya Israel shop\n\nSimple and safe either way!",
            "You can pay via:\n\n1. M-Pesa — order online at cloudoven.vercel.app and pay via STK Push\n2. Cash — pay when you pick up at Kenya Israel\n\nNo stress either way 😊",
            "Payment options at CloudOven:\n\n✅ M-Pesa (online via our website)\n✅ Cash on pickup\n\nOrder online at cloudoven.vercel.app for the M-Pesa option, or just bring cash to the shop!",
        ],
        "follow_up": "Which payment method works for you?",
    },

    # ════════════════════════════════════════════════════════
    # ONLINE ORDERING / WEBSITE
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "website", "online", "online order", "order online", "link",
            "app", "url", "site", "web", "online shop", "e-commerce",
            "cloudoven.vercel.app", "vercel", "online store",
            "order through phone", "order from phone", "order from home",
            "order remotely", "digital order", "place online order",
            "how to order online", "online payment link"
        ],
        "category": "transactional",
        "topic": "online_ordering",
        "intent": "online_order_info",
        "priority": 9,
        "responses": [
            "You can order online at 👉 cloudoven.vercel.app 🍪\n\nBrowse the menu, add to cart, pay with M-Pesa (STK Push to your phone), then pick up at Kenya Israel. Fast and easy!",
            "Our online shop is live at cloudoven.vercel.app 🔗\n\nFull menu, M-Pesa payments, order tracking — all in one place. Order from wherever you are and pick up at Kenya Israel!",
            "Yes, we have a full online shop! 🍪\n\ncloudoven.vercel.app\n\nYou can browse, order, and pay M-Pesa online. Then just come pick up at Kenya Israel.",
        ],
        "follow_up": "Want me to walk you through the online ordering process?",
    },

    # ════════════════════════════════════════════════════════
    # RECOMMENDATIONS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "recommend", "recommendation", "what should i get", "what do you suggest",
            "best cookie", "your favourite", "most popular", "top seller",
            "what's good", "what's best", "which one", "help me choose",
            "nisaidie chagua", "niambie", "surprise me", "customer favourite",
            "what do people like", "what sells most", "first time",
            "never tried", "new to cookies", "never had your cookies"
        ],
        "category": "transactional",
        "topic": "recommendation",
        "intent": "product_recommendation",
        "priority": 8,
        "responses": [
            "My top 3 picks 🍪✨\n\n1. 🌰 White Choc Macadamia (KSh 200) — rated a perfect 5.0 ⭐\n2. ❤️ Red Velvet (KSh 190) — silky smooth and stunning\n3. 🍪 Chocolate Chip (KSh 150) — the classic that never fails\n\nFirst time? Start with the Chocolate Chip. You can't go wrong.",
            "If I had to pick one, I'd say White Chocolate Macadamia 🌰 — our highest rated, most premium cookie. But if you want value, Chocolate Chip at KSh 150 is unbeatable.\n\nWhat are you in the mood for — classic or premium?",
            "Customer favourites right now:\n\n⭐ White Choc Macadamia — the perfect 5.0 rating says it all\n⭐ Red Velvet — people always come back for this one\n⭐ Chocolate Chip — the original classic\n\nWhat's your chocolate preference? 😄",
        ],
        "follow_up": "Want to do a mix? Most customers grab 2-3 flavours in one visit!",
    },

    # ════════════════════════════════════════════════════════
    # BULK / LARGE ORDERS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "bulk", "bulk order", "large order", "big order", "many cookies",
            "lot of cookies", "dozen", "50 cookies", "100 cookies", "200 cookies",
            "event cookies", "office cookies", "party cookies", "wedding cookies",
            "cookies for event", "cookies for party", "catering", "wholesale",
            "corporate", "school order", "church order", "harambee", "fundraiser",
            "cookies for many", "many pieces", "tray", "box of cookies",
            "can you make many", "large quantity", "high volume"
        ],
        "category": "transactional",
        "topic": "bulk_order",
        "intent": "bulk_order_inquiry",
        "priority": 10,
        "responses": [
            "Yes! We handle bulk orders 🍪🎉 Whether it's for an event, office, school, or party — we can bake for you.\n\nFor large orders, we can also arrange delivery:\n• Kenya Israel area — Free\n• Machakos Town — KSh 100\n• Machakos University — KSh 120\n\nShare your details and we'll make it happen!",
            "Bulk orders are welcome! 🍪 Tell me:\n1. How many cookies?\n2. Which flavours?\n3. When do you need them?\n4. Pickup or delivery?\n\nI'll connect you with our team to confirm everything.",
            "We love big orders! 🍪 Let me connect you with our team for custom bulk pricing and delivery arrangements. What's the occasion?",
        ],
        "follow_up": None,
        "escalate": True,
    },

    # ════════════════════════════════════════════════════════
    # GIFT ORDERS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "gift", "present", "zawadi", "birthday", "anniversary",
            "surprise", "treat someone", "buy for someone", "for a friend",
            "for my girlfriend", "for my boyfriend", "for my wife", "for my husband",
            "valentine", "christmas", "gift cookies", "cookie gift",
            "special occasion", "celebration", "congratulations gift",
            "graduation gift", "baby shower", "send as gift"
        ],
        "category": "transactional",
        "topic": "gift_order",
        "intent": "gift_purchase",
        "priority": 8,
        "responses": [
            "CloudOven cookies make the perfect gift 🎁🍪\n\nOur top gift picks:\n🌰 White Choc Macadamia (KSh 200) — rated 5 stars\n❤️ Red Velvet (KSh 190) — beautiful and delicious\n🍫 Double Chocolate (KSh 180) — for the choc lovers\n\nWant help putting together a special combination?",
            "Yes! Our cookies are a great gift 🎁 The Red Velvet and White Choc Macadamia are our most gifted cookies — stunning to look at and even better to eat.\n\nWhat's the occasion? I can help suggest the perfect combination.",
            "Cookies as a gift? 🎁 That's the most CloudOven thing ever! Tell me the occasion and I'll suggest the best flavours and quantities.",
        ],
        "follow_up": "Want packaging tips or a specific quantity?",
    },

    # ════════════════════════════════════════════════════════
    # FRESHNESS / INGREDIENTS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "fresh", "freshly baked", "how fresh", "baked today", "when baked",
            "ingredients", "what's in", "recipe", "homemade", "handmade",
            "natural", "preservatives", "artificial", "organic", "real ingredients",
            "quality", "made with", "baked from scratch", "fresh daily",
            "how long do they last", "shelf life", "expiry", "best before",
            "how long can i keep", "store cookies"
        ],
        "category": "transactional",
        "topic": "freshness_quality",
        "intent": "freshness_and_quality",
        "priority": 7,
        "responses": [
            "CloudOven cookies are baked fresh daily 🍪✨ No preservatives, no shortcuts — real ingredients, real love. That's the CloudOven way.",
            "Every cookie is baked fresh — that's our standard 🍪 We don't stock week-old cookies. What you get at CloudOven was made today.",
            "Freshly baked, daily 🍪 Real butter, real chocolate, real ingredients. Homemade quality at every single batch. Cookies are best eaten within 2-3 days but honestly they never last that long 😄",
        ],
        "follow_up": "Any dietary needs or allergies I should know about?",
    },

    # ════════════════════════════════════════════════════════
    # ALLERGENS / DIETARY
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "allergy", "allergies", "gluten", "gluten free", "dairy free",
            "vegan", "vegetarian", "nuts allergy", "peanut allergy",
            "diabetic", "sugar free", "halal", "kosher", "wheat",
            "lactose", "egg free", "dietary", "diet", "special diet",
            "intolerance", "celiac", "can i eat if", "safe for"
        ],
        "category": "transactional",
        "topic": "allergens_dietary",
        "intent": "dietary_and_allergens",
        "priority": 8,
        "responses": [
            "Great question! Our cookies contain standard baking ingredients including wheat flour, butter, eggs, and sugar 🍪\n\nIf you have a specific allergy (especially nuts — our Peanut Butter and Macadamia cookies contain nuts), please let me connect you with our team directly to confirm ingredients.",
            "For specific dietary requirements or allergies, I want to make sure you get accurate information 🍪 Let me connect you with our team who can confirm exact ingredients for each flavour. Your safety matters!",
        ],
        "follow_up": None,
        "escalate": True,
    },

    # ════════════════════════════════════════════════════════
    # CUSTOM ORDERS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "custom", "custom order", "special order", "customise", "customize",
            "special flavour", "special flavor", "my own flavour", "different flavour",
            "can you make", "bespoke", "personalised", "personalized",
            "custom design", "special request", "request", "special cookie",
            "create cookie", "design cookie", "unique cookie", "exclusive"
        ],
        "category": "transactional",
        "topic": "custom_order",
        "intent": "custom_order_inquiry",
        "priority": 8,
        "responses": [
            "Custom orders? Tell us more! 🍪✨ We love special requests. Share what you have in mind and we'll let you know what's possible.",
            "We can discuss custom orders for special occasions 🍪 Let me connect you with our team directly — they'll work with you on quantities, flavours, and any special requirements.",
        ],
        "follow_up": None,
        "escalate": True,
    },

    # ════════════════════════════════════════════════════════
    # WAIT TIME / ORDER READY
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "how long", "wait", "waiting time", "ready when", "when will it be ready",
            "how long to wait", "preparation time", "baking time", "order ready",
            "when can i pick up", "ready soon", "time to bake",
            "itachukua muda gani", "nangoja muda gani", "order yangu iko ready",
            "is my order ready", "ready", "done yet", "still waiting"
        ],
        "category": "transactional",
        "topic": "wait_time",
        "intent": "order_readiness",
        "priority": 7,
        "responses": [
            "If we have your flavour in stock, pickup is immediate — just come through Kenya Israel between 8am and 7pm 🍪 No waiting!",
            "For in-stock orders, you come and pick up straight away — no baking wait 🍪 If it's a custom or bulk order, our team will give you a specific time.",
            "Most orders are available for immediate pickup! 🍪 Come through Kenya Israel during our hours (8am-7pm) and we'll sort you out.",
        ],
        "follow_up": "Ready to place your order?",
    },

    # ════════════════════════════════════════════════════════
    # COMPLIMENTS / POSITIVE FEEDBACK
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "delicious", "amazing", "wonderful", "love your cookies", "best cookies",
            "so good", "yummy", "tasty", "great cookies", "excellent",
            "perfect", "outstanding", "you guys are great", "keep it up",
            "tamu sana", "poa sana", "nimependa", "zilikuwa nzuri",
            "cookies zenu ni best", "mzuri", "thank you for the cookies",
            "enjoyed", "loved it", "coming back", "will come again",
            "will order again", "highly recommend", "favourite bakery",
            "impressed", "blown away"
        ],
        "category": "smalltalk",
        "topic": "positive_feedback",
        "intent": "receive_compliment",
        "priority": 6,
        "responses": [
            "Thank you so much! 🍪❤️ That genuinely means everything to us. Baked with love from Machakos — glad it landed right. Come back soon!",
            "Aww, this makes our day! 🙏🍪 We bake every batch with care and it's wonderful to hear it shows. You're always welcome at CloudOven!",
            "That's what we're here for! 🍪✨ Thank you for the love — see you next time. Tell your people about us! 😄",
            "You just made the whole team smile 😊🍪 Thank you! We put a lot of heart into every batch and it's great to hear it. Come back anytime!",
        ],
        "follow_up": None,
    },

    # ════════════════════════════════════════════════════════
    # COMPLAINTS / ISSUES
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "complaint", "problem", "issue", "not happy", "disappointed",
            "bad cookies", "stale", "not fresh", "wrong order", "missing order",
            "bad experience", "refund", "money back", "unsatisfied",
            "terrible", "awful", "disgusting", "burnt", "raw", "undercooked",
            "overcooked", "too sweet", "too hard", "didn't like", "not good",
            "haikuwa fresh", "vibaya", "haikuwa nzuri", "nataka refund"
        ],
        "category": "escalate",
        "topic": "complaint",
        "intent": "handle_complaint",
        "priority": 15,
        "responses": [
            "I'm really sorry to hear this 🙏 That's not the CloudOven experience we want for you. Let me connect you directly with our team right now — we'll make this right.",
            "This isn't okay and I apologise. Let me get our team involved immediately so we can resolve this properly for you. Your satisfaction matters to us.",
        ],
        "follow_up": None,
        "escalate": True,
    },

    # ════════════════════════════════════════════════════════
    # ABOUT THE BUSINESS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "about you", "about cloudoven", "who are you", "what is cloudoven",
            "tell me about", "your story", "background", "history",
            "how long have you been", "when did you start", "founder",
            "owner", "who owns", "machakos bakery", "local bakery",
            "kenyan bakery", "small business", "story behind", "mission",
            "vision", "values", "what makes you different"
        ],
        "category": "smalltalk",
        "topic": "about_business",
        "intent": "business_info",
        "priority": 6,
        "responses": [
            "CloudOven is a homemade cookie brand based in Machakos, Kenya 🍪 We bake fresh daily from our shop at Kenya Israel — real ingredients, real flavours, no shortcuts. Born from the idea that great cookies should be available right here in Machakos.",
            "We're CloudOven — Machakos' own homemade cookie brand 🍪 Baked fresh every day at Kenya Israel. We believe in quality you can taste, prices that make sense, and cookies that bring people together.",
            "CloudOven started with a simple belief: Machakos deserves world-class homemade cookies 🍪 We bake daily from Kenya Israel with real ingredients and real passion. From the clan to the era.",
        ],
        "follow_up": "Want to see our menu? 😊",
    },

    # ════════════════════════════════════════════════════════
    # SWAHILI GENERAL QUERIES
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "nataka cookies", "niambie kuhusu cookies", "cookies zenu",
            "nitumie menu", "mna nini leo", "ninaomba", "tafadhali",
            "ninahitaji cookies", "ninataka kuorder", "naweza pata wapi",
            "mko open", "mfungua", "bei ya cookies ni ngapi",
            "cookies zinapatikana", "naweza order online",
            "kuna bei ya chini", "mna offer", "discount iko"
        ],
        "category": "transactional",
        "topic": "swahili_query",
        "intent": "swahili_general",
        "priority": 7,
        "responses": [
            "Habari! 🍪 CloudOven hapa — cookies za homemade kutoka Machakos. Hii ndiyo menu yetu:\n\n🍪 Choc Chip — KSh 150\n🍫 Double Choc — KSh 180\n🥜 Peanut Butter — KSh 170\n🌾 Oatmeal Raisin — KSh 10\n🌰 White Choc Macadamia — KSh 200\n❤️ Red Velvet — KSh 190\n🧁 CupCake — KSh 199\n\nKuja Kenya Israel au order online: cloudoven.vercel.app",
            "Karibu CloudOven! 🍪 Tuna cookies fresh kila siku. Unataka kuona menu? Au tayari unajua unataka nini?",
        ],
        "follow_up": "Unataka kuorder leo? 😊",
    },

    # ════════════════════════════════════════════════════════
    # DISCOUNT / OFFERS
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "discount", "offer", "promotion", "sale", "deal", "cheaper",
            "reduce price", "negotiate", "punguza bei", "offer iko",
            "promo", "coupon", "voucher", "loyalty", "loyalty program",
            "regular customer discount", "bulk discount", "student discount",
            "free cookie", "sample", "taster"
        ],
        "category": "transactional",
        "topic": "discounts_offers",
        "intent": "discount_inquiry",
        "priority": 7,
        "responses": [
            "Our prices are already set to give you real value 🍪 — especially the Oatmeal Raisin at just KSh 10!\n\nFor bulk orders, we can discuss special pricing. What are you thinking of ordering?",
            "No running promotions right now 🍪 but our prices are genuinely fair — homemade quality at Kenya prices. Oatmeal Raisin is KSh 10 if you want a taste without spending much!\n\nFor big orders, message our team — we can talk.",
            "Bulk orders can come with better deals 🍪 Tell me how many you need and I'll connect you with our team to discuss pricing.",
        ],
        "follow_up": "How many cookies are you looking at?",
    },

    # ════════════════════════════════════════════════════════
    # SOCIAL MEDIA / FOLLOW
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "instagram", "facebook", "tiktok", "twitter", "social media",
            "follow you", "social", "online presence", "post", "page",
            "ig", "fb", "insta", "find you online", "tag you",
            "your instagram", "your facebook", "your tiktok"
        ],
        "category": "smalltalk",
        "topic": "social_media",
        "intent": "social_media_info",
        "priority": 5,
        "responses": [
            "Follow our journey on social media 🍪✨ — we'll be posting fresh batches, new flavours, and behind-the-scenes from the Kenya Israel kitchen. Stay tuned!",
            "We're building our online presence 🍪 In the meantime, our website is live at cloudoven.vercel.app — and you can always reach us right here on WhatsApp!",
        ],
        "follow_up": None,
    },

    # ════════════════════════════════════════════════════════
    # FAREWELL / GOODBYE
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "bye", "goodbye", "later", "kwaheri", "sawa", "asante",
            "thank you", "thanks", "thanks a lot", "okay done", "noted",
            "got it", "will do", "coming through", "see you", "see you soon",
            "on my way", "nakuja", "nakuja sasa", "tutaonana", "ciao",
            "alright", "all good", "sorted", "perfect thanks"
        ],
        "category": "smalltalk",
        "topic": "farewell",
        "intent": "farewell",
        "priority": 4,
        "responses": [
            "See you soon at CloudOven! 🍪 Come through Kenya Israel — we'll have something fresh waiting. Kwaheri! 👋",
            "Thank you! 🍪 See you at Kenya Israel. Come early for the best selection!",
            "Kwaheri! 🍪✨ You're always welcome at CloudOven. Tell a friend!",
            "Take care! 🍪 See you next time — and if you haven't tried the White Choc Macadamia yet, make that your next order 😄",
        ],
        "follow_up": None,
    },

    # ════════════════════════════════════════════════════════
    # REPEAT CUSTOMER
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "i'm back", "im back", "came back", "ordering again", "order again",
            "second time", "third time", "regular customer", "i always order",
            "i was here before", "nilikuja", "niliorder", "nimekuwa nikisupport",
            "nimekuwa nikibuy", "loyal customer", "i love your cookies",
            "my favourite shop"
        ],
        "category": "smalltalk",
        "topic": "repeat_customer",
        "intent": "welcome_back",
        "priority": 7,
        "responses": [
            "Welcome back! 🍪❤️ Our regulars are the backbone of CloudOven — we see you and we appreciate you. What are you having today?",
            "Ah, you're back! That's what we love to hear 🍪 Thank you for the support — CloudOven is what it is because of customers like you. What's the order today?",
            "You came back and that means the world to us 🍪✨ Welcome! What flavour are we going with today?",
        ],
        "follow_up": "Sticking with your usual or trying something new today?",
    },

    # ════════════════════════════════════════════════════════
    # WAIT / PAUSE MESSAGE
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "one moment", "hold on", "wait", "just a sec", "ngoja",
            "ngoja kidogo", "still thinking", "let me think", "thinking",
            "give me a minute", "bado", "nafikiri"
        ],
        "category": "smalltalk",
        "topic": "pause",
        "intent": "customer_pause",
        "priority": 3,
        "responses": [
            "Take your time! 🍪 I'm here whenever you're ready.",
            "No rush at all 😊 CloudOven will be here. Let me know what you decide!",
            "All good — think it through! 🍪 We have great options at every price point.",
        ],
        "follow_up": None,
    },

    # ════════════════════════════════════════════════════════
    # ESCALATION TRIGGER (EXPLICIT)
    # ════════════════════════════════════════════════════════
    {
        "triggers": [
            "speak to someone", "talk to human", "talk to a person",
            "speak to owner", "manager", "speak to manager", "real person",
            "human support", "owner", "call me", "phone number",
            "direct contact", "reach you directly", "contact number",
            "wasiliana nawe moja kwa moja"
        ],
        "category": "escalate",
        "topic": "human_escalation",
        "intent": "escalate_to_human",
        "priority": 15,
        "responses": [
            "Absolutely — let me connect you directly with our team right now 🍪 Someone will be with you in a moment!",
            "Of course! Connecting you with our CloudOven team directly. They'll sort you out immediately 🙏",
        ],
        "follow_up": None,
        "escalate": True,
    },

]