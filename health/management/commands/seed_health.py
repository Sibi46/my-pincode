import json
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from health.models import HealthCondition, Fruit, Vegetable, Herb, Food, Recipe, Video

CONDITIONS = [
    {
        'name': 'Diabetes',
        'icon': '🩸',
        'order': 1,
        'is_featured': True,
        'overview': 'Diabetes is a condition where your blood sugar (glucose) levels are too high. Type 2 diabetes is the most common type. The right food choices can help control blood sugar and prevent complications.',
        'foods_to_eat': 'Brown rice, oats, whole wheat roti, moong dal, rajma, chickpeas, fish, eggs, tofu, leafy greens, bitter gourd (karela), fenugreek seeds, cinnamon, flaxseeds.',
        'foods_to_limit': 'White rice, maida, sugar, jaggery, sweets, fruit juices, white bread, fried foods, high-sugar fruits (mango in large amounts), soft drinks, alcohol.',
        'fruits_info': 'Best fruits: Guava, papaya, apple, pear, berries, jamun (Indian blackberry). Eat in small portions. Prefer whole fruit over juice. Avoid very sweet fruits like chikoo and banana in large quantities.',
        'vegetables_info': 'All green leafy vegetables — spinach, methi, palak. Bitter gourd (karela) is excellent for diabetes. Drumstick (moringa), brinjal, cauliflower, cucumber, tomato. Avoid potato in large amounts.',
        'herbs_info': 'Fenugreek (methi) seeds soaked overnight — excellent for blood sugar control. Bitter gourd juice. Cinnamon in tea. Turmeric in milk. Jamun seeds powder.',
        'spices_info': 'Turmeric (haldi), cinnamon (dalchini), fenugreek seeds (methi dana), cumin (jeera), coriander (dhania). These spices help manage blood sugar naturally.',
        'cooking_methods': 'Steam, boil, grill, bake. Avoid deep frying. Use minimal oil. Prefer cold-pressed coconut oil or mustard oil in small amounts.',
        'meal_timing': 'Eat every 2–3 hours in small portions. Never skip breakfast. Avoid heavy meals at night. Best dinner time: before 8 PM. Do not eat 2 hours before sleep.',
        'portion_guidance': 'Fill half your plate with non-starchy vegetables. One quarter with whole grains or legumes. One quarter with lean protein. Keep fruit portions to half a cup. Measure rice — 1 cup cooked max per meal.',
        'faq': json.dumps([
            {'q': 'Can I eat rice if I have diabetes?', 'a': 'Yes, in small portions. Prefer brown rice over white rice. Limit to ½ cup cooked per meal and combine with vegetables and protein to slow sugar absorption.'},
            {'q': 'Is banana safe for diabetics?', 'a': 'Eat only one small banana per day, preferably in the morning. Avoid overripe bananas as they have more sugar.'},
            {'q': 'Can I eat mango?', 'a': 'Yes, but only ½ cup per day. Eat it after a meal, not on an empty stomach. Avoid mango juice or pulp.'},
            {'q': 'What is the best breakfast for diabetes?', 'a': 'Oats porridge, vegetable upma, moong dal chilla, whole wheat roti with sabji, or eggs with vegetables are excellent choices.'},
            {'q': 'How much water should I drink?', 'a': 'Drink 8–10 glasses of water per day. Water helps flush excess sugar through urine and keeps you hydrated.'},
        ]),
    },
    {
        'name': 'Blood Pressure',
        'icon': '💓',
        'order': 2,
        'is_featured': True,
        'overview': 'High blood pressure (hypertension) means your heart has to work harder to pump blood. The right diet — especially reducing salt and eating potassium-rich foods — can significantly lower blood pressure.',
        'foods_to_eat': 'Banana, spinach, oats, low-fat dairy, garlic, beetroot, pomegranate, watermelon, flaxseeds, fatty fish (salmon, mackerel), legumes, dark chocolate (small amount).',
        'foods_to_limit': 'Salt and salty foods (pickles, papad, processed foods), red meat, butter, full-fat dairy, alcohol, caffeine in excess, fast food, canned soups.',
        'fruits_info': 'Banana (rich in potassium), pomegranate, watermelon, kiwi, berries, citrus fruits (oranges, lemon). These help dilate blood vessels and lower pressure.',
        'vegetables_info': 'Spinach, beetroot, broccoli, sweet potato, garlic, onion, tomato. Beetroot juice is particularly powerful for reducing blood pressure naturally.',
        'herbs_info': 'Garlic — eat 1–2 raw cloves daily. Hibiscus tea (gude hal) — lowers blood pressure effectively. Basil (tulsi) leaves in warm water. Coriander seeds water.',
        'spices_info': 'Garlic, ginger, cinnamon, cardamom, turmeric. These spices help relax blood vessels and reduce inflammation.',
        'cooking_methods': 'Cook without salt — use lemon juice and herbs for flavor. Steam, boil, or grill. Avoid sautéing with too much oil. Use herb-based seasonings.',
        'meal_timing': 'Eat 3 regular meals a day. Do not skip meals. Avoid large heavy dinners. Eat dinner by 7:30 PM. Have a light evening snack if needed.',
        'portion_guidance': 'Reduce sodium to less than 2000mg per day (about 1 teaspoon of salt). Eat 5 servings of fruits and vegetables daily. Keep portions moderate — overeating raises pressure.',
        'faq': json.dumps([
            {'q': 'Can I eat eggs if I have high BP?', 'a': 'Yes, 1–2 eggs daily are fine. Prefer boiled or poached eggs. Avoid egg yolk in excess if you also have high cholesterol.'},
            {'q': 'Is coffee bad for blood pressure?', 'a': 'Caffeine can raise BP temporarily. Limit to 1 cup per day. Switch to herbal teas like hibiscus or tulsi tea.'},
            {'q': 'How does salt affect blood pressure?', 'a': 'Salt causes your body to retain water, increasing blood volume and pressure. Reduce salt gradually — use lemon, herbs, and spices instead.'},
        ]),
    },
    {
        'name': 'Cholesterol',
        'icon': '🫀',
        'order': 3,
        'is_featured': True,
        'overview': 'Cholesterol is a fat in your blood. Too much LDL (bad) cholesterol can block arteries and cause heart disease. The right diet can reduce LDL and increase HDL (good) cholesterol.',
        'foods_to_eat': 'Oats, barley, legumes (rajma, chana), fatty fish, nuts (almonds, walnuts), olive oil, avocado, flaxseeds, fruits rich in fiber (apple, pear, guava), dark leafy greens.',
        'foods_to_limit': 'Ghee, butter, full-fat dairy, red meat, egg yolks (limit to 3 per week), fried foods, coconut oil, palm oil, processed meats, biscuits, cakes.',
        'fruits_info': 'Apple (eat with skin), pear, guava, citrus fruits, grapes, strawberries. These are high in soluble fiber which binds cholesterol and removes it from the body.',
        'vegetables_info': 'Brinjal (eggplant), okra (bhindi), spinach, beans, broccoli, sweet potato. Brinjal and okra are especially good at lowering LDL cholesterol.',
        'herbs_info': 'Garlic — reduces LDL cholesterol. Fenugreek seeds — soak overnight and eat in morning. Coriander seeds water. Turmeric with black pepper.',
        'spices_info': 'Turmeric, garlic, ginger, cinnamon, fenugreek seeds. Add these to daily cooking for natural cholesterol management.',
        'cooking_methods': 'Grill, bake, steam, stir-fry with minimal oil. Use mustard oil or olive oil in small amounts. Avoid deep frying. Use non-stick pans to reduce oil use.',
        'meal_timing': 'Eat oats for breakfast daily. Include a handful of nuts as mid-morning snack. Have a fiber-rich lunch and light dinner before 8 PM.',
        'portion_guidance': 'Limit saturated fats to less than 7% of daily calories. Add 5–10g of soluble fiber daily (oats, beans). Eat fish 2–3 times per week.',
        'faq': json.dumps([
            {'q': 'How fast can diet change cholesterol levels?', 'a': 'You can see improvement in cholesterol levels within 4–6 weeks of dietary changes. Consistent effort over 3 months shows significant results.'},
            {'q': 'Is coconut oil good for cholesterol?', 'a': 'Coconut oil is high in saturated fat and may raise LDL cholesterol. Use it sparingly. Olive oil and mustard oil are better choices.'},
        ]),
    },
    {
        'name': 'Fatty Liver',
        'icon': '🫁',
        'order': 4,
        'is_featured': True,
        'overview': 'Fatty liver (NAFLD) occurs when excess fat builds up in liver cells. It is mainly caused by poor diet, obesity, and lack of exercise. The right diet can reverse early-stage fatty liver.',
        'foods_to_eat': 'Green leafy vegetables, broccoli, oats, whole grains, walnuts, olive oil, coffee (without sugar), green tea, turmeric, garlic, fatty fish, berries, avocado.',
        'foods_to_limit': 'Alcohol (completely avoid), sugar, soft drinks, refined carbs (maida, white bread), fried foods, red meat, processed foods, too much salt.',
        'fruits_info': 'Berries (blueberry, strawberry), lemon, papaya, watermelon, avocado. Avoid very sweet fruits in large quantities. Lemon water first thing in the morning helps detox the liver.',
        'vegetables_info': 'Broccoli, cauliflower, bitter gourd (karela), drumstick, spinach, garlic, onion. Cruciferous vegetables (broccoli, cabbage) are particularly good for liver health.',
        'herbs_info': 'Milk thistle (silymarin) — the most studied herb for fatty liver. Dandelion root tea. Turmeric (curcumin) in warm milk. Amla (Indian gooseberry).',
        'spices_info': 'Turmeric — anti-inflammatory and liver protective. Ginger, garlic, black pepper. Drink turmeric milk (golden milk) before bed.',
        'cooking_methods': 'Bake, steam, boil. Avoid all fried and oily food. Use very minimal oil. No alcohol-based cooking. Prefer raw salads when possible.',
        'meal_timing': 'Eat breakfast within 1 hour of waking. Have 3 meals with small healthy snacks. Stop eating 3 hours before sleep to give liver rest during the night.',
        'portion_guidance': 'Reduce total calorie intake by 500 calories per day for gradual weight loss. Cut sugar completely. Limit fat to 20–30% of daily calories. Increase fiber to 25–35g per day.',
        'faq': json.dumps([
            {'q': 'Can fatty liver be cured with diet?', 'a': 'Yes! Early-stage fatty liver can be completely reversed with dietary changes, weight loss, and exercise within 6–12 months. Regular monitoring is needed.'},
            {'q': 'Is coffee good for fatty liver?', 'a': 'Studies show that 2–3 cups of black coffee per day (without sugar) can reduce liver inflammation and the progression of fatty liver disease.'},
        ]),
    },
    {
        'name': 'Arthritis',
        'icon': '🦴',
        'order': 5,
        'is_featured': True,
        'overview': 'Arthritis causes inflammation and pain in joints. Diet plays a key role — anti-inflammatory foods can reduce pain and swelling, while certain foods can worsen inflammation.',
        'foods_to_eat': 'Fatty fish (omega-3), walnuts, flaxseeds, turmeric, ginger, berries, broccoli, olive oil, green tea, cherries, spinach, beans.',
        'foods_to_limit': 'Sugar, refined carbs, fried foods, red meat, full-fat dairy, alcohol, salt, processed foods, gluten (for some people with rheumatoid arthritis).',
        'fruits_info': 'Cherries (reduce uric acid), berries (antioxidants), orange (vitamin C), pineapple (bromelain enzyme — anti-inflammatory), papaya, pomegranate.',
        'vegetables_info': 'Broccoli, spinach, kale, sweet potato, garlic, ginger, onion. Colorful vegetables are rich in antioxidants that fight inflammation.',
        'herbs_info': 'Turmeric with black pepper (curcumin) — powerful anti-inflammatory. Ginger tea. Boswellia (shallaki). Ashwagandha for joint health.',
        'spices_info': 'Turmeric, ginger, black pepper, cinnamon, clove. These spices have natural anti-inflammatory properties.',
        'cooking_methods': 'Gentle cooking methods — steaming, slow cooking. Add turmeric and ginger to all cooking. Avoid charring or overcooking vegetables.',
        'meal_timing': 'Regular meals to maintain a healthy weight (excess weight puts pressure on joints). Anti-inflammatory breakfast like oats with berries and walnuts.',
        'portion_guidance': 'Maintain healthy weight — every extra kg puts 4 kg pressure on knee joints. Eat omega-3 rich foods 3 times per week. Include vitamin C foods daily.',
        'faq': json.dumps([
            {'q': 'Does turmeric really help arthritis?', 'a': 'Yes! Curcumin in turmeric is a proven anti-inflammatory. Take with black pepper to improve absorption. Studies show it can reduce joint pain and swelling.'},
            {'q': 'Which fruits are best for arthritis?', 'a': 'Cherries are the best — they reduce uric acid levels. Berries, citrus fruits, and pineapple are also excellent for their anti-inflammatory properties.'},
        ]),
    },
    {
        'name': 'Thyroid',
        'icon': '🔬',
        'order': 6,
        'is_featured': True,
        'overview': 'The thyroid gland controls metabolism. Hypothyroidism (underactive) is most common. Certain nutrients — especially iodine, selenium, and zinc — are critical for thyroid function.',
        'foods_to_eat': 'Iodized salt (in moderation), seafood, eggs, dairy, Brazil nuts (selenium), pumpkin seeds (zinc), leafy greens, berries, chicken.',
        'foods_to_limit': 'Raw cruciferous vegetables in large amounts (cabbage, cauliflower, kale — can block iodine absorption when raw), soy in excess, millet (bajra) in hypothyroidism, gluten (for autoimmune thyroid).',
        'fruits_info': 'Berries, apple, kiwi, pomegranate. Avoid eating fruit with thyroid medication — wait 30–60 minutes after taking medicine before eating.',
        'vegetables_info': 'Cook cruciferous vegetables (broccoli, cauliflower, cabbage) — cooking reduces goitrogen content. Spinach, sweet potato, peas are good choices.',
        'herbs_info': 'Ashwagandha — helps normalize thyroid hormone levels. Tulsi (holy basil). Ginger — reduces inflammation. Liquorice root (mulethi).',
        'spices_info': 'Ginger, turmeric, black pepper, cinnamon. These support thyroid function and overall metabolism.',
        'cooking_methods': 'Cook all cruciferous vegetables — do not eat them raw in large amounts. Normal cooking methods are fine. Avoid excessive soy-based cooking.',
        'meal_timing': 'Take thyroid medication on empty stomach 30–60 minutes before breakfast. Never skip breakfast — thyroid patients need consistent meal timing.',
        'portion_guidance': 'Selenium: 1–2 Brazil nuts per day. Iodine from iodized salt in moderation. Zinc from pumpkin seeds, meat. Vitamin D from sunlight and dairy.',
        'faq': json.dumps([
            {'q': 'Should I avoid goitrogenic foods completely?', 'a': 'No, cooking eliminates most goitrogens. Eat broccoli, cauliflower and cabbage cooked, not raw in large amounts. Moderation is key.'},
            {'q': 'Can thyroid patients eat rice?', 'a': 'Yes, in moderation. Prefer brown rice. Focus on overall balanced nutrition rather than avoiding specific foods.'},
        ]),
    },
    {
        'name': 'PCOS',
        'icon': '🌸',
        'order': 7,
        'is_featured': True,
        'overview': 'Polycystic Ovary Syndrome (PCOS) is a hormonal condition affecting women. Insulin resistance is a key factor. A low-glycemic, anti-inflammatory diet helps manage PCOS symptoms effectively.',
        'foods_to_eat': 'Whole grains, legumes, leafy greens, fruits (low GI), fatty fish, nuts, seeds (especially flaxseeds and pumpkin seeds), olive oil, lean protein, cinnamon.',
        'foods_to_limit': 'Sugar, refined carbs, white rice, maida, soft drinks, processed foods, full-fat dairy, red meat, alcohol, soy in large amounts.',
        'fruits_info': 'Berries (low GI, antioxidants), apple, pear, kiwi, guava, papaya. Eat whole fruit, not juice. Avoid very sweet fruits like mango and banana in large amounts.',
        'vegetables_info': 'Spinach, broccoli, bitter gourd (karela), sweet potato, broccoli, cauliflower, peas. Focus on non-starchy vegetables which help with insulin resistance.',
        'herbs_info': 'Spearmint tea — reduces androgen levels in PCOS. Cinnamon — improves insulin sensitivity. Ashwagandha — balances cortisol and hormones. Shatavari for hormonal balance.',
        'spices_info': 'Cinnamon (most important for PCOS — add to every meal), turmeric, ginger. Half a teaspoon of cinnamon daily can significantly improve insulin sensitivity.',
        'cooking_methods': 'Grill, steam, bake. Use healthy oils in small amounts. Avoid fried foods completely. Choose cooking methods that preserve nutrients.',
        'meal_timing': 'Never skip breakfast — this is critical for PCOS. Eat every 3–4 hours to maintain blood sugar. Have protein with every meal. No late-night eating.',
        'portion_guidance': 'Aim for low-GI diet. Balance every meal with protein, healthy fat, and complex carbs. Reduce caloric intake by 200–300 calories if overweight. Focus on nutrient-dense foods.',
        'faq': json.dumps([
            {'q': 'Does dairy worsen PCOS?', 'a': 'Some women with PCOS find that dairy worsens acne and symptoms. Try reducing dairy for 4 weeks and see if symptoms improve. Non-dairy alternatives like almond milk work well.'},
            {'q': 'Is intermittent fasting good for PCOS?', 'a': 'Short eating windows can worsen cortisol for some women with PCOS. Focus on regular balanced meals rather than fasting. Consult your doctor before fasting.'},
        ]),
    },
    {
        'name': 'Obesity',
        'icon': '⚖️',
        'order': 8,
        'is_featured': True,
        'overview': 'Obesity increases the risk of diabetes, heart disease, and joint problems. Weight management through a sustainable, balanced diet is more effective than crash diets.',
        'foods_to_eat': 'Vegetables (especially leafy greens), legumes, whole grains, lean protein (eggs, fish, chicken), low-fat dairy, fruits, nuts in moderation, soup, salads.',
        'foods_to_limit': 'Fried foods, sweets, soft drinks, alcohol, white rice in excess, maida products, full-fat dairy, processed snacks, chips, biscuits, fast food.',
        'fruits_info': 'All fruits are generally good, but eat in moderation (2 per day). Best choices: guava (high fiber, low calories), papaya, watermelon, berries, apple. Avoid fruit juice.',
        'vegetables_info': 'Fill half your plate with vegetables at every meal. Cucumber, bottle gourd (lauki), ridge gourd (turai), zucchini are low-calorie and filling. Eat salad before meals.',
        'herbs_info': 'Green tea — boosts metabolism and burns fat. Fenugreek seeds water in morning. Cinnamon — reduces cravings. Ginger tea between meals.',
        'spices_info': 'Cayenne pepper (capsaicin boosts metabolism), cinnamon (reduces appetite), ginger, black pepper, turmeric. Add these to meals for flavor without calories.',
        'cooking_methods': 'Boil, steam, grill, air-fry. Avoid deep frying. Measure oil — use no more than 2–3 teaspoons per day total. Non-stick cookware reduces oil use.',
        'meal_timing': 'Eat 3 main meals and 1–2 small healthy snacks. Do not skip breakfast. Eat dinner early (by 7 PM). Stop eating at least 3 hours before sleep.',
        'portion_guidance': 'Use a smaller plate to naturally reduce portions. Fill half with vegetables, quarter with protein, quarter with grains. Drink a glass of water before eating. Chew slowly.',
        'faq': json.dumps([
            {'q': 'How much weight can I lose with diet alone?', 'a': 'With a 500-calorie daily deficit, you can lose 0.5–1 kg per week safely. Combine with 30 minutes of walking daily for best results.'},
            {'q': 'Is rice fattening?', 'a': 'Rice itself is not fattening — excess calories are. Limit to 1 cup cooked rice per meal, choose brown rice, and eat with lots of vegetables.'},
        ]),
    },
    {
        'name': 'Kidney Health',
        'icon': '🫘',
        'order': 9,
        'is_featured': True,
        'overview': 'The kidneys filter waste from blood. A kidney-friendly diet limits potassium, phosphorus, sodium, and protein in advanced stages. Early stage kidney disease benefits from staying hydrated and reducing processed foods.',
        'foods_to_eat': 'Cauliflower, cabbage, apple, cranberries, blueberries, egg whites, olive oil, garlic, onion, rice, pasta, white bread (low potassium).',
        'foods_to_limit': 'Bananas, oranges, potatoes, tomatoes (high potassium), dairy, nuts, seeds, whole grains (high phosphorus), processed meats, pickles, extra salt, protein in large amounts.',
        'fruits_info': 'Apple, grapes, cherries, strawberries, pineapple, cranberries. AVOID: banana, orange, kiwi, dried fruits (very high in potassium). Limit fruit to 1 portion per meal.',
        'vegetables_info': 'Cauliflower, cabbage, green beans, lettuce, cucumber. Leach vegetables (soak peeled vegetables in water for 2 hours, discard water) to reduce potassium content.',
        'herbs_info': 'Dandelion tea (gentle diuretic). Nettle leaf tea. Avoid herbal supplements without doctor approval — many can harm kidneys.',
        'spices_info': 'Garlic, onion powder, herbs (basil, rosemary, thyme) as salt substitutes. Avoid potassium chloride salt substitutes.',
        'cooking_methods': 'Boil vegetables and discard water to remove potassium. Avoid pressure cooking which retains potassium. Rinse canned foods thoroughly.',
        'meal_timing': 'Drink adequate water unless restricted by doctor. Spread protein intake throughout the day rather than large amounts at one meal.',
        'portion_guidance': 'Protein: 0.6–0.8g per kg of body weight (unless on dialysis). Limit potassium to 2000mg/day. Limit phosphorus to 800–1000mg/day. Sodium less than 2000mg/day.',
        'faq': json.dumps([
            {'q': 'How much water should a kidney patient drink?', 'a': 'This depends on your kidney condition and stage. Generally 1.5–2 liters per day, but your doctor will specify the right amount based on your urine output and test results.'},
            {'q': 'Can kidney patients eat tomatoes?', 'a': 'Tomatoes are high in potassium. In early stage kidney disease, moderate amounts are okay. In advanced stages, limit tomatoes or cook and drain them to reduce potassium.'},
        ]),
    },
    {
        'name': 'Heart Health',
        'icon': '❤️',
        'order': 10,
        'is_featured': True,
        'overview': 'Heart disease is the leading cause of death worldwide. A heart-healthy diet reduces LDL cholesterol, blood pressure, and inflammation — the three main factors that damage arteries.',
        'foods_to_eat': 'Fatty fish (salmon, mackerel, sardines), oats, nuts (almonds, walnuts), olive oil, avocado, berries, dark leafy greens, legumes, flaxseeds, dark chocolate (70%+).',
        'foods_to_limit': 'Trans fats (vanaspati, margarine), saturated fats, red and processed meat, full-fat dairy, salt, sugar, alcohol, fried foods, refined carbs.',
        'fruits_info': 'Pomegranate (lowers blood pressure), berries (reduce inflammation), avocado (healthy fats), citrus fruits (folate and potassium), watermelon (lycopene).',
        'vegetables_info': 'Spinach, kale, broccoli, garlic, onion, tomato, sweet potato. Garlic is particularly heart-protective. Aim for 5 servings of vegetables per day.',
        'herbs_info': 'Garlic — reduces cholesterol and blood pressure. Turmeric — reduces inflammation. Hawthorn berry tea — traditional heart tonic. Arjuna bark (Terminalia arjuna) — Ayurvedic heart remedy.',
        'spices_info': 'Turmeric, garlic, ginger, cinnamon, cayenne pepper. These spices reduce inflammation, improve circulation, and lower cholesterol.',
        'cooking_methods': 'Use olive oil or mustard oil. Avoid trans fats and vanaspati. Bake, grill, steam. Avoid frying. Mediterranean cooking style is ideal for heart health.',
        'meal_timing': 'Never skip breakfast — people who skip breakfast have higher risk of heart disease. Eat a light dinner by 7 PM. Avoid large meals at night.',
        'portion_guidance': 'Follow the Mediterranean or DASH diet pattern. 7–9 servings of fruits and vegetables daily. Fish 2–3 times per week. Nuts: one handful daily. Olive oil: 2–4 tablespoons daily.',
        'faq': json.dumps([
            {'q': 'Is ghee bad for the heart?', 'a': 'Ghee in small amounts (1–2 teaspoons per day) is acceptable. In excess, it raises LDL cholesterol. Replace with olive oil or mustard oil for daily cooking.'},
            {'q': 'Can heart patients eat eggs?', 'a': 'Yes! Current research shows 1 egg per day is safe for most heart patients. The egg white is always safe — it is pure protein with no cholesterol.'},
            {'q': 'What is the best diet for heart health?', 'a': 'The Mediterranean diet is the most studied and proven diet for heart health. It emphasizes vegetables, fruits, whole grains, olive oil, nuts, and fish.'},
        ]),
    },
]

