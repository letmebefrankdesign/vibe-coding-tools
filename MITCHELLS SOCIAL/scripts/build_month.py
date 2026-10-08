"""Builds Mitchell's week files (content/weeks/<YYYY-Www>.json) for Oct 8 - Nov 7, 2026.

Run: python3 scripts/build_month.py
Each post follows the playbook's week-file shape (section 5, step 14).
Captions here are written without the contact line; it's appended once per caption below.
"""
import datetime as dt
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTACT = "321.338.2909\nwww.MitchellsCocoa.com"
SITE = "https://www.mitchellscocoa.com"
BASE_TAGS = ["#MitchellsCocoa", "#CocoaFL", "#BrevardCounty", "#SpaceCoast", "#SpaceCoastEats"]
GBP_DAYS = {0, 2, 4}  # Mon, Wed, Fri
DRINK = "21+. Please drink responsibly."

# time: "AM" = 7:00 AM ET (doors open), "PM" = 7:30 PM ET (see-you-tomorrow posts), or "HH:MM"
POSTS = [
    dict(date="2026-10-08", time="20:30", pillar="See you tomorrow", goal="Tomorrow's breakfast",
         headline="See you at Mitchell's", media=["country-fried-chicken-breakfast-mitchells-cocoa"],
         text="Country fried chicken, sausage gravy made from scratch, two eggs your way, hash browns and a biscuit.\n\nThat's tomorrow morning sorted. Doors open at 7am.\n\nSee you at Mitchell's.",
         fbq="What are you ordering first?",
         tags=["#FloridaBreakfast", "#SouthernBreakfast", "#CountryFriedChicken", "#BreakfastTime"]),
    dict(date="2026-10-09", time="AM", pillar="Omelets", goal="World Egg Day traffic",
         headline=["World Egg Day", "Four-egg omelets"],
         media=["garbage-can-omelet-mitchells-cocoa-florida", "wild-western-omelet-mitchells-cocoa-florida"],
         text="Happy World Egg Day.\n\nWe celebrate with four eggs at a time. The Garbage Can Omelet comes loaded with bacon, sausage, ham, onions, peppers, tomatoes, mushrooms and American cheese. The Wild Western brings smoked applewood ham, onions and green peppers.\n\nPeople drive in from Melbourne for these. Open today 7am-2pm.",
         fbq="Garbage Can or Wild Western?",
         tags=["#WorldEggDay", "#Omelets", "#BreakfastAndBrunch", "#FloridaBreakfast"],
         gbp="Happy World Egg Day. Celebrate with a four-egg omelet, from the loaded Garbage Can Omelet to the Wild Western. Breakfast served 7am-2pm every day in Cocoa."),
    dict(date="2026-10-10", time="AM", pillar="Weekend brunch", goal="Saturday brunch + mimosas",
         headline=["Weekend brunch", "Mimosas are poured"],
         media=["mimosas-mitchells", "strawberry-blueberry-waffle-mitchells-restaurant"],
         text="Saturday brunch is on.\n\nMimosas by the glass or the pitcher, and a fresh-made waffle piled with strawberries, blueberries and whipped cream to go with them.\n\nWe're open 7am-2pm. Bring the crew.\n\n" + DRINK,
         fbq="Glass or pitcher?",
         tags=["#Mimosas", "#SaturdayBrunch", "#BrunchTime", "#Waffles", "#BrunchAndMimosas"]),
    dict(date="2026-10-11", time="AM", pillar="Weekend brunch", goal="Sunday brunch",
         headline="Sunday brunch", media=["southern-skillet-mitchells-restaurant-cocoa-florida-1000"],
         text="Sunday brunch looks like this.\n\nThe Southern Skillet: home fries or hash browns smothered in grilled onions, green peppers and sausage gravy, your choice of bacon, sausage or ham, and two eggs on top.\n\nBrunch and mimosas today, 7am-2pm.\n\n" + DRINK,
         fbq="Who are you bringing to brunch?",
         tags=["#SundayBrunch", "#SouthernSkillet", "#BrunchTime", "#Mimosas"]),
    dict(date="2026-10-12", time="AM", pillar="Breakfast", goal="Weekday breakfast",
         headline="Breakfast your way", media=["corned-beef-hash-eggs-american-cheese-grits-mitchells-restaurant-32922"],
         text="Monday calls for a real breakfast.\n\nTwo eggs, corned beef hash, cheese grits and toast. Or build your own: eggs your way, hash browns, home fries, grits or sliced tomatoes, and toast or a biscuit.\n\nMade to order from 7am.",
         fbq="Grits or hash browns?",
         tags=["#MondayMotivation", "#FloridaBreakfast", "#BreakfastTime", "#CornedBeefHash"],
         gbp="Start the week with breakfast made to order: two eggs, corned beef hash, cheese grits and toast. Open 7am-2pm every day on US-1 in Cocoa."),
    dict(date="2026-10-13", time="AM", pillar="Event trays", goal="Boss's Day tray orders",
         headline=["Boss's Day is Friday", "Event trays"],
         media=["the-spread-mitchells-restaurant-event-trays", "biscuit-sandwich-trays-mitchells-restaurant-event-trays"],
         text="Boss's Day is this Friday, Oct 16.\n\nFeed the whole office with Mitchell's event trays. The Spread serves 32+ meals, and our biscuit sandwich trays come with 15 big half biscuit sandwiches.\n\nTrays need 24-48 hours notice, so call today to have yours ready for Friday.",
         fbq="Tag the coworker who plans the office lunch.",
         tags=["#BossDay", "#OfficeLunch", "#Catering", "#EventTrays", "#BrevardCatering"]),
    dict(date="2026-10-14", time="PM", pillar="Brunch tease", goal="Midweek push for weekend brunch",
         headline=["Chicken & waffles", "This weekend"], media=["chicken-and-waffles-mitchells-restaurant"],
         text="Halfway to the weekend.\n\nPicture this on Saturday: four breaded chicken tenders on a fresh-made waffle, with mimosas on the side.\n\nWeekend brunch at Mitchell's, Saturday and Sunday, 7am-2pm. See you there.\n\n" + DRINK,
         fbq="Syrup or hot sauce on your chicken & waffles?",
         tags=["#ChickenAndWaffles", "#WeekendBrunch", "#Waffles", "#BrunchPlans"],
         gbp="Weekend brunch is Saturday and Sunday, 7am-2pm. Chicken & waffles, omelets, skillets and mimosas, all made to order in Cocoa."),
    dict(date="2026-10-15", time="PM", pillar="Burgers", goal="Tomorrow's lunch",
         headline="Tomorrow's lunch", media=["bacon-cheese-burger-mitchells-restaurant-cocoa-florida"],
         text="Tomorrow's lunch plan: the All American.\n\nAn 8 oz char grilled steak burger, fresh and never frozen, with two slices of bacon and American cheese on a soft bun.\n\nSee you at Mitchell's tomorrow. Open 7am-2pm.",
         fbq="What's your go-to burger topping?",
         tags=["#Burgers", "#SteakBurger", "#LunchTime", "#FreshNeverFrozen"]),
    dict(date="2026-10-16", time="AM", pillar="Lunch trays", goal="Boss's Day lunch",
         headline=["Happy Boss's Day", "Lunch is on you"], media=["kicken-bourbon-chicken-tender-tray-mitchells-cocoa-florida"],
         text="Happy Boss's Day.\n\nTreating the team to lunch? Our Kicken Bourbon chicken tender tray is hand battered, fried golden brown and glazed in our own bourbon sauce, with house-made chips and a pickle spear.\n\nCall ahead for pickup, or come in. Open 7am-2pm.",
         fbq="Tag your boss. They know what they did.",
         tags=["#BossDay", "#ChickenTenders", "#KickenBourbon", "#LunchTime"],
         gbp="Happy Boss's Day. Treat the team to lunch trays like our Kicken Bourbon chicken tenders, hand battered and made to order. Call ahead for pickup."),
    dict(date="2026-10-17", time="AM", pillar="Weekend brunch", goal="Saturday brunch",
         headline=["Peanut Butter", "Bacon Explosion"], media=["peanut-butter-bacon-explosion-waffle-mitchells-restaurant"],
         text="Meet the Peanut Butter Bacon Explosion.\n\nA fresh-made waffle with peanut butter drizzle, chocolate syrup, chocolate chips, bacon crumbles, berries and whipped cream. Yes, all of it.\n\nSaturday brunch and mimosas, 7am-2pm.\n\n" + DRINK,
         fbq="Too much? Or just right?",
         tags=["#Waffles", "#SaturdayBrunch", "#BrunchTime", "#Mimosas", "#TreatYourself"]),
    dict(date="2026-10-18", time="AM", pillar="Weekend brunch", goal="Sunday brunch",
         headline="Sunday skillet", media=["country-skillet-mitchells-cocoa-florida"],
         text="Sunday mornings were made for skillets.\n\nCrispy home fries, peppers, onions and sausage gravy under two sunny eggs. Add a mimosa and stay a while.\n\nBrunch today, 7am-2pm.\n\n" + DRINK,
         fbq="Sunny side up or over easy?",
         tags=["#SundayBrunch", "#SouthernBreakfast", "#BrunchTime", "#Mimosas"]),
    dict(date="2026-10-19", time="AM", pillar="Breakfast", goal="Lighter breakfast option",
         headline="Lighter side", media=["oatmeal-fruit-cup-mitchells-cocoa-florida-32922", "egg-whites-sliced-tomatoes-grilled-chicken-breast-mitchells-cocoa-florida"],
         text="Keeping it light this week?\n\nWarm oatmeal with a fresh-cut fruit cup of strawberries, bananas and blueberries. Or egg whites with sliced tomatoes and a grilled chicken breast.\n\nWe have something for everyone, 7am-2pm every day.",
         fbq="Oatmeal or egg whites?",
         tags=["#HealthyBreakfast", "#FreshFruit", "#FloridaBreakfast", "#BreakfastTime"],
         gbp="Lighter breakfast options every day: oatmeal with a fresh-cut fruit cup, or egg whites with sliced tomatoes and grilled chicken. Open 7am-2pm."),
    dict(date="2026-10-20", time="AM", pillar="Chicken", goal="Fresh never frozen chicken",
         headline=["Fresh, never frozen", "Popeye Grilled Chicken"], media=["popeye-grilled-chicken-mitchells-restaurant-cocoa-florida"],
         text="Our chicken is fresh, never frozen, and made to order.\n\nThe Popeye Grilled Chicken sandwich: grilled chicken breast with spinach, two slices of bacon and cheese on a soft bun.\n\nFreshness makes all the difference. Lunch today, 7am-2pm.",
         fbq="Grilled or fried? Pick a side.",
         tags=["#FreshNeverFrozen", "#ChickenSandwich", "#LunchTime", "#GrilledChicken"]),
    dict(date="2026-10-21", time="PM", pillar="Brunch tease", goal="Midweek push for weekend brunch",
         headline=["Erica's Favorite", "Weekend brunch"], media=["banana-peanut-butter-waffle-mitchells-restaurant"],
         text="Already thinking about Saturday?\n\nErica's Favorite waffle: sliced bananas, peanut butter and chocolate syrup on a waffle made fresh to order.\n\nWeekend brunch with mimosas, Saturday and Sunday, 7am-2pm. See you at Mitchell's.\n\n" + DRINK,
         fbq="Bananas and peanut butter: yes or no?",
         tags=["#Waffles", "#WeekendBrunch", "#BrunchPlans", "#PeanutButter"],
         gbp="Weekend brunch is Saturday and Sunday, 7am-2pm. Try Erica's Favorite waffle with bananas, peanut butter and chocolate syrup."),
    dict(date="2026-10-22", time="PM", pillar="Location", goal="Space Coast visitors",
         headline=["On US-1 in Cocoa", "See you tomorrow"], media=["mitchells-restaurant-cocoa-florida-1400-n-cocoa-blvd"],
         igmedia=["southern-belle-burger-mitchells-restaurant-cocoa-florida"],
         text="Heading to the beach or catching a launch this weekend?\n\nWe're right on US-1 in Cocoa, between the 520 and the 528 and close to I-95. The most delicious stop on the way to the Atlantic.\n\nBreakfast, brunch, lunch and mimosas, 7am-2pm every day. See you at Mitchell's.\n\n" + DRINK,
         fbq="Where are you headed this weekend?",
         tags=["#VisitSpaceCoast", "#CocoaBeach", "#CapeCanaveral", "#RoadTripFood"]),
    dict(date="2026-10-23", time="AM", pillar="Apps", goal="Friday lunch",
         headline=["Fried jalapenos", "Fried pickles"], media=["fried-jalapenos-mitchells-cocoa-apps-1", "fried-pickles-mitchells-cocoa-apps"],
         text="Friday lunch deserves an appetizer.\n\nFried jalapenos with ranch, fried pickles with dipping sauce, or both. We won't judge.\n\nOpen 7am-2pm. Come hungry.",
         fbq="Jalapenos or pickles?",
         tags=["#FriedPickles", "#FriedJalapenos", "#Appetizers", "#FridayLunch"],
         gbp="Friday lunch at Mitchell's: start with fried jalapenos or fried pickles, then a steak burger or fresh chicken sandwich. Open 7am-2pm in Cocoa."),
    dict(date="2026-10-24", time="AM", pillar="Weekend brunch", goal="Saturday brunch",
         headline="Deluxe Chicken Biscuit", media=["chicken-biscuit-sandwich-mitchells-brevard-county-florida"],
         text="The Deluxe Chicken Biscuit.\n\nA boneless chicken breast, hand breaded and fried, with American cheese, an egg and two slices of bacon on a biscuit.\n\nSaturday brunch and mimosas, 7am-2pm.\n\n" + DRINK,
         fbq="Rate this biscuit 1 to 10.",
         tags=["#ChickenBiscuit", "#SaturdayBrunch", "#BreakfastSandwich", "#Mimosas"]),
    dict(date="2026-10-25", time="AM", pillar="Weekend brunch", goal="Sunday brunch",
         headline="Sunday brunch", media=["haddock-breakfast-mitchells-cocoa"],
         text="Something different for Sunday brunch.\n\nBeer battered haddock, fried golden, with two eggs, cheese grits and toast.\n\nBrunch and mimosas today, 7am-2pm.\n\n" + DRINK,
         fbq="Ever had fish for breakfast?",
         tags=["#SundayBrunch", "#SouthernBreakfast", "#Mimosas", "#BrunchTime"]),
    dict(date="2026-10-26", time="AM", pillar="Comfort food", goal="Signature sausage gravy",
         headline=["Country fried chicken", "Famous sausage gravy"], media=["country-fried-chicken-entree-mitchells"],
         text="Smothered.\n\nOur 8 oz country fried chicken breast, deep fried and covered in our famous house-made sausage gravy.\n\nSouthern comfort, made to order. Open 7am-2pm.",
         fbq="Is there such a thing as too much gravy?",
         tags=["#CountryFriedChicken", "#SausageGravy", "#ComfortFood", "#SouthernFood"],
         gbp="Our 8 oz country fried chicken comes smothered in house-made sausage gravy. Southern comfort, made to order, 7am-2pm every day."),
    dict(date="2026-10-27", time="AM", pillar="Event trays", goal="Halloween party tray orders",
         headline=["Halloween party?", "Event trays"],
         media=["the-entertainer-mitchells-event-trays", "bacon-ranch-deviled-eggs-mitchells-restaurant-event-trays"],
         text="Hosting a Halloween party this weekend?\n\nLet us bring the food. The Entertainer tray, bacon ranch deviled eggs and more, made fresh here in Cocoa.\n\nEvent trays need 24-48 hours notice, so call this week to lock in Saturday.",
         fbq="Tag your party planner.",
         tags=["#HalloweenParty", "#EventTrays", "#Catering", "#PartyFood"]),
    dict(date="2026-10-28", time="PM", pillar="Brunch tease", goal="Halloween weekend brunch",
         headline=["Open on Halloween", "7am-2pm"], media=["peanut-butter-bacon-berry-waffle-mitchells-restaurant-cocoa-florida"],
         text="Halloween is Saturday, and so is brunch.\n\nWe're open 7am-2pm on Halloween. Fuel up with a waffle, an omelet and a mimosa before the trick-or-treating starts.\n\nSee you this weekend at Mitchell's.\n\n" + DRINK,
         fbq="Costume at brunch: yes or no?",
         tags=["#Halloween", "#HalloweenBrunch", "#WeekendBrunch", "#Waffles"],
         gbp="We're open on Halloween, Saturday Oct 31, 7am-2pm. Weekend brunch Saturday and Sunday with waffles, omelets and mimosas."),
    dict(date="2026-10-29", time="PM", pillar="Salads", goal="Tomorrow's lunch",
         headline="Fresh salads", media=["grilled-chicken-salad"],
         text="Tomorrow's lunch, for here or to go.\n\nGrilled chicken salad with cheddar, fresh tomatoes, onions and hard-boiled egg over a bed of romaine.\n\nSee you at Mitchell's tomorrow. Open 7am-2pm.",
         fbq="Grilled or fried chicken on your salad?",
         tags=["#FreshSalad", "#LunchTime", "#GrilledChicken", "#EatFresh"]),
    dict(date="2026-10-30", time="AM", pillar="Burgers", goal="Friday lunch",
         headline=["Humpty Dumpty", "Burger"], media=["humpty-dumpty-burger-mitchells-restaurant-cocoa-florida"],
         text="It's Friday. Put an egg on it.\n\nThe Humpty Dumpty: an 8 oz char grilled steak burger with a fried egg, two slices of bacon and American cheese.\n\nFresh, never frozen. Open 7am-2pm.",
         fbq="Egg on a burger: genius or too much?",
         tags=["#Burgers", "#SteakBurger", "#FridayLunch", "#FreshNeverFrozen"],
         gbp="Friday lunch: the Humpty Dumpty burger, 8 oz char grilled with a fried egg, bacon and American cheese. Fresh, never frozen. Open 7am-2pm."),
    dict(date="2026-10-31", time="AM", pillar="Holiday", goal="Halloween brunch",
         headline=["Happy Halloween", "Open 7am-2pm"], media=["spinach-shrimp-omelet"],
         notes="Swap in Frank's branded Halloween image from media/holiday-posts/ if one is there.",
         text="Happy Halloween from Mitchell's.\n\nWe're open today, 7am-2pm. Treat yourself to brunch and mimosas before the tricks start.\n\nCostumes welcome.\n\n" + DRINK,
         fbq="What are you dressing up as?",
         tags=["#HappyHalloween", "#Halloween", "#SaturdayBrunch", "#Mimosas"]),
    dict(date="2026-11-01", time="AM", pillar="Weekend brunch", goal="Fall back Sunday brunch",
         headline=["Extra hour?", "Spend it on brunch"], media=["veggie-omelet-mitchells-cocoa-florida"],
         text="Clocks fell back last night, which means one extra hour this morning.\n\nWe suggest spending it on brunch. Veggie omelet with onions, tomatoes, peppers, mushrooms and American cheese, with grits on the side.\n\nBrunch and mimosas today, 7am-2pm.\n\n" + DRINK,
         fbq="How are you spending your extra hour?",
         tags=["#FallBack", "#SundayBrunch", "#Omelets", "#Mimosas"]),
    dict(date="2026-11-02", time="AM", pillar="Comfort food", goal="Weekday lunch",
         headline="Fully loaded chili", media=["bowl-of-chili-mitchells-sides"],
         text="Fully loaded.\n\nA bowl of chili topped with jalapenos, bacon, cheddar and sour cream. Have it on its own or as your side.\n\nLunch is served until 2pm.",
         fbq="Beans in chili: yes or no?",
         tags=["#Chili", "#ComfortFood", "#LunchTime", "#SouthernFood"],
         gbp="A fully loaded bowl of chili with jalapenos, bacon, cheddar and sour cream. Breakfast, brunch and lunch every day, 7am-2pm."),
    dict(date="2026-11-03", time="AM", pillar="Sandwiches", goal="National Sandwich Day",
         headline=["National", "Sandwich Day"], media=["mitchells-club-sandwich", "kicken-bourbon-chicken-mitchells-restaurant-cocoa-florida"],
         text="Happy National Sandwich Day.\n\nThe Mitchell's Club, stacked with bacon, lettuce, tomato and mayo. Or the Kicken Bourbon Chicken Melt with grilled onions and provolone on grilled rye.\n\nCome celebrate, 7am-2pm.",
         fbq="Club or melt?",
         tags=["#NationalSandwichDay", "#ClubSandwich", "#LunchTime", "#Sandwiches"]),
    dict(date="2026-11-04", time="PM", pillar="Brunch tease", goal="Midweek push for weekend brunch",
         headline=["Shrimp & salad", "Weekend brunch"], media=["shrimp-salad-mitchells-cocoa"],
         notes="No waffle or brunch photos left unused this month; Frank's branded brunch images can replace this.",
         text="The weekend is almost here.\n\nBrunch at Mitchell's is Saturday and Sunday, 7am-2pm. Prefer something lighter? Our grilled jumbo shrimp salad pairs nicely with a mimosa.\n\nSee you this weekend.\n\n" + DRINK,
         fbq="Who's your brunch buddy?",
         tags=["#WeekendBrunch", "#BrunchPlans", "#ShrimpSalad", "#Mimosas"],
         gbp="Weekend brunch is Saturday and Sunday, 7am-2pm, with mimosas. Grilled jumbo shrimp salad, omelets, waffles and more."),
    dict(date="2026-11-05", time="PM", pillar="Entrees", goal="Tomorrow's lunch",
         headline="Sirloin for lunch", media=["sirloin-steak-entrees-mitchells-cocoa-florida"],
         text="Make tomorrow's lunch a steak lunch.\n\nUSDA Choice 8 oz sirloin, char grilled to perfection. Add five shrimp, because shrimp goes with everything.\n\nSee you at Mitchell's tomorrow. Open 7am-2pm.",
         fbq="How do you like your steak?",
         tags=["#Steak", "#Sirloin", "#LunchTime", "#SurfAndTurf"]),
    dict(date="2026-11-06", time="AM", pillar="Lunch trays", goal="Friday lunch",
         headline="Jumbo shrimp tray", media=["jumbo-shrimp-tray-mitchells-cocoa-florida"],
         text="Friday calls for shrimp.\n\nTen white jumbo shrimp, hand breaded and fried golden brown, with three hush puppies, fries and a pickle spear. Try it Frank's Buffalo style.\n\nOpen 7am-2pm. Dine in or call ahead for pickup.",
         fbq="Cocktail sauce or Buffalo?",
         tags=["#Shrimp", "#FriedShrimp", "#FridayLunch", "#Seafood"],
         gbp="Friday lunch: the jumbo shrimp tray with ten hand-breaded shrimp, hush puppies and fries. Dine in or call ahead for pickup, 7am-2pm."),
    dict(date="2026-11-07", time="AM", pillar="Weekend brunch", goal="Saturday brunch",
         headline=["Kicken Bourbon", "Chicken"], media=["kicken-bourbon-chicken-entrees-mitchells-cocoa-florida"],
         text="Saturday brunch, the savory way.\n\nKicken Bourbon Chicken: half a pound of grilled chicken breast smothered in sauteed onions and mushrooms and glazed in our own bourbon sauce.\n\nBrunch and mimosas today, 7am-2pm.\n\n" + DRINK,
         fbq="Sweet or savory brunch?",
         tags=["#SaturdayBrunch", "#KickenBourbon", "#Mimosas", "#BrunchTime"]),
]


