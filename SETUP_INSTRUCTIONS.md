# Setup Guide (One-Time, ~20-25 min)

Maine poora code bana diya hai (content generation + image + reel + auto-post,
sab free). Tumhe bas ye 5 steps karne hain, uske baad rozana automatic chalega.

---

## Step 1: Instagram ko Business/Creator account banao
1. Instagram app -> Settings -> Account type and tools -> Switch to Professional Account
2. "Creator" ya "Business" choose karo (dono chalega)

## Step 2: Facebook Page banao aur link karo
1. facebook.com pe ek naya Page banao (agar nahi hai) -- free hai, 2 min ka kaam
2. Instagram Settings -> Linked accounts -> Facebook -> apne page se connect karo

## Step 3: Facebook Developer App banao
1. developers.facebook.com pe jao -> login apne FB account se
2. "My Apps" -> "Create App" -> type: "Business" choose karo
3. App name kuch bhi de do (e.g. "MyIGAutoPoster")
4. App dashboard me "Add Product" -> **Instagram Graph API** add karo

## Step 4: Access Token aur IG User ID nikalo
1. developers.facebook.com/tools/explorer (Graph API Explorer) kholo
2. Apna App select karo, "User or Page" me apna Facebook Page select karo
3. Permissions me ye add karo:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
4. "Generate Access Token" click karo, login/allow karo
5. Ye token **short-lived** hoga (1 hour) -- isko **long-lived** banane ke liye:
   - Graph API Explorer me hi ek call karo:
     `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN`
   - (APP_ID aur APP_SECRET tumhe App Dashboard -> Settings -> Basic me milega)
   - Response me jo token milega wo ~60 din chalega
6. IG User ID nikalne ke liye:
   - `GET /me/accounts` call karo -> apne Page ki ID milegi
   - Fir `GET /{page-id}?fields=instagram_business_account` call karo
   - Response me jo ID aayegi wahi tumhara **IG_USER_ID** hai

> Agar ye step confusing lage, mujhe batana -- main tumhe exact click-by-click
> bhi guide kar sakta hoon jab tum yaha pahuncho.

## Step 5: GitHub par repo banao aur secrets daalo
1. github.com pe free account banao (agar nahi hai)
2. Naya repository banao (e.g. `ig-auto-poster`), **public ya private dono chalega**
3. Maine jo files banayi hain (generate_post.py, generate_reel.py,
   post_instagram.py, content_bank.py, requirements.txt, .github/workflows/daily-post.yml)
   -- inko us repo me upload/push kar do
4. Repo -> Settings -> Secrets and variables -> Actions -> "New repository secret"
   - `IG_USER_ID` = Step 4 wali ID
   - `IG_ACCESS_TOKEN` = Step 4 wala long-lived token
5. Repo -> Actions tab -> workflow ko enable karo agar prompt aaye

Bas! Uske baad daily automatically (10 AM IST default, .github/workflows/daily-post.yml
me cron change kar sakte ho) ek naya shayari/sad/motivational post + reel
generate aur publish ho jayega.

---

## Note
- Long-lived token ~60 din me expire hota hai -- usko refresh karna padega
  (main chahe to reminder script bhi bana sakta hoon)
- Agar reel ki jagah sirf post chahiye kisi din, workflow me
  `python post_instagram.py image` (ya `reel`) use kar sakte ho
- Content (shayari/sad/motivational lines) `content_bank.py` me hai --
  jitni chaho utni lines add kar sakte ho, script khud rotate kar lega