FRUITS = [
    {'name': 'Banana', 'icon': '🍌', 'description': 'A popular fruit rich in potassium and natural sugars.', 'nutrition': 'Calories: 89 kcal, Carbs: 23g, Fiber: 2.6g, Potassium: 358mg, Vitamin B6, Vitamin C', 'benefits': 'Energy boost, good for muscles and heart health, aids digestion, improves mood (serotonin precursor)', 'serving_size': '1 medium banana (118g)', 'best_time': 'Morning or pre-workout', 'diabetes_safe': False, 'diabetes_note': 'Limit to 1 small banana per day. Avoid overripe bananas as they have a higher glycemic index. Best eaten in the morning.', 'is_featured': True},
    {'name': 'Apple', 'icon': '🍎', 'description': 'The classic healthy fruit — eat with skin for maximum fiber.', 'nutrition': 'Calories: 52 kcal, Fiber: 2.4g, Vitamin C, Potassium, Quercetin, Pectin', 'benefits': 'Lowers cholesterol (soluble fiber), supports heart health, stabilizes blood sugar, improves gut health', 'serving_size': '1 medium apple (182g)', 'best_time': 'Morning or as a snack', 'diabetes_safe': True, 'diabetes_note': 'Excellent for diabetics — the fiber slows sugar absorption. Eat with the skin. One apple per day is ideal.', 'is_featured': True},
    {'name': 'Mango', 'icon': '🥭', 'description': 'The king of fruits — delicious and nutritious, but high in sugar.', 'nutrition': 'Calories: 60 kcal, Vitamin C: 36mg, Vitamin A, Folate, Potassium, Fiber: 1.6g', 'benefits': 'Boosts immunity, improves eye health, aids digestion, promotes healthy skin and hair', 'serving_size': '½ cup (82g) or 8–10 slices', 'best_time': 'Morning after breakfast', 'diabetes_safe': False, 'diabetes_note': 'Eat only ½ cup per day. Eat after a meal, not on empty stomach. Avoid mango juice or milkshake.', 'is_featured': True},
    {'name': 'Guava', 'icon': '🍈', 'description': 'Superfruit for diabetes — very low GI, extremely high in fiber and Vitamin C.', 'nutrition': 'Calories: 68 kcal, Vitamin C: 228mg, Fiber: 5.4g, Lycopene, Potassium, Magnesium', 'benefits': 'Lowers blood sugar, boosts immunity, improves digestion, heart health, skin health', 'serving_size': '1 medium guava (100g)', 'best_time': 'Morning on empty stomach or as a snack', 'diabetes_safe': True, 'diabetes_note': 'Excellent for diabetics! Low glycemic index, high fiber. Can eat 1–2 per day freely.', 'is_featured': True},
    {'name': 'Papaya', 'icon': '🍑', 'description': 'A digestive powerhouse with anti-inflammatory properties.', 'nutrition': 'Calories: 43 kcal, Vitamin C: 61mg, Vitamin A, Folate, Papain (enzyme), Fiber: 1.7g', 'benefits': 'Aids digestion (papain enzyme), reduces inflammation, boosts immunity, supports liver health', 'serving_size': '1 cup cubed papaya (140g)', 'best_time': 'Morning on empty stomach', 'diabetes_safe': True, 'diabetes_note': 'Safe for diabetics in moderate portions. The papain enzyme helps with digestion. 1 cup per day is fine.', 'is_featured': True},
    {'name': 'Orange', 'icon': '🍊', 'description': 'The most popular source of Vitamin C — great for immunity.', 'nutrition': 'Calories: 47 kcal, Vitamin C: 53mg, Fiber: 2.4g, Folate, Potassium, Flavonoids', 'benefits': 'Boosts immunity, lowers cholesterol, reduces blood pressure, anti-inflammatory, skin health', 'serving_size': '1 medium orange (131g)', 'best_time': 'Morning or afternoon', 'diabetes_safe': True, 'diabetes_note': 'Eat the whole fruit, not juice. The fiber in whole orange slows sugar absorption. 1 orange per day is fine.', 'is_featured': True},
    {'name': 'Pomegranate', 'icon': '❤️', 'description': 'One of the most antioxidant-rich fruits — excellent for heart health.', 'nutrition': 'Calories: 83 kcal, Fiber: 4g, Vitamin C, Vitamin K, Folate, Punicalagins, Punicic acid', 'benefits': 'Lowers blood pressure, fights inflammation, reduces arthritis pain, improves memory, anti-cancer', 'serving_size': '½ cup arils (87g)', 'best_time': 'Morning or afternoon', 'diabetes_safe': True, 'diabetes_note': 'Rich in antioxidants and fiber. Safe for diabetics in moderation. Avoid pomegranate juice which has concentrated sugar.', 'is_featured': True},
    {'name': 'Jamun', 'icon': '🫐', 'description': 'Indian blackberry — the best fruit for diabetes management.', 'nutrition': 'Calories: 62 kcal, Fiber, Iron, Vitamin C, Anthocyanins, Ellagic acid, Jamboline', 'benefits': 'Specifically controls blood sugar (jamboline compound), improves hemoglobin, liver health, oral health', 'serving_size': '15–20 jamun berries', 'best_time': 'Morning or afternoon snack', 'diabetes_safe': True, 'diabetes_note': 'The BEST fruit for diabetes. Jamboline slows conversion of starch to sugar. Seeds can be dried and powdered for even greater effect.', 'is_featured': True},
]