def clock(t):
    return {"AM": "07:00", "PM": "19:30"}.get(t, t)


def gbp_text(p):
    return p.get("gbp") or re.split(r"\n\n", p["text"])[0]


def build():
    cat = {c["id"]: c for c in json.load(open(os.path.join(ROOT, "media/catalog.json")))["photos"]}
    seen, weeks = set(), {}
    for p in POSTS:
        d = dt.date.fromisoformat(p["date"])
        for m in p["media"] + p.get("igmedia", []):
            assert m in cat, m
            assert m not in seen, "photo repeat: " + m
            seen.add(m)
        assert "delivery" not in p["text"].lower() and "dinner" not in p["text"].lower()
        if "mimosa" in p["text"].lower():
            assert DRINK in p["text"], p["date"]
        t = clock(p["time"])
        tags = BASE_TAGS + p["tags"]
        post = dict(
            id=f"mitchells-{p['date']}", date=p["date"], weekday=d.strftime("%A"),
            pillar=p["pillar"], goal=p["goal"], headline=p["headline"], media=p["media"],
            altText=[cat[m]["altText"] for m in p["media"]], notes=p.get("notes", ""), approved=False,
            variants=dict(
                instagram=dict(time=t, text=f"{p['text']}\n\n{CONTACT}\n\n{' '.join(tags)}", firstComment=""),

                facebook=dict(time=t, text=f"{p['text']}\n\n{p['fbq']}\n\n{CONTACT}", link=SITE),
            ),
            results={},
        )
        if p.get("igmedia"):
            post["variants"]["instagram"]["media"] = p["igmedia"]
        if d.weekday() in GBP_DAYS:
            post["variants"]["gbp"] = dict(
                time="07:15" if p["time"] != "PM" else "19:30",
                text=f"{gbp_text(p)}\n\n{CONTACT}",
                cta="CALL" if "tray" in p["pillar"].lower() else "LEARN_MORE", url=SITE,
                media=p["media"][:1])
        y, w, _ = d.isocalendar()
        weeks.setdefault(f"{y}-W{w:02d}", []).append(post)
    for wid, posts in weeks.items():
        out = dict(week=wid, client="Mitchell's Restaurant", locationId="McxtZDLFfQXmRr0Nx1gb",
                   timezone="America/New_York", status="draft", posts=posts)
        json.dump(out, open(os.path.join(ROOT, f"content/weeks/{wid}.json"), "w"), indent=1)
    n = sum(1 + 1 + ("gbp" in p["variants"]) for ps in weeks.values() for p in ps)
    print(f"{len(POSTS)} posts, {n} platform posts, {len(seen)} photos, weeks: {', '.join(weeks)}")


if __name__ == "__main__":
    build()
