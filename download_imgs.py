"""One-shot: download 44 FLUX images to assets/{category}/{slot}.jpg"""
import urllib.request, os, concurrent.futures

BASE = r"C:/Users/jmang/OneDrive/Desktop/Claude access/bc-demos/assets"

FILES = [
  ("electrician/hero.jpg",  "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205138_6404a96a-2385-48c9-ab79-d0411c790798.png"),
  ("electrician/services.jpg","https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205143_cdec397d-2156-4ba9-a2c9-e9f6739aa6c9.png"),
  ("electrician/about.jpg", "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205145_021f5c77-a209-4247-83b5-f2a7f31db5db.png"),
  ("electrician/contact.jpg","https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205146_5879edf7-2808-4213-b8bf-52a0b6f514f9.png"),
  ("landscaper/hero.jpg",   "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205148_a4ddd1fe-dac1-4aef-afb8-f3eba23b2eb1.png"),
  ("landscaper/services.jpg","https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205151_7873f170-f832-44af-85aa-c50cb3e663f8.png"),
  ("landscaper/about.jpg",  "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205409_376c64ab-2f9a-494d-8807-7fbb0996628e.png"),
  ("landscaper/contact.jpg","https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205156_b760dacf-787e-4897-9249-b81d2967f4b3.png"),
  ("excavator/hero.jpg",    "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205158_13f9b87b-b941-4def-8453-c27115112839.png"),
  ("excavator/services.jpg","https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205201_6f4428aa-3b03-4cb5-bd0d-17b40b14040e.png"),
  ("excavator/about.jpg",   "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205203_f45fdb16-efe3-4349-8e5b-b9cf7bf79c59.png"),
  ("excavator/contact.jpg", "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205205_137b143b-ffc8-4441-ab3b-dc29ec766cc6.png"),
  ("drywall/hero.jpg",      "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205208_267e53c5-c4c6-4f60-b0e7-483bb026aedd.png"),
  ("drywall/services.jpg",  "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205211_6f20925c-499d-47cd-b5ff-b70ec56fcb37.png"),
  ("drywall/about.jpg",     "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205213_d1f8a15a-c855-450c-a48d-2ce246b73dee.png"),
  ("drywall/contact.jpg",   "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205215_ffc67e57-17ad-4924-8b11-1f203ee92f73.png"),
  ("concrete/hero.jpg",     "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205218_19490b0a-0656-4225-a9f0-1546223246fe.png"),
  ("concrete/services.jpg", "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205221_4294ec1c-c697-40f9-acc9-569dfce8fb64.png"),
  ("concrete/about.jpg",    "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205223_19e51a3d-05df-4ab2-ad1d-0f49565f632b.png"),
  ("concrete/contact.jpg",  "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205225_04c23a66-62f7-4e36-a469-ba2a9c3386fe.png"),
  ("interior/hero.jpg",     "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205227_63dc9ffe-93fa-46e5-b6a5-02cf14213b25.png"),
  ("interior/services.jpg", "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205230_711247e9-6064-40a1-a4e1-4fb4940aa4fd.png"),
  ("interior/about.jpg",    "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205232_54cf3226-6d1c-4000-b222-07a70fe7b6d1.png"),
  ("interior/contact.jpg",  "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205234_bf104c37-e0c7-4372-817e-bc05f5beb62f.png"),
  ("hvac/hero.jpg",         "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205237_d6d0b75d-70c3-4e10-8aa7-786e4dfa88d4.png"),
  ("hvac/services.jpg",     "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205239_e46d86b3-42fe-423f-83a4-943639288218.png"),
  ("hvac/about.jpg",        "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205241_bdda2dbf-be97-489d-8c4d-9a325f009944.png"),
  ("hvac/contact.jpg",      "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205243_cbe41875-6700-4267-86c0-70360f27f47a.png"),
  ("flooring/hero.jpg",     "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205245_88a54c00-e45d-4ecd-b0f9-9f1e0f906ee6.png"),
  ("flooring/services.jpg", "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205248_66e936f7-509e-4ee4-a8a3-58c872939465.png"),
  ("flooring/about.jpg",    "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205250_44a7d940-572d-4427-a65e-12e971c26451.png"),
  ("flooring/contact.jpg",  "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205252_1b09bcae-3b56-4d11-ab75-35a51c5a2805.png"),
  ("handyman/hero.jpg",     "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205257_4e5f06a4-2fda-4933-9f98-92172bcce11e.png"),
  ("handyman/services.jpg", "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205259_841f2ec4-fd00-4411-8aad-7d1f87315dcf.png"),
  ("handyman/about.jpg",    "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205300_3ef3ed5d-242f-43e0-8660-0934de976d22.png"),
  ("handyman/contact.jpg",  "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205302_01bbd29d-4357-43b3-a1e7-8c99e6eb9bfa.png"),
  ("carpenter/hero.jpg",    "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205305_d8fa1947-6c13-4104-b068-e320d2c71dc4.png"),
  ("carpenter/services.jpg","https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205307_0b823256-dcdb-402e-99b4-f9da66771312.png"),
  ("carpenter/about.jpg",   "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205309_30231176-7856-4e4a-9a47-d0b48b84734e.png"),
  ("carpenter/contact.jpg", "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205311_56a17a0a-62a0-4f16-8027-5efbc3e48dd2.png"),
  ("fence-deck/hero.jpg",   "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205314_968fdd9a-1ece-42e9-b947-76f838bad510.png"),
  ("fence-deck/services.jpg","https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205316_bf2138f7-1eef-4e4f-bef2-8a0f08db7b18.png"),
  ("fence-deck/about.jpg",  "https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205318_024aa4cc-f579-4dc1-a370-811b0e801470.png"),
  ("fence-deck/contact.jpg","https://d8j0ntlcm91z4.cloudfront.net/user_3CxPcyQEDUgTRgi9qfjuwWuCsbQ/hf_20260528_205319_114f5479-b7e4-4e88-9afa-82293ebe6f35.png"),
]

def grab(item):
    rel, url = item
    dest = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    return f"OK {rel} ({os.path.getsize(dest)//1024} KB)"

with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    for r in ex.map(grab, FILES):
        print(r)
print(f"\nDownloaded {len(FILES)} images")