VEGETABLES = [
    {'name': 'Spinach (Palak)', 'description': 'Dark leafy green, one of the most nutritious vegetables.', 'nutrition': 'Calories: 23 kcal, Iron: 2.7mg, Vitamin K, Vitamin A, Folate, Magnesium, Lutein', 'benefits': 'Builds blood (iron), protects eyes, strengthens bones, anti-inflammatory, lowers blood pressure', 'cooking_methods': 'Saag, dal palak, smoothie, stir-fry, soup. Do not overcook — light cooking preserves nutrients', 'best_time': 'Lunch or dinner', 'serving_size': '1 cup cooked (180g)', 'is_featured': True},
    {'name': 'Bitter Gourd (Karela)', 'description': 'The most powerful vegetable for blood sugar control.', 'nutrition': 'Calories: 17 kcal, Vitamin C, Iron, Charantin (blood sugar lowering compound), Polypeptide-p', 'benefits': 'Dramatically lowers blood sugar, improves insulin sensitivity, liver tonic, boosts immunity', 'cooking_methods': 'Stir-fry with onion and spices, juice (1 glass morning), stuffed karela. Rub salt and squeeze to reduce bitterness.', 'best_time': 'Morning (as juice) or lunch', 'serving_size': '1 medium karela or ½ cup juice', 'is_featured': True},
    {'name': 'Broccoli', 'description': 'A cruciferous superfood packed with cancer-fighting compounds.', 'nutrition': 'Calories: 34 kcal, Vitamin C: 89mg, Vitamin K, Sulforaphane, Fiber: 2.6g, Calcium', 'benefits': 'Anti-cancer (sulforaphane), protects liver, reduces cholesterol, heart health, bone strength', 'cooking_methods': 'Steam lightly (do not overcook — kills nutrients), stir-fry, add to soup, eat raw in salads', 'best_time': 'Lunch', 'serving_size': '1 cup florets (91g)', 'is_featured': True},
    {'name': 'Drumstick (Moringa)', 'description': 'Called the miracle tree — every part is medicinal.', 'nutrition': 'Calories: 37 kcal, Protein: 2.1g, Calcium, Iron, Vitamin C, Vitamin A, Potassium, Antioxidants', 'benefits': 'Manages blood sugar, reduces inflammation, boosts energy, improves bone density, milk production in nursing mothers', 'cooking_methods': 'Sambar, dal, stir-fry. Moringa leaf powder in smoothies, chutney, roti', 'best_time': 'Any meal', 'serving_size': '2–3 drumsticks or 1 tbsp moringa powder', 'is_featured': True},
    {'name': 'Sweet Potato', 'description': 'A nutritious alternative to regular potato, rich in fiber and beta-carotene.', 'nutrition': 'Calories: 86 kcal, Fiber: 3g, Vitamin A: 961mcg, Potassium, Vitamin C, Manganese', 'benefits': 'Stabilizes blood sugar (despite sweetness), improves vision, immune booster, anti-inflammatory, gut health', 'cooking_methods': 'Bake, boil, steam. Avoid frying. Baked sweet potato is the healthiest preparation.', 'best_time': 'Lunch or pre-workout', 'serving_size': '1 medium sweet potato (130g)', 'is_featured': True},
    {'name': 'Garlic', 'description': 'One of the most powerful medicinal foods known to humanity.', 'nutrition': 'Calories: 4 kcal per clove, Allicin, Manganese, Vitamin B6, Vitamin C, Selenium', 'benefits': 'Lowers blood pressure, reduces cholesterol, boosts immunity (antibiotic effect), anti-cancer, anti-fungal', 'cooking_methods': 'Crush or chop and let rest 10 minutes before cooking (activates allicin). Add to all savory dishes. Eat 1–2 raw cloves daily for maximum benefit.', 'best_time': 'Morning on empty stomach (raw)', 'serving_size': '2–3 cloves per day', 'is_featured': True},
]

HERBS = [
    {'name': 'Turmeric (Haldi)', 'description': 'The golden spice of India — the most researched medicinal herb in the world.', 'traditional_uses': 'Used in Indian medicine for 4000 years for wounds, infections, digestion, liver problems, and joint pain.', 'scientific_evidence': 'Over 10,000 peer-reviewed studies. Curcumin reduces inflammation as effectively as anti-inflammatory drugs in some cases.', 'preparation': 'Golden milk (turmeric in warm milk with black pepper), turmeric in cooking, turmeric water, capsule supplement.', 'benefits': 'Powerful anti-inflammatory, antioxidant, improves brain function (BDNF), lowers heart disease risk, anti-cancer potential, helps arthritis.', 'precautions': 'High doses may cause digestive issues. Avoid if on blood thinners. Always combine with black pepper to improve absorption by 2000%.', 'is_featured': True},
    {'name': 'Tulsi (Holy Basil)', 'description': 'Sacred herb of India — an adaptogen that helps the body handle stress.', 'traditional_uses': 'Worshipped in Hindu tradition. Used for centuries to treat respiratory problems, fever, stress, and infections.', 'scientific_evidence': 'Proven adaptogenic properties. Studies show it reduces cortisol, blood sugar, cholesterol, and blood pressure.', 'preparation': '10–15 fresh tulsi leaves in warm water each morning. Tulsi tea. Chew fresh leaves. Tulsi ark (extract).', 'benefits': 'Reduces stress and anxiety, boosts immunity, fights infections, lowers blood sugar and blood pressure, liver protective.', 'precautions': 'May slow blood clotting. Avoid during pregnancy in large amounts. May interact with blood-thinning medications.', 'is_featured': True},
    {'name': 'Ginger (Adrak)', 'description': 'A warming spice and potent anti-nausea and anti-inflammatory herb.', 'traditional_uses': 'Used in Ayurveda for 5000 years for digestion, nausea, pain relief, and respiratory problems.', 'scientific_evidence': 'Gingerol and shogaol are the active compounds. Proven to reduce nausea, lower blood sugar, fight infections.', 'preparation': 'Fresh ginger tea, ginger in cooking, ginger water, grated ginger in smoothies, pickled ginger.', 'benefits': 'Eliminates nausea (including morning sickness), reduces muscle pain, lowers blood sugar, anti-inflammatory, fights infections.', 'precautions': 'Avoid more than 4g per day. May cause heartburn. Consult doctor if on blood thinners or diabetes medication.', 'is_featured': True},
    {'name': 'Neem', 'description': 'The village pharmacy — almost every part of the neem tree is medicinal.', 'traditional_uses': 'Used in Indian medicine for skin diseases, diabetes, fever, dental hygiene, and as a natural antiseptic.', 'scientific_evidence': 'Proven antibacterial, antifungal, anti-inflammatory, and blood sugar lowering effects.', 'preparation': 'Neem leaf juice (bitter, start with small amounts), neem twig for teeth brushing, neem water, neem capsules.', 'benefits': 'Controls blood sugar, purifies blood, treats skin conditions (acne, eczema), dental health, liver protection, anti-cancer.', 'precautions': 'Do NOT give to children or pregnant women. High doses can be toxic to liver. Consult doctor if on diabetes medications.', 'is_featured': True},
    {'name': 'Fenugreek (Methi)', 'description': 'A powerful herb for blood sugar control and cholesterol reduction.', 'traditional_uses': 'Used in Indian and Middle Eastern medicine for diabetes, digestive problems, inflammation, and increasing breast milk.', 'scientific_evidence': 'Multiple clinical trials confirm blood sugar lowering effects. Contains galactomannan fiber that slows carbohydrate digestion.', 'preparation': 'Soak 1 teaspoon seeds in water overnight. Drink water and eat seeds in morning. Methi leaves in cooking. Methi powder in roti.', 'benefits': 'Lowers blood sugar, reduces LDL cholesterol, reduces inflammation, aids digestion, increases breast milk, improves testosterone.', 'precautions': 'May cause gas and bloating initially. Do not use in high doses during pregnancy. May lower blood sugar too much combined with medication.', 'is_featured': True},
    {'name': 'Coriander (Dhania)', 'description': 'Used both as a herb (leaves) and spice (seeds) — excellent for digestion and cholesterol.', 'traditional_uses': 'One of the oldest herbs — used in ancient Egypt and India for digestive problems and as a preservative.', 'scientific_evidence': 'Coriander seed water lowers LDL cholesterol, blood sugar, and blood pressure in clinical studies.', 'preparation': 'Coriander seed water: boil 1 tbsp seeds in water, strain, drink warm. Fresh coriander in cooking and chutney.', 'benefits': 'Lowers cholesterol and blood sugar, improves digestion, reduces bloating, anti-inflammatory, anti-bacterial.', 'precautions': 'Very safe herb. Excessive intake may cause sun sensitivity. Rare allergy possible.', 'is_featured': True},
]

RECIPES = [
    {'name': 'Oats Upma', 'category': 'breakfast', 'description': 'A healthy twist on classic upma — perfect for diabetes and weight management.', 'ingredients': '1 cup rolled oats\n1 onion, chopped\n1 tomato, chopped\n1/2 cup mixed vegetables (carrot, beans, peas)\n1 green chilli\n1/4 tsp mustard seeds\n1/4 tsp cumin seeds\n1 tsp oil\nSalt to taste\nFresh coriander', 'steps': 'Dry roast oats in a pan until light golden. Set aside.\nHeat oil in a pan. Add mustard seeds, let them splutter.\nAdd cumin, green chilli, and onion. Saute until golden.\nAdd tomatoes and vegetables. Cook for 3-4 minutes.\nAdd 2 cups warm water and salt. Bring to boil.\nAdd roasted oats. Stir continuously on low heat for 3-4 minutes.\nGarnish with fresh coriander. Serve hot.', 'nutrition': 'Protein: 8g, Fiber: 4g, Carbs: 32g, Fat: 3g', 'calories': 210, 'prep_time': 5, 'cook_time': 15, 'servings': 2, 'difficulty': 'easy', 'is_featured': True},
    {'name': 'Moong Dal Chilla', 'category': 'breakfast', 'description': 'Protein-rich green moong pancakes — ideal for diabetes, PCOS, and weight loss.', 'ingredients': '1 cup green moong dal, soaked 4 hours\n1 green chilli\n1/2 inch ginger\nSalt to taste\n1/4 tsp cumin powder\nFresh coriander\nOil for cooking', 'steps': 'Drain soaked moong dal. Blend to smooth batter with chilli and ginger.\nAdd salt, cumin powder, and coriander. Mix well.\nBatter should be thin like dosa batter.\nHeat non-stick pan, brush lightly with oil.\nPour one ladle of batter, spread in circle.\nCook on medium heat 2-3 minutes, flip, cook 1-2 more minutes.\nServe with green chutney or curd.', 'nutrition': 'Protein: 14g, Fiber: 8g, Carbs: 28g, Fat: 2g', 'calories': 185, 'prep_time': 10, 'cook_time': 15, 'servings': 4, 'difficulty': 'easy', 'is_featured': True},
    {'name': 'Palak Dal', 'category': 'lunch', 'description': 'Iron-rich spinach with protein-packed dal — a complete nutritious meal.', 'ingredients': '1 cup toor dal\n2 cups fresh spinach, chopped\n1 onion, chopped\n2 tomatoes, chopped\n3-4 garlic cloves\n1 tsp cumin seeds\n1/2 tsp turmeric\n1/2 tsp coriander powder\n1 tsp oil\nSalt to taste', 'steps': 'Pressure cook toor dal with turmeric for 3-4 whistles until soft.\nHeat oil in pan. Add cumin seeds.\nAdd garlic and onion. Saute until golden.\nAdd tomatoes, cook until soft.\nAdd spinach, cook 2 minutes until wilted.\nMash cooked dal and add to pan.\nAdd spices and salt. Simmer 5 minutes.\nServe with roti or brown rice.', 'nutrition': 'Protein: 15g, Iron: 5mg, Fiber: 8g, Calcium: 120mg', 'calories': 220, 'prep_time': 10, 'cook_time': 20, 'servings': 3, 'difficulty': 'easy', 'is_featured': True},
    {'name': 'Vegetable Soup', 'category': 'snack', 'description': 'A warming detox soup with no oil — perfect for weight loss and fatty liver.', 'ingredients': '1 carrot, chopped\n1 cup cabbage, shredded\n1 cup spinach\n1 tomato, chopped\n2 garlic cloves\n1 inch ginger\n1/2 tsp black pepper\nSalt to taste\n4 cups water\nFresh coriander', 'steps': 'Bring water to boil in a pot.\nAdd carrots and garlic. Cook 5 minutes.\nAdd cabbage and tomato. Cook 3 minutes.\nAdd spinach, ginger, salt, and pepper.\nSimmer for 5 minutes.\nBlend half the soup for thicker consistency (optional).\nGarnish with coriander and lemon juice.\nServe hot.', 'nutrition': 'Calories: 60 kcal, Fiber: 4g, Vitamin C: 45mg, Potassium: 380mg', 'calories': 60, 'prep_time': 10, 'cook_time': 15, 'servings': 2, 'difficulty': 'easy', 'is_featured': True},
    {'name': 'Karela Sabji', 'category': 'lunch', 'description': 'Bitter gourd stir-fry — the most powerful dish for diabetes control.', 'ingredients': '3 medium bitter gourds (karela)\n1 onion, sliced\n1 tsp cumin seeds\n1/2 tsp turmeric\n1/2 tsp coriander powder\n1/4 tsp red chilli\n1 tsp oil\nSalt to taste\n1/2 tsp jaggery (optional, to balance bitterness)', 'steps': 'Slice karela thinly. Rub with salt, let sit 15 minutes. Squeeze out water (reduces bitterness).\nHeat oil in pan. Add cumin seeds.\nAdd onion and saute until golden.\nAdd karela slices. Cook on medium heat 10 minutes, stirring occasionally.\nAdd all spices and salt. Mix well.\nAdd jaggery if using.\nCook 5 more minutes until karela is tender.\nServe with roti.', 'nutrition': 'Calories: 85 kcal, Fiber: 3g, Vitamin C: 42mg, Blood sugar lowering compounds', 'calories': 85, 'prep_time': 20, 'cook_time': 20, 'servings': 2, 'difficulty': 'medium', 'is_featured': True},
    {'name': 'Turmeric Golden Milk', 'category': 'drink', 'description': 'Anti-inflammatory bedtime drink — helps with arthritis, immunity, and sleep.', 'ingredients': '1 cup warm milk (dairy or plant-based)\n1/2 tsp turmeric powder\n1/4 tsp cinnamon powder\nA pinch of black pepper (essential for curcumin absorption)\n1 tsp honey or dates (optional)\nPinch of ginger powder', 'steps': 'Heat milk until warm (not boiling).\nAdd turmeric, cinnamon, ginger, and black pepper.\nWhisk until well blended — no lumps.\nAdd sweetener if desired.\nDrink warm, 30 minutes before bedtime.\nDrink daily for best results.', 'nutrition': 'Calories: 120 kcal, Calcium: 280mg, Curcumin: 200mg, Anti-inflammatory compounds', 'calories': 120, 'prep_time': 2, 'cook_time': 3, 'servings': 1, 'difficulty': 'easy', 'is_featured': True},
]


class Command(BaseCommand):
    help = 'Seed initial health data — conditions, fruits, vegetables, herbs, recipes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding health conditions...')
        for c in CONDITIONS:
            faq = c.pop('faq', '[]')
            obj, created = HealthCondition.objects.update_or_create(
                slug=slugify(c['name']),
                defaults={**c, 'slug': slugify(c['name']), 'faq': faq}
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {obj.name}')

        self.stdout.write('Seeding fruits...')
        for f in FRUITS:
            icon = f.pop('icon', '')
            obj, created = Fruit.objects.update_or_create(
                slug=slugify(f['name']),
                defaults={**f, 'slug': slugify(f['name'])}
            )
            self.stdout.write(f'  {"Created" if created else "Updated"}: {obj.name}')

        self.stdout.write('Seeding vegetables...')
        for v in VEGETABLES:
            obj, created = Vegetable.objects.update_or_create(
                slug=slugify(v['name'].split('(')[0].strip()),
                defaults={**v, 'slug': slugify(v['name'].split('(')[0].strip())}
            )
            self.stdout.write(f'  {"Created" if created else "Updated"}: {obj.name}')

        self.stdout.write('Seeding herbs...')
        for h in HERBS:
            obj, created = Herb.objects.update_or_create(
                slug=slugify(h['name'].split('(')[0].strip()),
                defaults={**h, 'slug': slugify(h['name'].split('(')[0].strip())}
            )
            self.stdout.write(f'  {"Created" if created else "Updated"}: {obj.name}')

        self.stdout.write('Seeding recipes...')
        for r in RECIPES:
            obj, created = Recipe.objects.update_or_create(
                slug=slugify(r['name']),
                defaults={**r, 'slug': slugify(r['name'])}
            )
            self.stdout.write(f'  {"Created" if created else "Updated"}: {obj.name}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Seeded {len(CONDITIONS)} conditions, {len(FRUITS)} fruits, '
            f'{len(VEGETABLES)} vegetables, {len(HERBS)} herbs, {len(RECIPES)} recipes.'
        ))
